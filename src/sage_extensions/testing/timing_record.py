r"""Keep every test run's timing record, per run, in the durable record directory.

``pyproject.toml``'s ``addopts`` already make every run write
``tests/.report/run.jsonl`` (one line per reported phase, with its duration) and
``tests/.report/junit.xml`` (one ``time`` per test case).  Both are overwritten
by the next run, so a timing question about a run that already happened had no
record to read; this plugin copies them, once, at the end of the session, into
:func:`sage_extensions.timing.timing_directory` — ``.timings/`` at the checkout's
root, which ``.gitignore`` keeps out of git — named by the resolved commit and
the run's start time:

* ``run-<commit>-<start>.jsonl`` — the report log;
* ``junit-<commit>-<start>.xml`` — the JUnit file.

The library's own stage records (:mod:`sage_extensions.timing`) land in the same
directory, as ``stages-<commit>-<start>.jsonl``, so one directory holds the
per-test and per-stage wall times of the runs that produced them.

A run that wrote no report log — ``-o addopts=``, a ``--collect-only``, a host
without ``pytest-reportlog`` — is archived as far as it exists: a missing file
is skipped and never fails a session whose job is to keep a record, while a
directory that cannot be written propagates as the ordinary error it is.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sage_extensions import timing

REPORTED = ("run.jsonl", "junit.xml")
r"""The two files the run's own ``addopts`` write, and what is kept of it."""

_STARTED = pytest.StashKey[tuple[str, float]]()


def pytest_configure(config: pytest.Config) -> None:
    r"""Stamp the run's start, which names its record and dates what it wrote.

    The wall clock is kept beside the name because a file under
    ``tests/.report/`` that this run did not write is the previous run's: a host
    running with ``-o addopts=`` leaves the last run's report log in place, and
    copying it would file one run's timings under another run's name.
    """
    started = datetime.now(timezone.utc)
    config.stash[_STARTED] = (started.strftime("%Y%m%dT%H%M%SZ"), started.timestamp())


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    r"""Copy this run's report log and JUnit file into the durable record directory.

    ``trylast`` so the copy is of what every plugin has finished writing: the
    report log is appended to by ``pytest-reportlog`` as the run reports, and the
    JUnit file is written by pytest's own ``junitxml`` session finish.
    """
    directory = timing.timing_directory()
    if directory is None:
        return
    source = session.config.rootpath / "tests" / ".report"
    commit = timing.current_commit()[:12]
    stamp, epoch = session.config.stash[_STARTED]
    for name in REPORTED:
        written = source / name
        if not written.is_file() or written.stat().st_mtime < epoch:
            continue
        destination = directory / f"{Path(name).stem}-{commit}-{stamp}{Path(name).suffix}"
        shutil.copyfile(written, destination)
