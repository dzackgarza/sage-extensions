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
records, does a cached call run its stage once, and does a run keep its own
report log — so ``stage_records_of`` reads one call's records back out of the
record file, ``kept_test_run`` reports the files a probe run kept, and
``probe_run`` reports the log a run's own logging configuration filled.  All are
bound as builtins for the same reason: the lint admits exactly the names a
directory's ``conftest.py`` binds.
"""

from __future__ import annotations

import builtins
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from sage_extensions import timing as sage_timing

SOURCE_TREE = Path(__file__).resolve().parents[2]
PROBE_ROOT = SOURCE_TREE / ".tmp" / "plugin-probes"


@dataclass(frozen=True)
class ProbeRun:
    r"""What one pytest run over a probe tree reported.

    ``outcomes`` maps each node id the run reported to ``passed`` or
    ``failed``; ``messages`` holds the failure messages, so a test can ask
    which file a finding was reported against; ``transcript`` is the run's own
    output, where a plugin writes a measurement that fails no test; ``log`` is
    the file the probe's own configuration names with ``log_file``, which is
    where a library's own logging configuration decides whether a record
    arrives.
    """

    exit_status: int
    outcomes: dict[str, str]
    messages: tuple[str, ...]
    transcript: str
    log: str


def probe_run(tree: dict[str, str], *arguments: str) -> ProbeRun:
    r"""Run pytest over ``tree`` under ``arguments`` and report what it said.

    ``tree`` maps a file name to the file's contents.  ``arguments`` are
    pytest's own, the plugin under test among them.  The probe directory
    carries its own ``pytest.ini``, so the repository's ``addopts`` do not
    reach the run: each plugin is loaded only when a test asks for it, and
    nothing written there is linted or gated by the outer run.  That
    configuration names the run's log ``pytest.log``, so every probe writes the
    file :attr:`ProbeRun.log` reads and a run that writes none is an error
    rather than an empty string.
    """
    PROBE_ROOT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="probe-", dir=PROBE_ROOT))
    try:
        (root / "pytest.ini").write_text("[pytest]\nlog_file = pytest.log\n")
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
        written = root / "pytest.log"
        return ProbeRun(
            exit_status=completed.returncode,
            outcomes=_outcomes(records),
            messages=tuple(
                message for message in map(_failure_message, records) if message
            ),
            transcript=completed.stdout + completed.stderr,
            log=written.read_text(),
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
    builtins.kept_test_run = kept_test_run


def pytest_unconfigure(config) -> None:
    r"""Remove the session's abbreviation, leaving ``builtins`` as it was found."""
    del builtins.probe_run
    del builtins.stage_records_of
    del builtins.kept_test_run


@dataclass(frozen=True)
class RecordFile:
    r"""One file the timing record wrote, as its own name and its own lines say.

    ``kind``, ``commit`` and ``stamp`` are the three parts of the file's name,
    ``<kind>-<commit>-<stamp>.<suffix>``; ``head`` is the commit of this
    checkout read from git by the test side, so a test can ask whether the
    record names the commit it came from without asking the library that wrote
    it; ``records`` are the JSONL lines the call under test appended, empty for
    a file that carries no lines of its own.
    """

    name: str
    kind: str
    suffix: str
    commit: str
    stamp: str
    head: str
    records: tuple[dict, ...]


def _head_commit() -> str:
    r"""The commit of this checkout, read by git here and not by the library."""
    completed = subprocess.run(
        ("git", "-C", str(SOURCE_TREE), "rev-parse", "HEAD"),
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _sizes(directory: Path) -> dict[str, int]:
    r"""Each file of ``directory`` and how many bytes it holds."""
    return {
        entry.name: entry.stat().st_size for entry in directory.iterdir() if entry.is_file()
    }


def _record_file(path: Path, *, after: int = 0) -> RecordFile:
    r"""The file at ``path``, read by its name and by the lines past ``after``."""
    stem, _, suffix = path.name.partition(".")
    kind, commit, stamp = stem.split("-")
    return RecordFile(
        name=path.name,
        kind=kind,
        suffix=suffix,
        commit=commit,
        stamp=stamp,
        head=_head_commit(),
        records=sage_timing.read_stage_records(path, after=after) if suffix == "jsonl" else (),
    )


def stage_records_of(invoke) -> RecordFile:
    r"""The record file one stage-timed call appended to, read back from disk.

    ``invoke`` is the call.  The file is found by what the directory held before
    and after — the one file that grew — and not through the writer's own
    :func:`sage_extensions.timing.record_path`, so a name the writer got wrong
    is a name this reads and a test can refuse; and ``records`` are the lines
    that call appended, not those of an earlier call in the same process.
    """
    directory = sage_timing.timing_directory()
    before = _sizes(directory)
    invoke()
    grown = sorted(
        name for name, size in _sizes(directory).items() if size > before.get(name, 0)
    )
    assert len(grown) == 1, (
        f"one stage-timed call should append to one record file, but these grew: {grown}"
    )
    return _record_file(directory / grown[0], after=before.get(grown[0], 0))


def kept_test_run(tree, *arguments) -> tuple[RecordFile, ...]:
    r"""Run a probe pytest under the timing plugin and report the files it kept.

    The plugin keeps a run's report log and JUnit file where every run keeps
    them, so this asks what appeared in the record directory while the probe
    ran.  The probe tree, its isolated ``pytest.ini`` and the report log the run
    wrote are ``probe_run``'s — this adds the plugin and the JUnit file's own
    option to the run and reads the directory, rather than starting a second
    pytest of its own.
    """
    directory = sage_timing.timing_directory()
    before = set(_sizes(directory))
    probe_run(
        tree,
        "-p", "sage_extensions.testing.timing_record",
        "--junit-xml=junit.xml",
        *arguments,
    )
    return tuple(
        _record_file(directory / name) for name in sorted(set(_sizes(directory)) - before)
    )
