r"""Restriction of scalars on the actual homogeneous modules of a graded algebra."""

import operator

from sage.categories.action import Action
from sage.misc.cachefunc import cached_function
from sage.structure.element import parent as element_parent

from sage_extensions.categories.algebras.algebras import (
    Algebras,
    _algebra_on_module,
    _root_algebra_law_decisions,
)
from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras, _graded_multiplication_from_components
from sage_extensions.categories.modules.graded_direct_sums import (
    GradedDirectSumElement, _DirectSumOfModules, _direct_sum_of_modules,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import Sets


class _DegreeZeroAlgebraMultiplication(Action):
    r"""The retained coefficient-ring action on a scalar restriction."""

    def __init__(self, degree_zero_algebra, graded_module, *, actor_on_left):
        self._graded_module = graded_module
        super().__init__(degree_zero_algebra, graded_module, is_left=actor_on_left, op=operator.mul)

    def _act_(self, actor, element):
        module = self._graded_module
        return module.from_realization(module.extension_algebra().scalar_multiple(actor, module.realize(element)))


class _RestrictedGradedAlgebraElement(GradedDirectSumElement):
    def _acted_upon_(self, actor, self_on_left):
        module = self.parent()
        match element_parent(actor):
            case source if source is module.degree_zero_algebra():
                return module.from_realization(module.extension_algebra().scalar_multiple(actor, module.realize(self)))
            case _:
                return super()._acted_upon_(actor, self_on_left)

    def _repr_(self):
        r"""Restriction of scalars keeps each element, so it is written as its element of the original algebra."""
        return repr(self.parent().realize(self))


class _RestrictedGradedAlgebra(_DirectSumOfModules):
    r"""The direct-sum realization retaining restriction's original modules.

    The scalar restriction on each summand is constructed by its module owner.
    This engine only assembles their existing element readings and coefficient
    action; module arithmetic and algebra multiplication remain inherited.
    """

    def __init__(self, extension_algebra, ring_map, **rest) -> None:
        self._extension_algebra = extension_algebra
        self._ring_map = ring_map
        super().__init__(**rest)
        for actor_on_left in (True, False):
            self.register_action(_DegreeZeroAlgebraMultiplication(
                self.degree_zero_algebra(), self, actor_on_left=actor_on_left,
            ))

    def _direct_sum_realization(self):
        return _RestrictedGradedAlgebra, _RestrictedGradedAlgebraElement

    def _module_with_structure(self, categories, construction_data):
        return super()._module_with_structure(categories, {
            **construction_data,
            "extension_algebra": self.extension_algebra(), "ring_map": self.ring_map(),
        })

    def extension_algebra(self):
        return self._extension_algebra

    def degree_zero_algebra(self):
        return self.extension_algebra().base_ring()

    def ring_map(self):
        return self._ring_map

    def _element_constructor_(self, value):
        source = element_parent(value)
        match value:
            case _ if source is self:
                return value
            case _ if source is self.extension_algebra():
                return self.from_realization(value)
            case _ if source is self.degree_zero_algebra():
                return self.from_degree_zero(value)
            case _ if source in Modules(self.degree_zero_algebra()):
                return self.from_realization(self.extension_algebra()(value))
            case _ if source in Modules(self.base_ring()) and self._built_on_the_same_data(source):
                return super()._element_constructor_(value)
            case dict():
                return super()._element_constructor_(value)
            case _ if value in self.base_ring():
                return self.from_degree_zero(self.ring_map()(self.base_ring()(value)))
            case _:
                return super()._element_constructor_(value)

    def _get_action_(self, source, op, self_on_left):
        match (op is operator.mul, source is self.degree_zero_algebra()):
            case (True, True):
                return _DegreeZeroAlgebraMultiplication(source, self, actor_on_left=not self_on_left)
            case _:
                return super()._get_action_(source, op, self_on_left)

    def realize(self, element):
        r"""Read the homogeneous elements in their original scalar modules."""
        extension = self.extension_algebra()
        return sum((
            extension.from_component(degree, component.underlying_element())
            for degree, component in self(element).homogeneous_components().items()
        ), extension.zero())

    def from_realization(self, element):
        r"""Read the original homogeneous elements in the restricted modules."""
        return self.from_components({
            degree: self.graded_piece(degree)(component)
            for degree, component in self.extension_algebra()(element).homogeneous_components().items()
        })

    def from_degree_zero(self, element):
        return self.from_realization(self.extension_algebra()(self.degree_zero_algebra()(element)))

    def degree_zero_element(self, element):
        represented = self.realize(element)
        coordinates = self.extension_algebra().graded_piece(0).framing_morphism().lift(represented.homogeneous_component(0))
        return self.degree_zero_algebra()(coordinates(0))

    def _repr_(self):
        return f"{self.extension_algebra()} over {self.base_ring()}"


def RestrictedGradedAlgebraElement(parent, components):
    return parent.from_components(components)


def RestrictedGradedAlgebra(extension_algebra, ring_map):
    return extension_algebra.restrict_scalars(ring_map)


def _restricted_graded_algebra(algebra, ring_map, *, extra_categories=(), construction_data=None):
    r"""Restrict the summands, then classify the unchanged homogeneous product.

    For f:R->S, S-bilinearity implies R-bilinearity under r.x=f(r)x.
    All algebra identities are unchanged by that action restriction, so only
    the source's established identities are placed on the result.
    """
    ring = ring_map.domain()
    extension = algebra.base_ring()
    assert ring_map.codomain() is extension, (
        f"restricting the scalars of {algebra} along {ring_map} needs a ring map ending at {extension}, "
        f"but it ends at {ring_map.codomain()}"
    )
    monoid = algebra.grading_monoid()

    def piece(degree):
        return algebra.graded_piece(degree).restrict_scalars(ring_map)

    module = _direct_sum_of_modules(
        ring, monoid, indexed_family(monoid, piece),
        _realization=(_RestrictedGradedAlgebra, _RestrictedGradedAlgebraElement),
        construction_data={"extension_algebra": algebra, "ring_map": ring_map},
    )

    def component_product(s, x, t, y):
        product = algebra.from_component(s, x.underlying_element()) * algebra.from_component(t, y.underlying_element())
        degree = module.combine_degrees(s, t)
        return module.graded_piece(degree)(product.homogeneous_component(degree))

    multiplication = _graded_multiplication_from_components(module, component_product)
    categories = (GradedAlgebras(ring, monoid), *extra_categories, *(
        target for source, target in (
            (Algebras(extension).Commutative(), Algebras(ring).Commutative()),
            (GradedAlgebras(extension, monoid).Supercommutative(), GradedAlgebras(ring, monoid).Supercommutative()),
            (GradedAlgebras(extension, monoid).Supercommutative().Alternating(), GradedAlgebras(ring, monoid).Supercommutative().Alternating()),
        ) if algebra in source
    ))
    data = dict(construction_data or {})
    law_decisions = _root_algebra_law_decisions(algebra)
    law_decisions["grading"] = algebra.grading_compatibility_decision()
    if (extension.is_framed_algebra() and algebra.is_framed_algebra()
            and ring_map is extension.algebra_structure_morphism()):
        labels = Sets().coproduct(indexed_family(Sets.Δ[1], lambda i:
            extension.algebra_generating_set() if int(i) == 0 else algebra.algebra_generating_set()))

        def generator(label):
            match int(label.summand_index()):
                case 0:
                    return module.from_degree_zero(extension.algebra_generator(label.summand_element()))
                case 1:
                    return module.from_realization(algebra.algebra_generator(label.summand_element()))

        data["algebra_generating_family"] = indexed_family(labels, generator)
    return _algebra_on_module(
        module, multiplication, placement=categories,
        unit=module.from_realization(algebra.one()), construction_data=data,
        law_decisions=law_decisions,
    )


@cached_function(key=lambda algebra, ring_map: (id(algebra), id(ring_map)))
def _restrict_graded_algebra_scalars(algebra, ring_map):
    return _restricted_graded_algebra(algebra, ring_map)


__all__ = ["RestrictedGradedAlgebra", "RestrictedGradedAlgebraElement"]
