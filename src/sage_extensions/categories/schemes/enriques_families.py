r"""Enriques quotients of the Horikawa K3 family and their integral lattice data.

For a fixed-point-free involution ``sigma`` on a K3 surface in characteristic
not two, the quotient is an Enriques surface.  Its integral second cohomology
has one ``Z/2`` torsion class (the canonical class), while the free quotient is
the Enriques lattice ``U + E8(-1)``.  For the étale double cover
``p:X -> Y``, cup products satisfy

``(p^*a,p^*b)_X = 2 (a,b)_Y``.

Thus the image of ``H^2(Y,Z)_free`` is the invariant K3 lattice
``S_En = U(2) + E8(-2)``.  The complementary anti-invariant lattice and the
anti-isometry gluing the two primitive summands are not reconstructed here:
they are the existing primitive extension of the named Enriques involution on
the K3 lattice.

The source theorem is BHPV, Chapter VIII, 15.1, as recorded in the project
Enriques source notes.  The geometric quotient is independently constructed
from the actual fixed-point-free Horikawa lift by affine invariant quotients
and finite descent; the named lattice is used only after the geometric
hypotheses establish that this is an Enriques involution.
"""

from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.sage_object import SageObject

from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.schemes.gluing import SemilinearAlgebraMorphism
from sage_extensions.categories.schemes.k3_families import (
    HorikawaK3Family,
)
from sage_extensions.categories.schemes.schemes import _affine_spec_morphism
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)


def _cyclic_two_module():
    integers = _owned_integers()
    generators = integers.free_module(1)
    relations = integers.free_module(1)
    presentation = relations.Mor(generators)(
        {0: integers(2) * generators.module_generator(0)}
    )
    return presentation.cokernel()


class _EnriquesMarkedIntegralCohomology(SageObject):
    r"""A chosen equivariant marking of the quotient and K3 integral ``H^2`` data."""

    def __init__(self, enriques_surface) -> None:
        from sage_extensions.catalogue import Involutions, NamedLattices

        assert enriques_surface.is_enriques(), (
            f"cannot mark the integral cohomology of {enriques_surface} by E10: it is not known "
            "to be an Enriques surface (the quotient of a K3 surface by a free involution)"
        )
        k3_lattice = NamedLattices.LK3
        involution = Involutions.I_En
        extension = involution.primitive_extension()
        quotient_free = NamedLattices.E10
        invariant = extension.invariant
        invariant_inclusion = invariant.inclusion()
        quotient_labels = tuple(quotient_free.module_generating_set())
        invariant_labels = tuple(invariant.module_generating_set())
        assert len(quotient_labels) == len(invariant_labels), (
            f"the free part E10 of H^2 of an Enriques surface has rank {len(quotient_labels)}, "
            f"but the invariant lattice of the involution on the K3 lattice has rank "
            f"{len(invariant_labels)}; they must agree"
        )
        pullback = quotient_free.module_category().Mor(quotient_free, k3_lattice)(
            {
                quotient_label: invariant_inclusion(
                    invariant.module_generator(invariant_labels[position])
                )
                for position, quotient_label in enumerate(quotient_labels)
            }
        )
        assert all(
            pullback(left).b(pullback(right)) == 2 * left.b(right)
            for left in quotient_free.module_generators()
            for right in quotient_free.module_generators()
        ), (
            f"the pullback {pullback} from E10 to the K3 lattice does not multiply the "
            "intersection form by 2, as pullback along a degree-2 cover must"
        )
        assert all(
            involution(pullback(generator)) == pullback(generator)
            for generator in quotient_free.module_generators()
        ), (
            f"the pullback {pullback} from E10 does not land in the sublattice of the K3 lattice "
            f"fixed by the involution {involution}"
        )
        torsion = _cyclic_two_module()
        torsion_pullback = torsion.module_category().Mor(torsion, k3_lattice)(
            {
                label: k3_lattice.zero()
                for label in torsion.module_generating_set()
            }
        )
        self._surface = enriques_surface
        self._k3_lattice = k3_lattice
        self._involution = involution
        self._extension = extension
        self._quotient_free = quotient_free
        self._torsion = torsion
        self._pullback = pullback
        self._torsion_pullback = torsion_pullback

    def surface(self):
        return self._surface

    def k3_h2_lattice(self):
        return self._k3_lattice

    def enriques_involution_on_h2(self):
        return self._involution

    def primitive_extension(self):
        return self._extension

    def invariant_lattice(self):
        return self.primitive_extension().invariant

    def invariant_lattice_inclusion(self):
        return self.primitive_extension().invariant_inclusion()

    def anti_invariant_lattice(self):
        return self.primitive_extension().orthogonal_complement

    def anti_invariant_lattice_inclusion(self):
        return self.primitive_extension().orthogonal_complement_inclusion()

    def primitive_extension_inclusion(self):
        return self.primitive_extension().orthogonal_sum_inclusion()

    def enriques_free_h2_lattice(self):
        return self._quotient_free

    def canonical_torsion_submodule(self):
        return self._torsion

    def free_h2_pullback(self):
        return self._pullback

    def torsion_h2_pullback(self):
        return self._torsion_pullback

    def discriminant_gluing_subgroup(self):
        return self.primitive_extension().invariant_gluing_subgroup()

    def discriminant_gluing_map(self):
        return self.primitive_extension().glue()

    def primitive_gluing_index(self):
        return self.primitive_extension().index()

    def h2_trace(self):
        involution = self.enriques_involution_on_h2()
        linear = involution.domain().module_category().Mor(
            involution.domain(), involution.codomain()
        )(involution)
        return linear.trace()

    def topological_lefschetz_number(self):
        # H^0 and H^4 each contribute +1; H^1 and H^3 vanish for K3.
        return 2 + self.h2_trace()

    def lefschetz_matches_geometric_fixed_locus(self) -> bool:
        generator = next(iter(self.surface().acting_group().group_generators()))
        return (
            self.surface().quotient_data().fixed_locus_is_empty(generator)
            and self.topological_lefschetz_number() == 0
        )

    def _repr_(self) -> str:
        return f"Marked integral cohomology of {self.surface()}"



