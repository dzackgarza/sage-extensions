"""Selection-invariant pytest performance gates.

The gates measure three separate workloads: importing the session after
``sage.all``, collecting the selected tests, and the call phase of each selected
test.  A test's execution result depends only on its own duration; selecting
additional tests cannot increase its allowance.

The default ceilings are fresh-process measurements on this host at
``1e36cc7e03`` (2026-10-19):

* session import: 1.989, 1.397, 1.420, 1.337, 1.391 seconds;
* collection of the 26-test default tree then: 3.81, 2.91, 2.69 seconds;
* slowest call in that tree: 15.80 seconds (the complete run took 44.16
  seconds).

The rounded defaults leave about fifty percent headroom over the largest
startup measurements and about twenty-five percent over the slowest test call.
The independent 60-second pytest-timeout limit remains the hang bound.

Each ceiling is an ini setting -- ``time_gate_star_import_ceiling``,
``time_gate_collection_ceiling``, ``time_gate_call_ceiling`` -- whose default is
the measurement above, so a run states the ceilings it enforces and a host or a
probe measures against its own without editing this module.

A measurement over its ceiling is recorded with the workload it measured,
printed in the end-of-run summary, and makes the run red at session finish.
The run then executes every test it selected: the report of the selected tests
is what the ceilings are for, and a measurement taken is not a reason to skip
it.  ``--no-time-gates`` lifts what makes the run red, not what it measured.

The workloads differ in what a ceiling can mean.  A test's call phase is one
test's own duration, so its ceiling holds for any selection.  Collection and
the session import are properties of the whole selection: collecting 879 files
has no reason to finish in the time 26 took, so their ceilings are baselines of
a whole tree, not allowances a selection cannot raise.
"""

import time

import pytest

STAR_IMPORT_CEILING = 3.0
COLLECTION_CEILING = 6.0
TEST_CALL_CEILING = 20.0

_STAR_IMPORT_SECONDS = pytest.StashKey[float]()
_COLLECTION_START = pytest.StashKey[float]()
_SLOW_CALLS = pytest.StashKey[list[tuple[str, float]]]()
_OVER_CEILING = pytest.StashKey[list[str]]()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--no-time-gates",
        action="store_true",
        help="one-off measurement run: report timings without enforcing performance ceilings",
    )
    parser.addini(
        "time_gate_star_import_ceiling",
        "seconds allowed for importing the session after sage.all",
        default=str(STAR_IMPORT_CEILING),
    )
    parser.addini(
        "time_gate_collection_ceiling",
        "seconds allowed for collecting the selected tests",
        default=str(COLLECTION_CEILING),
    )
    parser.addini(
        "time_gate_call_ceiling",
        "seconds allowed for one test's call phase",
        default=str(TEST_CALL_CEILING),
    )


def _gated(config: pytest.Config) -> bool:
    return not config.getoption("no_time_gates")


def _ceiling(config: pytest.Config, setting: str) -> float:
    r"""The ceiling this run enforces for one workload."""
    return float(config.getini(setting))


def _measured(config: pytest.Config, workload: str, seconds: float, setting: str) -> None:
    r"""Record a workload over the ceiling this run enforces for it."""
    ceiling = _ceiling(config, setting)
    if seconds > ceiling:
        config.stash[_OVER_CEILING].append(
            f"{workload} took {seconds:.2f} s; the measured ceiling is {ceiling:.0f} s"
        )


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: pytest.Config) -> None:
    import sage.all  # noqa: F401  (Sage's own load is outside the measured workload)

    start = time.perf_counter()
    import sage_extensions.all  # noqa: F401

    early_config.stash[_STAR_IMPORT_SECONDS] = time.perf_counter() - start


def pytest_sessionstart(session: pytest.Session) -> None:
    session.config.stash[_OVER_CEILING] = []
    session.config.stash[_SLOW_CALLS] = []
    _measured(
        session.config,
        "session star import",
        session.config.stash[_STAR_IMPORT_SECONDS],
        "time_gate_star_import_ceiling",
    )
    session.config.stash[_COLLECTION_START] = time.perf_counter()


@pytest.hookimpl(trylast=True)
def pytest_collection_finish(session: pytest.Session) -> None:
    _measured(
        session.config,
        "collection",
        time.perf_counter() - session.config.stash[_COLLECTION_START],
        "time_gate_collection_ceiling",
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.duration > _ceiling(item.config, "time_gate_call_ceiling"):
        item.config.stash[_SLOW_CALLS].append((item.nodeid, report.duration))
    if not _gated(item.config):
        return
    if call.excinfo is not None and call.excinfo.errisinstance(pytest.fail.Exception):
        message = str(call.excinfo.value)
        if message.startswith('Timeout (>') and message.endswith("from pytest-timeout."):
            pytest.exit(f"{item.nodeid}: {message}", returncode=pytest.ExitCode.TESTS_FAILED)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    del exitstatus
    if not _gated(session.config):
        return
    if session.config.stash[_SLOW_CALLS] or session.config.stash[_OVER_CEILING]:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter) -> None:
    over = terminalreporter.config.stash[_OVER_CEILING]
    if over:
        terminalreporter.write_sep("=", "time-gate report")
        for line in over:
            terminalreporter.write_line(line)
    slow = terminalreporter.config.stash[_SLOW_CALLS]
    if not slow:
        return
    ceiling = _ceiling(terminalreporter.config, "time_gate_call_ceiling")
    terminalreporter.write_sep("=", "test-call performance gate")
    for nodeid, duration in slow:
        terminalreporter.write_line(f"{nodeid}: {duration:.2f} s > {ceiling:.0f} s")


def pytest_report_header(config: pytest.Config) -> str:
    gates = "on" if _gated(config) else "OFF (--no-time-gates)"
    return (
        f"time gates {gates}: star import {config.stash[_STAR_IMPORT_SECONDS]:.2f} s "
        f"(ceiling {_ceiling(config, 'time_gate_star_import_ceiling'):.0f} s), collection ceiling "
        f"{_ceiling(config, 'time_gate_collection_ceiling'):.0f} s, each test call ceiling "
        f"{_ceiling(config, 'time_gate_call_ceiling'):.0f} s"
    )
