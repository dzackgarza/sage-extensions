r"""One logger through which this library's long computations record their stages.

A timing question about a long computation — which stage of the isotropic orbit
row costs the hour, whether the walk or the transport — is answered by reading
the record of a run that already happened, not by re-running the computation
under a wrapper.  So every stage of those computations appends one JSONL line,
as it ends, to :func:`record_path`, and nothing else is asked of a caller.

**What a stage is.**  A named interval around a piece of work that is done once
per call — the ambient row, the parabolic family, one discriminant image, the
coset walk, the transport — and never around one element of an orbit.  The rule
is the one the call sites keep: a timer around a stage.  A wrapper per element
turns a stage measurement into an element measurement, and per-element costs
are what :meth:`module_generators`-level counting already answers.

**A cached method is timed in its body, never by a decorator.**  ``cached_method``
builds its cache key from the signature of the function it wraps, through
``sage_getargspec`` / ``ArgumentFixer``, and a decorator here would present
``(*arguments, **keywords)`` instead: the key would then keep a default keyword
the caller wrote apart from the same call without it, and one computation would
fill two cache entries.  So a method under ``cached_method`` opens
``with stage(...)`` on its first statement, and :func:`timed_stage` is only for
functions no cache reads a signature from.

**Where the record goes.**  :func:`timing_directory` is ``.timings/`` in the
source tree this module is a file of, which ``.gitignore`` keeps out of git and
``CONTRIBUTING.md`` ENV-03 states, and which the call creates and asserts.  One
file per process, named by the resolved commit, the process's start time to the
microsecond and its pid, so two runs of the same commit never overwrite each
other's records — two runs started in the same second are two processes, and two
processes are two pids — and a record is never a claim about which commit
produced it: the commit is in its name and in every line.

**What a record line holds.**  ``stage`` (the name), ``input`` (the name of what
was computed, written by the caller), ``seconds`` (wall time,
``time.perf_counter``), ``started`` and
``finished`` (UTC, ISO 8601), ``outcome`` (``"returned"`` or ``"raised"``, with
``error`` naming the exception class), ``commit``, ``run`` (the process's start
stamp, which is the file's own name) and ``pid``.

**What it costs when nobody reads it.**  A stage is two ``perf_counter``
readings, the fitting of its input's name, and one appended line.  Nothing is
measured per element, no computation is re-run to time it, and the handler is
added on the first record rather than at import, so importing the library writes
nothing.

**The input's name is the caller's.**  ``input`` is a string the call site builds
from what it already holds — the row's parameters, a plane's position, the
lattice's rank and generator labels — and this module inspects nothing it is
handed.  A record whose name came from reading its object would be a record that
depends on a class and on whatever that class happens to carry; a name read off a
display would be a computation, on a lattice an invariant one, bought for a log
line.  ``input`` is a name, so it is written where the name is known.

**Which logger it is.**  ``sage_extensions.timing``, a child of the package's
logger and nobody else's: this module sets that child's level and leaves
``sage_extensions`` and the root logger exactly as it found them, so the library's
own ``DEBUG`` records reach whatever handler the application or the test run put
on them.  A record is a :class:`logging.LogRecord` carrying a ``timing`` payload
that :class:`_JSONLineHandler` appends as one line of JSON; a reader that wants
the payload as :mod:`logging` intended installs its own handler.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache, wraps
from pathlib import Path

__all__ = [
    "LOGGER_NAME",
    "RECORD_DIRECTORY_NAME",
    "logger",
    "stage",
    "timed_stage",
    "timing_directory",
    "record_path",
    "current_commit",
    "read_stage_records",
]

LOGGER_NAME = "sage_extensions.timing"
r"""The name of the one logger this module owns, a child of the package's own."""

RECORD_DIRECTORY_NAME = ".timings"
r"""The durable record directory at the source tree's root, stated in ``CONTRIBUTING.md`` ENV-03."""

logger = logging.getLogger(LOGGER_NAME)
r"""The logger every stage record is emitted through."""

# A record is emitted at INFO, and a record that the application's root logger
# leaves at WARNING would never be built: the level is this child's own, so the
# package's logger and the root logger are left as their owners set them.
logger.setLevel(logging.INFO)

# Reentrant because the installed handler is resolved under it and the name it
# is given is resolved under it too: one lock for the process's record, taken
# once, rather than two that could disagree about which process this is.
_HANDLER_LOCK = threading.RLock()

