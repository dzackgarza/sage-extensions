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

**Where the record goes.**  :func:`timing_directory` is ``.timings/`` at the
root of the source checkout this module is a file of, which ``.gitignore`` keeps
out of git and ``CONTRIBUTING.md`` ENV-03 states; and, for a package installed
from a wheel, which has no checkout, the running user's own state directory:
``$XDG_STATE_HOME/sage-extensions/timings``, or
``~/.local/state/sage-extensions/timings`` when that variable is unset.  The
directory has an owner either way -- the checkout's, at its root, or the user's,
in the place the XDG Base Directory Specification sets aside for a program's
state -- so a run writes where its own owner keeps its records, never into the
directory it was started from, and the directory is created and asserted.  One
file per process, named by the resolved commit, the process's start time to the
microsecond and its pid, so two runs of the same commit never overwrite each
other's records — two runs started in the same second are two processes, and two
processes are two pids — and a record is never a claim about which commit
produced it: the commit is in its name and in every line.

**What a record line holds.**  ``stage`` (the name), ``id`` (this stage's own
id, unique within the run's file), ``parent`` (the ``id`` of the stage that
encloses it, ``null`` for a stage nothing encloses), ``input`` (the name of what
was computed, written by the caller), ``seconds`` (wall time,
``time.perf_counter``), ``started`` and
``finished`` (UTC, ISO 8601), ``outcome`` (``"returned"`` or ``"raised"``, with
``error`` naming the exception class), ``commit``, ``run`` (the process's start
stamp, which is the file's own name) and ``pid``.

**What identifies a record.**  Its run and its ``id``: ``run`` is the file, the
``id`` is the line, and ``parent`` says which line's stage contains it, so a
reader tells two records apart and finds a stage's sub-stages by these two
fields, in one file, without reading a name.  ``input`` is what a reader is told
about the computation -- the owner's public description of the input, which the
call site writes -- and it is a description, not an identity: two computations
may carry one name, and nothing here makes a name unique.

**What it costs when nobody reads it.**  A stage is two ``perf_counter``
readings, the fitting of its input's name, and one appended line.  Nothing is
measured per element, no computation is re-run to time it, and the handler is
added on the first record rather than at import, so importing the library writes
nothing.

**The input's name is the caller's.**  ``input`` is a string the call site builds
from what it already holds — the row's parameters, a plane's position, the
lattice's ring and Gram, the coordinates of a vector — and this module inspects
nothing it is handed.  A name whose text came from reading its object would be a
record that depends on a class and on whatever that class happens to carry; a
name read off a display would be a computation, on a lattice an invariant one,
bought for a log line.  ``input`` is a name, so it is written where the name is
known, and it is not asked to be unique: a record's identity is its run and its
stage id, above.

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
import re
import subprocess
import threading
import time
import tomllib
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache, wraps
from itertools import count
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
r"""The durable record directory at a checkout's root, stated in ``CONTRIBUTING.md`` ENV-03."""

STATE_DIRECTORY_PARTS = ("sage-extensions", "timings")
r"""The record directory of an installed package, below the user's state directory."""

STATE_HOME_VARIABLE = "XDG_STATE_HOME"
r"""The variable that states the running user's state directory, per the XDG Base Directory Specification."""

SOURCE_REVISION_FILE_NAME = "source_revision"
r"""The file a build writes the revision it built from into, beside this module (``setup.py``)."""

DISTRIBUTION_NAME = "sage-extensions"
r"""The project ``pyproject.toml`` declares this distribution to be, and what a source tree of it declares."""

_COMMIT_ID = re.compile(r"[0-9a-f]{40}")
r"""What a revision is: forty lowercase hexadecimal characters, and nothing else is one."""

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

# The id of the next stage this process opens.  One counter for the process is
# what makes an id unique within the run's file: one process writes one file, so
# two ids of one counter are two lines of that file, and a fork that takes a file
# of its own continues the counter rather than sharing a name with it.
_STAGE_COUNTER = count(1)


class _OpenStages(threading.local):
    r"""The stages one thread has open, innermost last, and the pid they opened under.

    A ``threading.local`` whose two fields exist in every thread because they are
    set when the thread's own copy is made, rather than being probed for on each
    read: a thread that has opened nothing has an empty stack, which is a state
    and not an absence.  The pid is the process the stack was emptied for: a
    forked child inherits its parent's stack and writes a file of its own, which
    holds none of those ids, so the child starts from an empty one.
    """

    def __init__(self) -> None:
        self.ids: list[int] = []
        self.pid = os.getpid()


_OPEN_STAGES = _OpenStages()

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
def _package_directory() -> Path:
    r"""The installed ``sage_extensions`` package directory this module is a file of."""
    package = Path(__file__).resolve().parent
    assert package.name == "sage_extensions", (
        f"this module is a file of {package}, which is not the sage_extensions package directory"
    )
    return package


@lru_cache(maxsize=1)
def _checkout_root() -> Path | None:
    r"""The source checkout this module is a file of, and ``None`` for an installed package.

    Three facts about the installation itself, each read and none inferred from a
    path: the tree above ``<tree>/src/sage_extensions`` declares this distribution
    as its project, that tree's git tracks this very module, and it is the tree
    whose ``HEAD`` the record is to name.  A package that an installation placed
    in a consumer's tree -- ``pip install --target <consumer>/src`` puts
    ``<consumer>/src/sage_extensions`` exactly where a checkout keeps one, under
    the consumer's own ``pyproject.toml`` and beside the consumer's own commit --
    sits in a tree that declares the consumer's project and tracks none of these
    files, so it is an installation here however much it looks like a source tree
    from above.
    """
    package = _package_directory()
    tree = package.parents[1]
    if _declared_project_name(tree) != DISTRIBUTION_NAME:
        return None
    if not _tracked(tree, package.relative_to(tree) / Path(__file__).name):
        return None
    return tree


def _declared_project_name(tree: Path) -> str | None:
    r"""The project ``<tree>/pyproject.toml`` declares, and ``None`` when it declares none.

    A file that does not parse as TOML, or that is not there, declares no
    project: the tree above an installation may hold a project file of its own,
    and one this reads nothing from is not a statement that the tree is this
    library's source.  That is the answer the caller acts on, not an error.
    """
    try:
        declared = tomllib.loads((tree / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None
    match declared.get("project"):
        case {"name": str(name)}:
            return name
        case _:
            return None


def _tracked(tree: Path, path: Path) -> bool:
    r"""Whether the repository at ``tree`` tracks ``path``, asked of git.

    A source checkout tracks its own module; a directory an installation was
    placed in holds files that are the installer's, and tracks none of them.
    """
    completed = subprocess.run(
        ("git", "-C", str(tree), "ls-files", "--error-unmatch", str(path)),
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


@lru_cache(maxsize=1)
def _built_revision() -> str | None:
    r"""The revision this installation was built from, and ``None`` if it recorded none.

    ``setup.py``'s ``build_py`` writes the source checkout's commit beside this
    module as ``source_revision`` at the moment the wheel is built, which is the
    only moment at which the revision the wheel's code came from is known: once
    the wheel is installed there is no checkout to ask, and an environment
    variable would name whatever the process was told -- in a consumer's job,
    the commit of a different repository.
    """
    recorded = _package_directory() / SOURCE_REVISION_FILE_NAME
    if not recorded.is_file():
        return None
    return recorded.read_text(encoding="utf-8").strip() or None


@lru_cache(maxsize=1)
def timing_directory() -> Path:
    r"""The record directory, created if it is not there, and asserted.

    ``.timings/`` at the root of the source checkout this module is a file of
    (:func:`_checkout_root`), so the library's stage records and the test runs'
    report logs are kept together there (``CONTRIBUTING.md`` ENV-03); and, for an
    installation that is not a checkout, the running user's state directory as
    the XDG Base Directory Specification states it, ``$XDG_STATE_HOME`` or
    ``~/.local/state``, under ``sage-extensions/timings``.  A directory that
    cannot be made is an error at the first stage rather than a record silently
    not written.
    """
    checkout = _checkout_root()
    if checkout is not None:
        directory = checkout / RECORD_DIRECTORY_NAME
    else:
        named = os.environ.get(STATE_HOME_VARIABLE)
        state = Path(named).expanduser() if named else Path.home() / ".local" / "state"
        directory = state.joinpath(*STATE_DIRECTORY_PARTS)
    directory.mkdir(parents=True, exist_ok=True)
    assert directory.is_dir(), (
        f"the timing record's directory {directory} is not a directory after it was made"
    )
    return directory


@lru_cache(maxsize=1)
def current_commit() -> str:
    r"""The revision of this library's source, resolved once per process.

    From the installation's own record of what it was built from, when it has one
    (:func:`_built_revision`): a wheel's build wrote the checkout's commit beside
    this module, and that is the revision its code came from whatever trees the
    wheel was installed into or beside.  From the checkout when this module is a
    file of one -- that tree's own git, and nothing else, because an environment
    variable names whatever the process was told.  An installation that has
    neither raises: a record attributed to a commit nothing resolved, such as the
    commit of the consumer tree the package sits in, would be a claim about code
    that did not produce it.
    """
    recorded = _built_revision()
    if recorded is not None:
        resolved = recorded
        source = (
            f"the build revision recorded in {_package_directory() / SOURCE_REVISION_FILE_NAME}"
        )
    else:
        checkout = _checkout_root()
        assert checkout is not None, (
            f"{_package_directory()} carries no {SOURCE_REVISION_FILE_NAME}, and the tree above it "
            f"is not a source checkout of {DISTRIBUTION_NAME} -- none of its pyproject.toml declares "
            "that project, or its git does not track this module -- so this installation knows no "
            "revision to attribute its timing records to"
        )
        completed = subprocess.run(
            ("git", "-C", str(checkout), "rev-parse", "HEAD"),
            capture_output=True,
            text=True,
            check=True,
        )
        resolved = completed.stdout.strip()
        source = f"git rev-parse HEAD in {checkout}"
    assert _COMMIT_ID.fullmatch(resolved) is not None, (
        f"{source} returned {resolved!r}, which is not a commit id"
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


def _open_stage_ids() -> list[int]:
    r"""The ids of the stages this thread has open, outermost first.

    Held per thread, because stages nest within a computation and two threads'
    stacks are not one; and emptied for a process that forked, because that
    process writes a file of its own and the parent's open ids are not lines of
    it.
    """
    if _OPEN_STAGES.pid != os.getpid():
        _OPEN_STAGES.ids = []
        _OPEN_STAGES.pid = os.getpid()
    return _OPEN_STAGES.ids


def _emit(entry: dict) -> None:
    r"""Hand one record to the logger, whose installed handler appends it."""
    _installed_handler()
    logger.info(entry["stage"], extra={"timing": entry})


@contextmanager
def stage(name: str, input: str):
    r"""Record the wall time of one stage of a computation, named for its input.

    ``name`` is the stage — ``"ambient O(L) row"``, ``"coset walk and
    transport"`` — and ``input`` is the name of what it was computed for, a
    string the caller writes from what it holds: ``"a rank-11 lattice of Gram
    ..."``, ``"the subgroup where ..."``, a vector's coordinates.  Nothing about
    the input is read here, so a record never depends on what an object happens
    to carry, and the name identifies nothing: two computations may be named
    alike.

    What identifies the record is its ``id`` and its ``parent``.  The ``id`` is
    this process's next, and one process writes one file, so it is unique there;
    the ``parent`` is the ``id`` of the stage that encloses this one, ``None``
    when nothing does.  A reader tells two records apart by the pair, and finds a
    stage's sub-stages as the records whose ``parent`` is its ``id``.

    The record is written when the block ends, whether it returned or raised,
    and the exception is re-raised unchanged: timing a stage is not a place to
    close an error.
    """
    open_stages = _open_stage_ids()
    entry = {
        "stage": name,
        "id": next(_STAGE_COUNTER),
        "parent": open_stages[-1] if open_stages else None,
        "input": " ".join(input.split()),
        "commit": current_commit(),
        "run": _process_stamp(),
        "pid": os.getpid(),
    }
    started = datetime.now(timezone.utc)
    clock = time.perf_counter()
    open_stages.append(entry["id"])
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
    finally:
        closed = open_stages.pop()
        assert closed == entry["id"], (
            f"the stage {name!r} of {entry['input']} has the id {entry['id']}, but the open stage "
            f"stack closed {closed}: the records would name one another's stages as parents"
        )
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
