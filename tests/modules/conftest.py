r"""Session instruments for the module tests.

A test may not name a private engine entry (``TL01``, ``TL02``), so the count of
engine work one action did is bound here as a builtin: a directory's
``conftest.py`` binds the abbreviations its tests use, and
``sage_extensions.testing.test_lint`` reads the allowed names after the
conftests have run.  Each instrument patches through
``pytest.MonkeyPatch.context()``, so a failing action leaves the process as it
found it.
"""

from __future__ import annotations

import builtins

import pytest


def matrices_materialized_by(action):
    r"""Return ``action()`` and the number of times it materialized a framed matrix.

    A presented module's relation matrix is materialized by the presented
    owner's ``_engine_matrix``: the engine's cover, its relation submodule and
    every Smith form are read through it.  That is where a presented module
    computes, so a construction that states it computes nothing leaves the count
    at zero and a first request for the invariant factors raises it.
    """
    from sage_extensions.categories.modules.framed.finitely_generated import (
        finitely_presented_modules,
    )

    materialized = []
    original = finitely_presented_modules._engine_matrix

    def counted(morphism):
        materialized.append(1)
        return original(morphism)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(finitely_presented_modules, "_engine_matrix", counted)
        value = action()
    return value, len(materialized)


builtins.matrices_materialized_by = matrices_materialized_by
