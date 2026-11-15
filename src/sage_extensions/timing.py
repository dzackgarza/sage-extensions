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

**Where the record goes.**  :func:`timing_directory` is ``.timings/`` at the
repository root (``SAGE_EXTENSIONS_TIMING_DIR`` overrides it), which
``.gitignore`` keeps out of git and ``CONTRIBUTING.md`` ENV-03 states.  One file
per process, named by the resolved commit and the process's start time, so two
runs of the same commit never overwrite each other's records and a record is
never a claim about which commit produced it: the commit is in its name and in
every line.

**What a record line holds.**  ``record`` (always ``"stage"``), ``stage`` (the
name), ``input`` (the name of what was computed, ``repr`` of the object the
stage was handed, whitespace collapsed and truncated), ``seconds`` (wall time,
``time.perf_counter``), ``started`` and ``finished`` (UTC, ISO 8601),
``outcome`` (``"returned"`` or ``"raised"``, with ``error`` naming the exception
class), ``commit``, ``run`` (the process's start stamp, the file's own name) and
``pid``.

**What it costs when nobody reads it.**  A stage is two ``perf_counter`` calls
and one appended line.  Nothing is measured per element, no computation is
re-run to time it, and the logger is silent: ``propagate`` is off, so a host
application's logging configuration is not what the record depends on, and the
handler is added on the first record rather than at import, so importing the
library writes nothing.

``logging`` is the record's carrier because it is the standard one: the record
is a :class:`logging.LogRecord` carrying a ``timing`` payload, the handler
:class:`_JSONLineHandler` writes that payload as one line of JSON, and a reader
that wants the payload as :mod:`logging` intended installs its own handler.
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
    "stage_names",
]

LOGGER_NAME = "sage_extensions"
r"""The name of the one logger this library owns: ``logging.getLogger("sage_extensions")``."""

RECORD_DIRECTORY_NAME = ".timings"
r"""The durable record directory at the repository root, stated in ``CONTRIBUTING.md`` ENV-03."""

logger = logging.getLogger(LOGGER_NAME)
r"""The logger every stage record is emitted through."""

logger.setLevel(logging.INFO)
# The record is the handler's, not a host application's: propagating would put
# stage lines into whatever configuration the importing program installed, and
# that configuration is not the record.
logger.propagate = False

_PROCESS_START = datetime.now(timezone.utc)
_FILE_STAMP = _PROCESS_START.strftime("%Y%m%dT%H%M%SZ")
_PROCESS_ID = os.getpid()
_HANDLER_LOCK = threading.Lock()
_INPUT_LIMIT = 240


class _JSONLineHandler(logging.Handler):
    r"""Write a record's ``timing`` payload as one JSON line appended to ``path``.

    Opened per line rather than held open: a run appends a few dozen stage
    records, no consumer needs the file to stay open, and a stage that raises
    still leaves its line behind for the next process to append to.
    """

    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path

    def emit(self, record: logging.LogRecord) -> None:
        payload = getattr(record, "timing", None)
        if payload is None:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload) + "\n")
        except OSError:
            self.handleError(record)


@lru_cache(maxsize=1)
def _repository_root() -> Path | None:
    r"""The checkout ``sage_extensions`` is installed from, by its ``pyproject.toml``.

    A stage record belongs to the checkout it was written in, so the directory
    is found from the package's own file and never from the current working
    directory: a test run from ``tests/`` and a probe run from elsewhere of the
    same checkout write to the same place.  ``None`` when the package was
    installed from a wheel, where there is no checkout to write into.
    """
    for ancestor in Path(__file__).resolve().parents:
        if (ancestor / "pyproject.toml").is_file():
            return ancestor
    return None


def timing_directory() -> Path | None:
    r"""The directory stage records and per-run test records are kept in.

    ``SAGE_EXTENSIONS_TIMING_DIR`` when it is set, otherwise
    :data:`RECORD_DIRECTORY_NAME` at the checkout's root, otherwise ``None``:
    an installation with no checkout keeps no record rather than inventing a
    location, and a stage costs only its two clock readings there.
    """
    override = os.environ.get("SAGE_EXTENSIONS_TIMING_DIR")
    if override:
        return Path(override).expanduser()
    root = _repository_root()
    return None if root is None else root / RECORD_DIRECTORY_NAME


