r"""Session abbreviations and instruments for the lattice tests.

A test may name the card row it asserts, and may not open the digest itself:
``sage_extensions.testing.test_lint`` rejects a file read inside a test file
(``TL01`` for ``json`` and ``pathlib``, ``TL13`` for ``__file__`` and ``Path``).
The digest is generated, not edited, by
``tests/cards/refresh_lattice_database_enriques.py`` from
``dzackgarza/lattice-database`` at the commit its ``_provenance.ref`` names, so
reading it in one place here keeps every expected number the database's.

This module binds the session's names as builtins, which is the mechanism the
lint documents: a directory's ``conftest.py`` binds the abbreviations its tests
use, and the lint reads the allowed names after the conftests have run.
``card`` is a row of the digest; ``spans_built_by`` and ``displays_rendered_by``
count what one action built and rendered; ``in_fresh_processes`` computes a
function of the test file again in new processes under chosen hash seeds.  Each instrument that patches does so
with ``pytest.MonkeyPatch.context()``, so a failing action leaves the process as
it found it.
"""

from __future__ import annotations

import builtins
import gc
import json
import os
import subprocess
import sys
import weakref
from pathlib import Path

import pytest

DIGEST = Path(__file__).resolve().parents[1] / "cards" / "lattice-database-enriques.json"


def card(section: str, tag: str) -> dict:
    r"""Return one card's rows from the digest.

    ``section`` is the digest's key for the row group (``arithmetic_groups``,
    ``polarization_counts``, ``plane_orbits``, ``discriminant_forms``) and
    ``tag`` the card's slug, so a test asks by tag and never by position:

        card("discriminant_forms", "6JRR")["orthogonal_group_order"]
    """
    return json.loads(DIGEST.read_text(encoding="utf-8"))[section][tag]


builtins.card = card


def counts_in_bounded_child(source, memory_bytes, alarm_seconds):
    r"""Return the ``count`` lines a child interpreter prints under two bounds.

    A row whose call grows without bound has to be this test's outcome and not the
    suite's: the child gets an address-space bound and an alarm, so the growth
    stops inside it, and the parent reads what it printed.  ``source`` runs in a
    fresh Sage interpreter with the same import path as the session, so it is the
    library the test imports that the child measures.

    The child's lines that begin ``count `` are returned as their last fields, in
    order, beside the exit status and the tail of its stderr.
    """
    import subprocess
    import sys

    program = "import signal\n" f"signal.alarm({alarm_seconds})\n"
    if memory_bytes:
        program += (
            "import resource\n"
            f"resource.setrlimit(resource.RLIMIT_AS, ({memory_bytes}, {memory_bytes}))\n"
        )
    program += "from sage_extensions.all import *  # noqa: F401,F403\n" + source
    completed = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True
    )
    counts = [
        line.split()[-1]
        for line in completed.stdout.splitlines()
        if line.startswith("count ")
    ]
    return completed.returncode, counts, completed.stderr.strip().splitlines()[-3:]


builtins.counts_in_bounded_child = counts_in_bounded_child

# A released object is observable only through a weak reference: identity and
# value say nothing about whether something still holds it.  ``weakref`` and
# ``gc`` are not session names, so they are bound here rather than imported by
# each test that observes a lifetime (``TL01``, ``TL13``).
builtins.weakref = weakref
builtins.gc = gc


def spans_built_by(action):
    r"""Return ``action()`` and the number of spans it built.

    A span of finitely many vectors of a lattice is built by
    ``Lattices.ParentMethods.subobject_on``.  A test asks for the count through
    this name, which is private to the arrangement and not to the mathematics,
    so the patch lives here (``TL02``, ``TL13``).
    """
    from sage_extensions.all import Lattices, ZZ

    parent_methods = Lattices(ZZ).ParentMethods
    original = parent_methods.subobject_on
    built = []

    def counted(self, generating_set):
        built.append(1)
        return original(self, generating_set)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(parent_methods, "subobject_on", counted)
        value = action()
    return value, len(built)


builtins.spans_built_by = spans_built_by


def displays_rendered_by(lattice, action):
    r"""Return ``action()`` and the number of displays ``lattice``'s class rendered.

    A lattice's display is its ``_repr_``, which computes the signature from the
    Gram, so counting it is how a test observes that a construction rendered
    nothing.  The shadow is set on the lattice's own class: ``_repr_`` is where
    the display is, while ``ParentMethods.__repr__`` is the inherited
    ``object.__repr__``, and a replacement of that would count a call which is
    not the display.
    """
    owner = lattice.__class__
    display = owner._repr_
    rendered = []

    def counted(self):
        rendered.append(1)
        return display(self)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(owner, "_repr_", counted)
        value = action()
    return value, len(rendered)