class _HorikawaEnriquesSurfaceEngine:
    r"""Private realization of the Enriques quotient on its actual quotient scheme."""

    def __init__(
        self,
        *,
        k3_member,
        acting_group,
        quotient_data,
        **rest,
    ) -> None:
        self._k3_member = k3_member
        self._group = acting_group
        self._quotient_data = quotient_data
        super().__init__(**rest)

    def k3_member(self):
        return self._k3_member

    def acting_group(self):
        return self._group

    def quotient_data(self):
        return self._quotient_data

    def scheme(self):
        return self

    def quotient_morphism(self):
        return self.quotient_data().quotient_morphism()

    def is_enriques(self) -> bool:
        r"""Apply the fixed-point-free K3 involution characterization."""
        return (
            self.k3_member().is_k3()
            and int(self.k3_member().base_ring().characteristic()) != 2
            and self.quotient_data().action_is_free()
            and self.k3_member().enriques_lift().top_form_scalar()
            == -self.k3_member().base_ring().one()
        )

    @cached_method
    def integral_cohomology(self):
        return _EnriquesMarkedIntegralCohomology(self)

    def invariant_lattice(self):
        return self.integral_cohomology().invariant_lattice()

    def anti_invariant_lattice(self):
        return self.integral_cohomology().anti_invariant_lattice()

    def discriminant_gluing_map(self):
        return self.integral_cohomology().discriminant_gluing_map()

    def base_change(self, ring_map):
        return _HorikawaEnriquesBaseChangeComparison(self, ring_map)

    def _repr_(self) -> str:
        return f"Horikawa Enriques quotient of {self.k3_member()}"


def HorikawaEnriquesSurface(k3_member=None):
    r"""Return the fixed-point-free Horikawa quotient as the quotient scheme itself."""
    if k3_member is None:
        k3_member = HorikawaK3Family().member()
    assert k3_member.is_k3(), (
        f"{k3_member} is not known to be a K3 surface, so its Enriques quotient is not defined"
    )
    assert int(k3_member.base_ring().characteristic()) != 2, (
        f"the Enriques quotient of {k3_member} is constructed only in characteristic other than 2, "
        f"but its base ring {k3_member.base_ring()} has characteristic 2"
    )
    assert k3_member.enriques_lift_is_fixed_point_free(), (
        f"the involution of {k3_member} has fixed points, so its quotient is not an Enriques surface"
    )
    group = k3_member.family().acting_group()
    quotient_data = k3_member.c2_chartwise_invariant_quotient(
        group,
        k3_member.enriques_lift().local_automorphisms(),
        _engine=_HorikawaEnriquesSurfaceEngine,
        construction_data={
            "k3_member": k3_member,
            "acting_group": group,
        },
    )
    assert quotient_data.source_scheme() is k3_member, (
        f"the quotient was computed from {quotient_data.source_scheme()}, not from the K3 "
        f"surface {k3_member}"
    )
    assert quotient_data.action_is_free(), (
        f"the involution does not act freely on {k3_member} on its affine charts, so the "
        "quotient is not an Enriques surface"
    )
    return quotient_data.quotient_scheme()



