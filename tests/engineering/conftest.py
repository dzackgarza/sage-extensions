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
records, does a cached call run its stage once, does a run keep its own report
log, and do two runs started together keep two — so ``stage_records_of`` reads
one call's records back out of the record file, ``kept_test_run`` reports the
files a probe run kept and what that run exited with, ``simultaneous_test_runs``
starts one probe per tree before waiting on any of them, and ``probe_run``
reports the log a run's own logging configuration filled.  All are bound as
builtins for the same reason: the lint admits exactly the names a directory's
``conftest.py`` binds.

The acceptance drivers are instruments of the same kind: each takes one row of
an orbit computation and reports what the row did.  ``incidence_row_outcome``
is the Γ_{Co,2} driver's row step on one subgroup under one cap, and
``incidence_row_contract`` is the same driver's contract on a relation it is
handed -- the relation is the input, so a test asks what the driver makes of a
broken one rather than handing it the answer.  ``RowStatus`` is that driver's
own vocabulary of row statuses, bound for the same reason: the lint admits
exactly the names a directory's ``conftest.py`` binds.
"""

from __future__ import annotations

import builtins
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sage_extensions import timing as sage_timing
from sage_extensions.testing.category_graph import read as read_category_graph

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

    ``pid`` and ``launched`` are what the run's own record files are found by:
    the pid is the process that kept them, which is the child this module
    started, and ``launched`` is the wall clock just before it started, so a
    file an earlier run of a reused pid left behind is not mistaken for this
    one's.
    """

    exit_status: int
    outcomes: dict[str, str]
    messages: tuple[str, ...]
    transcript: str
    log: str
    pid: int
    launched: float


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
    root = _probe_directory(tree)
    try:
        launched = time.time()
        process = subprocess.Popen(
            _probe_command(root, arguments),
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        output, _ = process.communicate()
        return _probe_report(
            root,
            process.returncode,
            output,
            pid=process.pid,
            launched=launched,
        )
    finally:
        shutil.rmtree(root)


def _probe_directory(tree: dict[str, str]) -> Path:
    r"""A probe tree on disk: its files, and the configuration the run is given.

    ``log_file`` is the probe's own, so every probe writes the log
    :attr:`ProbeRun.log` reads and a run that writes none is an error rather than
    an empty string.
    """
    PROBE_ROOT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="probe-", dir=PROBE_ROOT))
    (root / "pytest.ini").write_text("[pytest]\nlog_file = pytest.log\n")
    for name, source in tree.items():
        (root / name).write_text(source)
    return root


def _probe_command(root: Path, arguments: tuple[str, ...]) -> list[str]:
    r"""The command that runs pytest over the probe tree at ``root``."""
    return [
        sys.executable, "-m", "pytest",
        "-c", str(root / "pytest.ini"),
        f"--report-log={root / 'report.jsonl'}",
        *arguments,
        str(root),
    ]


def _probe_report(root: Path, exit_status: int, output: str, *, pid: int, launched: float) -> ProbeRun:
    r"""What the run in ``root`` reported, read off its own files."""
    records = [
        json.loads(line)
        for line in (root / "report.jsonl").read_text().splitlines()
        if line.strip()
    ]
    return ProbeRun(
        exit_status=exit_status,
        outcomes=_outcomes(records),
        messages=tuple(message for message in map(_failure_message, records) if message),
        transcript=output,
        log=(root / "pytest.log").read_text(),
        pid=pid,
        launched=launched,
    )


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


def declared_category_graph():
    r"""The category graph this checkout declares, read out of its source.

    ``just category-graph`` prints the same graph.  The reader parses the source
    with ``ast`` and imports nothing of the preamble, so a test of it asks about
    the declarations the tree writes rather than about the classes Sage joined
    from them; the checkout it reads is this file's own, whether the run works
    in a worktree or in the repository.
    """
    return read_category_graph(SOURCE_TREE)


def pytest_configure(config) -> None:
    r"""Bind the abbreviation for this session, as the lint documents.

    ``sage_extensions.testing.test_lint`` admits a name a directory's
    ``conftest.py`` binds as a builtin and reads that set after the conftests
    have run; ``tests/lattices/conftest.py`` binds ``card`` the same way.  The
    name is removed when the session ends, so the binding lasts exactly as long
    as the tests that name it.
    """
    builtins.declared_category_graph = declared_category_graph
    builtins.probe_run = probe_run
    builtins.stage_records_of = stage_records_of
    builtins.kept_test_run = kept_test_run
    builtins.simultaneous_test_runs = simultaneous_test_runs
    builtins.incidence_row_outcome = incidence_row_outcome
    builtins.incidence_row_contract = incidence_row_contract
    builtins.RowStatus = _script("coble_row_status").RowStatus