builtins.displays_rendered_by = displays_rendered_by


def built_without_display(named, action):
    r"""Return ``action()`` with the display of ``named`` replaced by a refusal.

    ``named`` is the object a construction states in the name it builds for its
    result: the lattice a shell is cut out of, the discriminant module whose
    isotropic subgroups are enumerated, the isometry whose fixed locus is taken.
    Storing that name is the construction's; rendering it is the reader's, so a
    construction that renders it has computed a display for nobody.  The refusal
    raises where the display is asked for, which is how a test observes that the
    construction asked, and the value of a construction that did not is returned.

    The shadow is set on the named object's own class, so it is that object's
    ``__repr__`` the construction would call -- ``_repr_`` is where the display
    is written, and the inherited ``__repr__`` is what reaches it.

    Sage's own hash is primed first and asked for nothing afterwards:
    ``CategoryObject.__hash__`` is ``hash(repr(self))``, kept once computed, so
    the first hash of an owned object renders it as the runtime's datum and not
    the construction's.  Every display after that one is the construction's own.
    A construction that keys a dictionary on the named object therefore passes,
    and one that names the object in a string does not.
    """
    hash(named)
    owner = named.__class__

    def refuse(self):
        raise AssertionError(
            "the construction asked the object it names for its display"
        )

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(owner, "__repr__", refuse)
        value = action()
    return value


builtins.built_without_display = built_without_display


def presentations_built_by(construction, request):
    r"""Return ``(value, presentations the construction built, the request's)``.

    A finite form's automorphism is built from the engine's matrix and states
    its two presented module maps as computations, asked for on the first
    request that needs one: a construction that presents them has computed two
    morphisms nobody asked for, which is the cost a matrix question must not
    carry.  The presentation is ``_transported_map``, the transport of the
    matrix back through the form's normalization, so counting it counts the
    presentations.

    The request runs inside the same patch, so a test can assert that the
    instrument is live: a first request that presents nothing leaves the
    construction's own count unfalsified.
    """
    from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
        TorsionFormOrthogonalGroup,
    )

    presented = []
    original = TorsionFormOrthogonalGroup._transported_map

    def counted(self, engine_automorphism):
        presented.append(1)
        return original(self, engine_automorphism)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(TorsionFormOrthogonalGroup, "_transported_map", counted)
        value = construction()
        during_construction = len(presented)
        request(value)
        during_request = len(presented) - during_construction
    return value, during_construction, during_request


builtins.presentations_built_by = presentations_built_by


FRESH_PROCESS_SCRIPT = """
import json, runpy, sys
from pathlib import Path

test_file, function_name = Path(sys.argv[1]), sys.argv[2]
for directory in reversed(test_file.resolve().parents):
    if (directory / "conftest.py").is_file():
        runpy.run_path(str(directory / "conftest.py"))
import sage.all_cmdline
import sage_extensions.all
from sage.repl.preparse import preparse_file

namespace = dict(vars(sage.all_cmdline))
source = test_file.read_text()
exec(compile(preparse_file(source) if test_file.suffix == ".sage" else source, str(test_file), "exec"), namespace)
print(json.dumps(namespace[function_name]()))
"""


def in_fresh_processes(function, seeds):
    r"""Return ``function()`` computed once per seed, each in a new Sage process with ``PYTHONHASHSEED`` that seed.

    ``function`` is a module-level function of the running test's file, taking
    no argument and returning a JSON value (integers, strings, lists,
    dictionaries with string keys).  Each new process runs the conftests above
    that file, executes the file and calls the function by name, so the
    function is linted with the test and is the same code in every process.
    The processes run at once, so the wall time is that of one.  A property
    that holds between processes (a partition, an order, a choice that must
    not depend on string hashing) is asserted by comparing the values:

        first, second = in_fresh_processes(partition, [1, 2])
        assert first == second

    A failure in a new process fails the test with that process's stderr.
    """
    test_file = os.environ["PYTEST_CURRENT_TEST"].split("::")[0]
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", FRESH_PROCESS_SCRIPT, test_file, function.__name__],
            env=dict(os.environ, PYTHONHASHSEED=str(int(seed)), PYTHONPATH=os.pathsep.join(sys.path)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for seed in seeds
    ]
    values = []
    for process in processes:
        output, errors = process.communicate()
        assert process.returncode == 0, errors
        values.append(json.loads(output.splitlines()[-1]))
    return tuple(values)


builtins.in_fresh_processes = in_fresh_processes

