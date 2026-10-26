r"""Higher direct images and monodromy for a sourced Legendre degeneration.

The selected family is the projective Legendre family

``E_t : y^2 z = x(x-z)(x-tz)``

over ``Spec QQ[t]``.  Its fibers at ``t=0`` and ``t=1`` are singular.  On the
analytic punctured disc ``0 < |t| < 3/4`` the family is smooth and proper, so
``R^1 pi_* ZZ`` is a rank-two integral local system and topological proper base
change identifies its stalk with ``H^1(E_t,ZZ)``.

For a positively oriented loop around ``t=0`` the sourced homology matrix is
``M_0=[[1,0],[-2,1]]`` in the standard symplectic basis.  The local system
here is cohomological, so in the dual basis its action is
``(M_0^{-1})^T=[[1,2],[0,1]]``.

The local system retains that basis convention and acts on the actual rank-two
formed module whose alternating pairing is the cup/intersection pairing.  Nearby/vanishing cycles are deliberately not inferred from proper
base change: the singular fiber is retained, but no specialization map is
created without its own comparison theorem.
"""

from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.sage_object import SageObject

from sage_extensions.categories.functors.group_actions import GroupActionFunctor
from sage_extensions.categories.group.groups import OwnedGroups
from sage_extensions.categories.manifolds import ComplexManifolds
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.categories.modules.framed.formed.form_modules import (
    FormModules,
)
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.schemes.complete_intersections import (
    ProjectiveCompleteIntersections,
)
from sage_extensions.categories.schemes.schemes import (
    ProjectiveSpaces,
    Schemes,
)
from sage_extensions.rings.real import RR


class PointedAnalyticFundamentalGroup(SageObject):
    r"""A represented pointed ``pi_1`` with its actual group and base point."""

    def __init__(self, space, base_point, group, generator) -> None:
        assert base_point.manifold() is space, (
            f"the base point {base_point} of a pointed fundamental group of {space} must be a "
            f"point of {space}, but it is a point of {base_point.manifold()}"
        )
        assert generator.parent() is group, (
            f"the loop {generator} is not an element of the fundamental group {group} of {space}; "
            f"it lies in {generator.parent()}"
        )
        self._space = space
        self._base_point = base_point
        self._group = group
        self._generator = generator

    def space(self):
        return self._space

    def base_point(self):
        return self._base_point

    def group(self):
        return self._group

    def positive_loop_generator(self):
        return self._generator

    def pointed_space(self):
        r"""``(space(), base_point())`` as an object of ``CosliceUnder(*)`` on ``TopologicalSpaces()``.

        ``group()`` is its ``fundamental_group()`` (``TopologicalSpaceCoslices``).
        """
        return TopologicalSpaces().pointed_space(self.space(), self.base_point())

    def _repr_(self) -> str:
        return f"pi_1({self.space()}, {self.base_point()}) = {self.group()}"







