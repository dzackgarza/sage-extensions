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
reports the log a run's own logging configuration filled.  ``installed_wheel_record``
asks the same question of an installation that is not a checkout: it builds a
wheel of this checkout, installs it outside the tree and reports the timed call
that wheel makes and the record it writes.  All are bound as builtins for the
same reason: the lint admits exactly the names a directory's ``conftest.py``
binds.

The declared category graph has the same shape of question, asked of a tree
written for it: ``declared_graph_report`` runs ``just category-graph`` -- the
recipe ``AGENTS.md`` names, not the module -- over a source tree the test
supplies, so the recipe's argument forwarding and its choice of interpreter are
what the tests exercise; ``declared_graph_document`` is the document the view
writes to the file ``--output`` names, required to exist so a view that refuses
the tree fails the test that asked for its data; and ``declared_graph_figures``
reads a view's printed figures back as numbers, because the answer ``shape`` and
``cells`` give is the reading they print, which ``CAT-25`` reads a change's
category-graph delta off; ``declared_graph_breadth`` is that reading's breadth
rows, one count per category; and ``declared_graph_reading`` is every other
view's answer read back in the form it answers in, so a view is tested by what
it says and not by its exit status.

The acceptance drivers are instruments of the same kind: each takes one row of
an orbit computation and reports what the row did.  ``incidence_row_outcome``
is the Γ_{Co,2} driver's row step on one subgroup under one cap, and
``incidence_row_contract`` is the same driver's contract on a relation it is
handed -- the relation is the input, so a test asks what the driver makes of a
broken one rather than handing it the answer -- and ``incidence_edge_containment``
is that contract's edge clause on one line/plane pair of a lattice, and
``incidence_rows_exit`` runs that driver's ``main`` on one argument list and
answers the exit status it reports.  ``RowStatus`` is that driver's
own vocabulary of row statuses, bound for the same reason: the lint admits
exactly the names a directory's ``conftest.py`` binds.
"""

from __future__ import annotations

import builtins
import importlib.util
import json
import os
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


GRAPH_ROOT = SOURCE_TREE / ".tmp" / "category-graph-probes"


@dataclass(frozen=True)
class GraphReport:
    r"""What one run of the declared-category-graph recipe said.

    ``exit_status`` is the run's; ``output`` is what it wrote to standard
    output, which is the view's own answer for the views that print one and
    empty for a view whose data went to ``--output``; ``transcript`` is that
    together with the diagnostics, so a test that fails says what the tool said
    about the tree it was given.
    """

    exit_status: int
    output: str
    transcript: str


def declared_graph_report(tree: dict[str, str], view: str, *arguments: str) -> GraphReport:
    r"""Run ``just category-graph`` over a source tree written for it.

    ``tree`` maps a path inside the tree to that file's source, so the run reads
    declarations written for the test and no file of this checkout: a category
    renamed here changes no assertion there.  ``view`` and ``arguments`` are the
    recipe's own -- the view as its first parameter, then what that view takes
    (``--operation``, ``--select``), and the tree last -- because the recipe is
    the subject: it supplies ``--format`` from its view parameter and drops that
    parameter before forwarding the rest, and it chooses the interpreter the
    view needs, so a run of it here fails if either is wrong.  ``shape``,
    ``cells``, ``audit`` and ``topology`` load Sage's graph library and the
    recipe runs them under the Sage interpreter; the rest run under ``python3``.
    The tree is written under ``.tmp/`` and removed.
    """
    root = _declared_graph_tree(tree)
    try:
        return _declared_graph_recipe(root, view, *arguments)
    finally:
        shutil.rmtree(root)


def _declared_graph_tree(tree: dict[str, str]) -> Path:
    r"""A source tree on disk: the files the test wrote, under ``.tmp/``."""
    GRAPH_ROOT.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="declared-graph-", dir=GRAPH_ROOT))
    for name, source in tree.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)
    return root


def _declared_graph_recipe(root: Path, view: str, *arguments: str) -> GraphReport:
    r"""One run of the recipe the repository spells, from the checkout, over ``root``."""
    finished = subprocess.run(
        ("just", "category-graph", view, *arguments, str(root)),
        capture_output=True,
        text=True,
        cwd=SOURCE_TREE,
    )
    return GraphReport(
        exit_status=finished.returncode,
        output=finished.stdout,
        transcript=f"{finished.stdout}{finished.stderr}",
    )


def declared_graph_document(tree: dict[str, str], view: str, *arguments: str) -> dict:
    r"""The document one data view of the graph wrote for ``tree``.

    The document is the file ``--output`` names, not what the view printed, so a
    view that answers by writing reads here as it reads in use.  A view that
    refuses the tree, or fails on it, leaves no document; the assertion carries
    the run's exit status and its own words rather than letting the caller read
    a missing file.
    """
    root = _declared_graph_tree(tree)
    try:
        document = root / "report.json"
        report = _declared_graph_recipe(root, view, *arguments, "--output", str(document))
        assert report.exit_status == 0, f"the {view} view: {report.transcript}"
        assert document.is_file(), (
            f"the {view} view wrote no report of the tree: exit status "
            f"{report.exit_status}: {report.transcript}"
        )
        return json.loads(document.read_text())
    finally:
        shutil.rmtree(root)


def declared_graph_figures(tree: dict[str, str], view: str) -> dict[str, int]:
    r"""The figures a view states, read back as numbers.

    ``shape`` and ``cells`` answer with a reading rather than a document --
    ``AGENTS.md`` ``CAT-25`` reads a change's category-graph delta off them -- so
    the figures they print *are* the answer, and a test asserts the numbers the
    tree's own declarations give.  Each is read from the answer: the header
    figures by name, and each heading's own count from its ``## heading (n)``.
    A view that states no such figure leaves it out, so a figure the answer
    stops stating is a failure of the test that asked for it.
    """
    report = declared_graph_report(tree, view)
    assert report.exit_status == 0, f"the {view} view: {report.transcript}"
    return _figures(report.output)


def declared_graph_breadth(tree: dict[str, str]) -> dict[str, int]:
    r"""Each category the shape view gives a breadth to, and the count it gives it.

    The view states one row per node it counts into -- the count, then the
    category -- so a node the answer omits is a node no declaration it read
    names, and a node whose count grew is a node more categories claim.
    """
    report = declared_graph_report(tree, "shape")
    assert report.exit_status == 0, f"the shape view: {report.transcript}"
    return {
        name: int(count)
        for count, name in re.findall(r"(?m)^ +(\d+) +(\S+)$", _section(report.output, "Breadth"))
    }


def _section(output: str, heading: str) -> str:
    r"""The text of the answer's ``## heading`` section, empty when it states none."""
    for section in output.split("\n## ")[1:]:
        if section.startswith(heading):
            return section
    return ""


