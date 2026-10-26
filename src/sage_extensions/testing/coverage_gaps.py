r"""Report the sage_extensions lines and branches that no passing test runs.

``just coverage`` records coverage per test: pytest-cov's ``--cov-context=test``
labels every measured line with the node id of the test that ran it
(https://pytest-cov.readthedocs.io/en/latest/contexts.html), and the run's
pytest report log records each test's outcome.  This report counts a line as
covered only when a passing test ran it, or when it ran at import, outside any
test.  A line that only failing or erroring tests reach is reported missing:
executing it proved nothing.

The report is coverage.py's own, restricted by ``Coverage.report(contexts=...)``
(https://coverage.readthedocs.io/en/latest/contexts.html#context-reporting).

Every report log in the coverage directory is read oldest first, so a test
rerun by ``just coverage-add`` or ``just coverage-update`` supersedes its
outcome in the full run.  A source file changed since the last measurement is
listed as stale: its recorded line numbers no longer describe the file.
``--select-affected`` purges the stale files and names the tests to rerun: the
ones recorded as running a line of them, and every edited test file.  So after
one full run, a check costs the tests the edits reach, not the suite.  A test
that reaches an edited file only through a call the edit introduced is not
selected; the next full run measures it.

A construction cached across tests is credited only to the test that first
built it.  When that test fails, the passing tests that reuse the cached
object get no credit for its lines, so the report undercounts there.

Run ``python -m sage_extensions.testing.coverage_gaps [--include GLOB ...]
[--touched-by DATAFILE] [--select-affected]``, or the ``just coverage-*``
recipes.
"""

import argparse
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from coverage import Coverage, CoverageData

COVERAGE_DIRECTORY = Path(".tmp/coverage")
DATA_FILE = COVERAGE_DIRECTORY / ".coverage"
MEASURED_STAMP = COVERAGE_DIRECTORY / "measured-at"
REPORT_FILE = COVERAGE_DIRECTORY / "report.txt"


def passing_tests(report_logs: list[Path]) -> set[str]:
    r"""The node ids whose setup, call and teardown all passed in their latest run."""
    phases: dict[str, dict[str, str]] = defaultdict(dict)
    for log in sorted(report_logs, key=lambda path: path.stat().st_mtime):
        latest: dict[str, dict[str, str]] = defaultdict(dict)
        for line in log.read_text().splitlines():
            record = json.loads(line)
            if record.get("$report_type") == "TestReport":
                latest[record["nodeid"]][record["when"]] = record["outcome"]
        phases.update(latest)
    return {
        nodeid
        for nodeid, outcomes in phases.items()
        if "call" in outcomes and set(outcomes.values()) == {"passed"}
    }


def context_pattern(tests: set[str]) -> str:
    r"""A regex matching the import-time context and every context of the given tests."""
    alternatives = "|".join(re.escape(nodeid) for nodeid in sorted(tests))
    return rf"^$|^(?:{alternatives})\|"


def stale_files(measured: list[str]) -> list[str]:
    r"""The measured source files modified since the last measurement."""
    started = MEASURED_STAMP.stat().st_mtime
    return sorted(path for path in measured if Path(path).stat().st_mtime > started)


def files_run_by_tests(data_file: Path) -> list[str]:
    r"""The source files in which some test, not only the import, ran a line."""
    data = CoverageData(str(data_file))
    data.read()
    return sorted(
        path
        for path in data.measured_files()
        if any(
            context
            for contexts in data.contexts_by_lineno(path).values()
            for context in contexts
        )
    )


def select_affected() -> list[str]:
    r"""The tests to rerun after edits since the last measurement, with stale data purged.

    A source file changed since then is purged from the data, and every test
    recorded as running a line of it is selected, with every test file changed
    since then.  The measurement stamp moves to now.
    """
    started = MEASURED_STAMP.stat().st_mtime
    data = CoverageData(str(DATA_FILE))
    data.read()
    changed = stale_files(sorted(data.measured_files()))
    selected = {
        context.rpartition("|")[0]
        for path in changed
        for contexts in data.contexts_by_lineno(path).values()
        for context in contexts
        if context
    }
    selected = {
        nodeid for nodeid in selected if Path(nodeid.partition("::")[0]).exists()
    }
    edited_tests = {
        str(path)
        for pattern in ("test_*.sage", "test_*.py")
        for path in Path("tests").rglob(pattern)
        if path.stat().st_mtime > started
    }
    data.purge_files(changed)
    MEASURED_STAMP.touch()
    return sorted(selected | edited_tests)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--include", nargs="*", default=None, help="source-path globs to report on"
    )
    parser.add_argument(
        "--touched-by",
        type=Path,
        default=None,
        help="report only the files the tests in this data file ran",
    )
    parser.add_argument(
        "--select-affected",
        action="store_true",
        help="print the tests to rerun after edits, purging the edited files' data",
    )
    arguments = parser.parse_args()

    if arguments.select_affected:
        sys.stdout.writelines(f"{nodeid}\n" for nodeid in select_affected())
        return

    include: list[str] | None = arguments.include
    if arguments.touched_by is not None:
        include = files_run_by_tests(arguments.touched_by)

    data = CoverageData(str(DATA_FILE))
    data.read()
    stale = stale_files(sorted(data.measured_files()))
    tests = passing_tests(sorted(COVERAGE_DIRECTORY.glob("*.jsonl")))

    coverage = Coverage(data_file=str(DATA_FILE))
    coverage.load()
    report = io.StringIO()
    total = coverage.report(
        file=report,
        include=include,
        contexts=[context_pattern(tests)],
        show_missing=True,
        skip_covered=True,
        sort="-miss",
    )
    sys.stdout.write(report.getvalue())
    sys.stdout.write(f"\ncovered by the {len(tests)} passing tests: {total:.1f}%\n")
    if include is None:
        REPORT_FILE.write_text(report.getvalue())
        sys.stdout.write(f"full report: {REPORT_FILE}\n")
    for path in stale:
        sys.stdout.write(
            f"stale, changed since the last measurement, run just coverage-update: {path}\n"
        )


if __name__ == "__main__":
    main()