_PROCESS_START = datetime.now(timezone.utc)
_PROCESS_ID = os.getpid()
_FILE_STAMP = f"{_PROCESS_START.strftime('%Y%m%dT%H%M%S%fZ')}-{_PROCESS_ID}"
_HANDLER: _JSONLineHandler | None = None


def _process_stamp() -> str:
    r"""This process's stamp: its start time to the microsecond and its pid.

    To the microsecond and with the pid, because a second is long enough for two
    runs to start in it: two runs are two processes, and two processes are two
    pids, so the pair names one process's record and no other's.

    Resolved here rather than once at import because a fork inherits this
    module's state: the child would otherwise append to the parent's file, which
    is one record of two runs.  A process that finds the pid it is running under
    different from the one it imported under takes a stamp of its own; the
    moment it can observe is the moment of its first stage, which is the
    earliest moment such a process has a record of.
    """
    global _PROCESS_START, _PROCESS_ID, _FILE_STAMP
    pid = os.getpid()
    with _HANDLER_LOCK:
        if pid != _PROCESS_ID:
            _PROCESS_ID = pid
            _PROCESS_START = datetime.now(timezone.utc)
            _FILE_STAMP = f"{_PROCESS_START.strftime('%Y%m%dT%H%M%S%fZ')}-{pid}"
        return _FILE_STAMP


class _JSONLineHandler(logging.Handler):
    r"""Write a record's ``timing`` payload as one JSON line appended to ``path``.

    Opened per line rather than held open: a run appends a few dozen stage
    records, no consumer needs the file to stay open, and a stage that raises
    still leaves its line behind for the next process to append to.  A write
    that fails raises: a record nobody kept is a timing question the next reader
    will re-answer by re-running the computation.

    The handler keeps the pid of the process it was made for, which is how a
    process that forked its parent's handler is told from the parent.
    """

    def __init__(self, path: Path, pid: int) -> None:
        super().__init__()
        self.path = path
        self.pid = pid

    def emit(self, record: logging.LogRecord) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.timing) + "\n")


@lru_cache(maxsize=1)
def _source_tree() -> Path:
    r"""The ``sage_extensions`` source tree this module is a file of.

    The package's file is ``<tree>/src/sage_extensions/timing.py``, so the tree
    is two directories up from the package here, and the assertion that its
    ``pyproject.toml`` is there is what makes the location a fact rather than a
    guess: an installation that is not a checkout has no source tree, and this
    says so instead of writing somewhere else.
    """
    package = Path(__file__).resolve().parent
    assert package.name == "sage_extensions", (
        f"this module is a file of {package}, which is not the sage_extensions package directory"
    )
    tree = package.parents[1]
    assert (tree / "pyproject.toml").is_file(), (
        f"the source tree of {package} is {tree}, which holds no pyproject.toml: the timing record "
        "has no checkout to be written into"
    )
    return tree


@lru_cache(maxsize=1)
def timing_directory() -> Path:
    r"""``.timings/`` in the source tree, created if it is not there, and asserted.

    One location, for every run of this checkout: the library's stage records
    and the test runs' report logs are kept together, and a directory that
    cannot be made is an error at the first stage rather than a record silently
    not written.
    """
    directory = _source_tree() / RECORD_DIRECTORY_NAME
    directory.mkdir(parents=True, exist_ok=True)
    assert directory.is_dir(), (
        f"the timing record's directory {directory} is not a directory after it was made"
    )
    return directory


@lru_cache(maxsize=1)
def current_commit() -> str:
    r"""The commit of the source tree this library is, resolved once per process.

    From that tree's own git and from nothing else: an environment variable
    names whatever the process was told, which in a consumer job is the commit
    of a different repository.  A tree that git cannot read raises, which is a
    record refusing to be attributable to a commit it does not know.
    """
    completed = subprocess.run(
        ("git", "-C", str(_source_tree()), "rev-parse", "HEAD"),
        capture_output=True,
        text=True,
        check=True,
    )
    resolved = completed.stdout.strip()
    assert len(resolved) == 40, (
        f"git rev-parse HEAD in {_source_tree()} returned {resolved!r}, which is not a commit id"
    )
    return resolved