class _HorikawaEnriquesBaseChangeComparison(SageObject):
    r"""Compatible scalar change of the K3 and Enriques quotient maps."""

    def __init__(self, source, ring_map) -> None:
        k3_comparison = source.k3_member().base_change(ring_map)
        changed_k3 = k3_comparison.changed_scheme()
        changed_lift = k3_comparison.changed_enriques_lift()
        changed_quotient = changed_k3.c2_chartwise_invariant_quotient(
            source.acting_group(),
            changed_lift.local_automorphisms(),
        )
        source_quotient = source.quotient_data()
        cyclic_comparison = k3_comparison.cyclic_cover_comparison()
        local_quotient_projections = {}
        local_maps_to_source_quotient = {}
        for index in source_quotient.chart_index_set():
            changed_index = changed_quotient.normalize_chart_index(index)
            source_acted = source_quotient.acted_chart(index)
            changed_acted = changed_quotient.acted_chart(changed_index)
            source_invariants = source_acted.invariant_algebra()
            changed_invariants = changed_acted.invariant_algebra()
            source_inclusion = source_acted.invariant_algebra_inclusion()
            cover_pullback = cyclic_comparison.local_projection(index).coordinate_algebra_morphism()
            images = {
                label: changed_acted.invariant_algebra_element(
                    cover_pullback(
                        source_inclusion(source_invariants.algebra_generator(label))
                    )
                )
                for label in source_invariants.algebra_generating_set()
            }
            semilinear = SemilinearAlgebraMorphism(
                source_invariants,
                changed_invariants,
                ring_map,
                images,
            )
            quotient_ring_map = source_invariants.Mor(changed_invariants)(
                semilinear,
            )
            local_projection = _affine_spec_morphism(quotient_ring_map)
            local_quotient_projections[index] = local_projection
            local_maps_to_source_quotient[index] = (
                source_quotient.quotient_scheme().gluing_datum().chart_embedding(index)
                * local_projection
            )
        quotient_projection = changed_quotient.quotient_scheme().Mor(
            source_quotient.quotient_scheme()
        )(local_maps_to_source_quotient)
        self._source = source
        self._ring_map = ring_map
        self._k3_comparison = k3_comparison
        self._changed_quotient = changed_quotient
        self._quotient_projection = quotient_projection
        self._local_quotient_projections = finite_indexed_family(
            source_quotient.chart_index_set(),
            lambda index: local_quotient_projections[index],
            name="Local projections of a scalar-changed Enriques quotient",
        )
        assert self.quotient_square_commutes(), (
            f"base change of the Enriques quotient {source} along {ring_map} does not commute "
            "with taking the quotient: the square of quotient maps and base-change projections "
            "does not commute"
        )

    def source(self):
        return self._source

    def ring_map(self):
        return self._ring_map

    def k3_comparison(self):
        return self._k3_comparison

    def changed_quotient_data(self):
        return self._changed_quotient

    def quotient_projection(self):
        return self._quotient_projection

    def local_quotient_projection(self, index):
        return self._local_quotient_projections[
            self.source().quotient_data().normalize_chart_index(index)
        ]

    def quotient_square_commutes(self) -> bool:
        source_quotient = self.source().quotient_data()
        changed_quotient = self.changed_quotient_data()
        cyclic_comparison = self.k3_comparison().cyclic_cover_comparison()
        return all(
            source_quotient.local_source_quotient_morphism(index)
            * cyclic_comparison.local_projection(index)
            == self.local_quotient_projection(index)
            * changed_quotient.local_source_quotient_morphism(
                changed_quotient.normalize_chart_index(index)
            )
            for index in source_quotient.chart_index_set()
        )

    def changed_action_is_free(self) -> bool:
        return self.changed_quotient_data().action_is_free()

    def _repr_(self) -> str:
        return f"Horikawa Enriques base change along {self.ring_map()} from {self.source()}"





__all__ = [
    "HorikawaEnriquesSurface",
]
