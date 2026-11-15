r"""Keep every test run's timing record, per run, in the durable record directory.

A run that writes ``--report-log`` and ``--junit-xml`` — ``pyproject.toml``'s
``addopts`` write ``tests/.report/run.jsonl`` (one line per reported phase, with
its duration) and ``tests/.report/junit.xml`` (one ``time`` per test case) —
overwrites both on the next run, so a timing question about a run that already
happened had no record to read.  This plugin copies them, once, at the end of
the session, into :func:`sage_extensions.timing.timing_directory` — ``.timings/``
at the source tree's root, which ``.gitignore`` keeps out of git — named by the
resolved commit and the run's start time, after the file's own name:

* ``run-<commit>-<start>.jsonl`` — the report log;
* ``junit-<commit>-<start>.xml`` — the JUnit file.

The library's own stage records (:mod:`sage_extensions.timing`) land in the same
directory, as ``stages-<commit>-<start>.jsonl``, so one directory holds the
per-test and per-stage wall times of the runs that produced them.

Both paths are the run's own options and not a second copy of the addopts: a
run whose configuration put its report log somewhere else is kept from where it
put it.  An option the run did not set asked for no file, and there is nothing
to keep; an option that names a file this run did not write is an error, because
the alternative is filing another run's timings under this run's name.

**Kept once per run, by the run's controller.**  ``pytest-xdist`` runs the whole
session again on each worker, ``pytest_sessionfinish`` included, and both files
this plugin copies are written by the controller alone: a worker that copied
them would file the controller's half-written report log under a start stamp of
its own, one more record per worker, and fail an assertion about a JUnit file
the run has not written yet — an assertion ``xdist`` swallows, so the run stays
green while the directory fills with records of nothing.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sage_extensions import timing

KEPT = ("report_log", "xmlpath")
r"""The pytest options that name the report log and the JUnit file."""

_STARTED = pytest.StashKey[tuple[str, float]]()


def _is_worker(config: pytest.Config) -> bool:
    r"""Whether this process is one of ``pytest-xdist``'s workers.

    A worker runs the session hooks in its own process, with the controller's
    options and a start time of its own; nothing it writes is the run's record.
    """
    return hasattr(config, "workerinput")


def pytest_configure(config: pytest.Config) -> None:
    r"""Stamp the run's start, which names its record and dates what it wrote."""
    if _is_worker(config):
        return
    started = datetime.now(timezone.utc)
    config.stash[_STARTED] = (started.strftime("%Y%m%dT%H%M%SZ"), started.timestamp())


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    r"""Copy this run's report log and JUnit file into the durable record directory.

    ``trylast`` so the copy is of what every plugin has finished writing: the
    report log is appended to by ``pytest-reportlog`` as the run reports, and the
    JUnit file is written by pytest's own ``junitxml`` session finish.

    The controller alone does this: under ``-n`` each worker finishes a session
    of its own, and both files are the controller's.
    """
    if _is_worker(session.config):
        return
    directory = timing.timing_directory()
    commit = timing.current_commit()[:12]
    stamp, epoch = session.config.stash[_STARTED]
    for option in KEPT:
        named = getattr(session.config.option, option)
        if named is None:
            continue
        written = Path(named)
        if not written.is_absolute():
            written = session.config.invocation_params.dir / written
        assert written.is_file(), (
            f"the run was asked for its {option} at {written}, and nothing is there to keep"
        )
        assert written.stat().st_mtime >= epoch, (
            f"the run was asked for its {option} at {written}, and the file there is one an earlier "
            "run wrote: keeping it would file one run's timings under this run's name"
        )
        destination = directory / f"{written.stem}-{commit}-{stamp}{written.suffix}"
        shutil.copyfile(written, destination)
