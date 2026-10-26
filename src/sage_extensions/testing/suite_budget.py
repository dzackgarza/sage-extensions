"""Selection-invariant pytest performance gates.

The gates measure three separate workloads: importing the session after
``sage.all``, collecting the selected tests, and the call phase of each selected
test.  A test's execution result depends only on its own duration; selecting
additional tests cannot increase its allowance.

The ceilings are based on fresh-process measurements on this host at
``1e36cc7e03`` (2026-10-19):

* session import: 1.989, 1.397, 1.420, 1.337, 1.391 seconds;
* collection of the current 26-test default tree: 3.81, 2.91, 2.69 seconds;
* slowest call in the default tree: 15.80 seconds (the complete run took
  44.16 seconds).

The rounded ceilings leave about fifty percent headroom over the largest
startup measurements and about twenty-five percent over the slowest test call.
The independent 60-second pytest-timeout limit remains the hang bound.
"""

import time

import pytest

STAR_IMPORT_CEILING = 3.0
COLLECTION_CEILING = 6.0
TEST_CALL_CEILING = 20.0

_STAR_IMPORT_SECONDS = pytest.StashKey[float]()
_COLLECTION_START = pytest.StashKey[float]()
_SLOW_CALLS = pytest.StashKey[list[tuple[str, float]]]()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--no-time-gates",
        action="store_true",
        help="one-off measurement run: report timings without enforcing performance ceilings",
    )


def _gated(config: pytest.Config) -> bool:
    return not config.getoption("no_time_gates")


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config: pytest.Config) -> None:
    import sage.all  # noqa: F401  (Sage's own load is outside the measured workload)

    start = time.perf_counter()
    import sage_extensions.all  # noqa: F401

    early_config.stash[_STAR_IMPORT_SECONDS] = time.perf_counter() - start


def pytest_sessionstart(session: pytest.Session) -> None:
    star_import = session.config.stash[_STAR_IMPORT_SECONDS]
    if _gated(session.config) and star_import > STAR_IMPORT_CEILING:
        pytest.exit(
            f"session star import took {star_import:.2f} s; "
            f"the measured ceiling is {STAR_IMPORT_CEILING:.0f} s",
            returncode=pytest.ExitCode.TESTS_FAILED,
        )
    session.config.stash[_COLLECTION_START] = time.perf_counter()
    session.config.stash[_SLOW_CALLS] = []


@pytest.hookimpl(trylast=True)
def pytest_collection_finish(session: pytest.Session) -> None:
    collection = time.perf_counter() - session.config.stash[_COLLECTION_START]
    if _gated(session.config) and collection > COLLECTION_CEILING:
        pytest.exit(
            f"collection took {collection:.2f} s; "
            f"the measured ceiling is {COLLECTION_CEILING:.0f} s",
            returncode=pytest.ExitCode.TESTS_FAILED,
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.duration > TEST_CALL_CEILING:
        item.config.stash[_SLOW_CALLS].append((item.nodeid, report.duration))
    if not _gated(item.config):
        return
    if call.excinfo is not None and call.excinfo.errisinstance(pytest.fail.Exception):
        message = str(call.excinfo.value)
        if message.startswith("Timeout (>") and message.endswith("from pytest-timeout."):
            pytest.exit(f"{item.nodeid}: {message}", returncode=pytest.ExitCode.TESTS_FAILED)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    del exitstatus
    if _gated(session.config) and session.config.stash[_SLOW_CALLS]:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter) -> None:
    slow = terminalreporter.config.stash[_SLOW_CALLS]
    if not slow:
        return
    terminalreporter.write_sep("=", "test-call performance gate")
    for nodeid, duration in slow:
        terminalreporter.write_line(
            f"{nodeid}: {duration:.2f} s > {TEST_CALL_CEILING:.0f} s"
        )


def pytest_report_header(config: pytest.Config) -> str:
    gates = "on" if _gated(config) else "OFF (--no-time-gates)"
    return (
        f"time gates {gates}: star import {config.stash[_STAR_IMPORT_SECONDS]:.2f} s "
        f"(ceiling {STAR_IMPORT_CEILING:.0f} s), collection ceiling "
        f"{COLLECTION_CEILING:.0f} s, each test call ceiling {TEST_CALL_CEILING:.0f} s"
    )
