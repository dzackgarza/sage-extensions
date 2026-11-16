r"""Session instruments for the group tests.

A test may not name a private entry point (``TL01``, ``TL02``) and may not read an
object's instance state (``TL03``), so the one measurement the group tests take is
bound here as a builtin: a directory's ``conftest.py`` binds the names its tests
use, and ``sage_extensions.testing.test_lint`` reads the allowed names after the
conftests have run.  The instrument patches through
``pytest.MonkeyPatch.context()``, so a failing action leaves the process as it
found it, and it measures work an action drives publicly -- a construction and a
first question about what it built -- rather than a private helper's return value.
"""

from __future__ import annotations

import builtins

import pytest


def orbit_sweeps_of(construction, question):
    r"""Return ``(built, answer, sweeps built with, sweeps asked with)``.

    ``_orbit_words`` is the one breadth-first sweep an orbit is reached by: it
    evaluates every selected letter at every point it reaches.  A construction that
    reaches points runs it, and a question about a point that construction already
    swept must not run it again -- the set it built holds the sweep's answer, so a
    second run is one orbit searched twice.

    The question is run inside the same patch as the construction, so a test can
    assert that the instrument was live: a question that leaves both counts where
    the construction left them is a count the test has not falsified.
    """
    from sage_extensions.categories.group import g_sets

    sweeps = []
    original = g_sets.FiniteGSets._orbit_words

    def counted(self, *arguments, **keywords):
        sweeps.append(1)
        return original(self, *arguments, **keywords)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(g_sets.FiniteGSets, "_orbit_words", counted)
        built = construction()
        during_construction = len(sweeps)
        answer = question(built)
        during_question = len(sweeps) - during_construction
    return built, answer, during_construction, during_question


builtins.orbit_sweeps_of = orbit_sweeps_of
