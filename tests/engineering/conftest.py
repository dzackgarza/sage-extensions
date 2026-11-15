r"""Session abbreviation for the tests of the repository's own pytest plugins.

``sage_extensions.testing.test_lint`` asks every collected test to name only
session names, and it reads the names it allows after the conftests have run: a
directory's ``conftest.py`` binds the abbreviations its tests use, as
``tests/lattices/conftest.py``'s ``card`` does.

The tests here ask what ``sage_extensions.testing.suite_budget`` and
``sage_extensions.testing.test_lint`` do to a run of *other* tests, so the
abbreviation starts a separate pytest over a tree written for it, and reports
the exit status, the outcome of each test the run reported, the failure
messages, and the run's own output.

The timing record has the same shape of question — does a stage-timed call leave
records, and does a run keep its own report log — so ``stage_records_of`` reads
one call's records back out of the record file and ``archived_test_run`` reports
the kinds of file a probe run kept.  Both are bound as builtins for the same
reason: the lint admits exactly the names a directory's ``conftest.py`` binds.
"""

from __future__ import annotations

import builtins
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from sage_extensions import timing as sage_timing

PROBE_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "plugin-probes"


@dataclass(frozen=True)
class ProbeRun:
    r"""What one pytest run over a probe tree reported.

    ``outcomes`` maps each node id the run reported to ``passed`` or
    ``failed``; ``messages`` holds the failure messages, so a test can ask
    which file a finding was reported against; ``transcript`` is the run's own
    output, where a plugin writes a measurement that fails no test.
    """

    exit_status: int
    outcomes: dict[str, str]
    messages: tuple[str, ...]
    transcript: str


def probe_run(tree: dict[str, str], *arguments: str) -> ProbeRun:
    r"""Run pytest over ``tree`` under ``arguments`` and report what it said.

    ``tree`` maps a file name to the file's contents.  ``arguments`` are
    pytest's own, the plugin under test among them.  The probe directory
    carries its own ``pytest.ini``, so the repository's ``addopts`` do not
    reach the run: each plugin is loaded only when a test asks for it, and
    nothing written there is linted or gated by the outer run.
    """
    PROBE_ROOT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="probe-", dir=PROBE_ROOT))
    try:
        (root / "pytest.ini").write_text("[pytest]\n")
        for name, source in tree.items():
            (root / name).write_text(source)
        report = root / "report.jsonl"
        completed = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "-c", str(root / "pytest.ini"),
                f"--report-log={report}",
                *arguments,
                str(root),
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        records = [
            json.loads(line) for line in report.read_text().splitlines() if line.strip()
        ]
        return ProbeRun(
            exit_status=completed.returncode,
            outcomes=_outcomes(records),
            messages=tuple(
                message for message in map(_failure_message, records) if message
            ),
            transcript=completed.stdout + completed.stderr,
        )
    finally:
        shutil.rmtree(root)


def _failure_message(record: dict) -> str:
    r"""What a failure said: its crash's message, or its long representation when that is text."""
    longrepr = record.get("longrepr")
    if isinstance(longrepr, dict):
        crash = longrepr.get("reprcrash")
        return crash.get("message", "") if isinstance(crash, dict) else ""
    return longrepr if isinstance(longrepr, str) else ""


def _outcomes(records: list[dict]) -> dict[str, str]:
    r"""Each node id the run reported, and whether its setup or call failed."""
    reported = {
        record["nodeid"] for record in records if record.get("when") in ("setup", "call")
    }
    failed = {
        record["nodeid"] for record in records
        if record.get("when") in ("setup", "call") and record.get("outcome") == "failed"
    }
    return {nodeid: "failed" if nodeid in failed else "passed" for nodeid in sorted(reported)}


def pytest_configure(config) -> None:
    r"""Bind the abbreviation for this session, as the lint documents.

    ``sage_extensions.testing.test_lint`` admits a name a directory's
    ``conftest.py`` binds as a builtin and reads that set after the conftests
    have run; ``tests/lattices/conftest.py`` binds ``card`` the same way.  The
    name is removed when the session ends, so the binding lasts exactly as long
    as the tests that name it.
    """
    builtins.probe_run = probe_run
    builtins.stage_records_of = stage_records_of
    builtins.archived_test_run = archived_test_run


def pytest_unconfigure(config) -> None:
    r"""Remove the session's abbreviation, leaving ``builtins`` as it was found."""
    del builtins.probe_run
    del builtins.stage_records_of
    del builtins.archived_test_run


def stage_records_of(invoke):
    r"""The stage records one call appends, read back from this process's own file.

    ``invoke`` is the call — a stage-timed call of the library — and the records
    are read from ``sage_extensions.timing.record_path()`` after it, from the
    byte offset that file had before, so a test reads the records of its own
    call rather than of any earlier call in the same process.  Reading the file
    is the point: the record is what a timing question is answered from, so a
    test that held the durations in memory would prove nothing about it.
    """
    path = sage_timing.record_path()
    before = path.stat().st_size if path is not None and path.is_file() else 0
    invoke()
    return sage_timing.read_stage_records(path, after=before)


def archived_test_run(tree, *arguments):
    r"""Run pytest over ``tree`` under the timing plugin and report what it kept.

    The run keeps its report log and JUnit file per run
    (``sage_extensions.testing.timing_record``), so this starts a run whose
    record directory is a fresh one and reports the *kinds* of file it left
    there: ``("junit", "run")` for a run that wrote both.  The directory is the
    plugin's own setting (``SAGE_EXTENSIONS_TIMING_DIR``), so the run under test
    writes beside the real record directory, never into it, and the probe tree
    carries its own ``pytest.ini`` so the repository's ``addopts`` — which want
    a host's ``pytest-reportlog`` — do not reach it.
    """
    PROBE_ROOT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="timing-", dir=PROBE_ROOT))
    kept = Path(tempfile.mkdtemp(prefix="record-", dir=PROBE_ROOT))
    try:
        (root / "pytest.ini").write_text("[pytest]\n")
        for name, source in tree.items():
            written = root / name
            written.parent.mkdir(parents=True, exist_ok=True)
            written.write_text(source)
        environment = dict(os.environ, SAGE_EXTENSIONS_TIMING_DIR=str(kept))
        subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "-c", str(root / "pytest.ini"),
                "-p", "sage_extensions.testing.timing_record",
                *arguments,
                str(root),
            ],
            cwd=root,
            capture_output=True,
            text=True,
            env=environment,
        )
        return tuple(sorted(entry.stem.split("-")[0] for entry in kept.iterdir()))
    finally:
        shutil.rmtree(root)
        shutil.rmtree(kept)
