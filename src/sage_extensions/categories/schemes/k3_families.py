r"""Horikawa ``(4,4)`` double-cover K3 family with its three involutions.

Let ``Y=P^1 x P^1`` and let

``tau([x0:x1],[y0:y1])=([x0:-x1],[y0:-y1])``.

The standard linearization on ``O_Y(4,4)`` splits its 25-dimensional section
space into the even and odd parity eigenspaces.  This module does not insert
the source dimensions ``13`` and ``12``: they are obtained from the actual
``C2`` action on the represented monomial basis and the common isotypic
construction.

For an invariant branch section ``f`` and ``L=O_Y(2,2)=-K_Y`` the cyclic-cover
algebra ``O_Y plus L^-1`` with ``z^2=f`` gives the double cover.  The two
linearizations of ``L`` with character ``+1`` and ``-1`` give the two lifts of
``tau``.  On the affine coordinates their maps are respectively
``(u,v,z) -> (-u,-v,z)`` and ``(u,v,z) -> (-u,-v,-z)``.  The covering
involution is ``z -> -z`` over the identity.

The selected branch

``x0^4 y0^4 + x0^4 y1^4 + x1^4 y0^4 - x1^4 y1^4``

is invariant and avoids the four ``tau``-fixed corners.  Smoothness is decided
chartwise by the existing affine hypersurface Jacobian/Fitting construction.
Under those hypotheses the standard smooth double-cover formula
``K_X = pi^*(K_Y+L)`` gives trivial canonical bundle, and
``pi_*O_X=O_Y plus O_Y(-2,-2)`` gives ``H^1(O_X)=0``.  Thus the selected smooth
member is a K3 surface.  This is the Horikawa/Pardini double-cover theorem used
in the project source notes; it is not a generic K3 recognition algorithm.
"""

from sage.misc.cachefunc import cached_method
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.sage_object import SageObject

from sage_extensions.categories.algebras.cyclic_cover_algebras import (
    CyclicCoverAlgebra,
)
from sage_extensions.categories.group.groups import OwnedGroups
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_rationals,
    _owned_ring,
)
from sage_extensions.categories.schemes.schemes import (
    ProjectiveSpaces,
    Schemes,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)


class HorikawaK3Family(SageObject):
    r"""Invariant ``(4,4)`` branch sections and their double covers."""

    def __init__(self, base_ring=None) -> None:
        base = _owned_rationals() if base_ring is None else _own_ring(base_ring)
        assert int(base.characteristic()) == 0, (
            f"the Horikawa family of K3 double covers of P^1 x P^1 needs a base ring of "
            f"characteristic zero, but {base} has characteristic {base.characteristic()}"
        )
        labels = finite_ordered_set(("left", "right"))
        line = ProjectiveSpaces(base)(1, names=("x0", "x1"))
        factors = finite_indexed_family(
            labels,
            lambda _label: line,
            name="Two labelled projective-line factors of the Horikawa base",
        )
        surface = Schemes(base).product(factors)
        cover_line_bundle = surface.O(2, 2)
        branch_line_bundle = cover_line_bundle.tensor_power(2)
        group = OwnedGroups().C(2)
        action = surface.c2_diagonal_sign_action(group)
        trivial = lambda element: base.one()
        sign = lambda element: (
            base.one() if group(element) == group.one() else -base.one()
        )
        branch_linearization = branch_line_bundle.linearize(
            action,
            trivial,
        )
        nikulin_linearization = cover_line_bundle.linearize(
            action,
            trivial,
        )
        enriques_linearization = cover_line_bundle.linearize(
            action,
            sign,
        )
        self._base_ring = base
        self._factor_labels = labels
        self._line = line
        self._base_surface = surface
        self._cover_line_bundle = cover_line_bundle
        self._branch_line_bundle = branch_line_bundle
        self._group = group
        self._base_action = action
        self._branch_linearization = branch_linearization
        self._nikulin_linearization = nikulin_linearization
        self._enriques_linearization = enriques_linearization

    def base_ring(self):
        return self._base_ring

    def factor_labels(self):
        return self._factor_labels

    def base_surface(self):
        return self._base_surface

    def cover_line_bundle(self):
        return self._cover_line_bundle

    def branch_line_bundle(self):
        return self._branch_line_bundle

    def acting_group(self):
        return self._group

    def base_action(self):
        return self._base_action

    def branch_linearization(self):
        return self._branch_linearization

    def nikulin_linearization(self):
        return self._nikulin_linearization

    def enriques_linearization(self):
        return self._enriques_linearization

    def branch_section_space(self):
        return self.branch_line_bundle().global_sections()

    def branch_group_module(self):
        return self.branch_linearization().section_group_module()

    @cached_method
    def branch_isotypic_decomposition(self):
        return self.branch_group_module().isotypic_decomposition()

    def invariant_branch_sections(self):
        return self.branch_isotypic_decomposition().trivial_component()

    def anti_invariant_branch_sections(self):
        nontrivial = tuple(
            self.branch_isotypic_decomposition().nontrivial_components()
        )
        assert len(nontrivial) == 1, (
            f"the space of (4,4) branch sections under the involution of order 2 should split "
            f"into the invariant part and one anti-invariant part, but it has "
            f"{len(nontrivial)} nontrivial isotypic components"
        )
        return nontrivial[0]

    @cached_method
    def default_branch_section(self):
        sections = self.branch_section_space()
        by_exponents = {
            tuple(
                tuple(value for value in block)
                for block in sections.monomial_exponents(monomial)
            ): monomial
            for monomial in sections.module_generating_set()
        }
        one = self.base_ring().one()
        section = sections.linear_combination(
            {
                by_exponents[((4, 0), (4, 0))]: one,
                by_exponents[((4, 0), (0, 4))]: one,
                by_exponents[((0, 4), (4, 0))]: one,
                by_exponents[((0, 4), (0, 4))]: -one,
            }
        )
        trivial = lambda _element: self.base_ring().one()
        assert self.branch_linearization().is_eigensection(section, trivial), (
            f"the default Horikawa branch section {section} is not invariant under the "
            "involution of P^1 x P^1"
        )
        return section

    def member(self, branch_section=None):
        section = (
            self.default_branch_section()
            if branch_section is None
            else self.branch_section_space()(branch_section)
        )
        trivial = lambda _element: self.base_ring().one()
        assert self.branch_linearization().is_eigensection(section, trivial), (
            f"the branch section {section} is not invariant under the involution tau of "
            "P^1 x P^1, so its double cover is not a member of the Horikawa family"
        )
        return _horikawa_k3_double_cover(self, section)

    def _repr_(self) -> str:
        return f"Horikawa K3 family over {self.base_ring()} on {self.base_surface()}"