def declared_graph_reading(tree: dict[str, str], view: str, *arguments: str):
    r"""The answer a view gives for a tree written for it, read back as data.

    A view answers in its own form -- a table of rows with the supercategories
    each states, a map from a supercategory to the categories claiming it, the
    owned categories naming a Sage supercategory, the defects the audit finds,
    the edges the drawing writes, the operations each category reports, the
    figures a reading states, the category an operation is defined at -- and
    this returns that form, so a test asserts what the view said rather than
    that a process exited.  ``arguments`` are the recipe's parameters after the
    view, so a view that takes one (``routes --operation NAME``) is asked the
    question it is there to answer.
    """
    report = declared_graph_report(tree, view, *arguments)
    assert report.exit_status == 0, f"the {view} view: {report.transcript}"
    return _READINGS[view](report.output)


def _table_reading(output: str) -> dict[str, tuple[str, ...]]:
    r"""Each row the table writes: the category, and the supercategories it states."""
    return {
        row: tuple(stated.split(", "))
        for row, stated in re.findall(r"(?m)^(\S+) {2,}(\S.*)$", output)
    }


def _claimants_reading(output: str) -> dict[str, tuple[str, ...]]:
    r"""Each supercategory the grouped view lists, and the categories under it."""
    groups: dict[str, tuple[str, ...]] = {}
    head = ""
    for line in output.splitlines():
        if line.startswith("    ") and head:
            groups[head] += (line.strip(),)
        elif counted := re.fullmatch(r"(\S+)  \(\d+\)", line):
            head = counted[1]
            groups[head] = ()
    return groups