def record_path() -> Path:
    r"""This process's stage-record file: ``stages-<commit>-<start>-<pid>.jsonl``.

    ``<commit>`` is the first twelve characters of :func:`current_commit`,
    ``<start>`` the process's start time to the microsecond as
    ``%Y%m%dT%H%M%S%fZ``, and ``<pid>`` its process id — the stamp
    :func:`_process_stamp` hands out, and the value of every line's ``run`` and
    ``pid``.  A second run of the same commit appends to a file of its own rather
    than to the first one's, and two runs that began in the same second — a
    worker and its controller, two probes started together — are two files,
    because they are two processes.
    """
    return timing_directory() / f"stages-{current_commit()[:12]}-{_process_stamp()}.jsonl"


def _installed_handler() -> _JSONLineHandler:
    r"""The record handler, added on the first record and kept for the process.

    Held in a module variable rather than looked for among the logger's
    handlers: a logger's handler list is shared with every other user of this
    child logger, and a record writer that recognised its own writer by its class
    would adopt one that some other code installed.  The pid in the handler is
    the one it was made for, so a process that forked it makes its own instead of
    appending to the parent's file.
    """
    global _HANDLER
    with _HANDLER_LOCK:
        if _HANDLER is not None and _HANDLER.pid == os.getpid():
            return _HANDLER
        if _HANDLER is not None:
            logger.removeHandler(_HANDLER)
        _HANDLER = _JSONLineHandler(record_path(), os.getpid())
        logger.addHandler(_HANDLER)
        return _HANDLER


def _emit(entry: dict) -> None:
    r"""Hand one record to the logger, whose installed handler appends it."""
    _installed_handler()
    logger.info(entry["stage"], extra={"timing": entry})


@contextmanager
def stage(name: str, input: str):
    r"""Record the wall time of one stage of a computation, named for its input.

    ``name`` is the stage — ``"ambient O(L) row"``, ``"coset walk and
    transport"`` — and ``input`` is the name of what it was computed for, a
    string the caller writes from what it holds.  Nothing about the input is read
    here (:func:`_named` only fits the text), so a record never depends on what
    an object happens to carry.  The record is written when the block ends,
    whether it returned or raised, and the exception is re-raised unchanged:
    timing a stage is not a place to close an error.
    """
    entry = {
        "stage": name,
        "input": " ".join(input.split()),
        "commit": current_commit(),
        "run": _process_stamp(),
        "pid": os.getpid(),
    }
    started = datetime.now(timezone.utc)
    clock = time.perf_counter()
    try:
        yield
    except BaseException as error:
        entry.update(
            started=started.isoformat(),
            finished=datetime.now(timezone.utc).isoformat(),
            seconds=time.perf_counter() - clock,
            outcome="raised",
            error=type(error).__name__,
        )
        _emit(entry)
        raise
    entry.update(
        started=started.isoformat(),
        finished=datetime.now(timezone.utc).isoformat(),
        seconds=time.perf_counter() - clock,
        outcome="returned",
    )
    _emit(entry)


def timed_stage(name: str, *, input):
    r"""Time a whole function as one stage, without touching its body.

    Only for a function no cache reads a signature from: under ``cached_method``
    the stage goes inside the method's body instead, because the wrapper's
    ``(*arguments, **keywords)`` is what the cache would then key on.  ``input``
    is a callable naming the stage's input out of the call's arguments, and
    :func:`functools.wraps` leaves the signature and docstring the function's own
    for every other reader.
    """

    def decorate(function):
        @wraps(function)
        def timed(*arguments, **keywords):
            with stage(name, input(*arguments, **keywords)):
                return function(*arguments, **keywords)

        return timed

    return decorate


def read_stage_records(path: str | Path, *, after: int = 0) -> tuple[dict, ...]:
    r"""The stage records in ``path``, from byte offset ``after`` onward.

    ``path`` is a record file, named as :func:`record_path` names this process's
    own.  ``after`` is how a reader takes the records one call appended without
    parsing the ones before it.

    A file that is not there raises.  A record is read because a run was asked
    what it measured, and an empty tuple would answer "it measured nothing" for
    a file the caller named and the run never wrote — the two are different
    findings and only one of them is true.
    """
    with Path(path).open("r", encoding="utf-8") as handle:
        handle.seek(after)
        return tuple(json.loads(line) for line in handle if line.strip())