class _HorikawaK3DoubleCoverEngine:
    r"""Private realization of one Horikawa K3 member on its cyclic-cover scheme."""

    def __init__(
        self,
        *,
        family,
        branch_section,
        compatible_branch_section,
        cyclic_algebra,
        **rest,
    ) -> None:
        self._family = family
        self._branch_section = branch_section
        self._compatible_branch = compatible_branch_section
        self._cyclic_algebra = cyclic_algebra
        super().__init__(**rest)

    def family(self):
        return self._family

    def base_ring(self):
        return self.family().base_ring()

    def base_surface(self):
        return self.family().base_surface()

    def branch_section(self):
        return self._branch_section

    def compatible_branch_section(self):
        return self._compatible_branch

    def cyclic_algebra(self):
        return self._cyclic_algebra

    def relative_cover(self):
        return self.cyclic_algebra().relative_spectrum()

    def scheme(self):
        return self

    def cover_morphism(self):
        return self.relative_cover().arrow()

    @cached_method
    def deck_involution(self):
        return self.cyclic_algebra().constant_deck_transformation()

    @cached_method
    def nikulin_lift(self):
        generator = next(iter(self.family().acting_group().group_generators()))
        return self.cyclic_algebra().lift_linearized_group_element(
            self.family().nikulin_linearization(),
            generator,
        )

    @cached_method
    def enriques_lift(self):
        generator = next(iter(self.family().acting_group().group_generators()))
        return self.cyclic_algebra().lift_linearized_group_element(
            self.family().enriques_linearization(),
            generator,
        )

    def branch_chart(self, index):
        chart = self.family().branch_line_bundle().gluing_datum().chart(index)
        return chart.closed_subscheme(
            self.cyclic_algebra().local_branch_coefficient(index)
        )

    @cached_method
    def branch_is_smooth(self) -> bool:
        return all(
            self.branch_chart(index).singular_subscheme().is_empty()
            for index in self.cyclic_algebra().chart_index_set()
        )

    @cached_method
    def branch_avoids_tau_fixed_corners(self) -> bool:
        base = self.base_ring()
        for index in self.cyclic_algebra().chart_index_set():
            ring = self.family().branch_line_bundle().gluing_datum().chart(
                index
            ).coordinate_algebra()
            evaluation = ring.Mor(base)(
                {
                    label: base.zero()
                    for label in ring.algebra_generating_set()
                }
            )
            if evaluation(self.cyclic_algebra().local_branch_coefficient(index)) == base.zero():
                return False
        return True

    def cover_line_bundle_is_anticanonical(self) -> bool:
        selected = self.family().cover_line_bundle().multidegree()
        anticanonical = self.base_surface().anticanonical_line_bundle().multidegree()
        labels = tuple(selected.index_set())
        return all(selected[label] == anticanonical[label] for label in labels)

    def k3_theorem_hypotheses_hold(self) -> bool:
        return (
            int(self.base_ring().characteristic()) != 2
            and self.cover_line_bundle_is_anticanonical()
            and self.branch_is_smooth()
        )

    def is_k3(self) -> bool:
        r"""Apply the smooth anticanonical double-cover theorem to this scheme."""
        return self.k3_theorem_hypotheses_hold()

    def deck_top_form_scalar(self):
        index = next(iter(self.cyclic_algebra().chart_index_set()))
        local = self.cyclic_algebra().local_algebra(index)
        labels = local.module_generating_set()
        z_label = labels[1]
        deck = self.cyclic_algebra().local_deck_transformation(
            index, -self.base_ring().one()
        )
        z = local.algebra_generator("z")
        coordinates = local.framing_morphism().lift(deck.coordinate_algebra_morphism()(z))
        expected = local.base_ring().algebra_structure_morphism()(
            -self.base_ring().one()
        )
        assert coordinates(z_label) == expected, (
            f"the deck transformation of {self} does not send the cover coordinate z to -z "
            f"on chart {index}: the coefficient of z in its image is "
            f"{coordinates(z_label)}, expected {expected}"
        )
        return -self.base_ring().one()

    def fixed_subschemes(self):
        labels = finite_ordered_set(("enriques", "nikulin"))
        fixed = {
            "enriques": self.enriques_lift().fixed_subscheme(),
            "nikulin": self.nikulin_lift().fixed_subscheme(),
        }
        return finite_indexed_family(
            labels,
            fixed.__getitem__,
            name="Fixed subschemes of the two Horikawa lifts",
        )

    def enriques_lift_is_fixed_point_free(self) -> bool:
        return self.enriques_lift().is_fixed_point_free()

    def both_lifts_have_order_two(self) -> bool:
        return (
            self.enriques_lift().has_order_two()
            and self.nikulin_lift().has_order_two()
        )

    def base_change(self, ring_map):
        return _HorikawaK3BaseChangeComparison(self, ring_map)

    def _repr_(self) -> str:
        return f"Horikawa K3 double cover over {self.base_surface()}"


