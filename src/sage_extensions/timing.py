r"""One logger through which this library's long computations record their stages.

A timing question about a long computation — which stage of the isotropic orbit
row costs the hour, whether the walk or the transport — is answered by reading
the record of a run that already happened, not by re-running the computation
under a wrapper (research #390 measured the ``Õ(T_Co)`` row's stages that way,
30 to 90 minutes a run).  So every stage of those computations appends one
JSONL line, as it ends, to :func:`record_path`, and nothing else is asked of a
caller.

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
file per process, named by the resolved commit and the process's start time, so
two runs of the same commit never overwrite each other's records and a record
is never a claim about which commit produced it: the commit is in its name and
in every line.

**What a record line holds.**  ``stage`` (the name), ``input`` (the name of what
was computed, read off the object and never rendered from it), ``seconds``
(wall time, ``time.perf_counter``), ``started`` and
``finished`` (UTC, ISO 8601), ``outcome`` (``"returned"`` or ``"raised"``, with
``error`` naming the exception class), ``commit``, ``run`` (the process's start
stamp, which is the file's own name) and ``pid``.

**What it costs when nobody reads it.**  A stage is two ``perf_counter``
readings, the reading of its input's name, and one appended line.  Nothing is
measured per element, no computation is re-run to time it, and the handler is
added on the first record rather than at import, so importing the library writes
nothing.

**The input is named, not rendered.**  ``repr`` is a computation, and for a
lattice it is an invariant one: ``Lattices``'s ``_repr_`` states the signature,
which it reads off the form.  Naming an input that way would put a
diagonalization inside a log line's cost, and a rendering that raised would take
a measured call down for the record's sake.  So an object states its own cheap
name with ``_timing_name`` — the lattice's is ``Integral lattice of rank 11`` —
and an object that states none is recorded by the name of its class.

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

# The record is emitted at INFO, and a record that the application's root logger
# leaves at WARNING would never be built: the level is this child's own, so the
# package's logger and the root logger are left as their owners set them.
logger.setLevel(logging.INFO)

_PROCESS_START = datetime.now(timezone.utc)
_FILE_STAMP = _PROCESS_START.strftime("%Y%m%dT%H%M%SZ")
_PROCESS_ID = os.getpid()
_HANDLER_LOCK = threading.Lock()
_INPUT_LIMIT = 240


class _JSONLineHandler(logging.Handler):
    r"""Write a record's ``timing`` payload as one JSON line appended to ``path``.

    Opened per line rather than held open: a run appends a few dozen stage
    records, no consumer needs the file to stay open, and a stage that raises
    still leaves its line behind for the next process to append to.  A write
    that fails raises: a record nobody kept is a timing question the next reader
    will re-answer by re-running the computation.
    """

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

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
    r"""This process's stage-record file: ``stages-<commit>-<start>.jsonl``.

    Named by the resolved commit and the process's start time, so a second run
    of the same commit appends to a file of its own rather than overwriting the
    first one's, and the two are comparable by name alone.
    """
    return timing_directory() / f"stages-{current_commit()[:12]}-{_FILE_STAMP}.jsonl"


def _installed_handler() -> _JSONLineHandler:
    r"""The record handler, added on the first record and kept for the process."""
    with _HANDLER_LOCK:
        for handler in logger.handlers:
            if isinstance(handler, _JSONLineHandler):
                return handler
        handler = _JSONLineHandler(record_path())
        logger.addHandler(handler)
        return handler


def _named(target) -> str:
    r"""The input's name: a string as given, else the cheap name the object states.

    Nothing is rendered.  ``repr`` is a computation and, on this library's
    lattices, an invariant one — the display states the signature, read off the
    form — so an object that can be named for nothing states the name with
    ``_timing_name``, and one that states none is named by its class.  Either way
    a stage's cost is a clock reading, not a rendering.
    """
    if isinstance(target, str):
        text = target
    else:
        stated = getattr(target, "_timing_name", None)
        text = type(target).__name__ if stated is None else stated()
    text = " ".join(text.split())
    return text if len(text) <= _INPUT_LIMIT else text[: _INPUT_LIMIT - 1] + "…"


def _emit(entry: dict) -> None:
    r"""Hand one record to the logger, whose installed handler appends it."""
    _installed_handler()
    logger.info(entry["stage"], extra={"timing": entry})


@contextmanager
def stage(name: str, input):
    r"""Record the wall time of one stage of a computation, named for its input.

    ``name`` is the stage — ``"ambient O(L) row"``, ``"coset walk and
    transport"`` — and ``input`` is what the stage was computed for, kept by
    :func:`_named`: a string passed here is recorded verbatim, an object by the
    name it states with ``_timing_name``, and one that states none by its class.
    The record is written when the block ends, whether it returned or raised, and
    the exception is re-raised unchanged: timing a stage is not a place to close
    an error.
    """
    entry = {
        "stage": name,
        "input": _named(input),
        "commit": current_commit(),
        "run": _FILE_STAMP,
        "pid": _PROCESS_ID,
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
    is a callable reading the name of the stage's input out of the call's
    arguments, and :func:`functools.wraps` leaves the signature and docstring the
    function's own for every other reader.
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
