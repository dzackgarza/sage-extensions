r"""Session instruments for the module tests.

A test may not name a private engine entry (``TL01``, ``TL02``), so the one
measurement the module tests take is bound here as a builtin: a directory's
``conftest.py`` binds the names its tests use, and
``sage_extensions.testing.test_lint`` reads the allowed names after the
conftests have run.  The instrument patches through
``pytest.MonkeyPatch.context()``, so a failing action leaves the process as it
found it, and it measures behaviour a test reaches publicly -- a construction
and its first request -- rather than a private helper's return value.
"""

from __future__ import annotations

import builtins

import pytest


def construction_work_of(construction, request):
    r"""Return ``(value, work the construction did, work the first request did)``.

    The construction this contract is about did two kinds of work for a cokernel:
    it realized the chosen resolution -- the arrow's Mor re-wrap, the relation
    images, the lifts of the added images and the fraction-field rank all run
    inside that one realization -- and it materialized the engine matrix.
    Counting the engine matrix alone leaves a construction that computes through
    the resolution green, so both are instruments here.

    ``_PendingResolution.realize`` is the only seam a chosen resolution is built
    through (``Objects.ParentMethods.selected_resolution``), so the first count
    covers every construction-time computation, whatever it reaches for.  The
    second covers the presented owner's ``_engine_matrix``, the materialization
    of the relation matrix, the cover and every Smith form.

    The request is run inside the same patch, so a test can assert that the
    instrument is live: an action whose first request raises neither count
    leaves the construction's own count unfalsified.
    """
    from sage_extensions.categories.abstract_categories import objects as resolution_records
    from sage_extensions.categories.modules.framed.finitely_generated import (
        finitely_presented_modules,
    )

    work = []
    original_realize = resolution_records._PendingResolution.realize
    original_matrix = finitely_presented_modules._engine_matrix

    def counted_realize(pending):
        work.append(1)
        return original_realize(pending)

    def counted_matrix(morphism):
        work.append(1)
        return original_matrix(morphism)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(resolution_records._PendingResolution, "realize", counted_realize)
        patch.setattr(finitely_presented_modules, "_engine_matrix", counted_matrix)
        value = construction()
        during_construction = len(work)
        request(value)
        during_request = len(work) - during_construction
    return value, during_construction, during_request


builtins.construction_work_of = construction_work_of


def relation_image_reads_of(subject, action):
    r"""Return how many times ``action`` reads ``subject``'s relation images.

    The claimed torsion placement's validator is the claim's refutation, and the
    relation matrix of the presentation is the presented-module owner's datum.
    A validator on the claim asks that owner for its torsion decision; it does
    not reach the descendant's relation-image adapter for the claimed module and
    hand-assemble the matrix itself (``OWN-05``, ``STY-03``).  The count is the
    boundary: it is zero exactly when the read goes through the module's own
    decision.
    """
    from sage_extensions.categories.modules.framed.finitely_generated import (
        finitely_presented_modules,
    )

    reads = []
    original = finitely_presented_modules._relation_images

    def counted(module):
        if module is subject:
            reads.append(1)
        return original(module)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(finitely_presented_modules, "_relation_images", counted)
        action()
    return len(reads)


builtins.relation_image_reads_of = relation_image_reads_of