def _horikawa_k3_double_cover(family, branch_section):
    r"""Construct one Horikawa member as the cyclic-cover scheme itself."""
    selected = family.branch_section_space()(branch_section)
    compatible_branch = family.branch_line_bundle().compatible_section(selected)
    cyclic_algebra = CyclicCoverAlgebra(
        family.cover_line_bundle(),
        compatible_branch,
        2,
        relative_spectrum_engine=_HorikawaK3DoubleCoverEngine,
        relative_spectrum_data={
            "family": family,
            "branch_section": selected,
            "compatible_branch_section": compatible_branch,
        },
    )
    relative = cyclic_algebra.relative_spectrum()
    return relative.arrow().domain()



class _HorikawaK3BaseChangeComparison(SageObject):
    r"""Base change of one Horikawa cover with commuting lifted involutions."""

    def __init__(self, source, ring_map) -> None:
        cyclic_comparison = source.cyclic_algebra().base_change(ring_map)
        changed_cyclic = cyclic_comparison.changed_cyclic_algebra()
        changed_line = cyclic_comparison.changed_line_bundle()
        changed_surface = changed_line.projective_product()
        group = source.family().acting_group()
        changed_action = changed_surface.c2_diagonal_sign_action(group)
        target_base = _owned_ring(ring_map.codomain())
        trivial = lambda _element: target_base.one()
        sign = lambda element: (
            target_base.one()
            if group(element) == group.one()
            else -target_base.one()
        )
        changed_nikulin_linearization = changed_line.linearize(
            changed_action,
            trivial,
        )
        changed_enriques_linearization = changed_line.linearize(
            changed_action,
            sign,
        )
        generator = next(iter(group.group_generators()))
        changed_nikulin_lift = changed_cyclic.lift_linearized_group_element(
            changed_nikulin_linearization,
            generator,
        )
        changed_enriques_lift = changed_cyclic.lift_linearized_group_element(
            changed_enriques_linearization,
            generator,
        )
        self._source = source
        self._ring_map = ring_map
        self._cyclic_comparison = cyclic_comparison
        self._changed_action = changed_action
        self._changed_nikulin_linearization = changed_nikulin_linearization
        self._changed_enriques_linearization = changed_enriques_linearization
        self._changed_nikulin_lift = changed_nikulin_lift
        self._changed_enriques_lift = changed_enriques_lift

    def source(self):
        return self._source

    def ring_map(self):
        return self._ring_map

    def cyclic_cover_comparison(self):
        return self._cyclic_comparison

    def changed_cyclic_algebra(self):
        return self.cyclic_cover_comparison().changed_cyclic_algebra()

    def changed_scheme(self):
        return self.changed_cyclic_algebra().relative_spectrum().arrow().domain()

    def cover_projection(self):
        return self.cyclic_cover_comparison().projection()

    def base_projection(self):
        return self.cyclic_cover_comparison().base_projection()

    def changed_nikulin_lift(self):
        return self._changed_nikulin_lift

    def changed_enriques_lift(self):
        return self._changed_enriques_lift

    def cover_square_commutes(self) -> bool:
        return self.cyclic_cover_comparison().cover_square_commutes()

    def involutions_commute_with_base_change(self) -> bool:
        comparison = self.cyclic_cover_comparison()
        return (
            comparison.lift_commutes(
                self.source().nikulin_lift(), self.changed_nikulin_lift()
            )
            and comparison.lift_commutes(
                self.source().enriques_lift(), self.changed_enriques_lift()
            )
            and comparison.deck_commutes(-self.source().base_ring().one())
        )

    def _repr_(self) -> str:
        return f"Horikawa K3 base change along {self.ring_map()} from {self.source()}"



__all__ = [
    "HorikawaK3Family",
]
