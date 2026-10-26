r"""Toric blowups of smooth surfaces at torus-fixed points."""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedIntegralDomains,
)
from sage_extensions.categories.schemes.blowups import Blowups
from sage_extensions.categories.schemes.schemes import (
    EffectiveCartierDivisors,
    Schemes,
)
from sage_extensions.categories.schemes.toric.fans import RationalPolyhedralFans
from sage_extensions.categories.schemes.toric.toric_schemes import ToricSchemes, _integers
from sage_extensions.categories.schemes.varieties import Surfaces


class ToricFixedPointBlowups(OwnedCategoryOverBaseRing):
    r"""Smooth toric surfaces obtained by blowing up one torus-fixed point.

    A torus-fixed point of a smooth toric surface is indexed by a maximal
    two-dimensional cone ``sigma = <u,v>``.  Its blowup is the star subdivision
    introducing the primitive ray ``u+v`` and replacing ``sigma`` by
    ``<u,u+v>`` and ``<u+v,v>`` (CLS Prop. 3.3.15).  The identity lattice map
    from the subdivided fan to the original fan is the blowdown morphism.

    The level datum is the blown-up surface, the center cone and the
    exceptional ray; an object is the toric variety of the subdivided fan,
    constructed in this category by :func:`_toric_fixed_point_blowup`.
    """

    def an_object(self):
        r"""The affine plane blown up at the origin, its one torus-fixed point.

        The fan of ``A^2`` is the single cone spanned by ``e_1`` and ``e_2``;
        its star subdivision at ``e_1 + e_2`` is the blowup described above.

        sage: from dzack_research.preamble.all import QQ, ToricFixedPointBlowups, ToricSchemes, Blowups, Surfaces
        sage: B = ToricFixedPointBlowups(QQ).an_object()
        sage: all(B in C(QQ) for C in (ToricFixedPointBlowups, ToricSchemes, Blowups, Surfaces))
        True
        sage: B.blowup_morphism().domain() is B and B.blowup_morphism().codomain() is B.blowup_source()
        True
        """
        cocharacters = _integers().free_module(2)
        plane = RationalPolyhedralFans(cocharacters)(([[1, 0], [0, 1]],)).toric_variety(self.base_ring())
        return plane.toric_fixed_point_blowup(plane.fan().maximal_cones()[0])

    def super_categories(self):
        base = self.base_ring()
        categories = [Blowups(base), ToricSchemes(base), Schemes(base).Smooth()]
        match base in OwnedIntegralDomains():
            case True:
                categories.append(Surfaces(base))
            case False:
                pass
        return categories

    def _repr_object_names(self):
        return f"toric fixed-point blowups over {self.base_ring()}"

    class ParentMethods:
        def __init__(self, blowup_center_cone, exceptional_ray, **rest) -> None:
            self._blowup_center_cone = blowup_center_cone
            self._exceptional_ray = exceptional_ray
            super().__init__(**rest)

        def is_toric_fixed_point_blowup(self) -> bool:
            return True

        def _blowup_morphism(self):
            r"""The blowdown ``Bl_p X -> X``, induced by the identity of ``N``.

            The star subdivision refines the fan of ``X``, so the identity
            lattice map is compatible and induces the toric morphism
            (CLS Thm. 3.3.4).
            """
            source = self.blowup_source()
            lattice = source.cocharacter_lattice()
            identity = lattice.module_category().Mor(lattice, lattice).identity()
            return self.toric_morphism(identity, source)

        def blowup_center_cone(self):
            r"""Return the maximal source-fan cone indexing the blown-up fixed point."""
            return self._blowup_center_cone

        def exceptional_ray(self):
            r"""The ray ``u+v`` of the subdivided fan, whose divisor is exceptional."""
            return self._exceptional_ray

        def exceptional_weil_divisor(self):
            r"""Return the torus-invariant Weil divisor supported on the exceptional ray."""
            return self.torus_invariant_prime_divisor(self.exceptional_ray())

        def _exceptional_divisor(self):
            exceptional = self.exceptional_weil_divisor()
            return self.torus_invariant_divisor_support_subscheme(
                exceptional,
                placements=(EffectiveCartierDivisors(self),),
                construction_data={
                    "effective_cartier_ideal_sheaf": self.invertible_sheaf_of_divisor(-exceptional),
                    "effective_cartier_picard_class": self._represented_exceptional_picard_class(),
                },
            )

        def exceptional_self_intersection(self):
            exceptional = self.exceptional_weil_divisor()
            return self.divisor_intersection(exceptional, exceptional)

        def _refined_ray_for_source_ray(self, source_ray):
            (source_vector,) = tuple(source_ray.rays())
            refined = next(
                (
                    target_ray
                    for target_ray in self.fan().cones(1)
                    if target_ray != self.exceptional_ray()
                    and tuple(target_ray.rays()) == (source_vector,)
                ),
                None,
            )
            assert refined is not None, (
                f"the ray {source_ray} of the original fan is missing from the fan of the blowup "
                f"{self}, but a star subdivision keeps every ray"
            )
            return refined

        def strict_transform_divisor(self, divisor):
            r"""Return the strict transform of a torus-invariant divisor.

            Star subdivision preserves every old ray.  The strict transform
            keeps the coefficient on each preserved prime divisor and has
            coefficient zero on the exceptional prime.  This is independent
            of the total transform supplied by :meth:`blowup_morphism`.
            """
            source = self.blowup_source()
            source_group = source.weil_divisor_group()
            target_group = self.weil_divisor_group()
            divisor = source_group(divisor)
            coordinates = divisor.to_vector()
            return target_group.linear_combination(
                {
                    self._refined_ray_for_source_ray(ray): coordinates(ray)
                    for ray in coordinates.support().domain()
                }
            )

        @cached_method
        def _picard_pullback_morphism(self):
            r"""Return ``f^*: Pic(X) -> Pic(Bl_p X)`` for the toric blowdown.

            The map is induced from the existing Cartier-divisor pullback.  Its
            construction through the quotient presentations verifies that
            principal-divisor relations vanish after pullback.
            """
            source = self.blowup_source()
            source_picard = self.source_picard_group()
            target_picard = self.picard_group()
            source_weil = source.weil_divisor_group()

            def image(label):
                pulled = self.blowup_morphism().pullback_divisor(
                    source_weil.module_generator(label)
                )
                coordinates = pulled.to_vector()
                return target_picard.linear_combination(
                    {ray: coordinates(ray) for ray in coordinates.support().domain()}
                )

            return source_picard.module_category().Mor(source_picard, target_picard)(image)

        def _represented_exceptional_picard_class(self):
            return self.picard_group().module_generator(self.exceptional_ray())