def pytest_unconfigure(config) -> None:
    r"""Remove the session's abbreviation, leaving ``builtins`` as it was found."""
    del builtins.declared_category_graph
    del builtins.probe_run
    del builtins.stage_records_of
    del builtins.kept_test_run
    del builtins.simultaneous_test_runs
    del builtins.incidence_row_outcome
    del builtins.incidence_row_contract
    del builtins.RowStatus


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


RECORD_NAME = re.compile(
    r"(?P<kind>[-\w]+)-(?P<commit>[0-9a-f]{12})-(?P<start>\d{8}T\d{12}Z)-(?P<pid>\d+)"
    r"\.(?P<suffix>[a-z]+)"
)
r"""A record file's whole name: kind, commit, start, pid and suffix.

A file whose name this does not match is not a record of a run -- the probe
directories, the report logs and the JUnit files keep their own names -- so the
search below selects by the pattern rather than reading a name and handling the
failure.
"""


def _record_name_parts(name: str):
    r"""A record file's name matched by ``RECORD_NAME``: kind, commit, start, pid, suffix.

    The one parse of a record's name: every reader -- the start's moment, the
    pid, the kind, the commit, the suffix -- asks here, so a name cannot be read
    one way by the selection and another by the reader, and a file that is not a
    record's is refused once rather than handled by each reader.
    """
    parts = RECORD_NAME.fullmatch(name)
    assert parts is not None, f"{name} is not the name of a timing record"
    return parts


def _stamp_of(name: str) -> tuple[float, str]:
    r"""A record file's start, as a wall clock, and the pid its stamp ends with."""
    parts = _record_name_parts(name)
    moment = datetime.strptime(parts["start"], "%Y%m%dT%H%M%S%fZ").replace(tzinfo=timezone.utc)
    return moment.timestamp(), parts["pid"]


def _record_file(path: Path, *, after: int = 0) -> RecordFile:
    r"""The file at ``path``, read by its name and by the lines past ``after``."""
    parts = _record_name_parts(path.name)
    return RecordFile(
        name=path.name,
        kind=parts["kind"],
        suffix=parts["suffix"],
        commit=parts["commit"],
        stamp=parts["start"] + "-" + parts["pid"],
        head=_head_commit(),
        records=(
            sage_timing.read_stage_records(path, after=after)
            if parts["suffix"] == "jsonl"
            else ()
        ),
    )


def stage_records_of(invoke) -> RecordFile:
    r"""The record file one stage-timed call appended to, read back from disk.

    ``invoke`` is the call, and the file is this process's own
    (:func:`sage_extensions.timing.record_path`): another test worker writes its
    own, under a pid of its own, so nothing this reads can be another process's
    record.  The name is required to exist and to grow — a stage-timed call that
    wrote no record is the finding, not an empty read — and ``records`` are the
    lines that call appended, not those of an earlier call in this process.
    """
    path = sage_timing.record_path()
    before = path.stat().st_size if path.is_file() else 0
    invoke()
    assert path.is_file(), (
        f"the stage-timed call wrote no record: there is no file at {path}, which is the name this "
        "process's record is required to have"
    )
    after = path.stat().st_size
    assert after > before, (
        f"the stage-timed call appended nothing to {path}, which held {before} bytes before it"
    )
    return _record_file(path, after=before)


def _kept_by(directory: Path, probe: ProbeRun) -> tuple[Path, ...]:
    r"""The record files ``probe`` kept, found by the probe's own stamp.

    Not by what the directory held before and after the run: the repository's
    own runs are parallel, and another worker's file appearing in that window
    would be read as this probe's.  A file is this probe's when its stamp ends
    with the pid of the process this module started and its start is at or after
    the moment that process was started.
    """
    selected = []
    for name in sorted(_sizes(directory)):
        if RECORD_NAME.fullmatch(name) is None:
            continue
        start, pid = _stamp_of(name)
        if pid == str(probe.pid) and start >= probe.launched:
            selected.append(directory / name)
    return tuple(selected)


