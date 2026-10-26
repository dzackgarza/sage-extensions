r"""Abelianization as the left adjoint to the inclusion of abelian groups.

For the owned group categories,

``(-)^ab ⊣ i : Ab -> Grp``.

The implementation uses GAP's natural quotient by the derived subgroup.  The
quotient map itself is retained as the unit, and morphisms are transported by
the universal property of that quotient rather than by a presentation chosen
in Python.
"""

from sage.groups.libgap_group import GroupLibGAP
from sage.libs.gap.libgap import libgap
from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.group.groups import (
    OwnedAbelianGroups,
    OwnedFiniteAbelianGroups,
    OwnedFiniteGroups,
    OwnedGroups,
    _element_from_engine,
    _element_to_engine,
    _gap_model,
    _own_group,
)


class _AbelianizationFunctor(Functor):
    r"""``G -> G/[G,G] : Grp -> Ab``."""

    def __init__(self) -> None:
        super().__init__(OwnedGroups(), OwnedAbelianGroups())
        self._quotient_projections = {}

    def _apply_object(self, group):
        match group:
            case _ if group in OwnedAbelianGroups():
                quotient = group
                quotient_projection = group.Mor(group).identity()
            case _ if group in OwnedFiniteGroups():
                model = _gap_model(group)
                derived = libgap.DerivedSubgroup(model)
                projection = libgap.NaturalHomomorphismByNormalSubgroup(model, derived)
                quotient = _own_group(
                    GroupLibGAP(projection.Range()),
                    refinements=(OwnedFiniteAbelianGroups(),),
                )
                quotient_projection = group.Mor(quotient)(projection)
            case _ if group in OwnedGroups().FinitelyPresentedAsGroup():
                assert False, (
                    f"the abelianization of the finitely presented group {group} is defined, but the current "
                    "preamble has no presentation-quotient route for G/[G,G]; add it at the group exact-sequence "
                    "owner rather than passing this group to GAP unconditionally"
                )
            case _:
                assert False, (
                    f"the abelianization of {group} is defined for every group, but the current preamble computes "
                    "only already-abelian groups and finite represented groups; no general quotient route is installed"
                )
        self._quotient_projections[id(group)] = (
            group,
            quotient,
            quotient_projection,
        )
        return quotient

    def quotient_projection(self, group):
        quotient = self(group)
        stored = self._quotient_projections.get(id(group))
        if (
            stored is None
            or stored[0] is not group
            or stored[1] is not quotient
        ):
            raise KeyError(
                f"the quotient map {group} -> {quotient} onto the abelianization is missing for {group}"
            )
        projection = stored[2]
        if projection.domain() is not group or projection.codomain() is not quotient:
            raise ValueError(
                f"the quotient map onto the abelianization of {group} must be {group} -> {quotient}, but it is "
                f"{projection.domain()} -> {projection.codomain()}"
            )
        return projection

    def _apply_morphism(self, morphism):
        source_abelianization = self(morphism.domain())
        target_abelianization = self(morphism.codomain())
        source_projection = self.quotient_projection(morphism.domain())
        target_projection = self.quotient_projection(morphism.codomain())
        match (morphism.domain(), morphism.codomain()):
            case (source, target) if source in OwnedAbelianGroups() and target in OwnedAbelianGroups():
                return source_abelianization.Mor(target_abelianization)(morphism)
            case (source, target) if source in OwnedFiniteGroups() and target in OwnedFiniteGroups():
                source_model = _gap_model(source_abelianization)
                target_model = _gap_model(target_abelianization)
                generators = tuple(source_model.GeneratorsOfGroup())
                images = tuple(
                    _element_to_engine(
                        target_abelianization,
                        target_projection(
                            morphism(
                                source_projection.lift(
                                    _element_from_engine(
                                        source_abelianization,
                                        generator,
                                    )
                                )
                            )
                        ),
                    )
                    for generator in generators
                )
                induced = libgap.GroupHomomorphismByImages(
                    source_model,
                    target_model,
                    list(generators),
                    list(images),
                )
                if induced.is_bool():
                    raise ValueError(
                        f"the group morphism {morphism} does not induce a map of abelianizations "
                        f"{source_abelianization} -> {target_abelianization}"
                    )
                return source_abelianization.Mor(target_abelianization)._from_engine_morphism(induced)
            case _:
                assert False, (
                    f"the induced map on abelianizations of {morphism} is defined by the universal property, but "
                    "the current preamble realizes it only for maps between already-abelian groups or finite "
                    "represented groups; the general quotient-factorization route is missing"
                )

    def _repr_(self):
        return "Abelianization functor"


class _AbelianGroupInclusionFunctor(Functor):
    r"""The full inclusion ``Ab -> Grp``."""

    def __init__(self) -> None:
        super().__init__(OwnedAbelianGroups(), OwnedGroups())

    def _apply_object(self, group):
        return group

    def _apply_morphism(self, morphism):
        return morphism

    def _repr_(self):
        return "Inclusion of abelian groups into groups"


class _AbelianizationAdjunction(Adjunction):
    r"""``(-)^ab ⊣ i``."""

    def __init__(self) -> None:
        super().__init__(_AbelianizationFunctor(), _AbelianGroupInclusionFunctor())

    def _unit_component(self, group):
        return self.left_adjoint().quotient_projection(group)

    def _counit_component(self, abelian_group):
        abelianization = self.left_adjoint()(abelian_group)
        assert abelianization is abelian_group, (
            f"the counit of abelianization at {abelian_group} must identify its abelianization with the same "
            f"abelian group, but the object map returned {abelianization}"
        )
        return abelian_group.Mor(abelian_group).identity()


    def _repr_(self):
        return "Abelianization/inclusion adjunction"


@cached_function
def _abelianization_functor() -> _AbelianizationFunctor:
    return _AbelianizationFunctor()


@cached_function
def _abelianization_adjunction() -> _AbelianizationAdjunction:
    return _AbelianizationAdjunction()


__all__ = []