@lru_cache(maxsize=1)
def current_commit() -> str:
    r"""The commit the running library is, resolved once per process.

    ``SAGE_EXTENSIONS_COMMIT`` and ``GITHUB_SHA`` first, because a CI job knows
    its own revision without a git command; otherwise ``git rev-parse HEAD`` in
    the checkout.  ``"unknown"`` rather than a guess when neither answers, which
    is a record that says it cannot identify its own source.
    """
    for variable in ("SAGE_EXTENSIONS_COMMIT", "GITHUB_SHA"):
        named = os.environ.get(variable)
        if named:
            return named
    root = _repository_root()
    if root is None:
        return "unknown"
    try:
        completed = subprocess.run(
            ("git", "-C", str(root), "rev-parse", "HEAD"),
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    resolved = completed.stdout.strip()
    return resolved if completed.returncode == 0 and resolved else "unknown"


def record_path() -> Path | None:
    r"""This process's stage-record file: ``stages-<commit>-<start>.jsonl``.

    Named by the resolved commit and the process's start time, so a second run
    of the same commit appends to a file of its own rather than overwriting the
    first one's, and the two are comparable by name alone.
    """
    directory = timing_directory()
    if directory is None:
        return None
    return directory / f"stages-{current_commit()[:12]}-{_FILE_STAMP}.jsonl"


def _installed_handler() -> _JSONLineHandler | None:
    r"""The record handler, added on the first record and kept for the process."""
    with _HANDLER_LOCK:
        for handler in logger.handlers:
            if isinstance(handler, _JSONLineHandler):
                return handler
        path = record_path()
        if path is None:
            return None
        handler = _JSONLineHandler(path)
        logger.addHandler(handler)
        return handler


def _named(target) -> str | None:
    r"""The input's name: a string as given, anything else by its own rendering."""
    if target is None:
        return None
    text = target if isinstance(target, str) else repr(target)
    text = " ".join(text.split())
    return text if len(text) <= _INPUT_LIMIT else text[: _INPUT_LIMIT - 1] + "…"


def _emit(payload: dict) -> None:
    r"""Hand one record to the logger, which the installed handler writes."""
    if _installed_handler() is None:
        return
    logger.info(payload["stage"], extra={"timing": payload})


@contextmanager
def stage(name: str, input=None, **fields):
    r"""Record the wall time of one stage of a computation, named for its input.

    ``name`` is the stage — ``"ambient O(L) row"``, ``"coset walk and
    transport"`` — and ``input`` is what the stage was computed for, recorded by
    :func:`_named`; ``fields`` add any further scalar a reader needs (a rank, a
    flag) to the record.  The record is written when the block ends, whether it
    returned or raised, and the exception is re-raised unchanged: timing a stage
    is not a place to close an error.
    """
    entry = {
        "record": "stage",
        "stage": name,
        "input": _named(input),
        "commit": current_commit(),
        "run": _FILE_STAMP,
        "pid": _PROCESS_ID,
    }
    entry.update(fields)
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


def timed_stage(name: str, *, input=None):
    r"""Time a whole function as one stage, without touching its body.

    ``input`` is a callable reading the name of the stage's input out of the
    call's arguments; omitted, the first positional argument is the input, which
    is the lattice or the group in every call site that uses the default.  The
    wrapper is one clock reading per call and no per-element work, and
    :func:`functools.wraps` leaves the signature and docstring the function's own.
    """

    def decorate(function):
        @wraps(function)
        def timed(*arguments, **keywords):
            subject = input(*arguments, **keywords) if input is not None else (arguments[0] if arguments else None)
            with stage(name, input=subject):
                return function(*arguments, **keywords)

        return timed

    return decorate


def read_stage_records(path=None, *, after: int = 0) -> tuple[dict, ...]:
    r"""The stage records in ``path``, from byte offset ``after`` onward.

    ``path`` defaults to this process's own record file; ``after`` is how a
    reader takes the records one call appended without parsing the ones before
    it.  A missing file is no records, never an error: a run that reached no
    measured stage has nothing to say.
    """
    location = record_path() if path is None else Path(path)
    if location is None or not location.is_file():
        return ()
    with location.open("r", encoding="utf-8") as handle:
        handle.seek(after)
        records = []
        for line in handle:
            line = line.strip()
            if line:
                record = json.loads(line)
                if record.get("record") == "stage":
                    records.append(record)
    return tuple(records)


def stage_names(records) -> tuple[str, ...]:
    r"""The stage names of ``records``, in the order the run wrote them."""
    return tuple(record["stage"] for record in records)