@dataclass(frozen=True)
class KeptRun:
    r"""One probe run, and the record files that run's own stamp names.

    ``probe`` is what the run itself reported — its exit status among it — so a
    test can refuse a run that failed anywhere, and not only in the assertion it
    went looking for.
    """

    files: tuple[RecordFile, ...]
    probe: ProbeRun


PLUGIN_ARGUMENTS = ("-p", "sage_extensions.testing.timing_record", "--junit-xml=junit.xml")
r"""The arguments that load the plugin under test and ask the run for its JUnit file."""


def kept_test_run(tree, *arguments) -> KeptRun:
    r"""Run a probe pytest under the timing plugin and report the files it kept.

    The plugin keeps a run's report log and JUnit file where every run keeps
    them, so this asks what appeared in the record directory while the probe
    ran.  The probe tree, its isolated ``pytest.ini`` and the report log the run
    wrote are ``probe_run``'s — this adds the plugin and the JUnit file's own
    option to the run and reads the directory, rather than starting a second
    pytest of its own.
    """
    directory = sage_timing.timing_directory()
    probe = probe_run(tree, *PLUGIN_ARGUMENTS, *arguments)
    return KeptRun(
        files=tuple(_record_file(path) for path in _kept_by(directory, probe)),
        probe=probe,
    )


def simultaneous_test_runs(*trees: dict[str, str]) -> tuple[tuple[RecordFile, ...], tuple[ProbeRun, ...]]:
    r"""Run one probe pytest per tree at once, and report the files they kept.

    Two runs started together is the case a record's name has to survive: both
    begin within the same second, so a name stamped to the second is one name.
    Every probe is started before any is waited on, which is what makes them
    concurrent, and each keeps its own report log and JUnit file through the same
    plugin arguments ``kept_test_run`` uses.
    """
    directory = sage_timing.timing_directory()
    roots = [_probe_directory(tree) for tree in trees]
    try:
        launched = time.time()
        processes = [
            subprocess.Popen(
                _probe_command(root, PLUGIN_ARGUMENTS),
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for root in roots
        ]
        probes = []
        for root, process in zip(roots, processes):
            output, _ = process.communicate()
            probes.append(
                _probe_report(root, process.returncode, output, pid=process.pid, launched=launched)
            )
        kept = sorted(path for probe in probes for path in _kept_by(directory, probe))
        return (tuple(_record_file(path) for path in kept), tuple(probes))
    finally:
        for root in roots:
            shutil.rmtree(root)


# The Coble acceptance drivers ------------------------------------------------
#
# A driver is a script, not part of the installed package: it imports the
# vocabulary of row statuses from the file beside it, so each is loaded by path
# with that name registered first.

DRIVER_SOURCE = SOURCE_TREE / "tests"


def _script(name: str):
    r"""The module the file ``<name>.py`` of ``tests/`` defines, loaded under that name.

    The drivers are scripts: each imports the shared row-status vocabulary by
    the name of the file beside it, so the vocabulary is registered first and
    the driver then resolves it.  A module this session has already loaded is
    the one returned, so the vocabulary a test names and the vocabulary the
    driver answers with are the same members.
    """
    loaded = sys.modules.get(name)
    if loaded is not None:
        return loaded
    path = DRIVER_SOURCE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _incidence_row_driver():
    r"""The Γ_{Co,2} incidence-row driver, with the row statuses it shares."""
    _script("coble_row_status")
    return _script("coble_gamma_co_2_incidence_rows")


def incidence_row_outcome(lattice, subgroup, label, cap):
    r"""What the Γ_{Co,2} driver's row step reports for one row of ``subgroup`` under ``cap``.

    The answer is the driver's own outcome: its status, the clause or cap that
    decided it, and the row's counts when it decided.  The cap is the caller's
    budget for the row's step, so a cap of zero seconds is a row with no time
    to run.
    """
    return _incidence_row_driver().run_row(lattice, subgroup, label, cap)


def incidence_row_contract(lattice, subgroup, lines, planes, incidences):
    r"""What the Γ_{Co,2} driver's contract makes of one relation of a row's vertices.

    ``lines``, ``planes`` and ``incidences`` are the row's own data: the vertices
    the row returned and the edges it joined them with.  The row step's contract
    is the driver's statement about that relation, so a test hands it the
    relation instead of the status the contract might have reached.
    """
    return _incidence_row_driver().row_contract(
        lattice, subgroup, "row", lines, planes, incidences
    )
