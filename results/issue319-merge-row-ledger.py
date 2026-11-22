r"""Merge the acceptance's raw evidence into its ledger, one line per attempted row.

The ledger (`results/issue319-rows-ledger.jsonl`) is #319's durable record: every
attempt at every row of `tests/enriques_polarization_rows_by_card.py`, with the
card, the dimension, the value the public call returned or the exception it raised,
the state, the elapsed time and the revision.  It is append-only, and this script
is how it is appended: it reads the evidence files the runs leave behind and adds
the lines they carry, skipping a line the ledger already holds (same row, revision,
state and elapsed time), so running it twice adds nothing.

    python3 results/issue319-merge-row-ledger.py <evidence>...

An evidence file is one of

* a run's printed log (`ROW <id>  [STATE]` blocks, with the `expected … call …`
  line beneath), which is what a run leaves when it predates the per-row record;
* a run's `rows-<revision12>-<pid>.jsonl` record, which the module writes since
  `1162f1d`, one JSON object a row;
* the ledger itself, so the script is idempotent.

A row's value is never inferred: a block that states no value is recorded with
`returned: null` and the state it reached.
"""

import json
import re
import sys
from pathlib import Path

LEDGER = Path(__file__).with_name("issue319-rows-ledger.jsonl")

#: The module's block header and its value line.
_ROW_HEADER = re.compile(r"^ROW (\S+)  \[(\w+)\]")
_ROW_VALUES = re.compile(r"^\s+expected (\d+)  call (\S+)   \((\S+) s\)")
_ROW_PLACEMENT = re.compile(r"^\s+lattice (\S.*?)   group (\S.*)$")
_ROW_DETAIL = re.compile(r"^\s+(?:BROKEN|UNDECIDED|FAIL|MISSING): (.*)$")
_ROW_SINGLE = re.compile(r"^@@ROW@@ (\{.*\})$")
_LOG_TREE = re.compile(r"\b([0-9a-f]{40})\b")
_LOG_STARTED = re.compile(r"^started: (\S+)$")


def _quantity(identifier):
    r"""The dimension a row's identifier names: the quantity, and the degree for 0128."""
    parts = identifier.split(":")
    if parts[0] == "0128":
        return parts[1], int(parts[2])
    return parts[-1], None


def _line(identifier, state, revision, measured_at, expected=None, returned=None,
          detail=None, elapsed=None, lattice=None, group=None, source=None):
    quantity, degree = _quantity(identifier)
    return {
        "row": identifier,
        "card": identifier.split(":")[0],
        "quantity": quantity,
        "degree": degree,
        "lattice": lattice,
        "group": group,
        "expected": expected,
        "returned": returned,
        "detail": detail,
        "state": state,
        "elapsed": elapsed,
        "revision": revision,
        "measured_at": measured_at,
        "source": source,
    }


def _from_log(path):
    r"""Every row block a printed log carries, at the revision the log states.

    A block is the module's `ROW <id>  [STATE]` header followed by its `expected …
    call …` line, the lattice and group it names, and a state detail when the state
    is not PASS; a single-row run writes an `@@ROW@@` object instead.  The log stops
    at its SUMMARY, whose `FAIL: 0` line is a count and not a row's detail.
    """
    text = path.read_text(encoding="utf-8").splitlines()
    revision = None
    started = None
    for line in text:
        tree = _LOG_TREE.search(line)
        if tree and revision is None:
            revision = tree.group(1)
        beginning = _LOG_STARTED.match(line)
        if beginning and started is None:
            started = beginning.group(1)
    lines = []
    current = None

    def finish(block):
        if block is None or ("expected" not in block and "detail" not in block):
            return
        lines.append(_line(
            block["id"], block["state"], revision, started,
            expected=block.get("expected"), returned=block.get("returned"),
            detail=block.get("detail"), elapsed=block.get("elapsed"),
            lattice=block.get("lattice"), group=block.get("group"),
            source=path.name,
        ))

    for raw in text:
        single = _ROW_SINGLE.match(raw)
        if single:
            finish(current)
            current = None
            block = json.loads(single.group(1))
            finish({
                "id": block["id"], "state": block["state"],
                "expected": block.get("expected"), "returned": block.get("computed"),
                "detail": block.get("detail"), "elapsed": block.get("elapsed"),
                "lattice": block.get("lattice"), "group": block.get("group"),
            })
            continue
        if raw.startswith("SUMMARY") or raw.startswith("COVERAGE"):
            finish(current)
            current = None
            continue
        header = _ROW_HEADER.match(raw)
        if header:
            finish(current)
            current = {"id": header.group(1), "state": header.group(2)}
            continue
        if current is None:
            continue
        values = _ROW_VALUES.match(raw)
        if values:
            current["expected"] = int(values.group(1))
            current["returned"] = None if values.group(2) == "-" else int(values.group(2))
            current["elapsed"] = float(values.group(3))
            continue
        placement = _ROW_PLACEMENT.match(raw)
        if placement:
            current["lattice"] = placement.group(1)
            current["group"] = placement.group(2)
            continue
        detail = _ROW_DETAIL.match(raw)
        if detail:
            current["detail"] = detail.group(1)
    finish(current)
    return lines


def _from_record(path):
    r"""Every line a run's own per-row record carries, already keyed by revision."""
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        attempt = json.loads(raw)
        if "row" in attempt:
            attempt.setdefault("source", path.name)
            lines.append(attempt)
            continue
        lines.append(_line(
            attempt["id"], attempt["state"], attempt.get("revision"), None,
            expected=attempt.get("expected"), returned=attempt.get("computed"),
            detail=attempt.get("detail"), elapsed=attempt.get("elapsed"),
            lattice=attempt.get("lattice"), group=attempt.get("group"),
            source=path.name,
        ))
    return lines


def _key(attempt):
    r"""What makes two lines the same attempt: the row, the revision, the state and the time."""
    return (attempt["row"], attempt["revision"], attempt["state"], attempt["elapsed"])


def main(argv):
    known = []
    if LEDGER.is_file():
        known = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = {_key(attempt) for attempt in known}
    added = 0
    for name in argv:
        path = Path(name)
        reader = _from_record if path.suffix == ".jsonl" and "issue319-rows-ledger" not in path.name else _from_log
        if path.name.startswith("issue319-rows-ledger"):
            continue
        for attempt in reader(path):
            if _key(attempt) in seen:
                continue
            seen.add(_key(attempt))
            known.append(attempt)
            added += 1
    LEDGER.write_text(
        "".join(json.dumps(attempt, ensure_ascii=False) + "\n" for attempt in known),
        encoding="utf-8",
    )
    print(f"{added} attempts appended, {len(known)} lines in {LEDGER}")


if __name__ == "__main__":
    main(sys.argv[1:])
