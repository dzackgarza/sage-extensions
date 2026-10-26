r"""Lattices with a group action: ``Lattices(R[G])``.

An object of ``Lattices(R[G])`` is an ``R[G]``-module whose underlying
``R``-module is a lattice with a form the group preserves, so the action is
a group morphism ``G -> O(L)``.  ``Lattices(S)`` constructs this category
whenever ``S`` is a group algebra; the constructor is
``Lattices(R[G])(L, action)``.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    MorCategoryConstruction,
)
from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.group.g_objects import GObjects
from sage_extensions.categories.group.groups import OwnedGroups
from sage_extensions.categories.lattice_morphisms import (
    LatticeMor,
    LatticeMorphismMethods,
)
from sage_extensions.categories.lattices import (
    Lattices,
    RootLattices,
)
from sage_extensions.categories.modules.group_modules.group_modules import (
    ModulesOverGroupAlgebra,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)
from sage_extensions.categories.sets.set_categories import Sets


class GroupLatticeMorphism(LatticeMorphismMethods):
    r"""Methods for a generated form-preserving equivariant lattice morphism."""

    def __mul__(self, other):
        if not isinstance(other, GroupLatticeMorphism):
            return super().__mul__(other)
        if other.codomain() is not self.domain():
            return NotImplemented
        return other.domain().Mor(self.codomain()).elementwise(
            lambda element: self(other(element))
        )


class GroupLatticeMor(LatticeMor):
    r"""Form-preserving maps commuting with one selected group action."""

    ElementMethods = GroupLatticeMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        if domain.group() != codomain.group():
            raise ValueError(
                f"no equivariant lattice morphisms {domain} -> {codomain}: the domain is acted on by "
                f"{domain.group()} but the codomain by {codomain.group()}; both must carry an action of one group"
            )
        if domain.base_ring() is not codomain.base_ring():
            raise ValueError(
                f"no equivariant lattice morphisms {domain} -> {codomain}: the domain is a lattice over "
                f"{domain.base_ring()} but the codomain over {codomain.base_ring()}; both must have one base ring"
            )
        super().__init__(mor_family, domain, codomain)

    def _check_equivariance(self, morphism) -> None:
        domain = self.domain()
        codomain = self.codomain()
        group = domain.group()
        assert group.has_selected_group_resolution(), (
            f"cannot check that a morphism {domain} -> {codomain} is {group}-equivariant: this needs a chosen "
            f"generating set of {group}, but {group} is only known to be in {group.category()}"
        )
        for group_generator in group.group_generators():
            for label in domain.module_generating_set():
                vector = domain.module_generator(label)
                if morphism(domain.act(group_generator, vector)) != codomain.act(
                    group_generator, morphism(vector)
                ):
                    raise ValueError(
                        f"{morphism} is not {group}-equivariant: it does not commute with the action of "
                        f"the group generator {group_generator} on the lattice generator {vector} of {domain}"
                    )

    def _element_constructor_(self, images):
        morphism = super()._element_constructor_(images)
        self._check_equivariance(morphism)
        return morphism

    def elementwise(self, function):
        morphism = super().elementwise(function)
        self._check_equivariance(morphism)
        return morphism


class GroupLatticeMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return GroupLatticeMor


class LatticesOverGroupAlgebra(OwnedCategoryOverBaseRing):
    r"""``Lattices(R[G])``: lattices over ``R`` carrying an action by isometries."""

    def group_algebra(self):
        return self.base_ring()

    def coefficient_ring(self):
        return self.base_ring().base_ring()

    def acting_group(self):
        return self.base_ring().group()

    def _repr_object_names(self):
        return f"lattices over {self.base_ring()}"

    def super_categories(self):
        r"""``Modules(R[G])`` alone; ``G``-objects in ``Lattices(R)`` are reached by :meth:`restriction_along_group_inclusion`."""
        return [ModulesOverGroupAlgebra(self.base_ring())]

    _MorCategory = GroupLatticeMorCategoryConstruction

    # The equivalence ``Lattices(R[G]) ~ GObjects(G, Lattices(R))``, in the
    # same two directions as for modules over the group algebra.

    @cached_method
    def restriction_along_group_inclusion(self):
        r"""``Lattices(R[G]) -> GObjects(G, Lattices(R))``, the action ``G -> O(L)`` of a lattice over ``R[G]``."""
        return _RestrictionAlongGroupInclusionLatticeFunctor(self.base_ring())

    @cached_method
    def linearization(self):
        r"""``GObjects(G, Lattices(R)) -> Lattices(R[G])``, the ``R``-linear extension of an action by isometries."""
        return _LatticeLinearizationFunctor(self.base_ring())

    @cached_method
    def linearization_equivalence(self):
        r"""Linearization left adjoint to restriction along ``G -> R[G]``, with invertible unit and counit."""
        return _LatticeLinearizationEquivalence(self.base_ring())

    def an_object(self):
        r"""The hyperbolic plane with the swap of its two isotropic generators."""
        plane = Lattices(self.coefficient_ring())("U")
        labels = plane.module_generating_set()
        left, right = plane.module_generators()
        swap = plane.Aut()({labels[0]: right, labels[1]: left})
        group = self.acting_group()
        assert group.cardinality() == 2, (
            f"the sample object of {self} is the hyperbolic plane with its swap, which needs a group of order 2, "
            f"but {group} has order {group.cardinality()}"
        )
        return self(plane, lambda g, vector: vector if g == group.one() else swap(vector))

    def _call_(self, lattice, action):
        r"""Equip ``lattice`` with the action ``action(g, v)``, which must preserve its form."""
        return _group_lattice(lattice, self.acting_group(), action)

    class ParentMethods:
        _derived_construction_parameters = ("unformed_module", "source_action_functor")

        def __init__(self, source_group_module, source_form, **rest) -> None:
            r"""Thread the same lattice through its form and its linearized action.

            The action was linearized on the lattice on which the form is
            stated.  The group-module level receives that exact module and
            action; the form level receives the form, which determines its
            module.  Neither level consumes or overwrites the other's datum.
            """
            module = source_group_module.unformed_module()
            assert source_form.module() is module, (
                f"cannot equip one lattice with both an action and a form: the {source_group_module.group()}-action "
                f"is on {module} but the form {source_form} is on {source_form.module()}"
            )
            self._preamble_source_group_module = source_group_module
            super().__init__(
                source_form=source_form,
                unformed_module=module,
                source_action_functor=source_group_module.action_functor(),
                **rest,
            )

        def source_group_module(self):
            r"""The ``R[G]``-module built on the lattice this action was stated on."""
            return self._preamble_source_group_module

        def group(self):
            return self.source_group_module().group()

        def group_algebra(self):
            return self.source_group_module().group_algebra()


        def _Hom_(self, codomain, category=None):
            group_lattices = Lattices(self.group_algebra())
            if codomain in group_lattices and (
                category is None or category.is_subcategory(group_lattices)
            ):
                return group_lattices.Mor(self, codomain)
            return super()._Hom_(codomain, category)

        def is_trivial_action(self) -> bool:
            return self.source_group_module().is_trivial_action()

        def _element_of_unformed_module(self, element):
            r"""The element of the lattice the action was stated on, with the same coefficients.

            A group lattice is built on the generating set of that lattice,
            so an element reads there with the coefficients it has here.
            Stated at this level because a group lattice is also an object of
            ``Modules(R[G])``, whose reading through the underlying additive
            group describes a module built on that group, not a lattice.
            """
            coordinates = self(element).to_vector()
            return self.unformed_module().linear_combination(
                {label: coordinates(label) for label in coordinates.support().domain()}
            )

        def _element_from_unformed_module(self, element):
            r"""The element of this group lattice with the coefficients ``element`` has in the lattice the action was stated on."""
            coordinates = self.unformed_module()(element).to_vector()
            return self.linear_combination(
                {label: coordinates(label) for label in coordinates.support().domain()}
            )

        @cached_method
        def action(self):
            source_group_module = self.source_group_module()
            group = source_group_module.group()

            def transported_image(group_element, label):
                backing_image = source_group_module.act(
                    group_element,
                    source_group_module.module_generator(label),
                )
                coordinates = source_group_module.framing_morphism().lift(backing_image)
                return self.linear_combination(
                    {label: coordinates(label) for label in coordinates.support().domain()}
                )

            orthogonal_group = self.Aut()
            action = Sets().Mor(group, orthogonal_group)(
                lambda group_element: orthogonal_group(
                    lambda label: transported_image(group_element, label)
                )
            )
            assert group.has_selected_group_resolution()
            for group_generator in group.group_generators():
                action(group_generator)
            return action

        @cached_method
        def group_module(self):
            r"""Return this lattice itself as its inherited ``R[G]``-module."""
            return self

        def act(self, group_element, vector):

            if vector.parent() is not self:
                raise TypeError(
                    f"{vector} is not an element of the lattice {self}, so {group_element} cannot act on it; "
                    f"its parent is {vector.parent()}"
                )
            return self.action()(group_element)(vector)

        def action_of(self, group_element):
            return self.action()(group_element)

        def is_invariant(self, vector) -> bool:
            group = self.group()
            assert group.has_selected_group_resolution()
            return all(self.act(group_generator, vector) == vector for group_generator in group.group_generators())

        def module_invariants(self):
            r"""Return the native fixed submodule of the underlying group module."""
            return super().module_invariants()

        def invariant_lattice(self):
            r"""Return ``L^G`` as a formed subobject of this lattice.

            This intersects the fixed lattices of a chosen finite generating
            set.  It deliberately does not reuse ``module_invariants()``, whose
            codomain is the unformed underlying module.
            """
            group = self.group()
            assert group.has_selected_group_resolution(), (
                f"cannot compute the invariant lattice of {self}: this needs a chosen finite generating set of "
                f"{group}, but {group} is only known to be in {group.category()}"
            )
            generators = tuple(group.group_generators())
            if not generators:
                return self.subobject_on(self.module_generators())
            invariants = self.action_of(generators[0]).invariant_lattice()
            for generator in generators[1:]:
                invariants = invariants.intersection(self.action_of(generator).invariant_lattice())
            return invariants

        def module_coinvariants(self):
            r"""Return the underlying module quotient by ``(g-1)M``."""
            return super().module_coinvariants()

        @cached_method
        def coinvariant_lattice(self):
            r"""Return ``(L^G)^perp`` as a formed subobject of ``L``.

            Module coinvariants remain available separately as
            ``module_coinvariants() = L / <g v-v>``.
            """
            return self.invariant_lattice().orthogonal_complement()

        def formed_coinvariants(self, *args, **kwargs):
            return self.coinvariant_lattice(*args, **kwargs)

        def isotypic_lattice(self, character):
            r"""Return the formed ``character``-isotypic sublattice with its restricted action.

            The underlying module component is the exact isotypic subobject of
            the associated ``R[G]``-module.  Its embedded basis is used to
            rebuild the restricted lattice form, and the ambient action is
            then restricted through that represented inclusion.  The result
            remains a subobject of this lattice rather than an isomorphic
            detached copy.
            """
            component = self.group_module().isotypic_component(character)
            module_inclusion = component.inclusion()
            component_module = module_inclusion.domain()
            if module_inclusion.codomain() is not self.unformed_module():
                raise ArithmeticError(
                    f"the {character}-isotypic component of {self} is not a submodule of its underlying module "
                    f"{self.unformed_module()}: its inclusion has codomain {module_inclusion.codomain()}"
                )
            embedded_basis = tuple(
                self(module_inclusion(component_module.module_generator(label)))
                for label in component_module.module_generating_set()
            )
            formed = self.subobject_on(embedded_basis)
            inclusion = formed.inclusion()

            def restricted_action(group_element, vector):
                return inclusion.lift(
                    self.action_of(group_element)(inclusion(vector))
                )

            # The component is an R-lattice carrying a G-action, not an
            # R[G]-valued bilinear lattice.  The group-algebra category is
            # the action-bearing owner; its constructor retains the R-form.
            assert formed.base_ring() is self.coefficient_ring()
            return LatticesOverGroupAlgebra(self.group_algebra())(formed, restricted_action)

        def character(self):
            return super().character()


def _group_lattice(lattice, group, action):
    r"""Equip ``lattice`` with a selected action of ``group`` preserving its form."""

    base_ring = lattice.base_ring()
    assert lattice in Lattices(base_ring).FinitelyGenerated()
    source_group_module = Modules(base_ring[group])(lattice, action)
    group = source_group_module.group()

    extra_categories = [Lattices(base_ring[group])]
    construction_data = [("source_group_module", source_group_module)]
    if lattice in RootLattices():
        extra_categories.append(RootLattices())
        construction_data.append(("root_system_type_name", lattice.root_system_type_name()))
    result = Lattices(base_ring)._specialize_existing_lattice(
        lattice,
        extra_categories=tuple(extra_categories),
        construction_data=tuple(construction_data),
        unformed_module=lattice,
    )
    assert group.has_selected_group_resolution()
    for group_generator in group.group_generators():
        result.action()(group_generator)
    return result


def _lattice_morphism_by_labels(source, target, image):
    r"""The lattice morphism ``source -> target`` sending the generator at ``label`` to ``image(label)``."""
    return Lattices(source.base_ring()).Mor(source, target)(image)


class _RestrictionAlongGroupInclusionLatticeFunctor(Functor):
    r"""``Lattices(R[G]) -> GObjects(G, Lattices(R))``: the action ``G -> O(L)`` of a lattice over ``R[G]``."""

    _faithful = True

    def __init__(self, group_algebra) -> None:
        lattices = Lattices(group_algebra)
        self._group = lattices.acting_group()
        self._coefficient_lattices = Lattices(lattices.coefficient_ring())
        super().__init__(lattices, GObjects(self._group, self._coefficient_lattices))

    def _apply_object(self, lattice):
        from sage_extensions.categories.functors.group_actions import (
            GroupActionFunctor,
        )

        endomorphisms = self._coefficient_lattices.Mor(lattice, lattice)
        return self.codomain()(
            GroupActionFunctor(
                self._group,
                self._coefficient_lattices,
                lattice,
                lambda group_element: endomorphisms.elementwise(lattice.action_of(group_element)),
            )
        )

    def _apply_morphism(self, morphism):
        source = self.object_image(morphism.domain())
        target = self.object_image(morphism.codomain())
        component = _lattice_morphism_by_labels(
            morphism.domain(),
            morphism.codomain(),
            lambda label: morphism(morphism.domain().module_generator(label)),
        )
        return self.codomain().Mor(source, target)(lambda _obj: component)

    def _repr_(self):
        return f"Restriction of {self.domain()} along {self._group} -> {self.domain().base_ring()}"


class _LatticeLinearizationFunctor(Functor):
    r"""``GObjects(G, Lattices(R)) -> Lattices(R[G])``: the ``R``-linear extension of an action by isometries."""

    _faithful = True

    def __init__(self, group_algebra) -> None:
        lattices = Lattices(group_algebra)
        self._group = lattices.acting_group()
        self._coefficient_lattices = Lattices(lattices.coefficient_ring())
        super().__init__(GObjects(self._group, self._coefficient_lattices), lattices)

    def _apply_object(self, acted):
        from sage_extensions.categories.functors.group_actions import (
            _action_functor_of,
        )

        action = _action_functor_of(acted, self._group, self._coefficient_lattices)
        point = action.domain().an_object()
        arrows = action.domain().Mor(point, point)
        return self.codomain()(
            action(point),
            lambda group_element, vector: action(arrows(group_element))(vector),
        )

    def _apply_morphism(self, arrow):
        from sage_extensions.categories.functors.group_actions import (
            _underlying_equivariant_arrow,
        )

        source = self.object_image(arrow.domain())
        target = self.object_image(arrow.codomain())
        component = _underlying_equivariant_arrow(arrow, self._group, self._coefficient_lattices)
        codomain_lattice = component.codomain()

        def image(generator_label):
            coordinates = codomain_lattice(
                component(component.domain().module_generator(generator_label))
            ).to_vector()
            return target.linear_combination(
                {label: coordinates(label) for label in coordinates.support().domain()}
            )

        return self.codomain().Mor(source, target)(image)

    def _repr_(self):
        return f"Linearization of {self._group}-actions on lattices over {self._coefficient_lattices.base_ring()}"


class _LatticeLinearizationEquivalence(Adjunction):
    r"""``GObjects(G, Lattices(R)) ~ Lattices(R[G])``, linearization left adjoint to restriction along ``G -> R[G]``.

    Unit and counit send each chosen generator to the generator with the same
    label, so both are isomorphisms.
    """

    def __init__(self, group_algebra) -> None:
        super().__init__(
            _LatticeLinearizationFunctor(group_algebra),
            _RestrictionAlongGroupInclusionLatticeFunctor(group_algebra),
        )

    def _unit_component(self, acted):
        from sage_extensions.categories.functors.group_actions import (
            _action_functor_of,
        )

        linearized = self.left_adjoint()(acted)
        lattices = self.right_adjoint().codomain().underlying_category()
        action = _action_functor_of(acted, self.right_adjoint().codomain().acting_group(), lattices)
        source = action(action.domain().an_object())
        component = _lattice_morphism_by_labels(source, linearized, linearized.module_generator)
        return self.left_adjoint().domain().Mor(acted, self.right_adjoint()(linearized))(
            lambda _obj: component
        )

    def _counit_component(self, lattice):
        relinearized = self.left_adjoint()(self.right_adjoint()(lattice))
        return self.right_adjoint().domain().Mor(relinearized, lattice)(lattice.module_generator)

    def _repr_(self):
        return f"Linearization equivalence {self.left_adjoint().domain()} <-> {self.left_adjoint().codomain()}"


__all__ = [
    "GroupLatticeMorCategoryConstruction",
    "GroupLatticeMor",
    "GroupLatticeMorphism",
    "LatticesOverGroupAlgebra",
]