class LegendreMonodromyFamily(SageObject):
    r"""The Legendre degeneration together with ``R^1 pi_* ZZ`` on a punctured disc."""

    def __init__(self) -> None:
        rationals = _owned_rationals()
        integers = _owned_integers()
        parameter = rationals.polynomial_ring("t")
        t = parameter.algebra_generator("t")
        ambient = ProjectiveSpaces(parameter)(2, names=("x", "y", "z"))
        section_ring = ambient.O(3).global_sections().homogeneous_coordinate_ring()
        x = section_ring.algebra_generator("x")
        y = section_ring.algebra_generator("y")
        z = section_ring.algebra_generator("z")
        scalar_t = section_ring.algebra_structure_morphism()(t)
        equation = y**2 * z - x * (x - z) * (x - scalar_t * z)
        family = ProjectiveCompleteIntersections(ambient.scheme_base_ring())(ambient, equation)

        at_zero = parameter.Mor(rationals)({"t": rationals.zero()})
        at_half = parameter.Mor(rationals)({"t": rationals(1) / rationals(2)})
        singular_fiber = family.base_change(at_zero)
        smooth_fiber = family.base_change(at_half)

        analytic_line = ComplexManifolds().affine_space(
            1,
            name="Legendre_parameter_line",
            coordinate_names=("t",),
        )
        smooth_stratum = ComplexManifolds().disc(
            RR(3) / RR(4), "Legendre_punctured_disc", containing_manifold=analytic_line,
            punctured=True,
        )
        base_point = smooth_stratum.point((0.5,))

        pi_one = OwnedGroups().Free(1, names="gamma0")
        generator = next(iter(pi_one.group_generators()))
        pointed_pi_one = PointedAnalyticFundamentalGroup(
            smooth_stratum,
            base_point,
            pi_one,
            generator,
        )

        underlying_cohomology = integers.free_module(2)
        cohomology = FormModules(integers)(
            underlying_cohomology.bilinear_hom_space(integers)([[0, 1], [-1, 0]])
        )
        labels = tuple(cohomology.module_generating_set())
        alpha_dual = cohomology.module_generator(labels[0])
        beta_dual = cohomology.module_generator(labels[1])
        forward_linear = cohomology.module_category().Mor(cohomology, cohomology)(
            {
                labels[0]: alpha_dual,
                labels[1]: 2 * alpha_dual + beta_dual,
            }
        )
        inverse_linear = cohomology.module_category().Mor(cohomology, cohomology)(
            {
                labels[0]: alpha_dual,
                labels[1]: -2 * alpha_dual + beta_dual,
            }
        )
        forward = cohomology.Mor(cohomology)(forward_linear)
        inverse = cohomology.Mor(cohomology)(inverse_linear)
        generator = next(iter(pi_one.group_generators()))

        def loop_action(loop):
            loop = pi_one(loop)
            result = cohomology.Mor(cohomology).identity()
            for letter in pi_one.reduced_word(loop):
                assert letter == generator or letter == ~generator, (
                    f"the fundamental group {pi_one} of the punctured disc is infinite cyclic on "
                    f"{generator}, but the reduced word of {loop} contains the letter {letter}"
                )
                result = (forward if letter == generator else inverse) * result
            return result

        action_functor = GroupActionFunctor(
            pi_one,
            FormModules(integers),
            cohomology,
            loop_action,
        )
        from sage_extensions.categories.abstract_categories.cat import Cat

        local_system = Cat().Mor(
            action_functor.domain(),
            action_functor.codomain(),
        ).object(action_functor)
        self._parameter_algebra = parameter
        self._family = family
        self._singular_fiber = singular_fiber
        self._smooth_fiber = smooth_fiber
        self._smooth_stratum = smooth_stratum
        self._base_point = base_point
        self._pointed_pi_one = pointed_pi_one
        self._fiber_h1 = cohomology
        self._positive_monodromy = forward
        self._negative_monodromy = inverse
        self._local_system = local_system

    def parameter_algebra(self):
        return self._parameter_algebra

    def family_scheme(self):
        return self._family

    def family_morphism(self):
        return self.family_scheme().family_morphism()

    def singular_parameter(self):
        return self.parameter_algebra().zero()

    def singular_fiber(self):
        return self._singular_fiber

    def smooth_reference_fiber(self):
        return self._smooth_fiber

    def smooth_stratum(self):
        return self._smooth_stratum

    def base_point(self):
        return self._base_point

    def pointed_fundamental_group(self):
        return self._pointed_pi_one

    def fiber_cohomology(self, point):
        assert point is self.base_point(), (
            f"the fiber cohomology H^1 of the Legendre family is computed only at the base point "
            f"{self.base_point()} (t = 1/2), not at {point}"
        )
        return self._fiber_h1

    def higher_direct_image(self):
        r"""The represented restriction of ``R^1 pi_* ZZ`` to the smooth stratum."""
        return self.local_system()

    def cohomological_degree(self):
        return _owned_integers().one()

    def local_system(self):
        return self._local_system

    def monodromy_representation(self):
        return self.local_system().functor()

    def positive_monodromy(self):
        return self._positive_monodromy

    def monodromy_preserves_pairing(self) -> bool:
        module = self.fiber_cohomology(self.base_point())
        action = self.positive_monodromy()
        generators = tuple(module.module_generators())
        return all(
            module.pairing(action(left), action(right)) == module.pairing(left, right)
            for left in generators
            for right in generators
        )

    def proper_base_change_hypotheses_hold(self, point) -> bool:
        return (
            point is self.base_point()
            and self.family_scheme() in Schemes(self.parameter_algebra()).Projective()
        )

    def stalk_to_fiber_comparison(self):
        r"""Topological proper-base-change comparison at the selected smooth point."""
        point = self.base_point()
        assert self.proper_base_change_hypotheses_hold(point), (
            f"proper base change does not apply at {point}: it needs {point} to be the base "
            f"point {self.base_point()} of the smooth locus and the family {self.family_scheme()} "
            f"to be projective over {self.parameter_algebra()}"
        )
        representation = self.monodromy_representation()
        stalk = representation(representation.domain().an_object())
        fiber = self.fiber_cohomology(point)
        forward = stalk.Mor(fiber).identity() if stalk is fiber else stalk.Mor(fiber)(
            stalk.module_category().Mor(stalk, fiber)(
                {
                    label: fiber.module_generator(label)
                    for label in stalk.module_generating_set()
                }
            )
        )
        inverse = fiber.Mor(stalk).identity() if stalk is fiber else fiber.Mor(stalk)(
            fiber.module_category().Mor(fiber, stalk)(
                {
                    label: stalk.module_generator(label)
                    for label in fiber.module_generating_set()
                }
            )
        )
        return stalk.module_category().Core().Mor(stalk, fiber)(forward, inverse)

    def _repr_(self) -> str:
        return f"Legendre monodromy family over {self.parameter_algebra()} with smooth stratum {self.smooth_stratum()}"



__all__ = [
    "LegendreMonodromyFamily",
    "PointedAnalyticFundamentalGroup",
]
