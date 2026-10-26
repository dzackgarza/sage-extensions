r"""The affine quotient of a group action and the sections it acts on, as functors.

For a ``G``-scheme ``X`` the scheme ``Spec(Gamma(X, O_X)^G)`` is universal
for invariant morphisms from ``X`` to affine schemes.  This is the affine
quotient, without asserting a quotient universal among all schemes.  Its
definition and the section action belong to ``GObjects(G, Schemes(R))``;
the selected invariant computation is supplied by affine ``X = Spec(A)``.
This module supplies the functorial arrows and the selected base-change
comparison.

Given an equivariant ``f: X -> Y``, the composite ``q_Y f`` is invariant
because ``f`` intertwines the two actions and ``q_Y`` is invariant, so it
factors uniquely through ``q_X`` as ``f/G: X/G -> Y/G``.  Uniqueness of that
factorization is what makes ``X -> X/G`` functorial: it forces
``(g f)/G = (g/G)(f/G)`` and ``id/G = id`` without either being computed
separately.  An equivariant automorphism of ``X`` therefore descends to an
automorphism of ``X/G``, which is how a symmetry compatible with the group
action reaches the quotient.

Sections go the other way.  Taking the coordinate algebra of an affine
``G``-scheme with the action pullback induces on it is contravariant, and
lands in the ``R[G]``-modules; the invariants of that module are the sections
of the quotient, which is the statement the two functors make together.

The regime is the one the invariant algebra is constructed in.  For a scalar
field extension, both invariant algebras can be constructed independently and
the canonical base-change comparison is represented below.  It is promoted to
an isomorphism only under the Reynolds hypothesis that the finite group order
is invertible in the target field.  No such assertion is made for arbitrary
base change, and in residue characteristic dividing the group order this
constant-group comparison is deliberately not used as a substitute for
group-scheme geometry.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.functors.group_actions import (
    _underlying_equivariant_arrow,
)
from sage_extensions.categories.group.g_objects import GObjects
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    OwnedRings,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_ring,
)
from sage_extensions.categories.schemes.schemes import (
    AffineGSchemes,
    Schemes,
    _affine_morphism_from_pullback,
    _evaluate_polynomial_in_algebra,
)




def _affine_invariant_quotient_base_change_morphism(
    parent,
    pullback,
    *,
    acted_scheme,
    ring_map,
    changed_acted_scheme,
    base_changed_old_quotient,
):
    r"""Construct the invariant-quotient comparison in its generated scheme Mor."""
    return parent.element_class(
        parent,
        None,
        mor=parent,
        pullback=pullback,
        affine_quotient_base_change_data={
            "acted_scheme": acted_scheme,
            "ring_map": ring_map,
            "changed_acted_scheme": changed_acted_scheme,
            "base_changed_old_quotient": base_changed_old_quotient,
        },
    )

def AffineInvariantQuotientBaseChangeComparison(
    acted_scheme, ring_map, *, _action_category=None
):
    r"""Return the canonical morphism ``X_{k'}/G -> (X/G)_{k'}``.

    The category-level entry supplies the retained action category for a
    generic functor presentation.  Evaluation gives its exact scheme carrier;
    a functor-category object is never reinterpreted as a scheme.
    """
    category = _action_category
    if category is None:
        category = GObjects(
            acted_scheme.acting_group(), Schemes(acted_scheme.scheme_base_ring())
        )
    action = category._scheme_action_functor(acted_scheme)
    source = category.underlying_category().base_ring()
    target = _owned_ring(ring_map.codomain())
    if ring_map.domain() is not source:
        raise ValueError(
            f"cannot base change the quotient of {acted_scheme} along {ring_map}: the map "
            f"starts at {ring_map.domain()}, but {acted_scheme} lies over {source}"
        )
    if ring_map not in OwnedRings().Mor(source, target):
        raise TypeError(
            f"the invariant-quotient base change needs a retained ring morphism "
            f"from {source} to {target}, not {ring_map}"
        )
    assert source in OwnedFields() and target in OwnedFields(), (
        f"the invariant-quotient base-change comparison along {ring_map} needs a field "
        f"extension, but its domain is {source} and its codomain is {target}"
    )
    # Establish the selected invariant-computation regime before constructing
    # a changed action.  An infinite or unrepresented action reaches its
    # named frontier here, without an eager enumeration of the acting group.
    old_quotient = category.affine_quotient(acted_scheme)
    old_quotient_map = category.quotient_morphism(acted_scheme)
    group = category.acting_group()
    point = action.domain().an_object()
    arrows = action.domain().Mor(point, point)
    carrier = action(point)
    change = Schemes(source).base_change_functor(ring_map)
    changed_carrier = change(carrier)
    changed_acted = AffineGSchemes(group, target)(
        changed_carrier,
        lambda group_element: change(action(arrows(group(group_element)))),
    )
    changed_old_quotient = change(old_quotient)
    changed_old_quotient_map = change(old_quotient_map)
    transported_quotient_map = _affine_morphism_from_pullback(
        changed_acted,
        changed_old_quotient,
        changed_old_quotient_map.coordinate_algebra_morphism(),
    )
    comparison = changed_acted.factor_through_affine_quotient(
        transported_quotient_map
    )
    mor = comparison.parent()
    pullback = comparison.coordinate_algebra_morphism()
    return mor(
        lambda selected_mor: _affine_invariant_quotient_base_change_morphism(
            selected_mor,
            pullback,
            acted_scheme=acted_scheme,
            ring_map=ring_map,
            changed_acted_scheme=changed_acted,
            base_changed_old_quotient=changed_old_quotient,
        )
    )



class AffineQuotientFunctor(Functor):
    r"""The universal affine-target quotient on ``GObjects(G, Sch_R)``.

    The represented affine invariant algorithm supplies computation; a
    different carrier retains the same definition and its named frontier.
    """

    def __init__(self, group, base_ring) -> None:
        base = _own_ring(base_ring)
        self._group = group
        self._base_ring = base
        Functor.__init__(self, GObjects(group, Schemes(base)), Schemes(base).Affine())

    def acting_group(self):
        return self._group

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, acted):
        return self.domain().affine_quotient(acted)

    def _apply_morphism(self, arrow):
        source = arrow.domain()
        target = arrow.codomain()
        category = self.domain()
        underlying = _underlying_equivariant_arrow(
            arrow, self.acting_group(), Schemes(self.base_ring())
        )
        return category.factor_through_affine_quotient(
            source, category.quotient_morphism(target) * underlying
        )

    def _repr_(self):
        return f"Affine quotient by {self.acting_group()}"


class _AffineSectionModuleFunctor(Functor):
    r"""``Gamma: GSch_R^op -> Modules(R[G])``, with affine computation.

    The original affine category adapter retains its affine source category;
    the common action category supplies the general source explicitly.

    The sections of an affine ``G``-scheme ``X = Spec(B)`` carry one
    ``G``-action, and contravariance fixes which one.  Pullback composes the
    wrong way round, ``sigma_g^* sigma_h^* = sigma_{hg}^*``, so the left
    action is ``g . b = sigma_{g^{-1}}^*(b)`` and nothing else.

    This is the linearization of ``pi_* O_X`` along the structure morphism
    ``pi: X -> Spec(R)``, read as an ``R``-module with its ``G``-action.  For
    a cyclic cover it is where the grading of the cover algebra becomes
    representation theory: the deck generator multiplies the summand
    ``A z^i`` by ``zeta^{-i}``, so each summand is an eigen-submodule and the
    invariants are the summand of character one, which is what descends to
    the quotient.  Evaluating at a fixed point of the action is a morphism of
    this category, so the fibre over a fixed point inherits the action, and
    over a ramification point of a cover it is where the deck action stops
    being free.

    An equivariant ``f: X -> Y`` pulls sections back, and ``f^*`` is a
    morphism of ``R[G]``-modules because ``f`` intertwines the two actions.
    """

    def __init__(self, group, base_ring, *, source_category=None) -> None:
        base = _own_ring(base_ring)
        self._group = group
        self._base_ring = base
        self._acted_category = GObjects(group, Schemes(base))
        schemes = (
            AffineGSchemes(group, base)
            if source_category is None
            else source_category
        )
        Functor.__init__(self, schemes.opposite(), Modules(base[group]))

    def acting_group(self):
        return self._group

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, opposite_acted):
        acted = opposite_acted.underlying_object()
        action_functor = self._acted_category._scheme_action_functor(acted)
        point = action_functor.domain().an_object()
        arrows = action_functor.domain().Mor(point, point)
        carrier = action_functor(point)
        match carrier:
            case _ if carrier in Schemes(self.base_ring()).Affine():
                algebra = carrier.coordinate_algebra()
                assert algebra.base_ring() is self.base_ring(), (
                    f"Gamma({carrier}, O) is an {self.base_ring()}-module through its "
                    f"structure map, but its retained coordinate-module realization "
                    f"is over {algebra.base_ring()}; no coefficient-module realization "
                    "along that exact structure map is selected for this section functor"
                )
            case _:
                raise AssertionError(
                    f"Gamma({carrier}, O) with its {self.acting_group()}-action is "
                    "defined, but no selected global-section computation for this "
                    "nonaffine scheme is available"
                )

        def action(group_element, section):
            element = self.acting_group()(group_element)
            pullback = action_functor(arrows(~element)).coordinate_algebra_morphism()
            return pullback(algebra(section))

        return self.codomain()(algebra, action)

    def _apply_morphism(self, opposite_arrow):
        arrow = opposite_arrow.underlying_arrow()
        source = self(opposite_arrow.domain())
        target = self(opposite_arrow.codomain())
        underlying = _underlying_equivariant_arrow(
            arrow, self.acting_group(), Schemes(self.base_ring())
        )
        pullback = underlying.coordinate_algebra_morphism()
        coefficient_mor = Modules(self.base_ring()).Mor(
            source.unformed_module(), target.unformed_module()
        )
        coefficient_map = (
            coefficient_mor(pullback)
            if pullback in coefficient_mor
            else coefficient_mor.elementwise(pullback)
        )
        # The actual coefficient pullback supplies the section map.  Its
        # group-module ingress retains the equivariance equations; no finite
        # module-generator table or unconditional diagnostic is inferred.
        return self.codomain().Mor(source, target)(coefficient_map)

    def _repr_(self):
        return f"Sections with their {self.acting_group()}-action"


__all__ = [
    "AffineInvariantQuotientBaseChangeComparison",
    "AffineQuotientFunctor",
]