def _toric_fixed_point_blowup(surface, center_cone):
    r"""Blow up the torus-fixed point indexed by ``center_cone`` on a smooth toric surface.

    The star subdivision of the fan at ``center_cone`` is computed first; its
    toric variety is then constructed in ``ToricFixedPointBlowups(k)`` with the
    surface, the center cone and the new ray as that level's data.
    """
    base = surface.scheme_base_ring()
    assert surface in ToricSchemes(base), (
        f"the blowup at a torus-fixed point needs a toric variety over {base}, but {surface} "
        f"is in {surface.category()}"
    )
    fan = surface.fan()
    assert int(fan.dimension()) == 2, (
        f"the blowup at a torus-fixed point is implemented only for toric surfaces, but "
        f"{surface} has dimension {fan.dimension()}"
    )
    assert fan.is_smooth(), (
        f"the blowup at a torus-fixed point is implemented only for smooth toric surfaces, but "
        f"the fan of {surface} is not smooth"
    )
    assert center_cone in fan.maximal_cones(), (
        f"the center of the blowup of {surface} must be a torus-fixed point, that is a maximal "
        f"cone of its fan, but {center_cone} is not a maximal cone"
    )
    assert center_cone.rays().cardinality() == 2, (
        f"the maximal cone {center_cone} of the smooth toric surface {surface} should have 2 "
        f"rays, but it has {center_cone.rays().cardinality()}"
    )
    center = surface.torus_fixed_point_subscheme(center_cone)
    first, second = tuple(center_cone.rays())
    new_ray_vector = first + second

    fans = RationalPolyhedralFans(fan.cocharacter_lattice())
    refined_fan = fans(
        tuple(
            subdivided
            for cone in fan.maximal_cones()
            for subdivided in (
                ((first, new_ray_vector), (new_ray_vector, second))
                if cone == center_cone
                else (tuple(cone.rays()),)
            )
        )
    )
    assert refined_fan.is_smooth(), (
        f"the star subdivision of the fan of {surface} at {center_cone} is not smooth, although "
        "the star subdivision of a smooth two-dimensional cone at the sum of its rays is smooth"
    )
    assert refined_fan.is_complete() or not fan.is_complete(), (
        f"the star subdivision of the complete fan of {surface} at {center_cone} is not complete"
    )
    exceptional = next(
        (
            ray_cone
            for ray_cone in refined_fan.cones(1)
            if tuple(ray_cone.rays()) == (new_ray_vector,)
        ),
        None,
    )
    assert exceptional is not None, (
        f"the star subdivision of the fan of {surface} at {center_cone} does not contain the new "
        f"ray u + v = {new_ray_vector}"
    )
    return refined_fan.toric_variety(
        base,
        placements=(ToricFixedPointBlowups(base),),
        blowup_source=surface,
        blowup_center=center,
        blowup_center_cone=center_cone,
        exceptional_ray=exceptional,
    )


__all__ = ["ToricFixedPointBlowups"]