def _foreign_reading(output: str) -> dict[str, str]:
    r"""Each category declaring a Sage supercategory, and what it declares."""
    return dict(re.findall(r"(?m)^(\S+)\n    declares  (.+)\n", output))


def _dot_reading(output: str) -> set[tuple[str, str]]:
    r"""Each edge the drawing writes, as the two names it joins."""
    return set(re.findall(r'(?m)^  "([^"]+)" -> "([^"]+)"', output))


def _constructions_reading(output: str) -> dict[str, tuple[str, ...]]:
    r"""Each category the view reports operations for, and the operations it lists."""
    found: dict[str, tuple[str, ...]] = {}
    for section in output.split("\n## ")[1:]:
        heading = section.split("\n", 1)[0]
        if matched := re.search(r" of (\S+)  \(", heading):
            found[matched[1]] = tuple(re.findall(r"(?m)^  \w\.(\w+)\(", section))
    return found


def _routes_reading(output: str) -> dict[str, str]:
    r"""Each operation the view reports, and the category the source defines it at."""
    return dict(
        re.findall(r"(?m)^## (\w+), (?:introduced by|defined at) (\S+) \(", output)
    )


_HEADER_FIGURES = (
    ("categories", r"categories (\d+)"),
    ("declarations", r"declarations (\d+)"),
    ("computed joins", r"computed joins (\d+)"),
    ("pieces", r"pieces (\d+)"),
    ("longest chain", r"longest chain of declarations and joins = (\d+)"),
    ("0-cells", r"0-cells (\d+)"),
    ("1-cells", r"1-cells (\d+)"),
    ("2-cells", r"2-cells (\d+)"),
)


def _figures(output: str) -> dict[str, int]:
    r"""The figures an answer states, by name, and each heading's count by heading.

    ``H_0`` is stated as a group, which Sage writes ``Z``, ``Z^2`` or ``Z x Z``,
    so its rank is the sum of the free summands.
    """
    figures = {
        name: int(found[1] or 1)
        for name, pattern in _HEADER_FIGURES
        if (found := re.search(pattern, output))
    }
    if zero := re.search(r"H_0 = ((?:Z(?:\^\d+)?)(?: x Z(?:\^\d+)?)*)", output):
        figures["H_0 rank"] = sum(
            int(power or 1) for power in re.findall(r"Z(?:\^(\d+))?", zero[1])
        )
    for heading, count in re.findall(r"(?m)^#+ (.+?) \((\d+)\)", output):
        figures[heading] = int(count)
    return figures


_READINGS = {
    "table": _table_reading,
    "by-supercategory": _claimants_reading,
    "foreign": _foreign_reading,
    "audit": _figures,
    "shape": _figures,
    "cells": _figures,
    "dot": _dot_reading,
    "constructions": _constructions_reading,
    "properties": _figures,
    "routes": _routes_reading,
}


def pytest_configure(config) -> None:
    r"""Bind the abbreviation for this session, as the lint documents.

    ``sage_extensions.testing.test_lint`` admits a name a directory's
    ``conftest.py`` binds as a builtin and reads that set after the conftests
    have run; ``tests/lattices/conftest.py`` binds ``card`` the same way.  The
    name is removed when the session ends, so the binding lasts exactly as long
    as the tests that name it.
    """
    builtins.declared_graph_report = declared_graph_report
    builtins.declared_graph_document = declared_graph_document
    builtins.declared_graph_figures = declared_graph_figures
    builtins.declared_graph_breadth = declared_graph_breadth
    builtins.declared_graph_reading = declared_graph_reading
    builtins.probe_run = probe_run
    builtins.stage_records_of = stage_records_of
    builtins.kept_test_run = kept_test_run
    builtins.simultaneous_test_runs = simultaneous_test_runs
    builtins.installed_wheel_record = installed_wheel_record
    builtins.incidence_row_outcome = incidence_row_outcome
    builtins.incidence_row_contract = incidence_row_contract
    builtins.incidence_edge_containment = incidence_edge_containment
    builtins.incidence_rows_exit = incidence_rows_exit
    builtins.incidence_page_comparison = incidence_page_comparison
    builtins.restricted_stabilizer_outcome = restricted_stabilizer_outcome
    builtins.incidence_rows_run = incidence_rows_run
    builtins.RowStatus = _script("coble_row_status").RowStatus


