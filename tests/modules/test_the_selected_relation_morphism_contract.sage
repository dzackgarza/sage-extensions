r"""The protected relation-morphism contract, on joined parents too.

``_selected_relation_morphism`` is the protected hook by which module, group
module and module-morphism constructions rebuild a kernel, quotient or scalar
change from a selected finite presentation.  A module with a chosen finite
presentation states its relations through ``presentation()`` — the zero morphism
from the empty free module when its framing is a basis — and a module without
one states nothing.

The generic ``Modules`` owner used to answer a static ``None``.  On a joined
parent that resolves the name before a specific owner's, that shadowed the
statement: measured on ``QQ[x]/(x)``, a one-dimensional object whose frame is a
basis, the hook reported "relations unknown" while ``presentation()`` answered
the empty relation family.  It now reads the retained presentation itself, so the
answer no longer depends on method order.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModulesWithChosenFinitePresentation,
)


def _reduced_point():
    r"""``QQ[x]/(x)``: a joined parent whose MRO put ``Modules`` ahead of its framed-free facet."""
    polynomials = QQ["x"]
    return polynomials.quotient_ring(polynomials.ideal([polynomials.gen()]))


def _fat_point_view():
    r"""``QQ[x]/(x^2)`` read over ``QQ``: a module with a chosen non-free presentation."""
    polynomials = QQ["x"]
    algebra = polynomials.quotient_ring(polynomials.gen() ** 2)
    return algebra.as_algebra_over(QQ)


def test_a_framed_free_module_states_the_empty_relation_family() -> None:
    r"""``QQ**1`` and the reduced point: no relations, and that is an answer, not ``None``."""
    for module in (QQ**1, _reduced_point()):
        assert module in ModulesWithChosenFinitePresentation(QQ)
        relation = module._selected_relation_morphism()
        assert relation is not None
        assert relation.domain().module_generating_set().cardinality() == 0
        assert relation.codomain() is module or (
            tuple(relation.codomain().module_generating_set())
            == tuple(module.module_generating_set())
        )


def test_a_module_with_a_chosen_presentation_states_its_relations() -> None:
    r"""The fat point's ``QQ``-module has a presentation with no relations: a basis."""
    view = _fat_point_view()

    assert view in ModulesWithChosenFinitePresentation(QQ)
    relation = view._selected_relation_morphism()
    assert relation is not None
    assert relation.domain().module_generating_set().cardinality() == 0
    assert view.module_generating_set().cardinality() == 2


def test_a_module_without_a_presentation_states_none() -> None:
    r"""A general module over ``QQ`` has no chosen presentation to report."""
    general = Modules(QQ)(QQ)

    assert general not in ModulesWithChosenFinitePresentation(QQ)
    assert general._selected_relation_morphism() is None


def test_the_hook_agrees_with_the_public_presentation() -> None:
    r"""The contract reports the module's own stated presentation, not a second one."""
    from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
        _relation_morphism,
    )

    for module in (QQ**1, _reduced_point(), _fat_point_view()):
        reported = module._selected_relation_morphism()
        stated = module.presentation()
        # Two constructions of one relation morphism need not be the same object;
        # what the contract promises is the same statement about it.
        assert (
            reported.domain().module_generating_set().cardinality()
            == stated.domain().module_generating_set().cardinality()
        )
        assert tuple(reported.codomain().module_generating_set()) == tuple(
            stated.codomain().module_generating_set()
        )
        assert _relation_morphism(module) is not None