def pytest_unconfigure(config) -> None:
    r"""Remove the session's abbreviation, leaving ``builtins`` as it was found."""
    del builtins.declared_graph_report
    del builtins.declared_graph_document
    del builtins.declared_graph_figures
    del builtins.declared_graph_breadth
    del builtins.declared_graph_reading
    del builtins.probe_run
    del builtins.stage_records_of
    del builtins.kept_test_run
    del builtins.simultaneous_test_runs
    del builtins.installed_wheel_record
    del builtins.incidence_row_outcome
    del builtins.incidence_row_contract
    del builtins.incidence_edge_containment
    del builtins.incidence_rows_exit
    del builtins.incidence_page_comparison
    del builtins.restricted_stabilizer_outcome
    del builtins.incidence_rows_run
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


# The installed package's timing record --------------------------------------
#
# A timing record is written by the library, from wherever it is installed:
# this checkout, or a wheel a consumer installed.  A wheel has no source tree
# and no git, so the two facts a record states about its origin -- which
# revision produced it, and where it is written -- are asked of an installation
# that is not a checkout, which is what `installed_wheel_record` builds.

WHEEL_ROOT = SOURCE_TREE / ".tmp" / "installed-wheels"

INSTALLED_CALL = """\
import json

from sage.all import ZZ
from sage_extensions.all import Lattices
import sage_extensions

lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
rows = lattice.stable_orthogonal_group().isotropic_orbit_representatives(1)
print(json.dumps({
    "package": sage_extensions.__file__,
    "cardinality": int(rows.cardinality()),
}))
"""
r"""The timed public orbit call one installed wheel makes, and what it answered.

One stage-timed row on ``L_1 = U + U + <-2>``, whose line orbits are one under
the discriminant kernel.  The run reports the file the library it imported is a
file of, so the reader below can refuse a run that reached this checkout
instead of the installed wheel, and the cardinality the call returned, which is
what the call is for.
"""

_CONSUMER_IDENTITY = ("-c", "user.name=consumer", "-c", "user.email=consumer@example.invalid")

_INSTALLED_WHEEL: tuple[Path, Path, str] | None = None
r"""The installed wheel's directory, the consumer tree it was installed into, and that tree's commit."""


def _installed_wheel() -> tuple[Path, Path, str]:
    r"""A wheel of this checkout, installed into a consumer's own project tree.

    One installation per session, because a wheel is what a consumer installs and
    building it costs the whole tree: ``pip install --target src`` builds the
    wheel of this checkout's working tree, ``setup.py``'s ``build_py`` writes the
    revision it was built from into it, and pip puts it where a consumer keeps it.

    The tree it is installed into is a consumer's, not this checkout's, and the
    installation is put in the one place a source checkout of this library also
    keeps a package: ``<consumer>/src/sage_extensions``, one directory below a
    ``pyproject.toml`` that declares the consumer's own project and beside a git
    repository whose commit is the consumer's.  So every fact a reader could take
    for this library's source -- a package under ``src``, a project file above
    it, a revision in that repository -- is present, and none of it is this
    library's.
    """
    global _INSTALLED_WHEEL
    if _INSTALLED_WHEEL is not None and _INSTALLED_WHEEL[0].is_dir():
        return _INSTALLED_WHEEL
    WHEEL_ROOT.mkdir(parents=True, exist_ok=True)
    tree = Path(tempfile.mkdtemp(prefix="wheel-", dir=WHEEL_ROOT))
    installed = tree / "src"
    placed = subprocess.run(
        (
            sys.executable, "-m", "pip", "install",
            "--no-deps", "--no-build-isolation", "--quiet",
            "--target", str(installed), str(SOURCE_TREE),
        ),
        capture_output=True,
        text=True,
    )
    assert placed.returncode == 0, (
        f"installing a wheel of {SOURCE_TREE} into {installed} failed: {placed.stdout}{placed.stderr}"
    )
    _INSTALLED_WHEEL = (installed, tree, _consumer_commit(tree))
    return _INSTALLED_WHEEL


def _consumer_commit(tree: Path) -> str:
    r"""Give ``tree`` a project file and a git commit of its own, and answer the commit.

    The commit is the revision a record could be misattributed to: the consumer's
    own, whose code produced none of the wall times.
    """
    (tree / "pyproject.toml").write_text('[project]\nname = "consumer"\nversion = "0.0.0"\n')
    for command in (("init", "--quiet"), ("commit", "--quiet", "--allow-empty", "-m", "the consumer's tree")):
        completed = subprocess.run(
            ("git", "-C", str(tree), *_CONSUMER_IDENTITY, *command),
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, (
            f"preparing the consumer tree at {tree} failed: {completed.stdout}{completed.stderr}"
        )
    resolved = subprocess.run(
        ("git", "-C", str(tree), "rev-parse", "HEAD"), capture_output=True, text=True, check=True
    )
    return resolved.stdout.strip()


def _records_under(root: Path, pid: int) -> tuple[Path, ...]:
    r"""The record files under ``root`` that the process ``pid`` wrote, by their own names.

    A record's name ends with the pid of the process that wrote it, so a run's
    own file is found without reading a line or being told where to look -- which
    is how a run that wrote outside the directory it was supposed to use is
    reported rather than passed over.
    """
    return tuple(
        path
        for path in sorted(root.rglob("*"))
        if RECORD_NAME.fullmatch(path.name) is not None
        and _stamp_of(path.name)[1] == str(pid)
    )


@dataclass(frozen=True)
class InstalledWheelRecord:
    r"""What one timed call from an installed wheel wrote, and where.

    ``revision`` is this checkout's commit, read here by git so the record is
    checked against a reader that does not ask the library, and ``consumer`` is
    the commit of the tree the wheel was installed into, which is the revision a
    record could be misattributed to; ``commit`` is the revision the record
    itself names; ``directory`` is the directory the record was found in and
    ``directory_parts`` its path below the home directory the run was given, so
    a reader asks whether the record is where its owner keeps its state;
    ``package`` is the file the run imported the library from, which is the
    installed wheel's and not this checkout's; ``cardinality`` is what the call
    returned, and ``records`` are the lines the call appended.
    """

    revision: str
    consumer: str
    commit: str
    directory: str
    directory_parts: tuple[str, ...]
    package: str
    cardinality: int
    records: tuple[dict, ...]
    transcript: str


def installed_wheel_record() -> InstalledWheelRecord:
    r"""One timed public orbit call from a wheel installed out of this checkout.

    The run's environment states nothing about where a record goes: its home
    directory is a fresh one, so the library resolves the record directory from
    the home of the user running it -- the process's own owner -- and the record
    is looked for exactly where that rule puts it,
    ``<home>/.local/state/sage-extensions/timings``, by the pid of the process
    that wrote it.  Nothing of this checkout is reachable from the run: its
    ``PYTHONPATH`` is the installed directory alone, and it is started in the
    consumer's tree, which holds a ``pyproject.toml`` and a revision of its own
    that are not this library's.
    """
    installed, tree, consumer = _installed_wheel()
    root = Path(tempfile.mkdtemp(prefix="installed-call-", dir=WHEEL_ROOT))
    try:
        home = root / "home"
        directory = home / ".local" / "state" / "sage-extensions" / "timings"
        environment = {
            key: value
            for key, value in os.environ.items()
            if key not in ("PYTHONPATH", "PYTHONHOME", "XDG_STATE_HOME")
        }
        environment["HOME"] = str(home)
        environment["PYTHONPATH"] = str(installed)
        process = subprocess.Popen(
            (sys.executable, "-c", INSTALLED_CALL),
            cwd=tree,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        output, _ = process.communicate()
        assert process.returncode == 0, (
            f"the timed orbit call from the installed wheel at {installed} failed: {output}"
        )
        answer = json.loads(output.strip().splitlines()[-1])
        assert Path(answer["package"]).parent.parent == installed, (
            f"the run imported the library from {answer['package']}, which is not the installed "
            f"wheel at {installed}: the record read below would be this checkout's, not a wheel's"
        )
        assert directory.is_dir(), (
            f"the call wrote no record directory at {directory}, which is where the record of a "
            f"package that is not a checkout is kept; what it left instead is "
            f"{_records_under(tree, process.pid)}: {output}"
        )
        written = _records_under(directory, process.pid)
        assert len(written) == 1, (
            f"the call left {len(written)} record files in {directory}, whose process was "
            f"{process.pid}: {output}"
        )
        records = sage_timing.read_stage_records(written[0])
        return InstalledWheelRecord(
            revision=_head_commit(),
            consumer=consumer,
            commit=records[0]["commit"],
            directory=str(directory),
            directory_parts=directory.relative_to(home).parts,
            package=answer["package"],
            cardinality=answer["cardinality"],
            records=records,
            transcript=output,
        )
    finally:
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


def incidence_edge_containment(lattice, line, plane):
    r"""Why the Γ_{Co,2} driver's edge contract rejects this line/plane edge, or ``None``.

    The clause is the row's: both terms are subobjects of the row's lattice, and
    the line's retained generator lies in the plane exactly when it is in the
    image of the plane's inclusion.
    """
    return _incidence_row_driver().containment_violation(lattice, line, plane)


def incidence_rows_exit(argv):
    r"""The exit status of one run of the Γ_{Co,2} driver's ``main`` on ``argv``.

    The driver's own command line is what the dispatched job calls, so a test
    asks it what it reports rather than re-deriving the selection it makes.
    """
    return _incidence_row_driver().main(argv)


def incidence_rows_run(argv):
    r"""One run of the incidence driver's ``main``: its exit status and its comparisons.

    The driver prints each stated value beside the computed one and keeps the
    answer in ``RECORDED_COMPARISONS``; this returns that list with the status,
    so a test asks what the run compared rather than what it printed -- text is
    not a datum, and a run that stopped comparing would leave only text.
    """
    driver = _incidence_row_driver()
    del driver.RECORDED_COMPARISONS[:]
    status = driver.main(argv)
    return status, tuple(driver.RECORDED_COMPARISONS)


def restricted_stabilizer_outcome(cap) -> int:
    r"""The exit status of one run of the restricted-stabilizer driver on `T_En`.

    The driver is a script of the acceptance tier, like the incidence drivers:
    it reports what the row did as an exit status -- 0 agreeing, 1 undecided
    inside the cap, 2 returned and differing -- and a test asks the row for that
    status rather than for the computation behind it.
    """
    return _script("coble_restricted_stabilizer").main(["--lattice", "TEn", "--cap", str(cap)])


def incidence_page_comparison(label, statement, computed, recorded, source) -> bool:
    r"""The Γ_{Co,2} driver's recording of a computed value beside a stated one.

    The driver prints the value, the source that states the other value, and the
    word ``agrees`` or ``DIFFERS``; the answer is that agreement, and the row's
    status is not reached with it.  A test asks this question directly, which is
    how "recorded, never asserted" is a property of the driver rather than of a
    run's green.
    """
    return _incidence_row_driver().record_comparison(
        label, statement, computed, recorded, source
    )


def incidence_row_contract(lattice, subgroup, lines, planes, incidences, route="certificate"):
    r"""What the Γ_{Co,2} driver's contract makes of one relation of a row's vertices.

    ``lines``, ``planes`` and ``incidences`` are the row's own data: the vertices
    the row returned and the edges it joined them with.  The row step's contract
    is the driver's statement about that relation, so a test hands it the
    relation instead of the status the contract might have reached.

    ``route`` is the route the relation was taken on, because the two routes'
    edges carry different clauses: a certificate route's edge retains a flag and
    its transporter, and the contract reads the line's containment in the plane
    off them; a class route's edge retains only the line's divided-class orbit
    and its clause is that orbit.  The default is the certificate route, whose
    clause is the stronger of the two and the one a relation with actual line
    and plane terms is read by.
    """
    return _incidence_row_driver().row_contract(
        lattice, subgroup, "row", lines, planes, incidences, route
    )
