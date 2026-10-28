"""Owned categories of modules and vector spaces."""

from __future__ import annotations

import functools
import itertools
import operator
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sage.categories.action import Action
from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.categories.commutative_additive_groups import CommutativeAdditiveGroups
from sage.categories.groups import Groups as SageGroups
from sage.matrix.constructor import matrix as engine_matrix
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.misc_c import prod
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import Element, ModuleElement
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.structure.richcmp import richcmp

from sage_extensions.categories.abstract_categories.mor_categories import (
    EndCategoryConstruction,
    IsoCategoryConstruction,
    MonoCategoryConstruction,
    MorCategoryConstruction,
    _category_accepts_morphism,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import (
    _fix_selected_resolution,
)
from sage_extensions.categories.abstract_categories.products import (
    SelectedColimitConstruction,
    SelectedLimitConstruction,
    _discrete_diagram,
    _factor_family,
    _finite_factor_family,
    _parallel_pair_diagram,
)
from sage_extensions.categories.group.magmas import AdditiveGroups
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleAutomorphismGroup,
    ModuleEmbeddingMor,
    ModuleMor,
    ModuleMorphism,
    ModuleMorphismMethods,
    TensorProductModuleMor,
    _framing_morphism,
)
from sage_extensions.categories.modules.module_morphisms.morphism_matrices import (
    _matrix_group,
    _row_normal_form,
)
from sage_extensions.categories.rings.ring_foundation import (
    IntegralDomains,
    LocalizationRings,
    LocalRings,
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedOrders,
    OwnedRings,
    PrincipalIdealDomains,
    RingMor,
    _engine_element,
    _engine_ring,
    _linear_algebra_element,
    _linear_algebra_ring,
    _owned_engine_element,
    _owned_integers,
    _owned_ring,
    _OwnedRingParent,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    finite_indexed_family,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import (
    NN,
    EnumeratedSets,
    Sets,
)
from sage_extensions.logic import (
    AtomicProposition,
    Predicate,
    Unknown,
    ask,
    conjunction,
)
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.refine import RealizationHook

if TYPE_CHECKING:
    from sage_extensions.lexicon.category_theory import ObjectOfCategory
    from sage_extensions.owned_category import ConstructionData

for _module_axiom in ("FinitelyGenerated", "Free", "Projective", "Torsion"):
    if _module_axiom not in all_axioms:
        all_axioms.add(_module_axiom)


class _ModuleScalarAction(Action):
    r"""The selected scalar action of the base ring on one module parent."""

    def __init__(self, scalar_parent, module, is_left) -> None:
        self._module = module
        Action.__init__(self, scalar_parent, module, is_left, operator.mul)

    def _act_(self, scalar, element):
        return self._module.scalar_multiple(scalar, element)


def _register_module_scalar_action(module) -> None:
    r"""Register ordinary ``r*m``/``m*r`` syntax for an owned module parent."""
    scalar_parent = module.base_ring()
    module.register_action(_ModuleScalarAction(scalar_parent, module, True))
    if scalar_parent in OwnedRings().Commutative():
        module.register_action(_ModuleScalarAction(scalar_parent, module, False))


class ModuleMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):

        return ModuleMor

    def fixed_category_class_for(self, domain, codomain):
        return domain._module_mor_class()


class MatrixEndomorphismMor(ModuleMor):
    r"""Linear endomorphism-space maps which also preserve composition and its unit."""

    class ElementMethods(ModuleMorphismMethods, RingMor.ElementMethods):
        pass


class MatrixEndomorphismMorCategoryConstruction(MorCategoryConstruction):
    r"""Fixed Mor of matrix endomorphism objects over an arbitrary base ring.

    These are unital algebra maps over the retained centre of the
    coefficient ring. The fixed Mor has no pointwise additive closure:
    the sum of two unit-preserving maps need not preserve the unit.
    The following source specimens are unverified under ``DEV-58``::

        sage: base = ZZ.matrix_space(2, 2)
        sage: matrices = base.matrix_space(1, 1)
        sage: mor = MatrixEndomorphismSpaces(base).Mor(matrices, matrices)
        sage: identity = mor.identity()
        sage: identity.parent() is mor
        True
        sage: identity(matrices.one()) == matrices.one() and identity.preserves_unit()
        True

    For a commutative coefficient ring its centre is the ring itself::

        sage: matrices = ZZ.matrix_space(2, 2)
        sage: identity = MatrixEndomorphismSpaces(ZZ).Mor(matrices, matrices).identity()
        sage: identity(matrices.one()) == matrices.one() and identity.preserves_unit()
        True
    """

    def fixed_category_class_for(self, domain, codomain):
        from sage_extensions.categories.algebras.algebras import (
            UnitalMultiplicativeAlgebraMor,
        )

        return UnitalMultiplicativeAlgebraMor


class ModuleMonoCategoryConstruction(MonoCategoryConstruction):
    r"""The declared monomorphisms of modules over one scalar ring."""

    def fixed_category_class(self):
        return ModuleEmbeddingMor


class LinearEndCategoryConstruction(EndCategoryConstruction):
    r"""Endomorphism rings for categories enriched in modules."""

    def Of(self, obj, codomain=None):
        if codomain is not None and codomain is not obj:
            raise ValueError(
                f"End({obj}) was asked with codomain {codomain}: an endomorphism has equal domain and codomain"
            )
        if obj not in self.base_category():
            raise TypeError(
                f"End({obj}) is not defined in {self.base_category()}: {obj} is not an object of it"
            )
        endomorphisms = super().Of(obj)
        endomorphisms.attach_end_family(self)
        if endomorphisms not in OwnedRings():
            raise TypeError(
                f"the endomorphisms {endomorphisms} of {obj} were not constructed as a ring; "
                f"End({obj}) must be a ring under composition"
            )
        return endomorphisms


class ModuleEndCategoryConstruction(LinearEndCategoryConstruction):
    r"""The ring-valued endomorphism family ``M |-> End_R(M)``."""


class ModuleIsoCategoryConstruction(IsoCategoryConstruction):
    r"""Module isomorphisms, with ``Aut_R(M)`` represented by its unit group."""

    def Of(self, domain, codomain=None):
        if codomain is None:
            codomain = domain
        if domain is not codomain:
            return super().Of(domain, codomain)
        if domain not in self.base_category():
            raise TypeError(
                f"Aut({domain}) is not defined in {self.base_category()}: {domain} is not a module there"
            )
        cached = self._cached_between(domain, domain)
        if cached is not None:
            return cached
        result = ModuleAutomorphismGroup(self, domain)
        return self._remember_between(domain, domain, result)


def _is_group_algebra(ring) -> bool:
    r"""Decide whether ``ring`` is an owned group algebra ``R[G]``.

    Read off the ring's own category: constructing ``GroupAlgebras(R)`` to
    ask would need ``Modules(R)``, which may be the category being built.
    """
    from sage_extensions.categories.algebras.group_algebras import GroupAlgebras

    if ring not in OwnedRings():
        return False
    # Sage realizes each category instance in a dynamic subclass, so the
    # placement is recognized by its category class, not by identity.
    return any(
        isinstance(placement, GroupAlgebras)
        for placement in ring.category().all_super_categories(proper=False)
    )


def _action_with_canonical_endomorphism_parent(base_ring, additive_group, action):
    r"""Re-home a scalar action in the canonical ``End_Ab(additive_group)`` parent.

    Category refinement may produce two endomorphism parents with the same
    literal object endpoints. Their pointwise functions are still actions on
    the same group; normalize that representation at the Modules boundary
    rather than changing the module object or rejecting the defining action.
    """
    endomorphisms = AdditiveGroups().AdditiveCommutative().End(additive_group)
    if action.domain() is base_ring and action.codomain() is endomorphisms:
        return action
    supplied_endomorphisms = action.codomain()
    assert (
        supplied_endomorphisms.domain() is additive_group
        and supplied_endomorphisms.codomain() is additive_group
    ), (
        f"the scalar action {action} has codomain {supplied_endomorphisms}, not an endomorphism ring "
        f"of its exact underlying additive group {additive_group}"
    )
    return base_ring.Mor(endomorphisms, category=OwnedRings())(
        lambda scalar, supplied_action=action: endomorphisms.elementwise(
            lambda element: supplied_action(scalar)(element)
        )
    )


class Modules(OwnedCategoryOverBaseRing):
    r"""Modules over a ring, on the owned additive and scalar spines."""

    @staticmethod
    def __classcall__(cls, base_ring, *args, **kwargs):
        r"""``Modules(R[G])`` is the category of modules over a group algebra.

        The owned placement of a group module is the ring it is a module
        over, so the group algebra selects the category class that knows its
        group; every other ring reaches the generic construction.
        """
        match base_ring:
            case _OwnedRingParent():
                # Native ring hosts are the regular rings adopted by the ring
                # owner, never the structured objects produced by the group-
                # algebra functor.  During the initial ZZ bootstrap their full
                # category placement is still being assembled, so do not ask
                # that unfinished placement merely to reject the group-algebra
                # specialization.
                pass
            case _ if cls is Modules and _is_group_algebra(base_ring):
                from sage_extensions.categories.modules.group_modules.group_modules import (
                    ModulesOverGroupAlgebra,
                )

                return ModulesOverGroupAlgebra(base_ring)
            case _:
                pass
        return OwnedCategoryOverBaseRing.__classcall__(cls, base_ring, *args, **kwargs)

    def Core(self):
        r"""The core groupoid of modules; at ``(M, M)`` its Mor is ``Aut_R(M)`` (``_ModuleCore``)."""
        from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
            _ModuleCore,
        )

        return _ModuleCore(self)

    def _core_isomorphism_witness(self, core_mor):
        r"""Implementer side of ``CoreMor``'s core contract for modules: the identity of ``Aut_R(M)``."""
        assert core_mor.domain() is core_mor.codomain(), (
            f"whether {core_mor.domain()} and {core_mor.codomain()} are isomorphic modules is not decided here"
        )
        return core_mor.identity()

    def _core_automorphism_generators(self, core_mor):
        r"""Implementer side of the core contract: generators of ``GL(M)`` from Sage's ``GL(n, R)`` on the selected basis."""
        return core_mor._basis_general_linear_generators()

    def free_module(self, labels):
        r"""``F_R(S)``, the free object of this category on the set ``S`` of labels.

        This is the object part of the free functor ``Sets().free_module(R)``
        for the base ring ``R`` of this category.  A finite family of labels
        names the ordered set of them, and a rank ``n`` names the ordinal
        ``{0, ..., n-1}`` (``CON-14``).
        """
        return self.base_ring().free_module(labels)

    def _augmentation(self, group):
        r"""The augmentation ``epsilon: R[G] -> R`` with this literal scalar ring."""
        from sage_extensions.categories.functors.group_actions import (
            _group_algebra_augmentation_ring_map,
        )

        return _group_algebra_augmentation_ring_map(self.base_ring()[group])

    def trivial_action(self, group):
        r"""``Triv_G : Modules(R) -> Modules(R[G])``, restriction along the augmentation."""
        return self.restriction_of_scalars(self._augmentation(group))

    def trivial_invariants_adjunction(self, group):
        r"""``Triv_G -| (-)^G``, restriction/coextension along the augmentation."""
        return self.restriction_coextension_adjunction(self._augmentation(group))

    def _call_(self, datum, scalar_action=None):
        r"""Construct the left module defined by ``rho : R -> End_Ab(X)``.

        ``Modules(R)(rho)`` obtains ``X`` from the target Mor endpoints.
        ``Modules(R)(X, rho)`` states those same endpoints explicitly.
        """
        from sage_extensions.categories.modules.general_modules import GeneralModules
        from sage_extensions.categories.modules.native_modules import (
            _RingModulePresentation,
        )
        from sage_extensions.owned_category import _object_of

        if isinstance(datum, _RingModulePresentation):
            assert scalar_action is None, (
                f"{datum} already determines its scalar action, so the separate scalar action {scalar_action} is not accepted"
            )
            return datum.construct(self)
        if scalar_action is None:
            scalar_action = datum
            module = scalar_action.codomain().domain()
        else:
            module = datum
        assert scalar_action.parent().mor_category().is_subcategory(OwnedRings()), (
            f"{scalar_action} cannot define a left module: the scalar action must be a unital ring morphism, "
            f"but it lies in {scalar_action.parent()}"
        )
        assert _owned_ring(scalar_action.domain()) is self.base_ring(), (
            f"{scalar_action} cannot define an object of {self}: the scalar action must be a ring morphism "
            f"out of {self.base_ring()}, but its domain is {scalar_action.domain()}"
        )
        scalar_action = _action_with_canonical_endomorphism_parent(
            self.base_ring(), module, scalar_action
        )
        return _object_of(
            GeneralModules(self.base_ring()),
            base_ring=self.base_ring(),
            rho=scalar_action,
        )

    @cached_method
    def underlying_additive_group_functor(self):
        r"""Return the forgetful functor ``Mod_R -> Ab`` on objects and maps."""
        from sage_extensions.categories.functors.module_additive_groups import (
            UnderlyingAdditiveGroupFunctor,
        )

        return UnderlyingAdditiveGroupFunctor(self)

    # Scalar change along a ring morphism ``f: R -> S``: the adjoint triple
    # ``S tensor_R - -| Res_f -| Hom_R(S, -)``, each functor spelled on its
    # domain category and each adjunction on its left adjoint's domain.

    @cached_method(key=lambda self, ring_map: id(ring_map))
    def scalar_extension(self, ring_map):
        r"""``S tensor_R - : Modules(R) -> Modules(S)`` along ``ring_map: R -> S``."""
        from sage_extensions.categories.functors.scalar_change import (
            _ScalarExtensionFunctor,
        )

        assert _owned_ring(ring_map.domain()) is self.base_ring()
        return _ScalarExtensionFunctor(ring_map)

    @cached_method
    def restriction_of_scalars(self, ring_map):
        r"""``Res_f : Modules(S) -> Modules(R)`` along ``ring_map: R -> S``.

        Along the augmentation ``R[G] -> R`` this is the trivial action.
        One functor per ring map (the cache key is the ring map itself), so
        the forward image ``Res_f(M)`` of a module is one object, cached by
        that functor.
        """
        from sage_extensions.categories.functors.group_actions import (
            _TrivialActionFunctor,
        )
        from sage_extensions.categories.functors.scalar_change import (
            _RestrictionOfScalarsFunctor,
        )

        assert _owned_ring(ring_map.codomain()) is self.base_ring()
        match ring_map:
            case _ if (
                ring_map.is_group_algebra_augmentation()
                and ring_map.codomain() is ring_map.domain().base_ring()
            ):
                return _TrivialActionFunctor(ring_map)
            case _:
                return _RestrictionOfScalarsFunctor(ring_map)

    def coextension_of_scalars(self, ring_map):
        r"""``Hom_R(S, -) : Modules(R) -> Modules(S)`` along ``ring_map: R -> S``."""
        from sage_extensions.categories.functors.scalar_change import (
            _CoextensionOfScalarsFunctor,
        )

        assert _owned_ring(ring_map.domain()) is self.base_ring()
        return _CoextensionOfScalarsFunctor(ring_map)

    def base_change_adjunction(self, ring_map):
        r"""``S tensor_R - -| Res_f`` along ``ring_map: R -> S``."""
        from sage_extensions.categories.functors.scalar_change import (
            _base_change_adjunction,
        )

        assert _owned_ring(ring_map.domain()) is self.base_ring()
        return _base_change_adjunction(ring_map)

    def restriction_coextension_adjunction(self, ring_map):
        r"""``Res_f -| Hom_R(S, -)`` along ``ring_map: R -> S``.

        Along the augmentation ``R[G] -> R`` this is ``Triv_G -| (-)^G``.
        """
        from sage_extensions.categories.functors.group_actions import (
            _TrivialInvariantsAdjunction,
        )
        from sage_extensions.categories.functors.scalar_change import (
            _restriction_coextension_adjunction,
        )

        assert _owned_ring(ring_map.codomain()) is self.base_ring()
        match ring_map:
            case _ if (
                ring_map.is_group_algebra_augmentation()
                and ring_map.codomain() is ring_map.domain().base_ring()
            ):
                return _TrivialInvariantsAdjunction(ring_map)
            case _:
                return _restriction_coextension_adjunction(ring_map)

    class SubcategoryMethods:
        r"""Constructions this category owns, reachable from any subcategory."""

        def Subobjects(self, base_object):
            r"""Return represented module subobjects of ``base_object``.

            Module subobjects retain their structured source parent and chosen
            linear inclusion.  They are therefore the generic structured
            subobjects of this module category, not the set-specific slice
            objects inherited from ``Sets``.
            """
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                SubobjectCategory,
            )

            return SubobjectCategory(self, base_object)

        # Properties of the objects, each an axiom on this category.

        def FinitelyGenerated(self):
            r"""Return this category with the axiom that its objects are finitely generated."""
            return self._with_axiom("FinitelyGenerated")

        def FinitelyPresented(self):
            r"""Return this category with the axiom that its objects are finitely presented."""
            return self._with_axiom("FinitelyPresented")

        def Free(self):
            r"""Return this category with the axiom that its objects are free."""
            return self._with_axiom("Free")

        def Projective(self):
            r"""Return this category with the axiom that its objects are projective."""
            return self._with_axiom("Projective")

        def resolutions(self, truncation=0, projective_class=None):
            r"""Return the category of chosen truncated projective resolutions.

            This is a data category over Modules(R).  It does not choose a
            resolution of an object merely because the object lies in a
            property subcategory.
            """
            from sage_extensions.categories.abstract_categories.resolutions import (
                Resolutions,
            )

            modules = OwnedCategoryOverBaseRing.__classcall__(Modules, self.base_ring())
            match projective_class:
                case None:
                    projective_class = modules.Projective()
                case _:
                    pass
            return Resolutions(
                modules,
                projective_class,
                truncation,
            )

        def Torsion(self):
            r"""Return this category with the axiom that its objects are torsion."""
            return self._with_axiom("Torsion")

        # Functors out of ``Mod_R``, each spelled as a method of this, their
        # domain category, and named by the construction it performs.

        def underlying_set(self):
            r"""``U : Mod_R -> Set``, the underlying-set functor.

            The right adjoint of the free-module functor spelled on ``Set``.
            On an object it is the identity: a module already is a set object,
            and forgetting the scalar action removes structure, not elements.
            """
            from sage_extensions.categories.functors.free_forgetful import (
                _underlying_set_functor,
            )

            return _underlying_set_functor(self.base_ring())

        def dualization(self):
            r"""``(-)^* = Hom_R(-, R)``, the contravariant ``R``-linear dualization.

            Which duality this is, is named by the category it is a method of:
            it is the ``R``-linear one, into the free module of rank one.  The
            represented functor has the finitely generated free modules for
            domain and codomain, where the dual basis frames ``M^*``.
            """
            from sage_extensions.categories.functors.linear_constructions import (
                _dualization_functor,
            )

            return _dualization_functor(self.base_ring())

        def symmetric_algebra(self):
            r"""``Sym_R : Mod_R -> CAlg_R``, the symmetric-algebra functor.

            Left adjoint of the underlying-module functor on commutative
            ``R``-algebras; the adjunction is ``symmetric_algebra_adjunction``.
            """
            from sage_extensions.categories.functors.free_algebras import (
                _symmetric_algebra_functor,
            )

            return _symmetric_algebra_functor(self.base_ring())

        def tensor_algebra(self):
            r"""``T_R : Mod_R -> Alg_R``, the tensor-algebra functor.

            Left adjoint of the underlying-module functor on associative unital
            ``R``-algebras; the adjunction is ``tensor_algebra_adjunction``.
            """
            from sage_extensions.categories.functors.free_algebras import (
                _tensor_algebra_functor,
            )

            return _tensor_algebra_functor(self.base_ring())

        def exterior_algebra(self):
            r"""``Lambda_R : Mod_R -> AltAlg_R``, the exterior-algebra functor.

            The alternating quotient of the tensor algebra, graded by the
            exterior powers ``Lambda^n M``.
            """
            from sage_extensions.categories.functors.free_algebras import (
                _alternating_algebra_functor,
            )

            return _alternating_algebra_functor(self.base_ring())

        def divided_power_algebra(self):
            r"""``Gamma_R : Mod_R -> DPAlg_R``, the divided-power algebra functor."""
            from sage_extensions.categories.functors.free_algebras import (
                _divided_power_algebra_functor,
            )

            return _divided_power_algebra_functor(self.base_ring())

        # An adjunction is a method of its left adjoint's domain category.
        # ``Sym_R`` and ``T_R`` are left adjoints out of ``Mod_R``, so their
        # adjunctions are asked for here.  ``Lambda_R`` has none.

        def symmetric_algebra_adjunction(self):
            r"""``Sym_R -| U``, between ``Mod_R`` and commutative ``R``-algebras."""
            from sage_extensions.categories.functors.free_algebras import (
                _symmetric_algebra_adjunction,
            )

            return _symmetric_algebra_adjunction(self.base_ring())

        def tensor_algebra_adjunction(self):
            r"""``T_R -| U``, between ``Mod_R`` and associative unital ``R``-algebras."""
            from sage_extensions.categories.functors.free_algebras import (
                _tensor_algebra_adjunction,
            )

            return _tensor_algebra_adjunction(self.base_ring())

        def bilinear_free_form_adjunction(self):
            r"""Return the free bilinear-form/underlying-module adjunction on ``Mod_R``."""
            from sage_extensions.categories.functors.free_forms import (
                _bilinear_free_form_adjunction,
            )

            return _bilinear_free_form_adjunction(self.base_ring())

        def free_bilinear_form_adjunction(self):
            r"""Return the free bilinear-form/underlying-module adjunction on ``Mod_R``."""
            return self.bilinear_free_form_adjunction()

        def quadratic_free_form_adjunction(self):
            r"""Return the free quadratic-form/underlying-module adjunction on ``Mod_R``."""
            from sage_extensions.categories.functors.free_forms import (
                _quadratic_free_form_adjunction,
            )

            return _quadratic_free_form_adjunction(self.base_ring())

        def free_quadratic_form_adjunction(self):
            r"""Return the free quadratic-form/underlying-module adjunction on ``Mod_R``."""
            return self.quadratic_free_form_adjunction()

        def tensor_product(self, factors):
            r"""Return the algebraic $\bigotimes_{i \in I} M_i$ for an indexed family of modules.

            The tensor product is taken over the index set: its generating set
            is the product of the factors' generating sets over $I$, so a
            generator is a section of that family rather than a nest of pairs.
            Completion and scalar change retain their own selected ring maps
            and completion data; neither is silently substituted for this
            algebraic tensor construction.
            """
            family = _finite_factor_family(factors, name="Tensor factors")
            assert all(factor in self for factor in family), (
                f"the tensor product over {self.base_ring()} is of objects of {self}, "
                f"but not every factor of {family} is one"
            )
            return _module_tensor_product(family)

        def _categorical_tensor_product(self, left, right):
            return self.tensor_product((left, right))

        def biproduct(
            self,
            factors,
            *,
            extra_categories=(),
            extra_construction_data=None,
        ):
            r"""Return $\bigoplus_{i \in I} M_i$ for an indexed family of modules.

            The biproduct is taken over the index set: its generating set is
            the coproduct of the factors' generating sets over $I$, so the
            injection and the projection at $i$ are arrows between $M_i$ and
            the one biproduct, not composites through a nested binary one.
            """
            family = _finite_factor_family(factors, name="Biproduct factors")
            assert all(factor in self for factor in family), (
                f"the direct sum over {self.base_ring()} is of objects of {self}, "
                f"but not every factor of {family} is one"
            )
            if extra_categories or extra_construction_data:
                return _module_biproduct_with_data(
                    family,
                    base_ring=self.base_ring(),
                    extra_categories=extra_categories,
                    extra_construction_data=extra_construction_data,
                )
            return _module_biproduct(family, self.base_ring())

        def _categorical_biproduct(self, left, right):
            return self.biproduct((left, right))

        def product(self, factors):
            r"""Return $\prod_{i \in I} M_i$, created on underlying sets in general."""
            return self._categorical_product_construction(factors).object()

        def product_element(self, construction, components):
            r"""Return the element of a selected module product with these components.

            ``components`` is an indexed family over the product diagram's
            object set.  A finite biproduct assembles it through its canonical
            injections; a product created by the underlying-set functor uses
            the corresponding dependent-set section.  This is one semantic
            operation at the module owner, not a representation choice for
            callers.
            """
            diagram = construction.diagram()
            match diagram.codomain() is self:
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"the product {construction.object()} is a limit in {diagram.codomain()}, not in {self}"
                    )
            factors = diagram.diagram_objects()
            match components.index_set() == factors.index_set():
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"an element of the product of {factors} needs one component for each factor, "
                        f"but the components are indexed by {components.index_set()}"
                    )
            product = construction.object()
            match product:
                case _ if product in BiproductModules(self.base_ring()):
                    value = product.zero()
                    for index in factors.index_set():
                        value += product.injection(index)(
                            factors.value(index)(components.value(index))
                        )
                    return value
                case _:
                    from sage_extensions.categories.modules.general_modules import (
                        GeneralModules,
                    )

                    assert product in GeneralModules(self.base_ring()), (
                        f"the product {product} over {self.base_ring()} is neither a direct sum nor a module "
                        f"on the Cartesian product of the underlying sets of its factors"
                    )
                    underlying = product.underlying_set()
                    return product(
                        underlying(
                            lambda index: factors.value(index)(components.value(index))
                        )
                    )

        def product_component(self, construction, element, index):
            r"""Project an element of a selected module product to one factor."""
            diagram = construction.diagram()
            match diagram.codomain() is self:
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"the product {construction.object()} is a limit in {diagram.codomain()}, not in {self}"
                    )
            return construction.structure_morphism(diagram.domain()(index))(element)

        def equalizer_element(self, construction, ambient_element):
            r"""Lift an ambient element satisfying a selected equalizer relation."""
            diagram = construction.diagram()
            match diagram.codomain() is self:
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"the equalizer {construction.object()} is a limit in {diagram.codomain()}, not in {self}"
                    )
            shape = diagram.domain()
            ambient = diagram(shape.source())
            ambient_element = ambient(ambient_element)
            equalizer = construction.object()
            inclusion = construction.structure_morphism(shape.source())
            match equalizer:
                case _ if equalizer in ModuleSubobjects(self.base_ring()):
                    return inclusion.lift(ambient_element)
                case _:
                    from sage_extensions.categories.modules.general_modules import (
                        GeneralModules,
                    )

                    assert equalizer in GeneralModules(self.base_ring()), (
                        f"the equalizer {equalizer} over {self.base_ring()} is neither a submodule nor a module "
                        f"on the subset of the domain where the two maps agree"
                    )
                    return equalizer(ambient_element)

        def _categorical_product(self, left, right):
            return self._categorical_product_construction((left, right)).object()

        def coproduct(self, factors):
            r"""Return $\coprod_{i \in I} M_i$, which over a finite index set is the biproduct."""
            return self._categorical_coproduct_construction(factors).object()

        def _categorical_coproduct(self, left, right):
            return self._categorical_coproduct_construction((left, right)).object()

        def _categorical_product_construction(self, factors):
            r"""Return the selected product cone in ``R-Mod``.

            A finite family whose factors already carry the framed-free or
            finite-presentation biproduct realization keeps that specialization.
            Every other represented family is created by the underlying-set
            functor: the underlying set is ``prod_i U(M_i)`` and the module
            operations are componentwise.  Both routes retain this same
            discrete diagram and universal cone.
            """
            family = _admitted_module_factor_family(
                self,
                factors,
                name="Product factors",
            )
            match _finite_biproduct_realizes_product(family):
                case True:
                    product = self.biproduct(family)
                case False:
                    assert self == Modules(self.base_ring()), (
                        f"the product of {family} in {self} is not a finite direct sum, and a product built on "
                        f"the underlying sets is only an object of Modules({self.base_ring()})"
                    )
                    product = _module_product_created_by_underlying_sets(
                        self.base_ring(),
                        family,
                    )
            if product not in self:
                raise TypeError(
                    f"the module product {product} of {family} does not belong to {self}; "
                    "a realization of the product in the ambient module category does not "
                    "establish closure in this subcategory"
                )
            # Reuse an established module-valued diagram rather than
            # reclassifying its values through a new unchecked callback.
            # This retains the original functor's actual object and arrow
            # actions for a nonconstant infinite family.
            diagram = family.selected_diagram()
            if diagram is None or diagram.codomain() is not self:
                constant = family.constant_value()
                if constant is not None:
                    from sage_extensions.categories.abstract_categories.cat import Cat
                    from sage_extensions.categories.abstract_categories.functors import (
                        DiscreteCategory,
                    )

                    diagram = (
                        Cat()
                        .Mor(DiscreteCategory(family.index_set()), self)
                        .constant_functor(constant)
                    )
                else:
                    diagram = _discrete_diagram(family, self)
            universal_cone = (
                (diagram)
                .ProductCones()
                .cone(
                    product,
                    lambda index: _module_product_projection(
                        product,
                        family,
                        index.value(),
                    ),
                )
            )

            def factorizer(cone):
                legs = indexed_family(
                    family.index_set(),
                    lambda label: cone.structure_morphism(diagram.domain()(label)),
                    name="Product cone legs",
                )
                if family.cardinality() == cardinal(0):
                    apex_map = (
                        cone.apex().module_category().Mor(cone.apex(), product).zero()
                    )
                else:
                    match product:
                        case _ if product in BiproductModules(self.base_ring()):
                            apex_map = product.from_product_cone(legs)
                        case _:
                            apex_map = _module_product_factor(
                                product, family, cone.apex(), legs
                            )
                return (
                    diagram.Cones()
                    .Mor(cone, universal_cone)
                    ._from_commuting_apex_map(
                        apex_map,
                    )
                )

            return SelectedLimitConstruction(diagram, universal_cone, factorizer)

        def _categorical_coproduct_construction(self, factors):
            r"""Return the selected finite coproduct cocone on the module biproduct."""
            family = _finite_factor_family(factors, name="Coproduct factors")
            assert all(factor in self for factor in family), (
                f"the coproduct over {self.base_ring()} is of objects of {self}, "
                f"but not every factor of {family} is one"
            )
            coproduct = self.biproduct(family)
            if coproduct not in self:
                raise TypeError(
                    f"the module coproduct {coproduct} of {family} does not belong to {self}; "
                    "its biproduct realization does not establish closure in this subcategory"
                )
            diagram = _discrete_diagram(family, self)
            universal_cocone = (
                (diagram)
                .CoproductCocones()
                .cocone(
                    coproduct,
                    lambda index: coproduct.injection(index.value()),
                )
            )

            def factorizer(cocone):
                legs = indexed_family(
                    family.index_set(),
                    lambda label: cocone.costructure_morphism(diagram.domain()(label)),
                    name="Coproduct cocone legs",
                )
                if family.cardinality() == cardinal(0):
                    return (
                        coproduct.module_category().Mor(coproduct, cocone.apex()).zero()
                    )
                return coproduct.from_coproduct_cocone(legs)

            return SelectedColimitConstruction(diagram, universal_cocone, factorizer)

        def _categorical_equalizer(self, left_morphism, right_morphism):
            r"""Realize an equalizer in ``R-Mod`` as ``ker(left-right)``."""
            return self._categorical_equalizer_construction(
                left_morphism, right_morphism
            ).object()

        @cached_method
        def _categorical_equalizer_construction(self, left_morphism, right_morphism):
            r"""Realize the selected equalizer in ``R-Mod``.

            The finite-presentation specialization is ``ker(left-right)``.
            Otherwise the forgetful functor creates the equalizer from the
            subset of the domain on which the two underlying set maps agree,
            with the inherited componentwise module operations.
            """
            if (
                left_morphism.domain() not in self
                or left_morphism.codomain() not in self
                or left_morphism.domain() is not right_morphism.domain()
                or left_morphism.codomain() is not right_morphism.codomain()
            ):
                raise ValueError(
                    f"the equalizer of {left_morphism} and {right_morphism} is not defined in {self}: "
                    f"the two maps must be parallel morphisms between objects of {self}"
                )
            ambient_modules = Modules(left_morphism.domain().base_ring())
            ambient_mor = ambient_modules.Mor(
                left_morphism.domain(),
                left_morphism.codomain(),
            )
            match left_morphism in ambient_mor, right_morphism in ambient_mor:
                case True, True:
                    pass
                case _:
                    raise ValueError(
                        f"the equalizer of {left_morphism} and {right_morphism} is not defined: "
                        f"both maps must be {left_morphism.domain().base_ring()}-linear maps in {ambient_mor}"
                    )
            if not all(
                _category_accepts_morphism(
                    self, left_morphism.domain(), left_morphism.codomain(), arrow
                )
                for arrow in (left_morphism, right_morphism)
            ):
                raise TypeError(
                    "the module equalizer requires arrows in the selected Mor category"
                )
            match (
                _represented_finite_presentation(left_morphism.domain()),
                _represented_finite_presentation(left_morphism.codomain()),
            ):
                case (True, True):
                    equalizer = (left_morphism - right_morphism).kernel()
                    inclusion = equalizer.inclusion()
                case _:
                    assert self == Modules(self.base_ring()), (
                        f"the equalizer of {left_morphism} and {right_morphism} in {self} is not a kernel of finitely "
                        f"presented modules, and an equalizer built on the underlying sets is only an object of "
                        f"Modules({self.base_ring()})"
                    )
                    equalizer, inclusion = _module_equalizer_created_by_underlying_sets(
                        left_morphism,
                        right_morphism,
                    )
            if equalizer not in self:
                raise TypeError(
                    f"the equalizer {equalizer} of {left_morphism} and {right_morphism} "
                    f"is not an object of {self}; an ambient module kernel does not "
                    "establish closure in the selected subcategory"
                )
            diagram = _parallel_pair_diagram(left_morphism, right_morphism, self)
            shape = diagram.domain()
            universal_cone = (
                (diagram)
                .Cones()
                .cone(
                    equalizer,
                    lambda index: (
                        inclusion
                        if index is shape.source()
                        else left_morphism * inclusion
                    ),
                )
            )

            def factorizer(cone):
                source_leg = cone.structure_morphism(shape.source())
                source = cone.apex()
                match equalizer:
                    case _ if equalizer in ModuleSubobjects(
                        left_morphism.domain().base_ring()
                    ):
                        return (
                            source.module_category()
                            .Mor(source, equalizer)
                            ._equalizer_factor(
                                source_leg,
                                inclusion=inclusion,
                            )
                        )
                    case _:
                        return _module_equalizer_factor(
                            equalizer,
                            source,
                            source_leg,
                            inclusion,
                        )

            return SelectedLimitConstruction(diagram, universal_cone, factorizer)

        def _categorical_coequalizer(self, left_morphism, right_morphism):
            r"""Realize a coequalizer in ``R-Mod`` as ``coker(left-right)``."""
            return self._categorical_coequalizer_construction(
                left_morphism, right_morphism
            ).object()

        @cached_method
        def _categorical_coequalizer_construction(self, left_morphism, right_morphism):
            r"""Realize the selected coequalizer cocone through ``coker(left-right)``."""
            if (
                left_morphism.domain() not in self
                or left_morphism.codomain() not in self
                or left_morphism.domain() is not right_morphism.domain()
                or left_morphism.codomain() is not right_morphism.codomain()
            ):
                raise ValueError(
                    f"the coequalizer of {left_morphism} and {right_morphism} is not defined in {self}: "
                    f"the two maps must be parallel morphisms between objects of {self}"
                )
            ambient_mor = Modules(self.base_ring()).Mor(
                left_morphism.domain(), left_morphism.codomain()
            )
            if left_morphism not in ambient_mor or right_morphism not in ambient_mor:
                raise ValueError(
                    f"the coequalizer of {left_morphism} and {right_morphism} needs "
                    f"two {self.base_ring()}-linear morphisms in {ambient_mor}"
                )
            if not all(
                _category_accepts_morphism(
                    self, left_morphism.domain(), left_morphism.codomain(), arrow
                )
                for arrow in (left_morphism, right_morphism)
            ):
                raise TypeError(
                    "the module coequalizer requires arrows in the selected Mor category"
                )
            difference = left_morphism - right_morphism
            raw_coequalizer = difference.cokernel()
            raw_projection = difference.cokernel_projection()

            # A stricter module category may still contain this particular
            # coequalizer even though cokernels do not stay in that category
            # in general.  Over a PID a torsion-free presented quotient is
            # finite free and supplies the actual trivialization.  Use that
            # isomorphic free representative when it lies in ``self`` so the
            # selected colimit is genuinely an object of its stated target
            # category, rather than a merely isomorphic presented module.
            from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
                _SelectedFinitePresentationModules,
            )

            ring = left_morphism.domain().base_ring()
            coequalizer = raw_coequalizer
            projection = raw_projection
            coequalizer_transport = None
            match raw_coequalizer:
                case _ if raw_coequalizer in self:
                    pass
                case _ if (
                    raw_coequalizer in _SelectedFinitePresentationModules(ring)
                    and ring in PrincipalIdealDomains()
                    and raw_coequalizer.is_torsion_free()
                ):
                    candidate_transport = raw_coequalizer.finite_free_trivialization()
                    if candidate_transport.codomain() in self:
                        coequalizer_transport = candidate_transport
                        coequalizer = candidate_transport.codomain()
                        projection = candidate_transport.forward() * raw_projection

            if coequalizer not in self:
                raise TypeError(
                    f"the coequalizer of {left_morphism} and {right_morphism} is {raw_coequalizer}, "
                    f"which has no selected representative in {self}; an ambient module "
                    "quotient is not automatically a colimit in this subcategory"
                )

            diagram = _parallel_pair_diagram(left_morphism, right_morphism, self)
            shape = diagram.domain()
            universal_cocone = (
                (diagram)
                .Cocones()
                .cocone(
                    coequalizer,
                    lambda index: (
                        projection * left_morphism
                        if index is shape.source()
                        else projection
                    ),
                )
            )

            def factorizer(cocone):
                target_leg = cocone.costructure_morphism(shape.target())
                target = cocone.apex()
                ambient = left_morphism.codomain()
                raw_factor = raw_coequalizer.module_category().Mor(
                    raw_coequalizer, target
                )(lambda label: target_leg(ambient.module_generator(label)))
                if coequalizer_transport is None:
                    return raw_factor
                return raw_factor * coequalizer_transport.inverse().forward()

            return SelectedColimitConstruction(diagram, universal_cocone, factorizer)

        def _categorical_equalizer_family(self, morphisms):
            r"""Realize a finite wide equalizer through kernels/intersections."""
            size = morphisms.cardinality()
            assert size.is_finite(), (
                f"the wide equalizer of {morphisms} is computed only for a finite family of maps, "
                f"but the family has cardinality {size}"
            )
            count = int(size.finite_value())
            if count == 0:
                raise ValueError(
                    f"the wide equalizer in {self} is not defined for the empty family {morphisms}: "
                    f"it needs at least one map to fix the domain"
                )
            index_set = morphisms.index_set()
            assert index_set in EnumeratedSets(), (
                f"computing the wide module equalizer requires an enumeration of {index_set}"
            )
            labels = tuple(index_set)
            reference = morphisms.value(labels[0])
            ambient_mor = Modules(self.base_ring()).Mor(
                reference.domain(), reference.codomain()
            )
            if reference.domain() not in self or reference.codomain() not in self:
                raise ValueError(
                    f"the wide equalizer of {morphisms} is not a diagram in {self}"
                )
            for label in labels:
                arrow = morphisms.value(label)
                if (
                    arrow.domain() is not reference.domain()
                    or arrow.codomain() is not reference.codomain()
                    or arrow not in ambient_mor
                    or not _category_accepts_morphism(
                        self, reference.domain(), reference.codomain(), arrow
                    )
                ):
                    raise ValueError(
                        f"the wide equalizer needs parallel {self.base_ring()}-linear arrows, but got {arrow}"
                    )
            if len(labels) == 1:
                # A singleton parallel family imposes no equality relation.
                # The limit is its literal source, not a newly computed
                # kernel of the zero morphism.
                return reference.domain()
            equalizer = self._categorical_equalizer(reference, reference)
            for label in labels[1:]:
                equalizer = equalizer.intersection(
                    self._categorical_equalizer(morphisms.value(label), reference)
                )
            if equalizer not in self:
                raise TypeError(
                    f"the wide equalizer {equalizer} is not an object of {self}"
                )
            return equalizer

        def _categorical_equalizer_family_construction(self, morphisms):
            r"""Retain the selected wide equalizer's diagram and inclusion."""
            from sage_extensions.categories.abstract_categories.products import (
                _parallel_family_diagram,
            )

            equalizer = self._categorical_equalizer_family(morphisms)
            reference = morphisms.value(next(iter(morphisms.index_set())))
            inclusion = (
                equalizer.Mor(equalizer).identity()
                if equalizer is reference.domain()
                else equalizer.inclusion()
            )
            diagram = _parallel_family_diagram(morphisms, self)
            shape = diagram.domain()
            universal_cone = diagram.Cones().cone(
                equalizer,
                lambda index: (
                    inclusion if index is shape.source() else reference * inclusion
                ),
            )

            def factorizer(cone):
                source = cone.apex()
                source_leg = cone.structure_morphism(shape.source())
                if equalizer is reference.domain():
                    return source_leg
                return (
                    source.module_category()
                    .Mor(source, equalizer)
                    ._equalizer_factor(source_leg, inclusion=inclusion)
                )

            return SelectedLimitConstruction(diagram, universal_cone, factorizer)

        def _categorical_coequalizer_family(self, morphisms):
            r"""Realize a finite wide coequalizer through images/sums/cokernels."""
            size = morphisms.cardinality()
            assert size.is_finite(), (
                f"the wide coequalizer of {morphisms} is computed only for a finite family of maps, "
                f"but the family has cardinality {size}"
            )
            count = int(size.finite_value())
            if count == 0:
                raise ValueError(
                    f"the wide coequalizer in {self} is not defined for the empty family {morphisms}: "
                    f"it needs at least one map to fix the codomain"
                )
            index_set = morphisms.index_set()
            assert index_set in EnumeratedSets(), (
                f"computing the wide module coequalizer requires an enumeration of {index_set}"
            )
            labels = tuple(index_set)
            reference = morphisms.value(labels[0])
            ambient_mor = Modules(self.base_ring()).Mor(
                reference.domain(), reference.codomain()
            )
            if reference.domain() not in self or reference.codomain() not in self:
                raise ValueError(
                    f"the wide coequalizer of {morphisms} is not a diagram in {self}"
                )
            for label in labels:
                arrow = morphisms.value(label)
                if (
                    arrow.domain() is not reference.domain()
                    or arrow.codomain() is not reference.codomain()
                    or arrow not in ambient_mor
                    or not _category_accepts_morphism(
                        self, reference.domain(), reference.codomain(), arrow
                    )
                ):
                    raise ValueError(
                        f"the wide coequalizer needs parallel {self.base_ring()}-linear arrows, but got {arrow}"
                    )
            if len(labels) == 1:
                return reference.codomain()
            relations = (reference - reference).image()
            for label in labels[1:]:
                relations = relations.sum((morphisms.value(label) - reference).image())
            quotient = relations.inclusion().cokernel()
            if quotient not in self:
                raise TypeError(
                    f"the wide coequalizer {quotient} is not an object of {self}"
                )
            return quotient

        def _categorical_coequalizer_family_construction(self, morphisms):
            r"""Retain the relation quotient and its universal wide cocone."""
            from sage_extensions.categories.abstract_categories.products import (
                _parallel_family_diagram,
            )

            quotient = self._categorical_coequalizer_family(morphisms)
            reference = morphisms.value(next(iter(morphisms.index_set())))
            target = reference.codomain()
            # This quotient was constructed as the cokernel of the inclusion
            # of the generated relation submodule. Retain that cokernel's
            # selected projection, rather than independently making another
            # arrow from generator labels.
            projection = (
                target.Mor(target).identity()
                if quotient is target
                else quotient.cokernel_projection()
            )
            if (
                projection.domain() is not target
                or projection.codomain() is not quotient
            ):
                raise ValueError(
                    "the wide module quotient's retained projection has incorrect endpoints"
                )
            diagram = _parallel_family_diagram(morphisms, self)
            shape = diagram.domain()
            universal_cocone = diagram.Cocones().cocone(
                quotient,
                lambda index: (
                    projection * reference if index is shape.source() else projection
                ),
            )

            def factorizer(cocone):
                target_leg = cocone.costructure_morphism(shape.target())
                if quotient is target:
                    return target_leg
                return quotient.module_category().Mor(quotient, cocone.apex())(
                    lambda label: target_leg(target.module_generator(label))
                )

            return SelectedColimitConstruction(diagram, universal_cocone, factorizer)

        def _categorical_product_morphism(
            self, left_morphism, right_morphism, source, target
        ):
            return left_morphism.biproduct_map(
                right_morphism, source=source, target=target
            )

        _categorical_coproduct_morphism = _categorical_product_morphism

    def _repr_object_names(self):
        return f"modules over {self.base_ring()}"

    def an_object(self):
        r"""The free module of rank one, which is the base ring itself."""
        return self.base_ring().free_module(1)

    def super_categories(self):
        base_ring = self.base_ring()
        match base_ring:
            case _OwnedRingParent():
                commutative = base_ring._commutativity_decision()
            case _:
                commutative = base_ring.is_commutative()
        match commutative:
            case True:
                from sage_extensions.categories.modules.fibered_modules import (
                    ModulesOverCommutativeRings,
                )

                return [ModulesOverCommutativeRings()]
            case _:
                return [AdditiveGroups().AdditiveCommutative()]

    def Mor(self, domain, codomain):
        r"""Return the unique Mor object ``Hom_R(domain,codomain)``."""
        domain = self._mor_endpoint(domain)
        codomain = self._mor_endpoint(codomain)
        if domain not in self or codomain not in self:
            raise TypeError(
                f"Mor({domain}, {codomain}) is not defined in {self}: both endpoints must be "
                f"{self.base_ring()}-modules"
            )
        return self.MorCategory().Of(domain, codomain)

    def _mor_endpoint(self, obj):
        r"""Read an ``R[G]``-module over ``R`` by restriction of scalars along ``R -> R[G]``.

        ``Hom_R(M, N)`` for two ``R[G]``-modules is the Mor of their
        restrictions, so the endpoints of this category's Mor are restricted
        before the Mor parent is built.
        """
        if obj in self:
            return obj
        from sage_extensions.categories.algebras.group_algebras import GroupAlgebras

        scalars = obj.base_ring()
        if scalars in GroupAlgebras(self.base_ring()):
            group_modules = Modules(scalars)
            return group_modules.restriction_of_scalars(
                group_modules.coefficient_inclusion()
            )(obj)
        return obj

    def _mor_parent_placement(
        self, domain, codomain, *, full_internal_mor=False, full_linear_mor=True
    ):
        r"""Place the chosen linear Mor without enlarging its arrow carrier.

        ``full_linear_mor`` states whether this constructor supplies a
        full-linear-Hom realization. Graded and cochain maps are defined
        by extra equations, which may be vacuous for particular endpoints.
        With ``False`` the Mor retains its central scalar action and
        diagonal endomorphism algebra, but endpoint framings alone supply
        no full-Hom basis or presentation. This construction datum neither
        decides equality with the full Hom nor proves any arrow law.
        """
        from sage_extensions.categories.group.additive_mors import (
            AdditiveEndomorphismRings,
        )
        from sage_extensions.owned_category import owned_category_join

        ring = self.base_ring()
        if not full_linear_mor:
            center = ring.ring_center()
            placement = [LinearMorModules(center)]
            if domain is codomain:
                placement.append(AdditiveEndomorphismRings(center))
            return owned_category_join(tuple(placement))
        if ring not in OwnedRings().Commutative():
            center = ring.ring_center()
            placement = [LinearMorModules(center)]
            if _coordinate_framed_free_module(
                domain, ring
            ) and _coordinate_framed_free_module(codomain, ring):
                placement.append(MatrixSpaces(ring))
                if domain is codomain:
                    placement.append(MatrixEndomorphismSpaces(ring))
            if domain is codomain:
                placement.append(AdditiveEndomorphismRings(center))
            return owned_category_join(tuple(placement))
        placement = [
            InternalMorModules(ring) if full_internal_mor else LinearMorModules(ring)
        ]
        matrix = _coordinate_framed_free_module(
            domain, ring
        ) and _coordinate_framed_free_module(codomain, ring)
        if matrix:
            placement.append(MatrixSpaces(ring))
            if domain is codomain:
                from sage_extensions.categories.algebras.algebras import (
                    Algebras,
                    MatrixAlgebras,
                )

                placement.append(MatrixAlgebras(ring))
                rank = domain.module_generating_set().cardinality()
                if int(rank.finite_value()) <= 1:
                    placement.append(
                        Algebras(ring).Associative().Unital().Commutative()
                    )
        elif domain is codomain:
            placement.append(AdditiveEndomorphismRings(ring))
        if full_internal_mor and not matrix:
            from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
                _SelectedFinitePresentationModules,
            )

            if _represented_finite_presentation(
                domain
            ) and _represented_finite_presentation(codomain):
                placement.append(_SelectedFinitePresentationModules(ring))
        if full_internal_mor and domain in TensorProductModules(ring):
            factors = domain.tensor_factors()
            if (
                factors.cardinality().is_finite()
                and int(factors.cardinality().finite_value()) == 2
                and factors[0] is factors[1]
            ):
                from sage_extensions.categories.forms.forms import BilinearFormMors

                placement.append(BilinearFormMors(ring))
        return owned_category_join(tuple(placement))

    _MorCategory = ModuleMorCategoryConstruction
    _MonoCategory = ModuleMonoCategoryConstruction
    _IsoCategory = ModuleIsoCategoryConstruction
    _EndCategory = ModuleEndCategoryConstruction

    class ElementMethods:
        __add__ = Element.__add__

        def order_ideal(self):
            r"""Return ``O_M(v) = {phi(v) : phi in Hom_R(M,R)}``.

            This is the image ideal of evaluation at this element. The
            represented computation uses generators of the linear dual;
            it does not require a chosen basis of ``M``.
            """
            module = self.parent()
            ring = module.base_ring()
            dual = module.dual_module()
            regular = dual.codomain()
            evaluation = Modules(ring).Mor(dual, regular)(
                lambda label: dual.module_generator(label)(self)
            )
            image = evaluation.image()
            regular_label = regular.module_generating_set()[0]
            return ring.ideal(
                *(
                    image.inclusion()(generator).to_vector()(regular_label)
                    for generator in image.module_generators()
                )
            )

        def __rmul__(self, scalar):
            r"""Return ring multiplication or the left module scalar action.

            For an algebra/ring viewed also as a module, two elements with the
            same owned ring parent multiply in that ring.  Only an element of
            the module's scalar ring acts through ``R -> End_Ab(U(M))``.
            For the regular left module over ``M_2(QQ)``, the operators
            given by left multiplication by ``E12`` and ``E21`` do not
            commute; scalar multiplication need not be R-linear.
            """
            match scalar:
                case _ if (
                    element_parent(scalar) is self.parent()
                    and self.parent() in OwnedRings()
                ):
                    return scalar._mul_(self)
                case _:
                    return self.parent().scalar_multiple(scalar, self)

    class ParentMethods:
        # The ring acting on this module: the datum this level introduces.
        _preamble_base_ring = None
        _preamble_native_module_presentation = None

        def _native_module_presentation(self):
            r"""The supplied native additive-group realization, or no such realization.

            Protected Modules constructor contract under OWN-05. The module
            constructor installs it through the retaining dispatcher; permitted
            readers are this module owner's scalar/coordinate construction and
            the algebra constructor deciding whether it is retaining the ring's
            original multiplication. It records the complete defining action,
            never a category claim or a deferred reconstruction. No engine
            handle crosses this contract.
            """
            # During deferred algebra construction this owner datum is queried
            # before the module category has been added to the parent's Sage
            # class. In that interval the category's class default is not in
            # the MRO; absence means the same initial state as its declared
            # default, not an unconstructed mathematical module.
            return getattr(self, "_preamble_native_module_presentation", None)

        def _retain_native_module_presentation(self, presentation):
            r"""Install the native module datum at its Modules owner.

            Protected Modules constructor contract under OWN-05. The sole
            caller is the native ring-module presentation constructor.
            Installation is one-shot and may not replace the module's selected
            scalar ring. Consumers read the retained owned constructor datum
            through the owner query rather than opening this object's storage.
            """
            assert (
                getattr(self, "_preamble_native_module_presentation", None) is None
            ), (
                f"the module structure of {self} over {self.base_ring()} is already defined and cannot be defined again"
            )
            assert self.base_ring() is presentation.base_ring(), (
                f"{self} is a module over {self.base_ring()} and cannot be given a scalar action of "
                f"{presentation.base_ring()}"
            )
            self._preamble_native_module_presentation = presentation

        def __init__(
            self,
            base_ring,
            module_generating_set=None,
            module_generator_function=None,
            framing_source=None,
            **rest,
        ) -> None:
            ring = _owned_ring(base_ring)
            self._preamble_base_ring = ring
            super().__init__(base=ring, **rest)
            match module_generating_set:
                case None:
                    pass
                case labels:
                    _fix_selected_module_resolution(
                        self,
                        ring,
                        labels,
                        module_generator_function,
                        None if framing_source is None else (lambda: framing_source),
                    )

        def __init_extra__(self) -> None:
            r"""Register the action of this module's ring on its own elements.

            A module is an abelian group together with a ring acting on it, so
            recording the ring is only half of what this level constructs; the
            action is the other half, and ``r*m`` is what it is called at a
            prompt.  Sage calls this hook from ``Parent.__init__`` for every
            parent of this category, whatever route constructed it, so one
            declaration here reaches a module built through the chain and a
            ring the preamble adopts alike, and neither has anything to state
            about its scalars afterwards.
            """
            _register_module_scalar_action(self)

        @object_level
        def Mono(self, codomain):
            r"""Return the declared injective linear maps into ``codomain``."""
            return Modules(self.base_ring()).Mono(self, codomain)

        @object_level
        def End(self):
            r"""Return ``End_R(M)``, the endomorphism ring of this module."""
            return Modules(self.base_ring()).End(self)

        def general_linear_group(self):
            r"""``GL(M) = Aut_R(M)``: the automorphism group of the underlying module, one object with ``Modules(R).Aut(M)``.

            For a lattice this is the group of the underlying module, of
            which ``O(L)`` is a subgroup; it is not ``L.Aut()``.
            """
            return self.module_category().Aut(self)

        @object_level
        def Aut(self):
            r"""Return ``Aut_R(M)``, the automorphisms of this module.

            The Mor packet gives every object its automorphisms, so a module
            reaches them the way a group and a lattice already do rather than
            through a class of its own.
            """
            return Modules(self.base_ring()).Aut(self)

        def module_category(self):
            return Modules(self.base_ring())

        def has_selected_module_resolution(self) -> bool:
            return self.has_selected_resolution(self.module_category())

        def selected_module_resolution(self):
            return self.selected_resolution(self.module_category())

        def module_generating_set(self):
            return self.selected_resolution_generating_set(self.module_category())

        def module_generator_morphism(self):
            return self.selected_module_resolution().generator_morphism()

        def module_generator(self, label):
            return self.selected_resolution_generator(self.module_category(), label)

        def module_generators(self):
            return self.selected_module_resolution().generators(
                name="Module generators"
            )

        def number_of_module_generators(self):
            return self.selected_module_resolution().generator_count()

        def sub_framing_morphism(self, codomain):
            r"""Return the free module functor applied to the inclusion of framings.

            An injection of framing sets is split, and the free functor is a
            left adjoint that carries the splitting, so this is a split
            monomorphism, and membership in its image and the lift are decided
            on labels: an element of ``codomain`` comes from this module
            exactly when it is supported on the smaller framing, and its
            preimage has the same coefficients.  The smaller framing may be
            infinite, as the degree-two piece of an algebra on countably many
            generators is, so no matrix of images is solved against.
            """
            match codomain.has_selected_module_resolution():
                case False:
                    raise TypeError(
                        f"the inclusion of the generators of {self} into {codomain} is not defined: "
                        f"{codomain} has no chosen module resolution"
                    )
                case True:
                    pass
            source_labels = self.module_generating_set()

            def preimage_on_labels(element):
                coordinates = codomain(element).to_vector()
                coefficients = coordinates.parent()._selected_module_coefficients(
                    coordinates
                )
                match conjunction(
                    coefficient == self.base_ring().zero()
                    for label, coefficient in coefficients.items()
                    if label not in source_labels
                ):
                    case False:
                        return None
                    case True:
                        return self.linear_combination(
                            {
                                label: coefficient
                                for label, coefficient in coefficients.items()
                                if label in source_labels
                            }
                        )
                    case _:
                        raise AssertionError(
                            "a framing preimage requires decided vanishing of coefficients outside its labels"
                        )

            return self.Mono(codomain)._from_constructed_embedding(
                codomain.module_generator,
                elementwise=False,
                lift=preimage_on_labels,
                lift_is_section=True,
            )

        def framing_source(self):
            r"""Return the free degree-zero term of the selected module resolution."""
            return self.selected_module_resolution().level(0)

        @cached_method
        def framing_morphism(self):
            r"""Return the selected degree-zero augmentation."""
            return self.selected_module_resolution().augmentation()

        def framing_object(self):
            r"""Return the selected module augmentation as an arrow object."""
            return self.module_category().ArrowCategory()(self.framing_morphism())

        def linear_combination(self, coefficients):
            r"""Return the linear combination of the selected module generators."""
            return self._linear_combination_from_generator_coefficients(coefficients)

        @RealizationHook
        def _linear_combination_from_generator_coefficients(self, coefficients):
            r"""Realize the selected augmentation on a finite coefficient mapping.

            Protected computation of ``Modules.linear_combination`` (OWN-05).
            That operation is the only caller. Keys are the selected generator
            labels, values are scalars, and the result belongs to this module
            and equals their linear combination. A realization may fuse this
            evaluation; the general formula needs no extra hypotheses.
            """
            return sum(
                (
                    self.scalar_multiple(
                        coefficient,
                        self.module_generator(label),
                    )
                    for label, coefficient in coefficients.items()
                ),
                self.zero(),
            )

        def inject_variables(self, scope=None, verbose=True):
            assert scope is not None, (
                f"the generators of {self} can be defined as variables only in a given namespace, but none was given"
            )
            assert self.module_generating_set().cardinality().is_finite(), (
                f"the generators of {self} can be defined as variables only when there are finitely many, "
                f"but its generating set has cardinality {self.module_generating_set().cardinality()}"
            )
            names = tuple(self.variable_names())
            generators = tuple(self.module_generators())
            match len(names) == len(generators):
                case False:
                    raise ValueError(
                        f"{self} has {len(generators)} generators but {len(names)} variable names {names}"
                    )
                case True:
                    pass
            match verbose:
                case True:
                    print(f"Defining {', '.join(names)}")
                case False:
                    pass
            scope.update(zip(names, generators, strict=True))

        def tensor_product(self, other):
            r"""Return this module tensored with ``other`` over the common base ring."""
            return self.module_category().tensor_product((self, other))

        def __add__(self, other):
            r"""Return the direct sum ``self ⊕ other``, the biproduct of the two summands.

            The two-index case of ``Modules(R).biproduct`` over the common
            base ring ``R``.
            """
            modules = Modules(self.base_ring())
            match other in modules:
                case True:
                    return modules.biproduct((self, other))
                case False:
                    return NotImplemented

        def function_module(self, domain):
            r"""Return ``B^A``: the ``R``-module of all maps ``domain -> self``, pointwise.

            Its underlying set is ``Sets().Mor(domain, self)``, so a map is
            constructed by that Mor's element constructor (a callable, or a
            formula binding its own variable), and ``(f + g)(a) = f(a) + g(a)``,
            ``(r f)(a) = r f(a)``.  This is Mathlib's ``Function.module``
            (``Mathlib/Algebra/Module/Pi.lean:52``), the product
            ``prod_{a in A} B`` in ``Mod_R``; its law is the one the module
            product uses (``_pointwise_module_operations``).  A space of maps
            ``A -> B`` cut out by a condition is a submodule of it
            (``CON-17``): ``self.function_module(A).condition_submodule(P)``.
            """
            from sage_extensions.categories.modules.general_modules import (
                _function_module,
            )

            return _function_module(self, domain)

        def condition_submodule(self, predicate):
            r"""Return the submodule ``{x in M : P(x)}`` of this module, with its inclusion.

            ``predicate`` answers ``True``, ``False`` or a proposition on
            elements of ``M``.  Its extension contains zero and is closed
            under addition and scalar multiplication: that is the caller's
            hypothesis, stated by asking for this construction, and not
            checked.  The result is an object of ``ModuleSubobjects(R)`` built
            on the condition set of ``P`` in ``M`` (``Sets().condition_set``),
            with ``M``'s operations; its inclusion is the inclusion of that
            set.  Constructing an element does not ask ``P`` (``OWN-22``):
            ``x in N`` asks it, and an element's
            ``validate_condition_membership`` raises when ``P(x)`` is false.
            """
            from sage_extensions.categories.modules.general_modules import (
                _condition_submodule,
            )

            return _condition_submodule(self, predicate)

        def pairings_with(self, right_module, value_module):
            r"""Return bilinear pairings ``self x right_module -> value_module``."""
            from sage_extensions.categories.forms.forms import _pairings

            return _pairings(self, right_module, value_module)

        def bilinear_forms(self, value_module):
            r"""Return the module Hom of bilinear maps ``self x self -> value_module``."""
            return self.bilinear_hom_space(value_module)

        def bilinear_hom_space(self, value_module):
            r"""Return ``Hom_R(self \otimes_R self, W)``, with ``W`` an R-module.

            The Cat-owned Mor constructor, not a form-specific fallback,
            checks that the tensor product and ``W`` are both R-modules.
            """
            from sage_extensions.categories.forms.forms import _bilinear_forms

            return _bilinear_forms(self, value_module)

        def quadratic_forms(self, value_module):
            r"""Return quadratic forms ``self -> value_module`` through ``Gamma^2(self)``."""
            from sage_extensions.categories.forms.forms import _quadratic_forms

            return _quadratic_forms(self, value_module)

        def quadratic_map(self, value_module, function):
            r"""Return the quadratic map classified by ``function``."""
            from sage_extensions.categories.forms.forms import _quadratic_map

            return _quadratic_map(self, value_module, function)

        def quadratic_map_from_morphism(self, morphism):
            r"""Recover the quadratic map classified by a map out of ``Gamma^2(self)``."""
            from sage_extensions.categories.forms.forms import (
                _quadratic_map_from_morphism,
            )

            return _quadratic_map_from_morphism(self, morphism)

        def equip_bilinear_form(self, form):
            r"""Equip this module with ``b`` already constructed in its bilinear Hom.

            A tensor or a callable is *not* a form: both are input data for
            ``self.bilinear_hom_space(W)``, which constructs the morphism.
            The formed-module constructor accepts only that morphism.
            """
            from sage_extensions.categories.modules.framed.formed.form_modules import (
                _bilinear_form,
            )

            return _bilinear_form(self, form)

        def equip_quadratic_form(self, value_module, datum):
            r"""Return this module construction equipped with the selected quadratic form."""
            from sage_extensions.categories.modules.framed.formed.form_modules import (
                _quadratic_form,
            )

            return _quadratic_form(self, value_module, datum)

        def tensor_algebra(self):
            r"""Return the tensor algebra ``T_R(self)``."""
            return self.module_category().tensor_algebra()(self)

        def mixed_tensor_algebra(self):
            r"""Return ``T(self) tensor T(self^*)`` with finite bidegree support."""
            from sage_extensions.tensors.tensor import _mixed_tensor_algebra

            return _mixed_tensor_algebra(self)

        def symmetric_algebra(self):
            r"""Return the symmetric algebra ``Sym_R(self)``."""
            return self.module_category().symmetric_algebra()(self)

        def exterior_algebra(self):
            r"""Return the exterior algebra ``Lambda_R(self)``."""
            return self.module_category().exterior_algebra()(self)

        def divided_power_algebra(self):
            r"""Return the divided-power algebra ``Gamma_R(self)``."""
            return self.module_category().divided_power_algebra()(self)

        def tensor_to_symmetric(self):
            r"""Return the canonical quotient ``T(self) -> Sym(self)``."""
            from sage_extensions.categories.algebras.comparison_maps import (
                _tensor_to_symmetric,
            )

            return _tensor_to_symmetric(self)

        def tensor_to_alternating(self):
            r"""Return the canonical quotient ``T(self) -> Lambda(self)``."""
            from sage_extensions.categories.algebras.comparison_maps import (
                _tensor_to_alternating,
            )

            return _tensor_to_alternating(self)

        def symmetric_to_divided(self):
            r"""Return the canonical comparison ``Sym(self) -> Gamma(self)``."""
            from sage_extensions.categories.algebras.comparison_maps import (
                _symmetric_to_divided,
            )

            return _symmetric_to_divided(self)

        def divided_to_symmetric(self):
            r"""Return ``Gamma(self) -> Sym(self)`` when the factorials are invertible."""
            from sage_extensions.categories.algebras.comparison_maps import (
                _divided_to_symmetric,
            )

            return _divided_to_symmetric(self)

        def connections(self):
            r"""Return the space of algebraic connections on this module."""
            from sage_extensions.categories.modules.connections import (
                _connections,
            )

            return _connections(self)

        def divided_square(self):
            r"""Return ``Gamma^2_R(self)``, the universal target for quadratic maps."""
            from sage_extensions.categories.modules.powers import _divided_square

            return _divided_square(self)

        def tensor_power(self, degree):
            r"""Return ``self^{tensor degree}``."""
            from sage_extensions.categories.modules.powers import _tensor_power

            return _tensor_power(self, degree)

        def symmetric_power(self, degree):
            r"""Return ``Sym^degree(self)``."""
            from sage_extensions.categories.modules.powers import _symmetric_power

            return _symmetric_power(self, degree)

        def exterior_power(self, degree):
            r"""Return ``Lambda^degree(self)``."""
            from sage_extensions.categories.modules.powers import _alternating_power

            return _alternating_power(self, degree)

        def divided_power_module(self, degree):
            r"""Return the divided-power module ``Gamma^degree(self)``."""
            from sage_extensions.categories.modules.powers import _divided_power

            return _divided_power(self, degree)

        def tensor_power_permutation(self, degree, positions):
            r"""Return the endomorphism permuting the factors of ``self^tensor degree``."""
            from sage_extensions.categories.modules.powers import (
                _tensor_power_permutation,
            )

            return _tensor_power_permutation(self, degree, positions)

        def divided_power_product(self, left_degree, left, right_degree, right):
            r"""Multiply homogeneous divided powers of ``self``."""
            from sage_extensions.categories.modules.powers import (
                _divided_power_product,
            )

            return _divided_power_product(self, left_degree, left, right_degree, right)

        def exterior_power_product(self, left_degree, left, right_degree, right):
            r"""Multiply homogeneous exterior powers of ``self`` by the wedge product."""
            from sage_extensions.categories.modules.powers import (
                _alternating_power_product,
            )

            return _alternating_power_product(
                self, left_degree, left, right_degree, right
            )

        def divided_power_element(self, degree, element):
            r"""Return ``gamma_degree(element)`` in ``Gamma^degree(self)``."""
            from sage_extensions.categories.modules.powers import (
                _divided_power_element,
            )

            return _divided_power_element(self, degree, element)

        def divided_power_invariant_inclusion(self, degree):
            r"""Return ``Gamma^degree(self) -> self^tensor degree`` by orbit sum."""
            from sage_extensions.categories.modules.powers import (
                _divided_power_invariant_inclusion,
            )

            return _divided_power_invariant_inclusion(self, degree)

        def tensor_power_polarization(self, degree):
            r"""Return ``self^tensor degree -> Gamma^degree(self)`` by polarization."""
            from sage_extensions.categories.modules.powers import (
                _tensor_power_polarization,
            )

            return _tensor_power_polarization(self, degree)

        def divided_square_invariant_inclusion(self):
            r"""Return the degree-two divided-power invariant inclusion."""
            return self.divided_power_invariant_inclusion(2)

        def tensor_square_polarization(self):
            r"""Return the degree-two tensor polarization map."""
            return self.tensor_power_polarization(2)

        def _module_mor_class(self):
            r"""Return the canonical fixed Mor for maps out of this module type."""

            return ModuleMor

        def base_ring(self):
            r"""Return the ring acting on this module.

            A module constructed through this level stores its ring; a parent
            refined into ``Modules(R)`` without running this level reads the
            ring it was built over.
            """
            match self._preamble_base_ring:
                case None:
                    return _owned_ring(self.base())
                case ring:
                    return ring

        def is_module(self) -> bool:
            return True

        def _freeness_decision(self):
            return AtomicProposition("is_free", self)

        def is_free(self):
            match self:
                case _ if self in Modules(self.base_ring()).Free():
                    return True
                case _:
                    return self._freeness_decision()

        def _finite_generation_decision(self):
            return AtomicProposition("is_finitely_generated", self)

        def is_finitely_generated(self):
            match self:
                case _ if self in Modules(self.base_ring()).FinitelyGenerated():
                    return True
                case _:
                    return self._finite_generation_decision()

        def _finite_presentation_decision(self):
            return AtomicProposition("is_finitely_presented", self)

        def is_finitely_presented(self):
            match self:
                case _ if self in Modules(self.base_ring()).FinitelyPresented():
                    return True
                case _:
                    return self._finite_presentation_decision()

        def projectivity_decision(self):
            r"""Decide projectivity from this module's data, never from its placement.

            ``Modules(R).Projective()`` certifies its objects by this
            statement, so a placement there is checked against it.  A module
            whose data does not decide projectivity answers the proposition
            ``is_projective(M)``.
            """
            presentation = Modules.ParentMethods._native_module_presentation(self)
            if presentation is not None:
                basis = presentation.module_basis()
                if basis is not None and basis.is_basis():
                    # A retained free basis is a construction witness for
                    # projectivity, independently of whether the projective
                    # category has already been added to this parent's class.
                    return True
            return AtomicProposition("is_projective", self)

        def is_projective(self):
            match self:
                case _ if self in Modules(self.base_ring()).Projective():
                    return True
                case _:
                    return self.projectivity_decision()

        def _torsion_decision(self):
            return AtomicProposition("is_torsion", self)

        def is_torsion(self):
            match self:
                case _ if self in Modules(self.base_ring()).Torsion():
                    return True
                case _:
                    return self._torsion_decision()

        def _torsion_freeness_decision(self):
            return AtomicProposition("is_torsion_free", self)

        def is_torsion_free(self):
            return self._torsion_freeness_decision()

        def is_framed_module(self) -> bool:
            r"""Whether this module was constructed with chosen generators, a degree-zero resolution."""
            return self.has_selected_module_resolution()

        def _finiteness_decision(self):
            return AtomicProposition("is_finite", self)

        def is_flat(self) -> bool | Predicate:
            r"""Decide flatness in the field and PID regimes.

            Every module over a field is flat.  Over a PID, flatness is
            equivalent to torsion-freeness (Stacks Project, Tag 0AUW), so the
            torsion-freeness decision of the module decides it.
            """

            ring = self.base_ring()
            match ring:
                case _ if ring in OwnedFields():
                    return True
                case _ if ring in PrincipalIdealDomains():
                    return self.is_torsion_free()
                case _:
                    raise AssertionError(
                        f"flatness is decided over a field or a principal ideal domain, and {ring} is neither"
                    )

        @RealizationHook
        def _rank_decision(self):
            r"""Protected rank of this module when its data does not reach the general case.

            ``module_rank`` is the only caller.  A realization or a more
            specific category supplies the answer as a cardinal; ``None``
            here means none is supplied.
            """
            return

        def module_rank(self):
            r"""Return ``rank_R(M)`` (Mathlib ``Module.rank``), a cardinal.

            Over a field ``k`` the rank is the dimension: the cardinality of a
            basis.  A basis of cardinality ``n`` identifies ``M`` with ``k^n``
            as a set, so when ``k`` and ``M`` are finite, ``|M| = |k|^n`` and
            ``n`` is the exact logarithm of ``|M|`` to the base ``|k|``.  A
            more specific category with a chosen basis or presentation answers
            from that datum; any other module answers through
            ``_rank_decision``.
            """
            ring = self.base_ring()
            match self:
                case _ if (
                    ring in OwnedFields()
                    and ring.is_finite() is True
                    and self.is_finite() is True
                ):
                    return cardinal(
                        SageZZ(int(self.cardinality())).exact_log(
                            int(ring.cardinality())
                        )
                    )
                case _:
                    decided = self._rank_decision()
                    assert decided is not None, (
                        f"the rank of {self} over {ring} is computed over a finite field for a finite "
                        f"module, or from a chosen basis or presentation, and {self} supplies none of these"
                    )
                    return decided

        def base_change(self, ring_map):
            r"""Return ``f_! M = S tensor_R M`` along ``ring_map = f : R -> S``.

            This is extension of scalars (lean-categories FOUNDATIONS,
            Definition 83.2): the tensor product over ``R`` of ``S``, read as
            an ``R``-module along ``f``, with ``M``, on which ``S`` acts
            through the left factor, ``s (t tensor m) = (s t) tensor m``.
            Multiplication by ``s`` on ``S`` is the ``S``-linear endomorphism
            ``mu_s`` of the regular module when ``S`` is commutative, and it
            acts on the left factor as ``Res_f(mu_s)``.  The tensor product is
            the generators-and-relations quotient, which is defined for every
            pair of modules.  A category whose objects carry a chosen basis or
            presentation computes the same module on that datum and is the
            more specific owner.
            """
            from sage_extensions.categories.modules.general_modules import (
                GeneralModules,
            )
            from sage_extensions.categories.modules.tensor_quotients import (
                _tensor_quotient,
            )

            ring = self.base_ring()
            assert ring_map.domain() is ring, (
                f"cannot extend the scalars of {self} along {ring_map}: the ring morphism must start at "
                f"the base ring {ring}, but it starts at {ring_map.domain()}"
            )
            scalars = _owned_ring(ring_map.codomain())
            assert scalars in OwnedRings().Commutative(), (
                f"the extension of scalars of {self} along {ring_map} is constructed here for a commutative "
                f"ring of scalars, where multiplication by s is S-linear, and {scalars} is in {scalars.category()}"
            )
            regular = scalars.regular_module()
            restriction = Modules(scalars).restriction_of_scalars(ring_map)
            scalars_over_ring = restriction(regular)
            tensor = _tensor_quotient(
                _finite_factor_family(
                    (scalars_over_ring, self), name="Scalar-extension factors"
                )
            )
            classes = tensor.underlying_set()
            endomorphisms = regular.module_category().Mor(regular, regular)

            def scalar_action(scalar, value):
                multiplication = restriction(
                    endomorphisms(
                        {
                            label: regular.scalar_multiple(
                                scalar, regular.module_generator(label)
                            )
                            for label in regular.module_generating_set()
                        }
                    )
                )
                return classes.evaluate(
                    value,
                    tensor,
                    lambda left, right: tensor.pure_tensor(multiplication(left), right),
                ).underlying_element()

            return GeneralModules(scalars).from_operations(
                classes,
                addition=classes.add,
                zero=classes.zero(),
                negation=lambda value: classes.scale(-ring.one(), value),
                scalar_action=scalar_action,
            )

        def vector_space(self):
            r"""Return ``M tensor_R Frac(R)`` along the canonical fraction-field map."""
            return self.base_change(self.base_ring().fraction_field_map())

        def _represented_fiber_dimension(self, point):
            _ = point
            return NotImplemented

        def _free_biproduct_over(
            self,
            labels,
            factors,
            *,
            extra_categories=(),
            extra_construction_data=None,
        ):
            _ = (labels, factors, extra_categories, extra_construction_data)
            return NotImplemented

        def _presented_biproduct_over(
            self,
            labels,
            factors,
            *,
            extra_categories=(),
            extra_construction_data=None,
        ):
            _ = (labels, factors, extra_categories, extra_construction_data)
            return NotImplemented

        def _presented_module_from_relation_morphism(
            self,
            presentation,
            *,
            extra_categories=(),
            extra_construction_data=None,
        ):
            _ = (presentation, extra_categories, extra_construction_data)
            return NotImplemented

        def _selected_relation_morphism(self):
            return None

        def _selected_module_coefficients(self, element):
            r"""Read the coefficients of the chosen preimage of ``element`` under the framing.

            Protected contract of ``Modules(R)``. Permitted callers are
            :meth:`_framing_lift` and module coordinate-transport or morphism
            evaluation constructors already holding an owned framing vector.
            The localized-module equality predicate also reads the stored
            coordinates of an actual free source vector to test whether its
            finitely many coefficients vanish after localization.
            A localized module, quotient or restriction of scalars implements
            it at the representation it constructs. The result is a finite
            label-to-owned-coefficient family keyed by
            ``module_generating_set()``; coefficients outside that family are
            zero. Its keys contain the support, and stored coefficients need
            not be proved nonzero. Such a family can be summed and transported
            without deciding its exact support. Algorithms requiring nonzero
            coordinates must establish that predicate separately.
            """
            return element._coefficient_data()

        def _framing_lift(self, element):
            r"""The chosen preimage of ``element`` under the framing ``F_R(S) ->> M``.

            Protected contract of ``Modules(R)``.  Its callers are
            ``FramingMorphism.lift``, ``ModuleMorphism.lift`` along the framing, ``FramedFreeModules`` elements'
            ``to_vector``, and ``ModuleMorphism._call_``, which
            evaluates ``f(v) = sum_s a(s) f(m_s)`` on this preimage ``a``:
            evaluation must not construct the framing morphism, whose Mor set
            evaluates morphisms while it is built.  On a basis the preimage is
            unique and it is the coordinate vector of ``element``; on a quotient
            it is the preimage the construction chose.
            """
            native = self._native_module_presentation()
            if native is not None and native.module_basis() is not None:
                selected = native.coefficients(element)
            else:
                match self:
                    case _ if self in OwnedOrders():
                        # The selected integral basis of an order: the engine
                        # reads coordinates in that basis, one per framing label.
                        labels = self.module_generating_set()
                        engine = _engine_ring(self)
                        backend_element = _engine_element(self, element)
                        coordinates = (
                            (SageZZ(backend_element),)
                            if engine is SageZZ
                            else tuple(engine.coordinates(backend_element))
                        )
                        base = self.base_ring()
                        base_engine = _engine_ring(base)
                        selected = {
                            label: _owned_engine_element(base, base_engine(coefficient))
                            for label, coefficient in zip(
                                labels, coordinates, strict=True
                            )
                            if coefficient != 0
                        }
                    case _:
                        selected = self._selected_module_coefficients(element)
            source = self.framing_source()
            match selected:
                case _ if element_parent(selected) is source:
                    return selected
                case IndexedFamily():
                    return source(
                        {label: selected[label] for label in selected.index_set()}
                    )
                case _:
                    return source(dict(selected))

        def _represented_kernel_of_morphism(self, morphism):
            _ = morphism
            return NotImplemented

        def _represented_cokernel_of_morphism(self, morphism):
            _ = morphism
            return NotImplemented

        def _represented_annihilator_ideal(self):
            r"""An exact scalar-action kernel, or ``NotImplemented``.

            The public module annihilator reads this result. The localized
            module owner also reads it for a finitely generated source,
            whose annihilator commutes with localization.
            """
            return NotImplemented

        def _scalar_restriction_data(self, ring_map):
            r"""A represented field dimension and optional basis along ``ring_map``.

            Protected module-owner contract. The restriction constructor and
            ``finite_length_at_closed_point`` are the callers; a
            selected-presentation owner may return
            ``(dimension, basis)`` for the actual scalar action. ``dimension``
            is an owned cardinal, and ``basis`` is a ``_NativeModuleBasis``
            whose images are elements of this module, or ``None`` when no
            finite basis is supplied. A return value of ``None`` means that
            this owner has no represented calculation along the given map;
            it never means that a proved infinite dimension may be discarded.
            """
            _ = ring_map

        def _represented_vector_space_dimension(self):
            r"""An owned dimension, or ``NotImplemented`` when not represented.

            ``VectorSpaces.dimension`` and the selected-presentation rank,
            zero predicate and cardinality suppliers read this value. The
            scalar restriction constructor also reads it for a field-to-field
            tower with a selected finite scalar basis. A known dimension
            does not supply a finite framing or require an enumeration.
            """
            return NotImplemented

        def _represented_vector_space_basis_generator_labels(self):
            return NotImplemented

        def _owned_scalar_multiple(self, scalar, element):
            r"""Apply the owned scalar action to an owned module element."""
            native = self._native_module_presentation()
            if native is not None:
                return native.scalar_multiple(scalar, element)
            if element not in self:
                raise TypeError(f"{element} is not an element of {self}")
            scalar = self.base_ring()(scalar)
            return element._lmul_(scalar)

        def underlying_additive_group(self):
            r"""Return the additive group on which this module's scalars act."""
            return self

        def _underlying_additive_element(self, element):
            r"""Element map used by scalar evaluation and the forgetful functor.

            Module representations with a distinct underlying additive group
            implement this protected conversion together with
            ``underlying_additive_group``.  An ``R[G]``-module built on the
            data of ``M`` has the underlying additive group of ``M``, and its
            :meth:`_element_of_unformed_module` reads an element there.
            """
            return self(element)

        def unformed_module(self):
            r"""Return the module this module is built on.

            A form or a group action stated on an ``R``-module ``M`` builds a
            module on the data of ``M`` that retains ``M`` (``CON-16``); the
            level stating that structure answers ``M`` here.  A module on
            which no structure was stated is built on its own data.
            """
            return self

        def _element_of_unformed_module(self, element):
            r"""Read an element of this module in :meth:`unformed_module`.

            Protected contract of ``Modules(R)``.  Every level whose
            constructor retains the module its structure was stated on
            implements it together with :meth:`_element_from_unformed_module`;
            its one caller is :meth:`_element_on_the_same_data`.  It takes an
            element of this module and returns the element of
            ``unformed_module()`` on the same data.
            """
            assert self.unformed_module() is self, (
                f"{self} is built on the module {self.unformed_module()}, but no identification of its "
                f"elements with elements of {self.unformed_module()} is defined"
            )
            return element

        def _element_from_unformed_module(self, element):
            r"""Read an element of :meth:`unformed_module` in this module.

            The inverse half of :meth:`_element_of_unformed_module`, with the
            same owner, implementers and caller.
            """
            assert self.unformed_module() is self, (
                f"{self} is built on the module {self.unformed_module()}, but no identification of "
                f"elements of {self.unformed_module()} with elements of {self} is defined"
            )
            return element

        def _with_structure(
            self,
            categories: tuple[Category, ...],
            construction_data: dict[str, ConstructionData],
            *,
            engine: type | None = None,
        ) -> ObjectOfCategory:
            r"""The protected construction contract of ``Objects``, supplied by the module owner.

            Contract, roles and the reason no public operation does this: see
            ``Objects.ParentMethods._with_structure`` (``OWN-05``).  The module
            owner constructs on this exact module's data (``OWN-16``) and
            keeps the structure this module already adds.  It selects its own
            realization, so it takes no further computation class.
            """
            assert engine is None, (
                f"cannot construct {self} again with the computation class {engine}: the module "
                "owner selects the realization of a module with added structure"
            )
            added_categories, added_data = self._added_structure(construction_data)
            return self._module_with_structure(
                (*added_categories, *categories), added_data
            )

        def _module_with_structure(self, categories, construction_data):
            r"""Construct further structure on this exact module's data.

            The module owner, not the stronger algebra/form/action owner,
            selects its realization.  A realization with additional intrinsic
            data (for example a direct sum's pieces) supplies this operation.
            """
            match self:
                case _ if self in ModulesWithChosenFinitePresentation(self.base_ring()):
                    return self._same_presentation_module(
                        self.module_generating_set(),
                        _extra_categories=categories,
                        _extra_construction_data=construction_data,
                    )
                case _ if _represented_framed_free(self):
                    from sage_extensions.categories.modules.framed.framed_free_modules import (
                        _fresh_free_module_on,
                    )

                    return _fresh_free_module_on(
                        self.base_ring(),
                        self.module_generating_set(),
                        _extra_categories=categories,
                        _extra_construction_data=construction_data,
                    )
                case _:
                    from sage_extensions.categories.modules.general_modules import (
                        GeneralModules,
                    )
                    from sage_extensions.owned_category import (
                        _object_of,
                        owned_category_join,
                    )

                    return _object_of(
                        owned_category_join(
                            (GeneralModules(self.base_ring()), *categories)
                        ),
                        base_ring=self.base_ring(),
                        rho=self.scalar_action(),
                        **construction_data,
                    )

        def _built_on_the_same_data(self, source) -> bool:
            r"""Decide whether ``source`` and this module are built on the data of one module.

            That holds when ``source`` retains this module, this module
            retains ``source``, or both retain the same module.  It is asked
            of the parent of an element, by its membership in ``Modules`` over
            its own ring and by the identity of the retained modules.
            """
            ring = source.base_ring()
            if ring not in OwnedRings() or source not in Modules(ring):
                return False
            retained = source.unformed_module()
            return (
                retained is self
                or self.unformed_module() is source
                or self.unformed_module() is retained
            )

        def _element_on_the_same_data(self, source, element):
            r"""Read an element of ``source`` as the element of this module on the same data.

            The dispatcher of the protected pair
            :meth:`_element_of_unformed_module` and
            :meth:`_element_from_unformed_module`, called from an element
            constructor once :meth:`_built_on_the_same_data` holds.  A module
            built on the data of ``M`` has no identification morphism back to
            ``M`` (``CON-16``), and Sage's registered conversions do not reach
            these parents: their ``__call__`` goes straight to
            ``_element_constructor_`` because the generic conversion map Sage
            would build (``Parent.discover_convert_map_from``,
            ``sage/structure/parent.pyx``) takes its Mor in
            ``SetsWithPartialMaps``, which owned parents are not in.  So the
            level that retains the module declares the reading, and the
            receiving constructor asks the element's parent for it.
            """
            if source.unformed_module() is self:
                return source._element_of_unformed_module(element)
            if self.unformed_module() is source:
                return self._element_from_unformed_module(element)
            assert source.unformed_module() is self.unformed_module(), (
                f"{element} of {source} cannot be read in {self}: {source} is built on "
                f"{source.unformed_module()} and {self} on {self.unformed_module()}, not on one common module"
            )
            return self._element_from_unformed_module(
                source._element_of_unformed_module(element)
            )

        def _ring_morphism_defining_module_action(
            self, endomorphisms, additive_group, scalar_multiple=None
        ):
            r"""Return ``rho_M : R -> End_Ab(U(M))``, ``r |-> (m |-> r m)``, from the scalar multiplication.

            A module whose datum is ``rho`` itself states it at its own level.
            """
            ring = self.base_ring()
            assert (
                endomorphisms.domain() is additive_group
                and endomorphisms.codomain() is additive_group
            ), (
                f"the scalar action of {self} can only be represented in "
                f"End({additive_group}), not {endomorphisms}"
            )
            if scalar_multiple is None:
                scalar_multiple = self._owned_scalar_multiple

            return ring.Mor(endomorphisms, category=OwnedRings())(
                lambda scalar: endomorphisms.elementwise(
                    lambda element: scalar_multiple(scalar, element),
                ),
            )

        def scalar_action(self):
            # A category construction hook can ask for the generic action
            # before a native ring's deferred module presentation is
            # installed.  Prefer the native datum once present, but normalize
            # its endpoint against the *current* End(U(M)): category
            # refinement may intern a different End parent after the action
            # was first retained.  The action's pointwise map remains the
            # defining datum; only its equivalent codomain parent is changed.
            native = self._native_module_presentation()
            # During native module construction, the selected presentation is
            # retained before Modules(R)'s category hooks are installed. In
            # that interval the parent may not yet have
            # underlying_additive_group(); the native datum already names the
            # exact additive-group object on which its action is defined.
            additive_group = (
                native.module()
                if native is not None
                else self.underlying_additive_group()
            )
            endomorphisms = AdditiveGroups().AdditiveCommutative().End(additive_group)
            # Use the module owner's one construction for rho_M in both cases.
            # During native construction U(M) is already specified by the
            # retained module presentation, even if its category refinement has
            # not yet installed underlying_additive_group() on the parent.
            # Preserve the native constructor's actual scalar operation when
            # supplied; reconstructing it through the generic module method
            # can silently replace a selected coefficient embedding. The
            # endpoint and ring-morphism construction remain common to both
            # native and generic modules.
            return Modules.ParentMethods._ring_morphism_defining_module_action(
                self,
                endomorphisms,
                additive_group,
                None if native is None else native.scalar_multiple,
            )

        def annihilator(self):
            r"""Return ``Ann_R(M)=ker(rho_M: R -> End_Ab(U(M)))``.

            Here ``rho_M(r)(m)=rm`` is additive, but not necessarily
            R-linear. Its kernel is precisely the two-sided ideal of scalars
            annihilating every point. The selected module representation
            computes this ideal without requiring a general algorithm for
            kernels of morphisms between represented rings.
            """
            represented = self._represented_annihilator_ideal()
            assert represented is not NotImplemented, (
                f"the annihilator Ann_R({self}) over {self.base_ring()} has no algorithm for a module in {self.category()}"
            )
            return represented

        @cached_method
        def zero_subobject(self):
            r"""The zero module with its unique monomorphism into this module.

            This construction does not require generators of the ambient
            module: its image is the singleton consisting of zero.
            """
            ring = self.base_ring()
            zero = ring._fresh_free_module_on(Sets.Δ[-1])

            def inclusion(source):
                arrow = (
                    Modules(ring)
                    .Mor(source, self)
                    ._from_constructed_element_map(lambda element: self.zero())
                )
                return (
                    Modules(ring)
                    .Mono(source, self)
                    ._subobject_inclusion(
                        arrow,
                        lift=lambda value: (
                            source.zero() if value == self.zero() else None
                        ),
                    )
                )

            return zero._module_with_structure(
                (ModuleSubobjects(ring),),
                {"subobject_ambient": self, "subobject_inclusion_factory": inclusion},
            )

        def scalar_multiple(self, scalar, element):
            r"""Return ``r*m = rho_M(r)(m)``."""
            underlying = self._underlying_additive_element(element)
            return self(self.scalar_action()(self.base_ring()(scalar))(underlying))

        def dual_module(self):
            r"""Return the linear dual ``Hom_R(M, R)`` over a commutative ring.

            For left modules over a noncommutative ring, ``Hom_R(M,R)`` is
            naturally a right module and therefore is not an object of this
            left-module category without a separate bimodule/opposite-ring
            construction.  The commutative case is the internal Mor into the
            regular rank-one module and inherits its selected presentation
            whenever the endpoint data represent one.
            """
            ring = self.base_ring()
            if ring not in OwnedRings().Commutative():
                raise TypeError(
                    f"the dual module Hom_R({self}, R) is a left module only over a commutative ring, "
                    f"and R = {ring} is not known to be commutative"
                )
            return self.module_category().Mor(self, ring.regular_module())

        @cached_method
        def projectivization(self):
            r"""Return ``P(M) = Proj_R(Sym_R(M)) -> Spec R``, Grothendieck's projectivization.

            The points of ``P(M)`` with values in an ``R``-algebra ``T`` are the
            invertible quotients of ``M tensor_R T`` (EGA II, 4.1.1 and 4.2.3), so a
            ``k``-point of ``P(V)`` over a field ``k`` is a one-dimensional quotient of
            ``V``, equivalently a hyperplane of ``V`` or a line of the dual ``V^*``.
            For ``V`` free of rank ``n+1`` this is ``P^n_k``, whose homogeneous
            coordinates are a basis of ``V`` itself, since ``Sym(V) = k[x_0, ..., x_n]``.

            ``P(M)`` is the projectivization of the quasi-coherent sheaf ``M~`` on
            ``Spec R``, so it is computed by that sheaf's ``projectivization()``.
            """
            ring = self.base_ring()
            assert ring in OwnedRings().Commutative(), (
                f"P({self}) = Proj Sym(M) needs Spec R, which exists only for a commutative ring, and "
                f"R = {ring} is not known to be commutative"
            )
            from sage_extensions.categories.schemes.schemes import Schemes

            return (
                Schemes(ring)
                .base_scheme()
                .associated_module_sheaf(self)
                .projectivization()
            )

        @cached_method
        def restrict_scalars(self, ring_map):
            r"""Read this module over the domain of ``ring_map``."""
            return _restricted_scalars_view(self, ring_map)

        def twist_scalar_action(self, ring_endomorphism):
            r"""Twist this module's scalar action along an endomorphism ``R -> R``.

            This is restriction of scalars along an endomorphism of the scalar
            ring; it is unrelated to ``L.twist(a)``, which rescales a lattice
            form while leaving its scalar action unchanged.
            """
            ring = self.base_ring()
            if (
                ring_endomorphism.domain() is not ring
                or ring_endomorphism.codomain() is not ring
            ):
                raise ValueError(
                    f"{ring_endomorphism} cannot twist the scalar action of {self}: it must be an endomorphism of "
                    f"{ring}, but it is a map {ring_endomorphism.domain()} -> {ring_endomorphism.codomain()}"
                )
            return self.restrict_scalars(ring_endomorphism)

        def localize(self, *datum):
            r"""Return ``S^{-1}M`` by scalar extension to ``S^{-1}R``.

            ``datum`` may be a represented localization ring, a represented
            submonoid ``S <= (R,*)``, or the finite generators used by the
            ring-localization convenience API.
            """
            ring = self.base_ring()
            if len(datum) == 1 and datum[0] in LocalizationRings():
                localization_ring = datum[0]
                if localization_ring.localization_source() is not ring:
                    raise ValueError(
                        f"{self} cannot be localized along {localization_ring}: it is a localization of "
                        f"{localization_ring.localization_source()}, not of the base ring {ring}"
                    )
            else:
                localization_ring = ring.localization(*datum)
            return localization_ring.localize_module(self)

        localization = localize

        def localize_at_prime(self, prime):
            r"""Return the localized module ``M_p`` at a represented prime."""
            ring = self.base_ring()
            if self is ring:
                return ring.localize_at_prime(prime)
            localization_ring = ring.spectrum()(prime).local_ring()
            return self.localize(localization_ring)

        localization_at_prime = localize_at_prime

    class FinitelyGenerated(CategoryWithAxiom):
        r"""Modules admitting a finite generating set."""

        @cached_method
        def resolution_category(self):
            r"""Finite-free degree-zero resolutions whose target image is this property."""
            from sage_extensions.categories.modules.resolutions import (
                finitely_generated_resolution_category,
            )

            return finitely_generated_resolution_category(self.base_ring())

        @cached_method
        def resolution_classifier(self):
            r"""The target projection from finite-free degree-zero resolution data."""
            return self.resolution_category().target_functor()

        def an_object(self):
            r"""The free module of rank one."""
            return self.base_ring().free_module(1)

        class ParentMethods:
            @cached_method
            def fiber(self, point):
                r"""Return ``M(p)=M tensor_R kappa(p)`` at ``p in Spec(R)``."""
                ring = self.base_ring()
                if point.parent().ring() is not ring:
                    raise ValueError(
                        f"the fibre of {self} at {point} is not defined: {point} must be a point of "
                        f"Spec({ring}), but it is a point of Spec({point.parent().ring()})"
                    )
                localized = self.localize_at_prime(point)
                fiber = localized.base_change(point.local_ring().residue_map())
                residue = point.residue_field()
                assert fiber in VectorSpaces(residue), (
                    f"the fibre {fiber} of {self} at {point} is not a vector space over the residue field {residue}"
                )
                return fiber

            def fiber_dimension(self, point):
                r"""Return ``dim_{kappa(p)} M(p)`` when the finite fiber is represented."""
                return self.fiber(point).dimension()

            def rank_at(self, point):
                r"""Return the local fiber rank ``dim_{kappa(p)} M(p)``."""
                return self.fiber_dimension(point)

            def rank_function(self):
                r"""Return ``r_M : Spec(R) -> NN``, ``p |-> dim_{kappa(p)} M(p)``.

                A module that is not locally free has no rank; it has a rank at
                each point, and those values vary.  So the rank of a finitely
                generated module is a function on the spectrum, and this returns
                that function as a morphism of sets: it composes with maps of
                spectra, restricts to a subset, and is the object whose fibres are
                the rank strata, rather than a number a caller recomputes at every
                point.

                This is a different invariant from the generic rank, which is one
                value of it, and from the local free rank of a finite projective
                module, which is this function where it is locally constant.
                """
                return Sets().Mor(self.base_ring().spectrum(), NN)(self.rank_at)

            def local_number_of_generators(self, point):
                r"""Return the minimal number of generators of ``M_p`` by Nakayama."""
                return self.localize_at_prime(point).minimal_number_of_generators()

            def local_minimal_generators(self, point):
                r"""Return a selected minimal generating set of ``M_p`` when represented."""
                return self.localize_at_prime(point).minimal_module_generators()

            def residue_module(self):
                r"""Return ``M/mM = M tensor_R k`` for a represented local base ring."""

                ring = self.base_ring()
                if ring not in LocalRings():
                    raise TypeError(
                        f"the residue module M/mM of {self} is not defined: its base ring {ring} is not known to be local"
                    )
                residue = ring.residue_field()
                module = self.base_change(ring.residue_map())
                if module not in VectorSpaces(residue):
                    raise TypeError(
                        f"the residue module {module} of {self} is not a vector space over the residue field {residue}"
                    )
                return module

            def minimal_number_of_generators(self):
                r"""Return ``dim_k(M/mM)`` for a finite module over a local ring."""

                ring = self.base_ring()
                if ring not in LocalRings():
                    raise TypeError(
                        f"the minimal number of generators of {self} is computed by Nakayama's lemma only over "
                        f"a local ring, and {ring} is not known to be local"
                    )
                return self.residue_module().dimension()

            def generic_rank(self):
                r"""Return ``dim_K(M tensor_R K)`` for an integral-domain base ``R``."""

                ring = self.base_ring()
                if ring not in IntegralDomains():
                    raise TypeError(
                        f"the generic rank of {self} is not defined: its base ring {ring} is not known to be an integral domain"
                    )
                return self.fiber_dimension(ring.spectrum().generic_point())

            def _torsion_decision(self) -> bool:
                r"""Return whether ``K tensor_R M = 0`` over an integral domain.

                The generic fibre is a vector space over ``K``, so it vanishes
                exactly when its dimension does.  A free module of positive rank is
                therefore not torsion, whatever its relations look like.
                """
                return self.generic_rank() == 0

    class FinitelyPresented(CategoryWithAxiom):
        r"""Modules admitting a finite presentation."""

        @cached_method
        def resolution_category(self):
            r"""Finite-free degree-one partial resolutions whose target image is this property."""
            from sage_extensions.categories.modules.resolutions import (
                finitely_presented_resolution_category,
            )

            return finitely_presented_resolution_category(self.base_ring())

        @cached_method
        def resolution_classifier(self):
            r"""The target projection from finite-free degree-one resolution data."""
            return self.resolution_category().target_functor()

        def an_object(self):
            r"""The free module of rank one, presented by no relations."""
            return self.base_ring().free_module(1)

        def extra_super_categories(self):
            r"""A finitely presented module is finitely generated over the same ring.

            sage: C = Modules(ZZ)
            sage: C.FinitelyPresented().extra_super_categories()[0] is C.FinitelyGenerated()
            True
            sage: X = ZZ.free_module(1)
            sage: X in C.FinitelyPresented() and X in C.FinitelyGenerated()
            True
            """
            return [self.base_category().FinitelyGenerated()]

        def biproduct_bifunctor(self):
            r"""Return the biproduct bifunctor on finitely presented modules."""
            from sage_extensions.categories.functors.linear_constructions import (
                _biproduct_bifunctor,
            )

            return _biproduct_bifunctor(self.base_ring())

        def cokernel_arrow_functor(self):
            r"""Return the cokernel functor on this module arrow category."""
            from sage_extensions.categories.functors.linear_constructions import (
                _cokernel_arrow_functor,
            )

            return _cokernel_arrow_functor(self.base_ring())

        class ParentMethods:
            def tor(self, other, degree=0):
                r"""Return ``Tor_degree(self, other)`` from the selected free resolution."""
                from sage_extensions.categories.modules.derived_functors import _tor

                return _tor(self, other, degree=degree)

            def ext(self, other, degree=0):
                r"""Return ``Ext^degree(self, other)`` from the selected free resolution."""
                from sage_extensions.categories.modules.derived_functors import _ext

                return _ext(self, other, degree=degree)

            def projective_dimension(self):
                r"""Return the projective dimension in the regimes where it is decided exactly.

                A projective module has dimension zero.  Over a principal ideal
                domain every submodule of a free module is free, so every finitely
                presented module has projective dimension at most one; a
                nonprojective one therefore has dimension exactly one.  No finite
                bound is inferred over a more general ring.
                """
                if self.is_projective():
                    return NN(0)
                assert self.base_ring() in PrincipalIdealDomains(), (
                    f"the projective dimension of {self} is decided only for projective modules or over a PID; "
                    f"{self} is not projective and {self.base_ring()} is not known to be a PID"
                )
                return NN(1)

        class Torsion(CategoryWithAxiom):
            r"""Finitely presented torsion modules over a PID."""

            def an_object(self):
                r"""The discriminant group of U."""
                from sage_extensions.categories.lattices import Lattices

                return Lattices(self.base_ring())("U").discriminant_group()

            def _call_(self, presentation):
                match self.base_ring() in PrincipalIdealDomains():
                    case True:
                        pass
                    case False:
                        raise TypeError(
                            f"a finitely presented torsion module over {self.base_ring()} is constructed only over a PID, "
                            f"and {self.base_ring()} is not known to be one"
                        )
                match presentation.codomain().base_ring() is self.base_ring():
                    case True:
                        pass
                    case False:
                        raise ValueError(
                            f"{presentation} cannot present a torsion module over {self.base_ring()}: its codomain "
                            f"is a module over {presentation.codomain().base_ring()}"
                        )
                from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
                    _presented_module_from_morphism,
                )

                return _presented_module_from_morphism(
                    presentation,
                    _extra_categories=(self,),
                    _require_torsion=True,
                )

            class ParentMethods:
                def invariants(self):
                    r"""Return the invariant factors of this finite presented torsion module."""
                    return self.invariant_factors()

                @cached_method
                def elements(self):
                    r"""Return all elements through the private finite Smith workspace."""

                    assert _engine_ring(self.base_ring()) is SageZZ, (
                        f"the elements of the torsion module {self} are enumerated only over ZZ, not over {self.base_ring()}"
                    )
                    if self.is_zero():
                        return FiniteOrderedSets().from_indexed(
                            Sets.Δ[0],
                            lambda _position: self.zero(),
                            name="Finite torsion elements",
                        )
                    engine = self._smith_engine()
                    assert engine is not None, (
                        f"the elements of the finite abelian group {self} cannot be enumerated: its Smith normal form is not available"
                    )
                    positions = Sets.Δ[int(engine.cardinality()) - 1]
                    return FiniteOrderedSets().from_indexed(
                        positions,
                        lambda position: self._from_smith_engine_element(
                            engine[int(position)]
                        ),
                        name="Finite torsion elements",
                    )

                def __iter__(self):
                    return iter(self.elements())

            def direct_sum_of_cyclics(self, orders):
                r"""Return ``\bigoplus_i R/(a_i)`` for the selected nonzero scalars.

                Over ``ZZ`` the ``a_i`` are the usual cyclic-group orders.  Over a
                general PID the same diagonal presentation is the invariant-factor
                construction; unit entries contribute zero summands, as they should.
                A zero entry would contribute a free copy of ``R`` and hence would not
                define an object of the torsion category.
                """
                ring = self.base_ring()
                assert ring in PrincipalIdealDomains(), (
                    f"a direct sum of cyclic modules R/(a_i) is a torsion module of this category only over a PID, "
                    f"and R = {ring} is not known to be one"
                )
                orders = tuple(ring(order) for order in orders)
                if any(order == ring.zero() for order in orders):
                    raise ValueError(
                        f"the orders {orders} include 0, and R/(0) = {ring} is not a torsion module"
                    )
                orders = tuple(order for order in orders if not order.is_unit())
                # The relation morphism r: R^n -> R^n, e_i |-> a_i e_i.
                free = ring.free_module(len(orders))
                relations = free.module_category().Mor(free, free)(
                    {
                        label: free.scalar_multiple(order, free.module_generator(label))
                        for label, order in zip(
                            free.module_generating_set(), orders, strict=True
                        )
                    }
                )
                return self(relations)

            def from_abelian_group(self, group):
                r"""Return a finite abelian group as a torsion ``ZZ``-module presentation.

                The selected group generators remain the module-generator labels.  In
                particular a represented ``C_2 x C_3`` remains a two-generator object;
                it is not silently replaced by an isomorphic one-generator ``C_6``.
                Relations are the complete kernel of the map from the free abelian
                group on those selected generators, found inside the finite box cut out
                by their individual orders and reduced to Hermite row normal form.
                """
                assert _engine_ring(self.base_ring()) is SageZZ, (
                    f"a finite abelian group {group} is a torsion ZZ-module, not a module over {self.base_ring()}"
                )
                if not group.is_finite():
                    raise ValueError(
                        f"{group} is not a finite torsion ZZ-module: the group is not finite"
                    )
                from sage_extensions.categories.group.groups import OwnedGroups

                if not group.has_selected_resolution(OwnedGroups()):
                    raise TypeError(
                        f"{group} cannot be read as a ZZ-module with chosen generators: the group has no chosen "
                        f"generating set; it is only known to be in {group.category()}"
                    )
                additive = group.category().is_subcategory(CommutativeAdditiveGroups())
                if not additive:
                    commutative = group.category().is_subcategory(
                        SageGroups().Commutative()
                    )
                    if not commutative and not bool(group.is_abelian()):
                        raise ValueError(
                            f"{group} is not a ZZ-module: the group is not abelian"
                        )

                generators = tuple(group.group_generators())
                ring = self.base_ring()
                # The relation morphism r: F(relations) -> F(group generators).
                target = ring.free_module(finite_ordered_set(generators))
                if not generators:
                    source = ring.free_module(0)
                    return self(source.module_category().Mor(source, target)({}))
                orders = tuple(int(generator.order()) for generator in generators)
                search_size = prod(orders)
                assert search_size <= 10**6, (
                    f"the relations among the generators of {group} are found by searching all exponent vectors, "
                    f"which is limited to 10^6 vectors; the generator orders {orders} give {search_size}"
                )

                if additive:
                    identity = group.zero()

                    def combine(exponents):
                        return sum(
                            (
                                exponent * generator
                                for exponent, generator in zip(
                                    exponents, generators, strict=True
                                )
                            ),
                            identity,
                        )
                else:
                    identity = group.one()

                    def combine(exponents):
                        return prod(
                            (
                                generator**exponent
                                for exponent, generator in zip(
                                    exponents, generators, strict=True
                                )
                            ),
                            identity,
                        )

                relation_rows = [
                    exponents
                    for exponents in itertools.product(
                        *(range(order) for order in orders)
                    )
                    if combine(exponents) == identity
                ]
                relation_rows.extend(
                    tuple(
                        order if row == column else 0 for column in range(len(orders))
                    )
                    for row, order in enumerate(orders)
                )
                relations = engine_matrix(SageZZ, relation_rows)
                reduced = _row_normal_form(relations, include_zero_rows=True)
                full_rank_rows = reduced.matrix_from_rows(tuple(range(len(generators))))
                source = ring.free_module(len(generators))

                def relation_image(row):
                    return target.linear_combination(
                        {
                            generator: ring(coefficient)
                            for generator, coefficient in zip(
                                generators, row, strict=True
                            )
                            if coefficient
                        }
                    )

                return self(
                    source.module_category().Mor(source, target)(
                        {
                            relation: relation_image(row)
                            for relation, row in zip(
                                source.module_generating_set(),
                                full_rank_rows.rows(),
                                strict=True,
                            )
                        }
                    )
                )

    class Free(CategoryWithAxiom):
        r"""Modules admitting a basis."""

        class ElementMethods:
            def content(self):
                r"""Return the nonnegative generator of ``O_M(self)`` over ``ZZ``.

                The order ideal is intrinsic to the module element. Its
                computation in a basis yields the gcd of the coordinates.
                The zero element has content zero.
                """
                ring = self.parent().base_ring()
                if _engine_ring(ring) is not SageZZ:
                    raise TypeError("integer content requires a free module over ZZ")
                generator = ring.zero()
                for value in self.order_ideal().ideal_generators():
                    generator = generator.gcd(value)
                return abs(generator)

            def primitive_part(self):
                r"""Return the unique ``w`` with ``content(self)*w = self``.

                This is the preimage under scalar multiplication by the
                nonzero content, which is injective on a free ZZ-module.
                """
                content = self.content()
                if not content:
                    raise ValueError("the zero vector has no primitive part")
                module = self.parent()
                multiplication = Modules(module.base_ring()).Mor(module, module)(
                    lambda label: module.scalar_multiple(
                        content, module.module_generator(label)
                    )
                )
                return multiplication.preimage(self)

        def an_object(self):
            r"""The free module of rank one."""
            return self.base_ring().free_module(1)

        def extra_super_categories(self):
            r"""A free module is projective over the same scalar ring.

            sage: C = Modules(ZZ)
            sage: C.Free().extra_super_categories()[0] is C.Projective()
            True
            sage: X = ZZ.free_module(1)
            sage: X in C.Free() and X in C.Projective()
            True
            """
            return [self.base_category().Projective()]

    class Projective(CategoryWithAxiom):
        r"""Direct summands of free modules."""

        _certifying_predicate = "projectivity_decision"

        def an_object(self):
            r"""The free module of rank one, which is projective."""
            return self.base_ring().free_module(1)

        class ParentMethods:
            def projective_rank(self, point):
                r"""Return the local free rank of a finite projective module at ``point``."""
                if self not in Modules(self.base_ring()).FinitelyGenerated():
                    raise TypeError(
                        f"the local free rank of {self} at {point} is computed only for a finitely generated "
                        f"projective module, and {self} is not known to be finitely generated"
                    )
                return self.fiber_dimension(point)

            def local_free_trivialization(self, point):
                r"""Return the isomorphism ``R_p^r -> M_p`` at a point of the spectrum.

                By Nakayama a family whose images span the fibre ``M(p)`` generates
                ``M_p``, and a projective module is free there, so a family of that
                size generating a free module of that rank is a basis.  The
                residue field already selects such a family among the chosen
                generators, so the trivialization is the map carrying the standard
                basis to it, and it is an isomorphism rather than merely a
                surjection because the ranks agree.
                """

                localized = self.localize_at_prime(point)
                labels = localized.residue_module().basis_generator_labels()
                free = localized.base_ring().free_module(labels)
                return free.module_category().Mor(free, localized)(
                    lambda label: localized.module_generator(label)
                )

            def local_determinant_line(self, point):
                r"""Top exterior line of a finite projective module at ``point``.

                Compute the exterior power of the actual localization, with
                the rank determined by the selected local trivialization.
                Do not substitute the abstract free source for the determinant
                of the localized module or claim a global basis.
                """
                if self not in Modules(self.base_ring()).FinitelyGenerated():
                    raise TypeError(
                        f"local determinant requires a finitely generated projective module: {self}"
                    )
                trivialization = self.local_free_trivialization(point)
                return trivialization.codomain().exterior_power(
                    int(trivialization.domain().module_rank())
                )

    class Torsion(CategoryWithAxiom):
        r"""Modules whose generic fibre vanishes."""

        _certifying_predicate = "_torsion_decision"

        def an_object(self):
            r"""The discriminant group of U, which is torsion."""
            from sage_extensions.categories.lattices import Lattices

            return Lattices(self.base_ring())("U").discriminant_group()


FinitelyGeneratedModules = Modules.FinitelyGenerated
FinitelyPresentedModules = Modules.FinitelyPresented
FinitelyPresentedTorsionModules = Modules.FinitelyPresented.Torsion
FreeModules = Modules.Free
ProjectiveModules = Modules.Projective
TorsionModules = Modules.Torsion


class ModulesOverIntegralDomains(OwnedCategoryOverBaseRing):
    r"""Modules over an integral domain, with their canonical generic fibre."""

    def super_categories(self):
        if self.base_ring() not in IntegralDomains():
            raise TypeError(
                "generic-fibre modules require an integral-domain coefficient ring"
            )
        return [Modules(self.base_ring())]

    def an_object(self):
        return self(Modules(self.base_ring()).an_object())

    def _call_(self, module):
        from sage_extensions.refine import refine

        if module not in Modules(self.base_ring()):
            raise TypeError(
                "the supplied module does not have this integral-domain base"
            )
        return refine(module, self)

    class ParentMethods:
        @cached_method
        def generic_fibre_map(self):
            r"""The unit ``M -> Frac(R) tensor_R M`` of fraction-field extension."""
            ring = self.base_ring()
            return (
                Modules(ring)
                .base_change_adjunction(ring.fraction_field_map())
                .unit(self)
            )

        def torsion_submodule(self):
            r"""The kernel of ``M -> Frac(R) tensor_R M``."""
            return self.generic_fibre_map().kernel()

        def _torsion_freeness_decision(self) -> bool:
            return self.generic_fibre_map().is_injective()


def FinitelyGeneratedFreeModules(base_ring):
    r"""``FramedFreeModules(R).FinitelyGenerated()``, under the name the session catalogue uses."""
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        FramedFreeModules,
    )

    return FramedFreeModules(base_ring).FinitelyGenerated()


class LinearMorModules(OwnedCategoryOverBaseRing):
    r"""Represented Mor parents closed under pointwise ``R``-linear operations."""

    def an_object(self):
        r"""The endomorphisms of the free module of rank one."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        free = modules.an_object()
        return modules.Mor(free, free)

    def _repr_object_names(self):
        return f"linear Mor modules over {self.base_ring()}"

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def base_ring(self):
            r"""The commutative scalar ring retained by this Mor's enrichment.

            Ordinary ``Hom_S(M, N)`` retains ``Z(S)``. A selected
            equivariant Mor may retain the centre of its coefficient
            ring instead, acting through its chosen coefficient map into
            ``S = R[G]``. The fixed Mor stores that datum before placement;
            recomputing a centre from its endpoints would change it.
            """
            return self._preamble_base_ring

        def automorphism_action(self, source_action, target_action):
            r"""The action on Hom(M,N) induced by supplied actions on M and N.

            For ``a`` acting on M and ``b`` on N, the action is
            ``t |-> b ∘ t ∘ a^(-1)``. Addition on Hom is written
            multiplicatively by its existing GroupExp identification, so
            the result is a group morphism ``G x H -> Aut(exp(Hom))``.
            This is the Hom bifunctor on automorphisms; composing this
            action with the group owner's semidirect product gives the
            split radical extension when N is the radical of M ⊕ N.
            """
            from sage_extensions.categories.group.groups import OwnedGroups
            from sage_extensions.categories.sets.finite_ordered_sets import (
                finite_ordered_set,
            )

            source, target = self.domain(), self.codomain()
            assert source_action.codomain().domain() is source
            assert source_action.codomain().codomain() is source
            assert target_action.codomain().domain() is target
            assert target_action.codomain().codomain() is target
            product = OwnedGroups().product_construction(
                (source_action.domain(), target_action.domain())
            )
            factors = product.object()
            shape = product.diagram().domain()
            source_projection = product.structure_morphism(shape(0))
            target_projection = product.structure_morphism(shape(1))
            exponential = self.multiplicative_group_identification()
            normal = exponential.codomain()
            logarithm = exponential.inverse()
            automorphisms = normal.Aut()

            def induced(pair):
                a = source_action(source_projection(pair))
                b = target_action(target_projection(pair))

                forward_action = (~a).internal_mor_map(
                    b, source_internal_mor=self, target_internal_mor=self
                )
                inverse_action = a.internal_mor_map(
                    ~b, source_internal_mor=self, target_internal_mor=self
                )
                forward = normal.Mor(normal).elementwise(
                    lambda element: exponential(forward_action(logarithm(element)))
                )
                inverse = normal.Mor(normal).elementwise(
                    lambda element: exponential(inverse_action(logarithm(element)))
                )
                return automorphisms(forward, inverse)

            if (
                self.base_ring() is _owned_integers()
                and self.has_selected_module_resolution()
                and self.module_generating_set() in Sets().Finite()
            ):
                normal.select_group_generators(
                    lambda: finite_ordered_set(
                        tuple(exponential(t) for t in self.module_generators())
                    )
                )
            return factors.Mor(automorphisms).elementwise(induced)

        def source_module(self):
            return self.domain()

        def target_module(self):
            return self.codomain()

        def scalar_multiple(self, scalar, morphism):
            r"""The pointwise action ``(r f)(m) = r f(m)`` of the Mor representation, not the generic module action."""
            return self._module_scalar_multiple(scalar, morphism)

        def as_morphism(self, element):
            return self(element)

        def from_morphism(self, morphism):
            return self(morphism)

        def evaluation(self, map_element, source_element):
            return self(map_element)(source_element)


class InternalMorModules(OwnedCategoryOverBaseRing):
    r"""The canonical full enriched Mor modules ``Hom_R(M,N)``."""

    def an_object(self):
        r"""The endomorphisms of the free module of rank one."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        free = modules.an_object()
        return modules.Mor(free, free)

    def _repr_object_names(self):
        return f"internal Mor modules over {self.base_ring()}"

    def super_categories(self):
        return [LinearMorModules(self.base_ring())]

    class ParentMethods:
        def _smith_engine(self):
            r"""Read the native FGP workspace of the endpoint-determined model."""
            return self._internal_mor_model()._smith_engine()

        def _to_smith_engine_element(self, morphism):
            model = self._internal_mor_model()
            return model._to_smith_engine_element(
                self._internal_model_from_morphism(morphism)
            )

        def _from_smith_engine_element(self, element):
            model = self._internal_mor_model()
            return self._morphism_from_internal_model(
                model._from_smith_engine_element(element)
            )

        def _internal_mor_model(self):
            r"""The presented module ``ker(N^{gens(M)} -> N^{rels(M)})`` modelling ``Hom_R(M, N)``.

            A map out of ``M = coker(F_1 -> F_0)`` is an assignment of an
            element of ``N`` to each generator of ``M`` killing every relation,
            so ``Hom_R(M, N)`` is the kernel of the evaluation of relations on
            generator assignments; its endpoints determine it.
            """
            from sage_extensions.categories.modules.internal_mor import (
                _internal_mor_model_data,
            )

            model, _inclusion, _presentation = _internal_mor_model_data(self)
            return model

        def inclusion_into_generator_maps(self):
            r"""The inclusion of the presented model of ``Hom(M, N)`` into ``N^{gens(M)}``."""
            from sage_extensions.categories.modules.internal_mor import (
                _internal_mor_model_data,
            )

            _model, inclusion, _presentation = _internal_mor_model_data(self)
            return inclusion

        def _morphism_from_internal_model(self, model_element):
            r"""Read an element of :meth:`_internal_mor_model` as the linear map it assigns."""
            assignment_space = self.inclusion_into_generator_maps().codomain()
            assignment = self.inclusion_into_generator_maps()(model_element)
            coordinates = assignment_space.framing_morphism().lift(assignment)
            assignment_labels = assignment_space.module_generating_set()
            return self(
                {
                    source_label: self.codomain().linear_combination(
                        {
                            target_label: coordinates(
                                assignment_labels(
                                    lambda index: (
                                        source_label
                                        if int(index) == 0
                                        else target_label
                                    )
                                )
                            )
                            for target_label in self.codomain().module_generating_set()
                        }
                    )
                    for source_label in self.domain().module_generating_set()
                }
            )

        def _internal_model_from_morphism(self, morphism):
            r"""Read a linear map as the element of :meth:`_internal_mor_model` assigning its generator images."""
            model = self._internal_mor_model()
            power = self.inclusion_into_generator_maps().codomain()
            power_labels = power.module_generating_set()
            coefficients = {}
            for source_label in self.domain().module_generating_set():
                image = (
                    self.codomain()
                    .framing_morphism()
                    .lift(morphism(self.domain().module_generator(source_label)))
                )
                for target_label, coefficient in (
                    image.parent()._selected_module_coefficients(image).items()
                ):
                    coefficients[
                        power_labels(
                            lambda index: (
                                source_label if int(index) == 0 else target_label
                            )
                        )
                    ] = coefficient
            assignment = power.linear_combination(coefficients)
            inclusion = self.inclusion_into_generator_maps()
            if inclusion.has_selected_lift():
                return inclusion.lift(assignment)
            return model(assignment)

        def _selected_module_coefficients(self, morphism):
            r"""Coordinates of a linear map in the framing of the presented model."""
            model = self._internal_mor_model()
            coordinates = model.framing_morphism().lift(
                self._internal_model_from_morphism(self(morphism))
            )
            return coordinates.parent()._selected_module_coefficients(coordinates)


class ModuleSubobjectConstruction:
    r"""The selected data defining one module subobject and its inclusion."""

    def __init__(
        self,
        *,
        ambient=None,
        generator_images=None,
        lift=None,
        inclusion_factory=None,
    ) -> None:
        if inclusion_factory is None and (ambient is None or generator_images is None):
            raise ValueError(
                "a submodule needs its inclusion: give either the module containing it and the images of "
                f"its generators (got {ambient} and {generator_images}) or a constructor of the inclusion"
            )
        self._ambient = ambient
        self._generator_images = generator_images
        self._lift = lift
        self._inclusion_factory = inclusion_factory

    def ambient_module(self):
        return self._ambient

    def generator_images(self):
        return self._generator_images

    def selected_lift(self):
        return self._lift

    def inclusion_factory(self):
        return self._inclusion_factory

    def inclusion(self, subobject):
        factory = self.inclusion_factory()
        if factory is not None:
            return factory(subobject)
        lift = self.selected_lift()
        return subobject.Mono(self.ambient_module())._subobject_inclusion(
            self.generator_images(),
            lift=(None if lift is None else lambda element: lift(subobject, element)),
        )


class ModuleSubobjects(OwnedCategoryOverBaseRing):
    r"""Modules carrying a chosen monomorphism into another module."""

    def an_object(self):
        r"""The ideal (2), a submodule of the base ring."""
        return self.base_ring().ideal(2)

    def _repr_object_names(self):
        return f"module subobjects over {self.base_ring()}"

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            subobject_ambient=None,
            subobject_generator_images=None,
            subobject_lift=None,
            subobject_inclusion_factory=None,
            **rest,
        ) -> None:
            self._module_subobject_construction = ModuleSubobjectConstruction(
                ambient=subobject_ambient,
                generator_images=subobject_generator_images,
                lift=subobject_lift,
                inclusion_factory=subobject_inclusion_factory,
            )
            super().__init__(**rest)

        def is_contained_in(self, other) -> bool:
            r"""Whether this submodule lies in the submodule ``other`` of the same ambient module.

            ``S <= T`` exactly when every generator of ``S`` lies in the image
            of ``T``'s inclusion; equality is containment both ways.
            """
            if self.inclusion().codomain() is not other.inclusion().codomain():
                raise ValueError(
                    f"{self} and {other} are submodules of different modules"
                )
            target = other.inclusion()
            inclusion = self.inclusion()
            for label in self.module_generating_set():
                decision = ask(
                    target.is_in_image(inclusion(self.module_generator(label)))
                )
                assert decision is True or decision is False, (
                    f"containment of {self} in {other} requires decided membership of its generators"
                )
                if decision is False:
                    return False
            return True

        def module_subobject_construction(self):
            r"""Return the selected construction defining this module subobject."""
            return self._module_subobject_construction

        def __contains__(self, element) -> bool:
            r"""Test ambient elements through the selected subobject inclusion."""
            if element_parent(element) is self:
                return True
            inclusion = self.inclusion()
            if element_parent(element) is inclusion.codomain():
                return inclusion.is_in_image(element)
            return super().__contains__(element)

        @cached_method
        def inclusion(self):
            r"""Return the chosen monomorphism represented by constructor data."""
            return self.module_subobject_construction().inclusion(self)

        def ambient_module(self):
            r"""Return the ambient module, i.e. the codomain of the inclusion."""
            return self.inclusion().codomain()

        def embedded_module_generators(self):
            r"""Return the indexed family of selected generator images."""
            labels = self.module_generating_set()
            return finite_indexed_family(
                labels,
                lambda label: self.inclusion()(self.module_generator(label)),
                name=f"Embedded framing of {self}",
            )

        def is_primitive(self) -> bool:
            r"""Return whether the cokernel of the inclusion is torsion-free.

            The inclusion is the subobject's chosen monomorphism, so the
            injectivity that ``Mor``-level primitivity decides first is
            part of the datum.
            """
            return self.inclusion().cokernel().is_torsion_free()

        is_saturated = is_primitive

        def index(self):
            return self.inclusion().index()

        def orthogonal_complement(self):
            r"""Return the orthogonal complement by deferring to the inclusion."""
            return self.inclusion().orthogonal_complement()

        @RealizationHook
        def _subobject_binary_realization(self, other, operation):
            r"""Return a structure-preserving realization of a subobject join or meet.

            Protected construction contract (OWN-05): only `sum` and
            `intersection` call this hook, after confirming the same ambient
            module. An already represented structural subcategory may supply
            the join/meet at its own computation owner with the correct
            inclusion, generators and preserved structure. Inputs and output
            are owned module subobjects; `None` means no such specialization
            was selected and the ordinary module construction is used.
            """
            return

        def sum(self, other):
            r"""Return the join of two subobjects of the same codomain."""
            if self.inclusion().codomain() is not other.inclusion().codomain():
                raise ValueError(
                    f"the sum of {self} and {other} is not defined: they are submodules of "
                    f"{self.inclusion().codomain()} and {other.inclusion().codomain()}, not of one module"
                )
            specialized = self._subobject_binary_realization(other, "sum")
            if specialized is not None:
                if (
                    specialized not in ModuleSubobjects(self.base_ring())
                    or specialized.inclusion().codomain()
                    is not self.inclusion().codomain()
                ):
                    raise TypeError(
                        f"the selected sum of {self} and {other} must remain a module "
                        f"subobject of {self.inclusion().codomain()}, but returned {specialized}"
                    )
                return specialized
            codomain = self.inclusion().codomain()
            summands = Sets().coproduct(
                indexed_family(
                    Sets.Δ[1],
                    lambda index: (
                        self.module_generating_set()
                        if int(index) == 0
                        else other.module_generating_set()
                    ),
                )
            )
            generators = finite_indexed_family(
                summands,
                lambda tagged: (
                    self.inclusion()(self.module_generator(tagged.summand_element()))
                    if int(tagged.summand_index()) == 0
                    else other.inclusion()(
                        other.module_generator(tagged.summand_element())
                    )
                ),
                name="Subobject-sum generators",
            )
            return codomain.subobject_on(generators)

        def intersection(self, other):
            r"""Return the meet as the image of the kernel of ``(i,-j)``."""
            if self.inclusion().codomain() is not other.inclusion().codomain():
                raise ValueError(
                    f"the intersection of {self} and {other} is not defined: they are submodules of "
                    f"{self.inclusion().codomain()} and {other.inclusion().codomain()}, not of one module"
                )
            specialized = self._subobject_binary_realization(other, "intersection")
            if specialized is not None:
                if (
                    specialized not in ModuleSubobjects(self.base_ring())
                    or specialized.inclusion().codomain()
                    is not self.inclusion().codomain()
                ):
                    raise TypeError(
                        f"the selected intersection of {self} and {other} must remain a module "
                        f"subobject of {self.inclusion().codomain()}, but returned {specialized}"
                    )
                return specialized

            direct_sum = Modules(self.base_ring()).biproduct((self, other))
            difference = direct_sum.from_summands(self.inclusion(), -other.inclusion())
            kernel = difference.kernel()
            into_left = direct_sum.left_projection() * kernel.inclusion()
            into_codomain = self.inclusion() * into_left
            return into_codomain.image()

        def saturation(self):
            r"""Return the primitive closure by deferring to the inclusion."""
            return self.inclusion().saturation()


class VectorSpaces(OwnedCategoryOverBaseRing):
    r"""Vector spaces over a field."""

    def an_object(self):
        r"""The free module of rank one over the base field."""
        from sage_extensions.categories.modules.pure.modules import Modules

        return Modules(self.base_ring()).an_object()

    def _repr_object_names(self):
        return f"vector spaces over {self.base_ring()}"

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def dimension(self):
            r"""Return the dimension from this vector space's represented basis."""
            represented = self._represented_vector_space_dimension()
            assert represented is not NotImplemented, (
                f"the dimension of the vector space {self} over {self.base_ring()} has no algorithm: no basis of it is known"
            )
            return represented

        def basis_generator_labels(self):
            r"""Return selected framing labels whose classes form a basis."""
            represented = self._represented_vector_space_basis_generator_labels()
            assert represented is not NotImplemented, (
                f"no subset of the generators of the vector space {self} over {self.base_ring()} is known to be a basis"
            )
            return represented


class ModulesWithChosenComponentPresentation(OwnedCategoryOverBaseRing):
    r"""Framed modules retaining an exact decomposition of framing labels into components.

    The datum consists of a component key for every framing label, the module
    represented by each component, and the two inverse translations between a
    component generator label and the corresponding global framing label.
    Constructions such as word quotients may use this datum directly; method
    presence is not evidence that an arbitrary framed module carries it.
    """

    def _repr_object_names(self):
        return f"modules with a chosen component presentation over {self.base_ring()}"

    def an_object(self):
        from sage_extensions.categories.modules.word_modules import (
            _module_on_word_quotient,
        )

        return _module_on_word_quotient(
            Modules(self.base_ring()).an_object(),
            "tensor",
        )

    def super_categories(self):
        return [Modules(self.base_ring())]


class ModulesWithChosenFinitePresentation(OwnedCategoryOverBaseRing):
    r"""Finitely presented modules carrying one selected finite presentation.

    The selected presentation refines the generic finitely presented module
    category over precisely the same scalar ring::

        sage: from dzack_research.preamble.all import ZZ, Modules
        sage: P = ModulesWithChosenFinitePresentation(ZZ)
        sage: P.super_categories()[0] is Modules(ZZ).FinitelyPresented()
        True
        sage: M = P.an_object()
        sage: M in P and M in Modules(ZZ).FinitelyPresented()
        True
    """

    def an_object(self):
        r"""The hyperbolic plane U, presented by its Gram matrix."""
        from sage_extensions.categories.lattices import Lattices

        return Lattices(self.base_ring())("U")

    def _repr_object_names(self):
        return f"modules with a chosen finite presentation over {self.base_ring()}"

    def __call__(self, morphism, category=None, **construction_data):
        r"""Construct the presented module even when ``morphism`` is itself in this category.

        Sage's generic category call returns its first argument whenever that
        argument is already an object of the category.  A presentation between
        finite free modules is a matrix Mor element, and matrix Mor objects are
        themselves finitely presented modules.  Here the morphism is constructor
        data, not a candidate presented module, so the call always constructs its
        cokernel.
        """
        return self._call_(morphism, category=category, **construction_data)

    def _call_(self, morphism, category=None, **construction_data):
        r"""Construct ``coker(rho)`` for ``rho: A -> B`` into a module with a chosen finite presentation.

        A presentation ``F_1 -> F_0`` is the case ``B = F_0`` free.  The
        chosen presentation of the cokernel is the presentation of ``B`` with
        the images of the module generators of ``A`` added as relations, and
        the cokernel retains ``rho`` as the morphism it is the cokernel of.
        ``category`` joins a structured category to the cokernel; the levels
        of that category read their data from ``construction_data``.
        """
        from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
            _presented_module_from_morphism,
        )

        ring = self.base_ring()
        assert morphism.domain().has_selected_module_resolution(), (
            f"the cokernel of {morphism} with a finite presentation needs a chosen generating set of "
            f"its domain {morphism.domain()}, which is only known to be in {morphism.domain().category()}"
        )
        assert morphism.domain().module_generating_set().cardinality().is_finite(), (
            f"the cokernel of {morphism} is finitely presented by this construction only if its domain "
            f"{morphism.domain()} is finitely generated, but its generating set has cardinality "
            f"{morphism.domain().module_generating_set().cardinality()}"
        )
        assert morphism.codomain() in ModulesWithChosenFinitePresentation(ring), (
            f"the cokernel of {morphism} with a finite presentation needs its codomain {morphism.codomain()} "
            f"to have a chosen finite presentation over {ring}, but it is only known to be in "
            f"{morphism.codomain().category()}"
        )
        subobject_ambient = construction_data.pop("subobject_ambient", None)
        subobject_generator_images = construction_data.pop(
            "subobject_generator_images", None
        )
        subobject_lift = construction_data.pop("subobject_lift", None)
        subobject_inclusion_factory = construction_data.pop(
            "subobject_inclusion_factory", None
        )
        return _presented_module_from_morphism(
            morphism,
            _cokernel_morphism=morphism,
            _extra_categories=() if category is None else (category,),
            _extra_construction_data=construction_data or None,
            _subobject_ambient=subobject_ambient,
            _subobject_generator_images=subobject_generator_images,
            _subobject_lift=subobject_lift,
            _subobject_inclusion_factory=subobject_inclusion_factory,
        )

    def super_categories(self):
        # FinitelyPresented is declared on Modules, not on the specialized
        # ModulesOverGroupAlgebra subclass returned by Modules(R[G]).
        ordinary = OwnedCategoryOverBaseRing.__classcall__(Modules, self.base_ring())
        return [ordinary.FinitelyPresented()]

    @cached_method
    def presentation_category(self):
        r"""Return the category of selected presentation arrows in ``R-Mod``.

        A chosen presentation is additional structure on a module, and its
        morphisms are commuting squares between the selected free-module
        arrows.  The common arrow-category owner already supplies exactly
        those objects and morphisms, so this category exposes that owner
        rather than inventing a second presentation-morphism implementation.
        """
        return Modules(self.base_ring()).ArrowCategory()

    class ParentMethods:
        @cached_method
        def invariant_factor_form(self):
            r"""Return ``self -> M_if`` with only non-unit invariant factors."""
            from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
                _module_invariant_factor_form,
            )

            return _module_invariant_factor_form(self)

        def base_change(self, ring_map, *, _extra_construction_data=None):
            r"""Transport the selected finite presentation along R -> S."""
            from sage_extensions.categories.modules.base_change import (
                _base_change_codomain,
                _base_change_scalar,
            )
            from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
                _presented_module_from_morphism,
            )

            _base_change_codomain(self, ring_map)
            if ring_map.is_identity() is True and not _extra_construction_data:
                return self
            presentation = self.presentation()
            source = presentation.domain().base_change(ring_map)
            target = presentation.codomain().base_change(ring_map)
            generator_labels = tuple(
                zip(
                    target.module_generating_set(),
                    presentation.codomain().module_generating_set(),
                    strict=True,
                )
            )

            def changed_image(relation_label):
                image = presentation(
                    presentation.domain().module_generator(relation_label)
                ).to_vector()
                return target.linear_combination(
                    {
                        changed_label: _base_change_scalar(ring_map, image(label))
                        for changed_label, label in generator_labels
                        if image(label)
                    }
                )

            images = {
                changed_label: changed_image(relation_label)
                for changed_label, relation_label in zip(
                    source.module_generating_set(),
                    presentation.domain().module_generating_set(),
                    strict=True,
                )
            }
            return _presented_module_from_morphism(
                source.module_category().Mor(source, target)(images),
                _extra_construction_data=_extra_construction_data,
            )

        @cached_method
        def _scalar_restriction_data(self, ring_map):
            r"""Retain one exact coefficient-field dimension and its finite basis.

            The private polynomial-presentation adapter owns the calculation.
            Its result is cached together, so the restriction constructor,
            vector-space dimension, and ``finite_length_at_closed_point``
            share one standard basis and one selected monomial basis of this
            module's quotient.
            """
            from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
                _singular_scalar_restriction_data,
            )

            return _singular_scalar_restriction_data(self, ring_map)

        @cached_method
        def tensor_mor_adjunction(self):
            r"""Return ``- tensor self ⊣ Hom_R(self,-)`` on chosen finite presentations."""
            from sage_extensions.categories.functors.tensor_mor import (
                _TensorMorAdjunction,
            )

            return _TensorMorAdjunction(self)

        def _selected_relation_morphism(self):
            r"""Return the selected relation morphism ``r: F_1 -> F_0`` to module-construction adapters.

            Protected presented-module contract under OWN-05--07. Permitted
            callers are module, group-module and module-morphism constructors
            that rebuild owned kernels, quotients, direct constructions, or
            scalar changes from the selected finite presentation.  Every
            module with a chosen finite presentation answers it, whichever
            constructor fixed that presentation.
            """
            return self.presentation()

        def presentation(self):
            r"""Return the selected relation morphism ``F_1 -> F_0``."""
            selected = self.selected_module_resolution()
            match selected.truncation():
                case 1:
                    return selected.differential(1)
                case _:
                    raise TypeError(
                        f"{self} has no selected relation map F_1 -> F_0: its chosen module resolution "
                        f"is truncated in degree {selected.truncation()}"
                    )

        def _rank_decision(self):
            r"""``rank_R M = rank_R coker(r)`` for the chosen presentation ``r: F_1 -> F_0``.

            The presentation is exact, ``F_1 -> F_0 -> M -> 0``, so ``M`` is
            isomorphic to ``coker(r)``, and rank is an isomorphism invariant.
            """
            return self.presentation().cokernel().module_rank()

        @cached_method
        def presentation_object(self):
            r"""Return this module's selected presentation as an arrow object."""
            category = ModulesWithChosenFinitePresentation(
                self.base_ring()
            ).presentation_category()
            return category(self.presentation())

        def adic_completion(self, ideal, *, precision=20):
            r"""Return ``M tensor_R R_hat`` along the represented ``I``-adic completion."""
            ring = self.base_ring()
            if ideal.ring() is not ring:
                raise ValueError(
                    f"the {ideal}-adic completion of {self} is not defined: {ideal} must be an ideal of "
                    f"the base ring {ring}, but it is an ideal of {ideal.ring()}"
                )
            completion = ring.adic_completion(ideal, precision=precision)
            return self.base_change_to_completion(completion)

        def base_change_to_completion(self, completion):
            r"""Return ``M tensor_R R_hat`` for one already selected completion."""
            ring = self.base_ring()
            if completion.completion_source() is not ring:
                raise ValueError(
                    f"{self} cannot be base changed to {completion}: it is a completion of "
                    f"{completion.completion_source()}, not of the base ring {ring}"
                )
            adjunction = Modules(ring).base_change_adjunction(
                completion.completion_map()
            )
            return adjunction.left_adjoint()(self)

        # The completion M_hat is an ordinary scalar-extension image and holds
        # no record of M; the maps that need both are stated on M, whose
        # base-change functor answers M_hat by object identity.

        def completion_unit(self, completion):
            r"""Return the canonical ``R``-linear map ``M -> Res_R(M_hat)`` for one selected completion."""
            ring = self.base_ring()
            if completion.completion_source() is not ring:
                raise ValueError(
                    f"{self} cannot be base changed to {completion}: it is a completion of "
                    f"{completion.completion_source()}, not of the base ring {ring}"
                )
            return (
                Modules(ring)
                .base_change_adjunction(completion.completion_map())
                .unit(self)
            )

        @cached_method
        def adic_module_truncation(self, completion, exponent):
            r"""Return ``M tensor_R R/I^exponent`` from the same selected presentation."""
            quotient = completion.adic_truncation(exponent)
            return self.base_change(quotient.quotient_map())

        @cached_method
        def adic_module_projection(self, completion, exponent):
            r"""Return ``M_hat -> Res(M/I^exponent M)`` over ``R_hat``."""
            completed = self.base_change_to_completion(completion)
            target = self.adic_module_truncation(completion, exponent)
            ring_map = completion.adic_projection(exponent)
            restricted = target.restrict_scalars(ring_map)
            labels = completed.module_generating_set()
            target_labels = target.module_generating_set()
            if labels.cardinality() != target_labels.cardinality():
                raise ArithmeticError(
                    f"the completion {completed} of {self} has {labels.cardinality()} generators, but its "
                    f"truncation {target} has {target_labels.cardinality()}; base change must keep the generators"
                )
            return completed.module_category().Mor(completed, restricted)(
                {
                    label: restricted(
                        target.module_generator(
                            target_labels[int(labels.ranking_map()(label))]
                        )
                    )
                    for label in labels
                }
            )

        @cached_method
        def adic_module_transition_map(
            self, completion, higher_exponent, lower_exponent
        ):
            r"""Return ``M/I^higher M -> Res(M/I^lower M)`` for one selected completion."""
            higher_exponent = int(higher_exponent)
            lower_exponent = int(lower_exponent)
            higher = self.adic_module_truncation(completion, higher_exponent)
            lower = self.adic_module_truncation(completion, lower_exponent)
            ring_map = completion.adic_transition_map(
                higher_exponent,
                lower_exponent,
            )
            restricted = lower.restrict_scalars(ring_map)
            higher_labels = higher.module_generating_set()
            lower_labels = lower.module_generating_set()
            if higher_labels.cardinality() != lower_labels.cardinality():
                raise ArithmeticError(
                    f"the truncations {higher} and {lower} of {self} have {higher_labels.cardinality()} and "
                    f"{lower_labels.cardinality()} generators; base change must keep the generators"
                )
            return higher.module_category().Mor(higher, restricted)(
                {
                    label: restricted(
                        lower.module_generator(
                            lower_labels[int(higher_labels.ranking_map()(label))]
                        )
                    )
                    for label in higher_labels
                }
            )


def _module_subobjects_agree(image, kernel, term) -> bool:
    r"""Whether two represented subobjects of term are equal."""
    subobjects = Modules(term.base_ring()).Subobjects(term)
    return subobjects.leq(image, kernel) and subobjects.leq(kernel, image)


@dataclass(frozen=True)
class FreeResolution:
    r"""The exact resolution ``0 -> F_n -> ... -> F_0 -> M -> 0`` by free modules.

    The datum is an indexed family of free modules over the degrees carrying a
    term, together with the family of differentials over the degrees that carry
    one, which are the nonzero ones.  A module over a principal ideal domain
    resolves in one step, while ``k = R/(x,y)`` over ``R = k[x,y]`` needs the
    Koszul complex and two, so the degrees are what varies and the top degree is
    read off them.  Outside those degrees everything is the zero module and the
    zero map, which is what makes the resolution finite.
    """

    _module: Parent
    _degrees: Parent
    _terms: IndexedFamily
    _differentials: IndexedFamily
    _augmentation: ModuleMorphism
    _zero_term: Parent

    def module(self):
        return self._module

    def degrees(self):
        r"""Return the degrees carrying a term, an owned ordered set."""
        return self._degrees

    def term(self, degree):
        if int(degree) < 0:
            raise ValueError(
                f"the resolution of {self.module()} has no term in degree {degree}: degrees are nonnegative"
            )
        if degree in self._degrees:
            return self._terms.value(degree)
        return self._zero_term

    def differential(self, degree):

        if int(degree) <= 0:
            raise ValueError(
                f"the resolution of {self.module()} has no differential d_{degree}: differentials "
                f"d_i : F_i -> F_(i-1) exist only for i > 0"
            )
        if degree in self._differentials.index_set():
            return self._differentials.value(degree)
        source = self.term(degree)
        target = self.term(int(degree) - 1)
        return source.module_category().Mor(source, target).zero()

    def augmentation(self):
        return self._augmentation

    def length(self):
        r"""Return the largest degree carrying a nonzero term."""
        return _owned_integers()(int(max(self._degrees)))

    def is_exact(self):
        r"""Decide exactness of ``0 -> F_n -> ... -> F_0 -> M -> 0``.

        Exactness is checked where it is stated: the augmentation is onto, the
        last differential is injective, and at every intermediate spot the
        image of the incoming map equals the kernel of the outgoing one, each
        equality decided as a pair of subobject containments.
        """

        if not self.augmentation().is_surjective():
            return False
        length = self.length()
        if length == 0:
            return self.augmentation().is_injective()
        if not self.differential(length).is_injective():
            return False

        if not _module_subobjects_agree(
            self.differential(1).image(),
            self.augmentation().kernel(),
            self.term(0),
        ):
            return False
        return all(
            _module_subobjects_agree(
                self.differential(int(degree) + 1).image(),
                self.differential(degree).kernel(),
                self.term(degree),
            )
            for degree in self._differentials.index_set()
            if int(degree) != length
        )

    def lift_morphism(self, morphism, target_resolution=None):
        r"""Lift ``morphism : M -> N`` to a chain map of selected free resolutions.

        The lift is constructed degree by degree by projectivity of the free
        terms.  In degree zero, lift ``f epsilon_F`` through the target
        augmentation.  In degree ``i>0``, exactness puts the already-defined
        composite ``f_{i-1} d_i`` in the image of the target differential, so
        lift each selected free generator through that differential.  No
        coordinate chain-map formula is introduced here; the common module
        image/preimage operations supply the lifts.
        """
        if morphism.domain() is not self.module():
            raise ValueError(
                f"{morphism} cannot be lifted to this resolution of {self.module()}: its domain is "
                f"{morphism.domain()}"
            )
        if target_resolution is None:
            target_resolution = morphism.codomain().free_resolution(self.length() + 1)
        if target_resolution.module() is not morphism.codomain():
            raise ValueError(
                f"the target resolution of {target_resolution.module()} does not resolve the codomain "
                f"{morphism.codomain()} of {morphism}"
            )

        components = {}
        source_zero = self.term(0)
        target_augmentation = target_resolution.augmentation()
        components[0] = source_zero.module_category().Mor(
            source_zero, target_resolution.term(0)
        )(
            {
                label: target_augmentation.preimage(
                    morphism(self.augmentation()(source_zero.module_generator(label)))
                )
                for label in source_zero.module_generating_set()
            }
        )

        for degree in range(1, self.length() + 1):
            source_term = self.term(degree)
            target_differential = target_resolution.differential(degree)
            previous = components[degree - 1]
            source_differential = self.differential(degree)
            components[degree] = source_term.module_category().Mor(
                source_term, target_resolution.term(degree)
            )(
                {
                    label: target_differential.preimage(
                        previous(
                            source_differential(source_term.module_generator(label))
                        )
                    )
                    for label in source_term.module_generating_set()
                }
            )
        return FreeResolutionMorphism(self, target_resolution, morphism, components)


@dataclass(frozen=True)
class FreeResolutionMorphism:
    r"""A chain map between free resolutions lying over one module morphism."""

    _domain: FreeResolution
    _codomain: FreeResolution
    _module_morphism: ModuleMorphism
    _components: dict

    def __post_init__(self):
        degree_zero = self.component(0)
        source_zero = self.domain().term(0)
        for label in source_zero.module_generating_set():
            generator = source_zero.module_generator(label)
            if self.codomain().augmentation()(
                degree_zero(generator)
            ) != self.module_morphism()(self.domain().augmentation()(generator)):
                raise ValueError(
                    f"the degree-0 component of the lift of {self.module_morphism()} does not commute with "
                    f"the augmentations: the two paths differ on the generator {generator}"
                )
        for degree in range(1, self.domain().length() + 1):
            component = self.component(degree)
            previous = self.component(degree - 1)
            source_differential = self.domain().differential(degree)
            target_differential = self.codomain().differential(degree)
            for label in component.domain().module_generating_set():
                generator = component.domain().module_generator(label)
                if target_differential(component(generator)) != previous(
                    source_differential(generator)
                ):
                    raise ValueError(
                        f"the lift of {self.module_morphism()} is not a chain map: the square in degree {degree} "
                        f"does not commute on the generator {generator}"
                    )

    def domain(self):
        return self._domain

    def codomain(self):
        return self._codomain

    def module_morphism(self):
        return self._module_morphism

    def component(self, degree):
        degree = int(degree)
        selected = self._components.get(degree)
        if selected is not None:
            return selected
        source = self.domain().term(degree)
        target = self.codomain().term(degree)
        return source.module_category().Mor(source, target).zero()

    def chain_homotopy_to(self, other):
        r"""Return a chain homotopy from this lift to ``other``.

        Two chain maps between free resolutions lifting the same module map are
        homotopic.  The homotopy is constructed degree by degree using exactness
        of the target resolution, exactly as :meth:`FreeResolution.lift_morphism`
        constructs a lift by projectivity of the free source terms.
        """
        if (
            other.domain() is not self.domain()
            or other.codomain() is not self.codomain()
        ):
            raise ValueError(
                f"a chain homotopy from {self} to {other} is not defined: they are chain maps "
                f"{self.domain()} -> {self.codomain()} and {other.domain()} -> {other.codomain()}, "
                f"not between the same resolutions"
            )
        if other.module_morphism() is not self.module_morphism():
            raise ValueError(
                f"a chain homotopy from {self} to {other} is constructed only between lifts of one map, "
                f"but they lift {self.module_morphism()} and {other.module_morphism()}"
            )
        source = self.domain()
        target = self.codomain()
        components = {}
        for degree in range(source.length() + 1):
            source_term = source.term(degree)
            target_next = target.term(degree + 1)
            target_differential = target.differential(degree + 1)

            def residual(generator, degree=degree):
                value = self.component(degree)(generator) - other.component(degree)(
                    generator
                )
                if degree > 0:
                    previous_homotopy = components[degree - 1]
                    value -= previous_homotopy(source.differential(degree)(generator))
                return value

            components[degree] = source_term.module_category().Mor(
                source_term, target_next
            )(
                {
                    label: target_differential.preimage(
                        residual(source_term.module_generator(label))
                    )
                    for label in source_term.module_generating_set()
                }
            )
        return FreeResolutionMorotopy(self, other, components)


@dataclass(frozen=True)
class FreeResolutionMorotopy:
    r"""A selected homotopy ``h`` with ``f-g = d h + h d``."""

    _source: FreeResolutionMorphism
    _target: FreeResolutionMorphism
    _components: dict

    def __post_init__(self):
        source_resolution = self._source.domain()
        target_resolution = self._source.codomain()
        for degree in range(source_resolution.length() + 1):
            source_term = source_resolution.term(degree)
            for label in source_term.module_generating_set():
                generator = source_term.module_generator(label)
                right = target_resolution.differential(degree + 1)(
                    self.component(degree)(generator)
                )
                if degree > 0:
                    right += self.component(degree - 1)(
                        source_resolution.differential(degree)(generator)
                    )
                left = self._source.component(degree)(
                    generator
                ) - self._target.component(degree)(generator)
                if left != right:
                    raise ValueError(
                        f"{self} is not a chain homotopy between {self.source()} and {self.target()}: "
                        f"h d + d h differs from the difference of the maps in degree {degree} on {generator}"
                    )

    def source(self):
        return self._source

    def target(self):
        return self._target

    def component(self, degree):
        degree = int(degree)
        selected = self._components.get(degree)
        if selected is not None:
            return selected
        chain_map = self.source()
        source = chain_map.domain().term(degree)
        target = chain_map.codomain().term(degree + 1)
        return source.module_category().Mor(source, target).zero()


def _fix_selected_module_resolution(
    module,
    base_ring,
    labels,
    generator_function,
    source_construction=None,
) -> None:
    r"""Retain one chosen degree-zero free resolution of a module.

    ``source_construction`` builds the free module the generators are read
    from; omitted, it is the free module on ``labels``.  Like the resolution
    itself it is fixed now and built on the first module-data read, so a Mor
    parent that is never read as a module never builds its matrix-unit module.
    """
    match callable(generator_function):
        case False:
            raise TypeError(
                f"the generators of {module} must be given by a function from {labels} to {module}, "
                f"but {generator_function} is not callable"
            )
        case True:
            pass

    def framing_source():
        match source_construction:
            case None:
                return base_ring.free_module(labels)
            case _:
                source = source_construction()
        match source.base_ring() is base_ring:
            case False:
                raise ValueError(
                    f"the generators of {module} over {base_ring} cannot be given by a map from {source}: "
                    f"it must be a free module over {base_ring}, but it is over {source.base_ring()}"
                )
            case True:
                pass
        # The registration below states S before the source is built, so the
        # built source must be free on that same set, not on an equal copy.
        assert source is module or source.module_generating_set() is labels, (
            f"the free module {source} cannot give the generators of {module}: it must be free on "
            f"the stated set {labels}, but it is free on {source.module_generating_set()}"
        )
        return source

    def selected_resolution():
        source = framing_source()
        ordinary_modules = OwnedCategoryOverBaseRing.__classcall__(Modules, base_ring)
        generator_morphism = Sets().Mor(labels, module)(
            lambda label: module(generator_function(label))
        )
        augmentation = _framing_morphism(module, source, generator_morphism)
        match source is module, labels.cardinality().is_finite():
            case (True, True):
                return (
                    ordinary_modules.FinitelyPresented()
                    .resolution_category()
                    .selected_constant(
                        module,
                        generating_set=labels,
                        generator_morphism=generator_morphism,
                    )
                )
            case _:
                pass
        return ordinary_modules.resolutions(0).selected_degree_zero(
            module,
            source,
            augmentation,
            generating_set=labels,
            generator_morphism=generator_morphism,
        )

    _fix_selected_resolution(
        module,
        Modules(base_ring),
        selected_resolution,
        generating_set=labels,
        generator_function=lambda label: module(generator_function(label)),
    )


class RestrictedScalarsModules(OwnedCategoryOverBaseRing):
    r"""Modules ``Res_f(M)``: an ``S``-module ``M`` read over ``R`` along ``f: R -> S``.

    The datum is the pair ``(M, f)``.  The underlying additive group is that
    of ``M`` and ``r`` acts as ``f(r)``.  When ``Res_f(S)`` is finite free
    over ``R`` on ``(s_i)`` and ``M`` is finitely framed over ``S`` on
    ``(m_j)``, the products ``s_i m_j`` frame ``Res_f(M)``, and a chosen
    finite presentation of ``M`` induces one of ``Res_f(M)``.  The basis
    ``(s_i)`` is selected by ``S`` along ``f`` and retained as
    ``scalar_basis``. Independently, a finite presentation of ``M`` over a
    polynomial quotient may supply its dimension and a finite basis over the
    coefficient field even when ``S`` itself is infinite dimensional. These
    data belong to the actual pair ``(M, f)`` and are retained as
    ``restriction_data``.
    """

    def an_object(self):
        r"""``Res_{id}(R^2)``: a free module along the identity of ``R``."""

        from sage_extensions.categories.sets.set_categories import finite_ordinal_set

        ring = self.base_ring()
        return ring.free_module(finite_ordinal_set(2)).restrict_scalars(
            ring.Mor(ring)(lambda element: element)
        )

    def _repr_object_names(self):
        return f"restricted-scalars modules over {self.base_ring()}"

    def super_categories(self):
        return [Modules(self.base_ring())]

    def _call_(self, module, ring_map):
        r"""Construct ``Res_f(M)`` for an ``S``-module ``M`` along ``f: R -> S``."""
        assert _owned_ring(ring_map.domain()) is self.base_ring(), (
            f"{module} cannot be restricted to {self.base_ring()} along {ring_map}: the ring morphism must "
            f"start at {self.base_ring()}, but its domain is {ring_map.domain()}"
        )
        return _restricted_scalars_view(module, ring_map)

    class ElementMethods(ModuleElement):
        r"""An element of ``Res_f(M)``, which is an element of ``M`` read over ``R``."""

        def __init__(self, parent, underlying_element) -> None:
            ModuleElement.__init__(self, parent)
            self._underlying_element = underlying_element

        def underlying_element(self):
            r"""Return this element read in ``M``."""
            return self._underlying_element

        def __hash__(self):
            r"""Restriction of scalars retains the underlying element's hash."""
            return hash(self._underlying_element)

        def _add_(self, other):
            return self.parent().element_class(
                self.parent(),
                self._underlying_element + other._underlying_element,
            )

        def _neg_(self):
            return self.parent().element_class(self.parent(), -self._underlying_element)

        def _lmul_(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def _richcmp_(self, other, op):
            return richcmp(
                self._underlying_element,
                other._underlying_element,
                op,
            )

        def _repr_(self):
            return repr(self._underlying_element)

    class ParentMethods:
        _derived_construction_parameters = frozenset(
            {"base_ring", "module_generating_set", "module_generator_function"}
        )

        def __init__(
            self,
            module_over_extension,
            ring_map,
            framing_source=None,
            scalar_basis=None,
            restriction_data=None,
            **rest,
        ) -> None:
            self._module_over_extension = module_over_extension
            self._ring_map = ring_map
            self._scalar_basis = scalar_basis
            self._restriction_data = restriction_data
            ring = _owned_ring(ring_map.domain())
            framing = {}
            if framing_source is not None:
                framing.update(
                    module_generating_set=framing_source.module_generating_set(),
                    module_generator_function=self._restricted_scalar_generator,
                    framing_source=framing_source,
                )
            super().__init__(base_ring=ring, **framing, **rest)

        def ring_map(self):
            r"""Return the selected scalar map ``R -> S``."""
            return self._ring_map

        def module_over_extension(self):
            r"""Return the original ``S``-module before restriction of scalars."""
            return self._module_over_extension

        def subobject_on(self, module_generators) -> ModuleSubobjects.ParentMethods:
            r"""Return the finite span over the restricted base ring, with its inclusion.

            For restriction from the fraction field of a PID, Sage computes
            the span over the PID, retaining fractional generator entries.

            EXAMPLES::

                sage: V = QQ**2
                sage: M = V.restrict_scalars(ZZ.fraction_field_map())
                sage: a = M(V.linear_combination({0: QQ(1)/QQ(2)}))
                sage: b = M(V.linear_combination({0: QQ(1)/QQ(3)}))
                sage: S = M.subobject_on((a, b))
                sage: c = M(V.linear_combination({0: QQ(1)/QQ(6)}))
                sage: S.inclusion().is_in_image(c)
                True
                sage: S.inclusion().is_in_image(M(V.linear_combination({0: QQ(1)/QQ(12)})))
                False
            """
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                FramedFreeModules,
                _module_subobject_on,
                _restricted_fraction_field_subobject_on,
            )

            if self in FramedFreeModules(self.base_ring()):
                return _module_subobject_on(self, module_generators)
            return _restricted_fraction_field_subobject_on(self, module_generators)

        def extension_ring(self):
            return _owned_ring(self.module_over_extension().base_ring())

        @cached_method
        def regular_module_identification(self):
            r"""The isomorphism ``Res_f(S^1) -> S`` of ``R``-modules, ``s e_0 |-> s``.

            Here ``f: R -> S`` is the structure morphism of the ``R``-algebra
            ``S`` and ``S^1`` is the regular ``S``-module.  The target is
            ``S`` with its own ``R``-module structure, on which ``r`` acts as
            multiplication by ``f(r)``.  Both modules have the underlying set
            of ``S``, and the map is ``R``-linear because
            ``r.(s e_0) = (f(r) s) e_0 |-> f(r) s = r.s``.
            """
            from sage_extensions.categories.algebras.algebras import Algebras

            scalars = self.extension_ring()
            assert self.module_over_extension() is scalars.regular_module(), (
                f"{self} is not restricted from the regular module of {scalars}, so it has no identification "
                f"with {scalars}"
            )
            assert (
                scalars in Algebras(self.base_ring())
                and self.ring_map() is scalars.algebra_structure_morphism()
            ), (
                f"{self} is restricted along {self.ring_map()}, which is not the structure morphism of {scalars} "
                f"as a {self.base_ring()}-algebra"
            )
            to_scalars = scalars.regular_module_isomorphism()
            return (
                self.module_category()
                .Mor(self, scalars)
                ._from_constructed_element_map(
                    lambda element: to_scalars(self(element).underlying_element())
                )
            )

        def underlying_additive_group(self):
            r"""Return the unchanged additive group of the extension-ring module."""
            return self.module_over_extension().underlying_additive_group()

        def is_zero(self) -> bool:
            r"""Return whether the unchanged underlying additive group is zero."""
            return self.module_over_extension().is_zero()

        def _finiteness_decision(self):
            r"""``Res_f(M)`` is the set of ``M``, so it is finite exactly when ``M`` is."""
            return self.module_over_extension().is_finite()

        def _cardinality_decision(self):
            r"""``|Res_f(M)| = |M|``: restriction of scalars keeps the underlying set."""
            return self.module_over_extension()._cardinality_decision()

        def _scalars_act_by_units(self):
            r"""Whether every nonzero ``r in R`` acts on ``Res_f(M)`` invertibly.

            When ``S`` is a field and ``f`` is injective, ``f(r)`` is a nonzero
            element of a field for ``r != 0``, so ``r m = f(r) m`` vanishes
            only when ``m`` does.
            """
            return (
                self.extension_ring() in OwnedFields()
                and self.ring_map().is_injective() is True
            )

        def _torsion_freeness_decision(self):
            r"""``Res_f(M)`` is torsion-free when ``S`` is a field and ``f`` is injective.

            ``r m = f(r) m = 0`` with ``r != 0`` gives ``m = f(r)^{-1} f(r) m = 0``.
            """
            match self._scalars_act_by_units():
                case True:
                    return True
                case False:
                    return AtomicProposition("is_torsion_free", self)

        def _torsion_decision(self):
            r"""``Res_f(M)`` is torsion only when ``M = 0``, when ``S`` is a field and ``f`` is injective.

            No nonzero element is killed by a nonzero scalar, so every element
            is torsion exactly when there is no nonzero element.
            """
            match self._scalars_act_by_units():
                case True:
                    return self.is_zero()
                case False:
                    return AtomicProposition("is_torsion", self)

        def _rank_decision(self):
            r"""``rank_R Res_f(M) = rank_R Res_f(S) * rank_S(M)``, the tower law.

            Mathlib ``rank_mul_rank`` (``Mathlib.LinearAlgebra.Dimension.Free``)
            states it when ``Res_f(S)`` is free over ``R``, ``M`` is free over
            ``S``, and ``R`` and ``S`` have the strong rank condition, which
            every nonzero commutative ring has.  ``Res_f(S)`` is free on the
            retained ``scalar_basis``; ``M`` is free when it is placed so, and
            always when ``S`` is a field.
            """
            ring = self.base_ring()
            extension_ring = self.extension_ring()
            module = self.module_over_extension()
            match self:
                case _ if self._restriction_data is not None:
                    return self._restriction_data[0]
                case _ if (
                    self._scalar_basis is not None
                    and ring in OwnedRings().Commutative()
                    and extension_ring in OwnedRings().Commutative()
                    and extension_ring.one() != extension_ring.zero()
                    and (
                        extension_ring in OwnedFields()
                        or module in Modules(extension_ring).Free()
                    )
                ):
                    return (
                        self._scalar_basis.source().module_rank() * module.module_rank()
                    )
                case _:
                    return Unknown

        def _represented_vector_space_dimension(self):
            r"""Read the dimension retained for this module and this scalar map."""
            if self._restriction_data is not None:
                return self._restriction_data[0]
            # Restriction preserves the underlying additive group. A proved
            # zero module therefore has dimension zero over any field,
            # without a coefficient-presentation algorithm or a new framing.
            if self.module_over_extension().is_zero() is True:
                return cardinal(0)
            return super()._represented_vector_space_dimension()

        def _underlying_additive_element(self, element):
            element = self(element)
            extension = self.module_over_extension()
            return extension._underlying_additive_element(element.underlying_element())

        @cached_method
        def _ring_morphism_defining_module_action(self):
            r"""Return ``rho_M compose f`` with this module's exact endomorphism parent.

            The extension action and the restricted module act on the same
            underlying abelian group, but their construction paths need not
            intern the identical ``End`` parent.  The native module constructor
            requires the scalar action to land in the exact endomorphism parent
            of ``self.underlying_additive_group()``.  Re-express each composite
            endomorphism in that parent instead of relying on parent identity
            across the restriction boundary.
            """
            ring = self.base_ring()
            extension_action = self.module_over_extension().scalar_action()
            endomorphisms = (
                AdditiveGroups()
                .AdditiveCommutative()
                .End(self.underlying_additive_group())
            )
            ring_map = self.ring_map()
            return ring.Mor(endomorphisms, category=OwnedRings())(
                lambda scalar: endomorphisms.elementwise(
                    lambda element: extension_action(ring_map(scalar))(element)
                ),
            )

        def scalar_multiple(self, scalar, element):
            element = self(element)
            underlying = self._underlying_additive_element(element)
            return self.wrap(self.scalar_action()(self.base_ring()(scalar))(underlying))

        def _element_constructor_(self, value):
            if isinstance(value, self.element_class) and value.parent() is self:
                return value
            source = element_parent(value)
            if source in Modules(self.base_ring()) and source.unformed_module() is self:
                return source._element_of_unformed_module(value)
            if isinstance(value, RestrictedScalarsModules.ElementMethods):
                value = value.underlying_element()
            return self.wrap(self.module_over_extension()(value))

        def wrap(self, underlying_element):
            r"""Read an element of ``M`` as the same element of ``Res_f(M)``."""
            return self.element_class(
                self, self.module_over_extension()(underlying_element)
            )

        def _coerce_map_from_(self, source):
            # Restriction of scalars is a change of structure, not a coercion of
            # mathematical objects.  ``wrap`` reads an element of ``M`` here
            # explicitly when the same additive-group element is meant.
            if source is self.module_over_extension():
                return None
            return super()._coerce_map_from_(source)

        def __contains__(self, value) -> bool:
            if isinstance(value, self.element_class) and value.parent() is self:
                return True
            return value in self.module_over_extension()

        def _restricted_scalar_generator(self, label):
            r"""Return the retained basis image, or ``s_i m_j`` in the scalar tower."""
            labels = self.module_generating_set()
            assert label in labels, (
                f"{label!r} does not index a generator of {self}; its generators are indexed by {labels}"
            )
            label = labels(label)
            if (
                self._restriction_data is not None
                and self._restriction_data[1] is not None
            ):
                return self.wrap(self._restriction_data[1].image(label))
            extension_module = self.module_over_extension()
            scalar = self._scalar_basis.image(label.component(0))
            module_generator = extension_module.module_generator(label.component(1))
            return self.element_class(
                self,
                extension_module.scalar_multiple(scalar, module_generator),
            )

        def _selected_module_coefficients(self, element):
            r"""``m = sum_j t_j m_j`` and ``t_j = sum_i c_ij s_i`` give ``m = sum_ij c_ij s_i m_j``."""
            element = self(element)
            if (
                self._restriction_data is not None
                and self._restriction_data[1] is not None
            ):
                return self._restriction_data[1].coordinates(
                    element.underlying_element()
                )
            module_coordinates = (
                self.module_over_extension()
                .framing_morphism()
                .lift(element.underlying_element())
            )
            framing = self.module_generating_set()
            coefficients = {}
            for module_label, coefficient in (
                module_coordinates.parent()
                ._selected_module_coefficients(module_coordinates)
                .items()
            ):
                scalar_coordinates = self._scalar_basis.coordinates(coefficient)
                for scalar_label, value in scalar_coordinates.items():
                    coefficients[framing((scalar_label, module_label))] = (
                        self.base_ring()(value)
                    )
            return coefficients

        def _represented_kernel_of_morphism(self, morphism):
            r"""Compute a finite-free source kernel in a restricted fraction-field module.

            If ``W`` is finitely framed over ``Frac(R)``, the images of a
            finite basis of ``F`` in ``Res(W)`` have finitely many rational
            coordinates.  Multiplying every coordinate by one common
            denominator embeds the same kernel problem in a finite free
            ``R``-module, where the ordinary matrix-kernel owner applies.
            """
            if morphism.codomain() is not self:
                return NotImplemented
            domain = morphism.domain()
            ring = self.base_ring()
            if not _coordinate_framed_free_module(domain, ring):
                return NotImplemented
            fractions = self.extension_ring()
            if fractions is not ring.fraction_field():
                return NotImplemented
            extension = self.module_over_extension()
            if not (
                extension.has_selected_module_resolution()
                and extension in FinitelyGeneratedModules(fractions)
            ):
                return NotImplemented

            if not _coordinate_framed_free_module(extension, fractions):
                coordinates = extension.finite_free_trivialization().forward()
                restricted = Modules(fractions).restriction_of_scalars(self.ring_map())(
                    coordinates
                )
                return (restricted * morphism).kernel()

            framing = extension.framing_morphism()
            image_coordinates = {
                label: framing.lift(
                    morphism(domain.module_generator(label)).underlying_element()
                )
                for label in domain.module_generating_set()
            }
            denominator = ring.one()
            for coordinates in image_coordinates.values():
                for coefficient in (
                    coordinates.parent()
                    ._selected_module_coefficients(coordinates)
                    .values()
                ):
                    denominator = denominator.lcm(coefficient.denominator())
            scale = self.ring_map()(denominator)
            cleared_module = ring._fresh_free_module_on(
                extension.module_generating_set()
            )

            def cleared(coordinates):
                return cleared_module.linear_combination(
                    {
                        label: ring(scale * coefficient)
                        for label, coefficient in coordinates.parent()
                        ._selected_module_coefficients(coordinates)
                        .items()
                    }
                )

            cleared_morphism = Modules(ring).Mor(domain, cleared_module)(
                {
                    label: cleared(coordinates)
                    for label, coordinates in image_coordinates.items()
                }
            )
            return cleared_morphism.kernel()

        def zero(self):
            return self.element_class(self, self.module_over_extension().zero())

        def an_element(self):
            return self.element_class(self, self.module_over_extension().an_element())

        def _repr_(self):
            return f"{self.module_over_extension()} restricted to {self.base_ring()} along {self.ring_map()}"


def _restricted_scalar_framing_labels(module, scalar_basis):
    r"""Return the framing labels ``I x J`` of ``Res_f(M)`` for ``Res_f(S)`` framed on ``I``, ``M`` on ``J``."""
    scalar_labels = scalar_basis.source().module_generating_set()
    module_labels = module.module_generating_set()
    return Sets().product(
        indexed_family(
            Sets.Δ[1],
            lambda index: scalar_labels if int(index) == 0 else module_labels,
        )
    )


def _restricted_scalar_presentation(module, ring_map, labels, scalar_basis):
    r"""Return the relation morphism of ``Res_f(M)`` induced by the one of ``M``.

    Suppose ``Res_f(S)`` is finite free over ``R`` on ``(s_i)`` and ``M`` is
    presented over ``S`` by ``r: F_S(K) -> F_S(J)``.  The restricted
    module is generated over ``R`` by ``s_i m_j``.  For every relation
    ``r(e_k)`` and every ``s_i`` the relation ``s_i r(e_k)`` is expanded
    in the basis ``scalar_basis`` of ``Res_f(S)``.  These generate the
    restriction of the ``S``-relation submodule to ``R``.
    """
    from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
        _morphism_on_elements,
    )

    ring = _owned_ring(ring_map.domain())
    extension_ring = _owned_ring(module.base_ring())
    scalar_labels = scalar_basis.source().module_generating_set()
    relations = module._selected_relation_morphism()
    assert relations is not None, (
        f"the restriction of scalars of {module} needs the relations of its finite presentation, "
        f"but {module} has none"
    )
    generators = ring._fresh_free_module_on(labels)

    def restricted_relation(relation_label, scalar_label):
        scalar_generator = scalar_basis.image(scalar_label)
        relation = relations(
            relations.domain().module_generator(relation_label)
        ).to_vector()
        coefficients = {}
        for module_label, coefficient in (
            relation.parent()._selected_module_coefficients(relation).items()
        ):
            product = extension_ring(scalar_generator * extension_ring(coefficient))
            for output_scalar_label, value in scalar_basis.coordinates(product).items():
                label = labels(
                    lambda index: (
                        output_scalar_label if int(index) == 0 else module_label
                    )
                )
                coefficients[label] = coefficients.get(label, ring.zero()) + ring(value)
        return generators.linear_combination(coefficients)

    restricted = tuple(
        restricted_relation(relation_label, scalar_label)
        for relation_label in relations.domain().module_generating_set()
        for scalar_label in scalar_labels
    )
    return _morphism_on_elements(
        generators,
        tuple(
            relation
            for relation in restricted
            if (relation == generators.zero()) is not True
        ),
    )


@cached_function(
    key=lambda module, ring_map, *data: (
        id(module),
        id(ring_map),
        tuple(id(value) for value in data),
    )
)
def _restricted_scalars_view(
    module,
    ring_map,
    # Sage's cached_function argument fixer cannot read keyword-only
    # defaults, so these selected-subobject data are ordinary keywords.
    _subobject_ambient=None,
    _subobject_generator_images=None,
    _subobject_lift=None,
    _subobject_inclusion_factory=None,
):
    r"""Return ``Res_f(M)`` along ``f: R -> S``, placed by what ``M`` and ``S`` already are.

    ``Res_f(M)`` is framed, finitely generated and finitely presented over
    ``R`` when ``Res_f(S)`` is finite free over ``R`` and ``M`` is so over
    ``S``; a selected inclusion places it among the subobjects.  The basis of
    ``Res_f(S)`` is the one ``S`` selects along ``f``, so it is taken along
    the given map and never from ``S``'s structure over its own base ring.
    A basis of ``Res_f(M)`` supplied by the module's selected presentation
    gives a second framing route without requiring ``Res_f(S)`` to be finite.
    Along a field-to-field map with a selected finite scalar basis, an
    already represented dimension is multiplied by that basis cardinality.
    This dimension transport does not require or create a finite frame of M.
    """
    extension_ring = _owned_ring(module.base_ring())
    assert _owned_ring(ring_map.codomain()) is extension_ring, (
        f"{module} cannot be restricted along {ring_map}: the ring morphism must end at the scalar ring "
        f"{extension_ring} of the module, but its codomain is {ring_map.codomain()}"
    )
    from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
        _SelectedFinitePresentationModules,
    )
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        FramedFreeModules,
    )

    base_ring = _owned_ring(ring_map.domain())
    # The restricted module's addition is abelian by construction.  Owned
    # category joins do not necessarily materialize inherited facets on the
    # concrete parent, and the native scalar-action constructor checks this
    # prerequisite before retaining the module presentation.  Record it at
    # the shared restriction-of-scalars construction owner.
    placement = [
        RestrictedScalarsModules(base_ring),
        AdditiveGroups().AdditiveCommutative(),
    ]
    if base_ring in OwnedFields():
        placement.append(VectorSpaces(base_ring))
    data = {"module_over_extension": module, "ring_map": ring_map}

    finitely_framed = (
        module.has_selected_module_resolution()
        and module in Modules(extension_ring).FinitelyGenerated()
    )
    field_tower = (
        base_ring in OwnedFields()
        and extension_ring in OwnedFields()
        and ring_map.codomain() is extension_ring
    )
    scalar_basis = (
        extension_ring._module_basis_along(ring_map)
        if finitely_framed or field_tower
        else None
    )
    finite_scalar_basis = (
        scalar_basis is not None
        and scalar_basis.source() in FinitelyGeneratedFreeModules(base_ring)
    )
    framed_over_finite_free_scalars = finitely_framed and finite_scalar_basis
    restriction_data = None
    if not framed_over_finite_free_scalars:
        restriction_data = module._scalar_restriction_data(ring_map)
        if restriction_data is None and field_tower and finite_scalar_basis:
            dimension = module._represented_vector_space_dimension()
            if dimension is not NotImplemented:
                restriction_data = (
                    cardinal(dimension) * scalar_basis.source().module_rank(),
                    None,
                )
                data["scalar_basis"] = scalar_basis
        if restriction_data is not None:
            data["restriction_data"] = restriction_data
    match module:
        case _ if (
            framed_over_finite_free_scalars
            and module in ModulesWithChosenFinitePresentation(extension_ring)
        ):
            presentation = _restricted_scalar_presentation(
                module,
                ring_map,
                _restricted_scalar_framing_labels(module, scalar_basis),
                scalar_basis,
            )
            placement.append(_SelectedFinitePresentationModules(base_ring))
            data.update(
                presentation=presentation,
                framing_source=presentation.codomain(),
                scalar_basis=scalar_basis,
            )
        case _ if framed_over_finite_free_scalars:
            placement.append(Modules(base_ring).FinitelyGenerated())
            data.update(
                framing_source=base_ring._fresh_free_module_on(
                    _restricted_scalar_framing_labels(module, scalar_basis)
                ),
                scalar_basis=scalar_basis,
            )
        case _ if restriction_data is not None and restriction_data[1] is not None:
            placement.append(FramedFreeModules(base_ring).FinitelyGenerated())
            data["framing_source"] = restriction_data[1].source()

    if _subobject_inclusion_factory is not None or (
        _subobject_ambient is not None and _subobject_generator_images is not None
    ):
        placement.append(ModuleSubobjects(base_ring))
        if _subobject_ambient is not None:
            placement.append(Modules(base_ring).Subobjects(_subobject_ambient))
        data.update(
            subobject_ambient=_subobject_ambient,
            subobject_generator_images=_subobject_generator_images,
            subobject_lift=_subobject_lift,
            subobject_inclusion_factory=_subobject_inclusion_factory,
        )

    from sage_extensions.owned_category import _object_of, owned_category_join

    return _object_of(owned_category_join(tuple(placement)), **data)


def _tensor_label_set(factors):
    r"""Return $\prod_{i \in I} S_i$, the generating set of $\bigotimes_i M_i$.

    A generator of the tensor product is one generator chosen in each factor,
    which is a section of the family of generating sets over the index set.
    """
    return Sets().product(
        indexed_family(
            factors.index_set(),
            lambda index: factors.value(index).module_generating_set(),
        )
    )


def _tensor_pair(label_set, left_label, right_label):
    return label_set(lambda index: left_label if int(index) == 0 else right_label)


def BilinearMap(left, right, codomain, generator_images):
    r"""Construct the represented bilinear map in ``Hom_R(left tensor right, codomain)``.

    ``BilinearMap`` is generator-image ingress, not a second representation of
    a pairing.  The returned object is the actual tensor-domain module
    morphism.  Consequently its ordinary module-Mor admission is the one
    authority that checks every selected tensor relation.
    """
    ring = left.base_ring()
    match right.base_ring() == ring, codomain in Modules(ring):
        case True, True:
            pass
        case _:
            raise ValueError(
                f"a bilinear map {left} x {right} -> {codomain} is not defined over {ring}: {right} and "
                f"{codomain} must be modules over {ring} as {left} is"
            )
    match left.has_selected_module_resolution(), right.has_selected_module_resolution():
        case True, True:
            pass
        case _:
            raise TypeError(
                f"a bilinear map {left} x {right} -> {codomain} given by images of pairs of generators needs "
                f"chosen generators of {left} and {right}; for modules without them, give a morphism "
                f"out of their tensor product"
            )

    factor_family = _factor_family((left, right), name="Tensor factors")
    pair_labels = _tensor_label_set(factor_family)
    match generator_images:
        case dict() as assignment:
            size = pair_labels.cardinality()
            match size.is_finite():
                case True:
                    pass
                case False:
                    raise TypeError(
                        f"the bilinear map {left} x {right} -> {codomain} has {size} pairs of generators; "
                        f"infinitely many images must be given by a function, not a dict"
                    )

            def raw_image(pair):
                key = (pair.component(0), pair.component(1))
                match key in assignment:
                    case True:
                        return assignment[key]
                    case False:
                        raise ValueError(
                            f"the bilinear map {left} x {right} -> {codomain} has no image for the pair of generators {key!r}"
                        )

            for pair in pair_labels:
                raw_image(pair)
        case _ if callable(generator_images):

            def raw_image(pair):
                return generator_images(pair.component(0), pair.component(1))
        case _:
            raise TypeError(
                f"the bilinear map {left} x {right} -> {codomain} must be given by a function or a dict "
                f"on pairs of generators, not by {generator_images}"
            )

    tensor_product = Modules(ring).tensor_product(factor_family)
    match tensor_product.has_selected_module_resolution():
        case True:
            labels = tensor_product.module_generating_set()
            images = indexed_family(
                labels,
                lambda pair: codomain(raw_image(pair)),
                name="Bilinear generator images",
            )
            return tensor_product.module_category().Mor(tensor_product, codomain)(
                images
            )
        case False:

            def evaluation(left_element, right_element):
                left_coordinates = left.framing_morphism().lift(left_element)
                right_coordinates = right.framing_morphism().lift(right_element)
                left_coefficients = (
                    left_coordinates.parent()._selected_module_coefficients(
                        left_coordinates
                    )
                )
                right_coefficients = (
                    right_coordinates.parent()._selected_module_coefficients(
                        right_coordinates
                    )
                )
                return sum(
                    (
                        left_coefficient
                        * right_coefficient
                        * codomain(
                            raw_image(
                                _tensor_pair(
                                    pair_labels,
                                    left_label,
                                    right_label,
                                )
                            )
                        )
                        for left_label, left_coefficient in left_coefficients.items()
                        for right_label, right_coefficient in right_coefficients.items()
                    ),
                    codomain.zero(),
                )

            return tensor_product.from_bilinear_map(codomain, evaluation)


class TensorProductModules(OwnedCategoryOverBaseRing):
    r"""Modules carrying a selected tensor-product universal object."""

    def an_object(self):
        r"""The tensor square of the free module of rank one."""
        free = Modules(self.base_ring()).an_object()
        return Modules(self.base_ring()).tensor_product((free, free))

    def _repr_object_names(self):
        return f"chosen tensor-product modules over {self.base_ring()}"

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def __init__(self, tensor_factors, **rest) -> None:
            self._preamble_tensor_factors = tensor_factors
            super().__init__(**rest)

        def _module_mor_class(self):

            return TensorProductModuleMor

        @cached_method
        def tensor_factors(self):
            r"""Return the family of factors, indexed by the product's own index set."""

            return _finite_factor_family(
                self._preamble_tensor_factors, name="Tensor factors"
            )

        def tensor_factor(self, index):
            return self.tensor_factors()[index]

        def _two_factors(self):
            r"""The two factors, where the universal map of this product is bilinear.

            A tensor product over an index set of any size is constructed
            here, but its universal multilinear map is represented only for
            two factors, where the classifier is the tensor-domain module Mor.
            """
            factors = self.tensor_factors()
            assert factors.cardinality() == cardinal(2), (
                f"the universal multilinear map of {self} is computed only for two factors, where it is "
                f"bilinear, but {self} has {factors.cardinality()} factors"
            )
            return self.tensor_factor(0), self.tensor_factor(1)

        def pure_tensor(self, left_element, right_element):
            r"""Return the universal pure tensor of two elements."""
            left, right = self._two_factors()

            # A zero factor makes every pure tensor zero, even when the
            # factor's selected finite presentation has redundant generators.
            if self.module_generating_set().cardinality() == 0:
                return self.zero()

            left_coordinates = left.framing_morphism().lift(left_element)
            right_coordinates = right.framing_morphism().lift(right_element)
            left_coefficients = left_coordinates.parent()._selected_module_coefficients(
                left_coordinates
            )
            right_coefficients = (
                right_coordinates.parent()._selected_module_coefficients(
                    right_coordinates
                )
            )
            labels = self.module_generating_set()
            return self.linear_combination(
                {
                    _tensor_pair(labels, left_label, right_label): left_coefficient
                    * right_coefficient
                    for left_label, left_coefficient in left_coefficients.items()
                    for right_label, right_coefficient in right_coefficients.items()
                }
            )

        def universal_bilinear_map(self):
            self._two_factors()
            labels = self.module_generating_set()
            return self.module_category().Mor(self, self)(
                indexed_family(
                    labels,
                    self.module_generator,
                    name="Universal pure-tensor generator images",
                )
            )

        def from_bilinear_map(self, codomain, bilinear):
            r"""Classify a stated R-bilinear evaluation without inferring its law from framing values."""
            self._two_factors()
            mor = self.module_category().Mor(self, codomain)
            return mor._from_bilinear_evaluation(bilinear)


def _represented_finite_presentation(module) -> bool:
    r"""Return whether ``module`` carries selected finite presentation data."""
    return module in ModulesWithChosenFinitePresentation(module.base_ring())


def _represented_framed_free(module) -> bool:
    r"""Return whether ``module`` carries the framed free construction.

    Membership, not ``is_framed_module() and is_free()``.  Those two are true of
    every module that happens to be framed and free -- the zero presented
    module is one, and it is the discriminant module of a unimodular lattice
    -- while the backend they were standing in for is the one a module gets
    by being *constructed* free.
    """
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        FramedFreeModules,
    )

    return module in FramedFreeModules(module.base_ring())


def _finite_biproduct_realizes_product(factors) -> bool:
    r"""Whether the existing finite biproduct backend realizes this product.

    The empty biproduct is the zero module, hence also the terminal product.
    Otherwise the existing biproduct realization is retained exactly when all
    factors share one of its represented construction routes: framed free or
    chosen finite presentation.
    """
    size = factors.cardinality()
    match size.is_finite():
        case False:
            return False
        case True:
            match int(size.finite_value()):
                case 0:
                    return True
                case _:
                    values = tuple(factors)
                    return all(
                        _represented_framed_free(factor) for factor in values
                    ) or all(
                        _represented_finite_presentation(factor) for factor in values
                    )


def _admitted_module_factor_family(modules, factors, *, name):
    r"""Return the represented family with module membership checked on access.

    A finite family is admitted immediately.  An infinite represented family
    cannot be exhaustively traversed merely to establish its codomain; each
    requested value is therefore checked lazily against the exact module
    category, so a bad factor cannot enter the product diagram or its
    componentwise realization.
    """
    family = _factor_family(factors, name=name)

    # A selected constant family already supplies every factor without
    # enumerating its index set. Preserve that datum: replacing it with an
    # opaque callback would erase the proof that the infinite product has
    # one fixed module as every factor.
    constant = family.constant_value()
    if constant is not None:
        if constant not in modules:
            raise TypeError(
                f"the product in {modules} is not defined: the constant factor {constant} is not a module"
            )
        return indexed_family(family.index_set(), constant, name=name)

    diagram = family.selected_diagram()
    if diagram is not None and diagram.codomain().is_subcategory(modules):
        # A diagram in a stricter module category also supplies a diagram
        # in Mod_R. Transport along its actual category inclusion rather
        # than discard its arrows by replacing it with an object callback.
        if diagram.codomain() is modules:
            return family
        inclusion = diagram.codomain().inclusion_into(modules)
        return indexed_family(family.index_set(), diagram.then(inclusion), name=name)

    def admitted(index):
        factor = family.value(index)
        match factor in modules:
            case True:
                return factor
            case False:
                raise TypeError(
                    f"the product in {modules} is not defined: the factor {factor} is not an object of {modules}"
                )

    selected = indexed_family(
        family.index_set(),
        admitted,
        name=name,
    )
    match selected.cardinality().is_finite():
        case True:
            for index in selected.index_set():
                selected.value(index)
        case False:
            pass
    return selected


def _module_product_cache_key(base_ring, factors):
    size = factors.cardinality()
    match size.is_finite():
        case True:
            return (
                id(base_ring),
                id(factors.index_set()),
                tuple(id(factor) for factor in factors),
            )
        case False:
            return id(base_ring), id(factors)


@cached_function(key=_module_product_cache_key)
def _module_product_created_by_underlying_sets(base_ring, factors):
    r"""Create ``prod_i M_i`` from ``prod_i U(M_i)`` with pointwise operations."""
    from sage_extensions.categories.modules.general_modules import GeneralModules

    ring = _owned_ring(base_ring)
    modules = Modules(ring)
    forgetful = modules.underlying_set()
    constant = factors.constant_value()
    diagram = factors.selected_diagram()
    if constant is not None:
        underlying_values = forgetful(constant)
    elif diagram is not None and diagram.codomain() is modules:
        underlying_values = diagram.then(forgetful)
    else:
        underlying_values = lambda index: forgetful(factors.value(index))
    underlying_factors = indexed_family(
        factors.index_set(),
        underlying_values,
        name="Underlying sets of module product factors",
    )
    underlying_product = Sets().product(underlying_factors)

    def combine(operation, operands):
        return underlying_product(
            lambda index: operation(
                factors.value(index),
                *(operand.component(index) for operand in operands),
            )
        )

    return GeneralModules(ring).from_operations(
        underlying_product,
        **_pointwise_module_operations(combine),
    )


def _pointwise_sum(module, left, right):
    r"""``f(i) + g(i)`` in the module at ``i``."""
    return module(left + right)


def _pointwise_zero(module):
    r"""The zero of the module at ``i``."""
    return module.zero()


def _pointwise_negative(module, value):
    r"""``-f(i)`` in the module at ``i``."""
    return -value


def _pointwise_scalar_multiple(scalar, module, value):
    r"""``r f(i)`` in the module at ``i``."""
    return module.scalar_multiple(scalar, value)


def _pointwise_module_operations(combine):
    r"""The pointwise ``R``-module law on functions ``i |-> f(i) in M_i``.

    This is the one statement of the law for every module of functions with
    values in modules: the product ``prod_i M_i`` (whose points are families
    of components) and the module ``B^A`` of all maps ``A -> B``
    (``_function_module`` in ``general_modules.py``, Mathlib
    ``Function.module``, ``Mathlib/Algebra/Module/Pi.lean:52``) differ only in
    how a function is read at an index and assembled from its values, which
    ``combine`` supplies: ``combine(operation, operands)`` is the function
    whose value at ``i`` is ``operation(M_i, f_1(i), ..., f_k(i))``.  The
    operations are the four module-level functions above, so a consumer that
    reads an assembled function back (the function-space formula adapter)
    can recognize which operation built it.
    """
    return {
        "addition": lambda left, right: combine(_pointwise_sum, (left, right)),
        "zero": combine(_pointwise_zero, ()),
        "negation": lambda element: combine(_pointwise_negative, (element,)),
        "scalar_action": lambda scalar, element: combine(
            functools.partial(_pointwise_scalar_multiple, scalar), (element,)
        ),
    }


def _module_product_projection(product, factors, index):
    r"""Return the module projection induced by the underlying set projection."""
    match product:
        case _ if product in BiproductModules(product.base_ring()):
            return product.projection(index)
        case _:
            underlying_projection = product.underlying_set().projection(index)
            target = factors.value(index)
            return (
                product.module_category()
                .Mor(product, target)
                ._product_projection(underlying_projection)
            )


def _module_product_factor(product, factors, source, legs):
    r"""Factor a module cone through a product created on underlying sets."""
    assert legs.index_set() == factors.index_set(), (
        f"a cone over the product {product} needs one map for each factor, but the maps are indexed by "
        f"{legs.index_set()} and the factors by {factors.index_set()}"
    )
    forgetful = Modules(product.base_ring()).underlying_set()
    underlying_product = product.underlying_set()
    underlying_family = underlying_product.family()
    if not Sets().is_provably_finite(factors.index_set()) and (
        underlying_family.selected_diagram() is not None
        or underlying_family.constant_value() is not None
    ):
        from sage_extensions.categories.abstract_categories.cat import Cat
        from sage_extensions.categories.abstract_categories.functors import (
            DiscreteCategory,
        )
        from sage_extensions.categories.functors.core import NaturalTransformation

        shape = DiscreteCategory(factors.index_set())
        functor_category = Cat().Mor(shape, Sets())
        target = underlying_family.selected_diagram()
        if target is None:
            target = functor_category.constant_functor(
                underlying_family.constant_value()
            )
        constant_source = functor_category.constant_functor(forgetful(source))
        components = NaturalTransformation(
            constant_source,
            target,
            lambda obj: forgetful(legs.value(obj.value())),
        )
        # The underlying set product also lies in the more specific
        # CartesianProductsOfAdditiveMonoids category, whose `from_maps`
        # classifies additive arrows and therefore requires an AddMon-valued
        # transformation. Here the actual transported cone is Set-valued;
        # invoke the inherited Set-product universal construction at its
        # declared owner rather than misclassifying its component arrows.
        from sage_extensions.categories.sets.set_categories import (
            CartesianProductsOfSets,
        )

        underlying_factor = CartesianProductsOfSets.ParentMethods.from_maps(
            underlying_product, forgetful(source), components
        )
    else:
        # A module cone supplies these legs independently of an optional
        # set-valued diagram presentation; retain its exact pointwise map.
        underlying_factor = Sets().Mor(forgetful(source), underlying_product)(
            lambda point: underlying_product(
                lambda index: forgetful(legs.value(index))(point)
            )
        )
    return (
        source.module_category()
        .Mor(source, product)
        ._product_factor(
            underlying_factor,
            legs,
        )
    )


def _module_equalizer_created_by_underlying_sets(left_morphism, right_morphism):
    r"""Create the module equalizer from the equalizer of the underlying set maps."""
    from sage_extensions.categories.modules.general_modules import GeneralModules

    source = left_morphism.domain()
    ring = source.base_ring()
    forgetful = Modules(ring).underlying_set()
    set_equalizer = Sets().equalizer_construction(
        forgetful(left_morphism),
        forgetful(right_morphism),
    )
    underlying_equalizer = set_equalizer.object()
    equalizer = GeneralModules(ring).from_operations(
        underlying_equalizer,
        addition=lambda left, right: underlying_equalizer(source(left) + source(right)),
        zero=underlying_equalizer(source.zero()),
        negation=lambda element: underlying_equalizer(-source(element)),
        scalar_action=lambda scalar, element: underlying_equalizer(
            source.scalar_multiple(scalar, source(element))
        ),
    )
    shape = set_equalizer.diagram().domain()
    underlying_inclusion = set_equalizer.structure_morphism(shape.source())
    inclusion = (
        equalizer.module_category()
        .Mor(equalizer, source)
        ._equalizer_inclusion(
            underlying_inclusion,
            (left_morphism, right_morphism),
        )
    )
    return equalizer, inclusion


def _module_equalizer_factor(equalizer, source, source_leg, inclusion):
    r"""Factor an equalizing module map through a set-created equalizer."""
    return (
        source.module_category()
        .Mor(source, equalizer)
        ._equalizer_factor(
            source_leg,
            inclusion=inclusion,
        )
    )


@cached_function(key=lambda factors: (factors.index_set(), tuple(map(id, factors))))
def _module_tensor_product(factors):
    r"""Return $\bigotimes_{i \in I} M_i$ over the family's own index set."""
    return _module_tensor_product_with_data(factors)


def _module_tensor_product_with_data(
    factors,
    *,
    extra_categories=(),
    extra_construction_data=None,
):
    r"""Construct a represented tensor product with additional owned structure."""
    values = tuple(factors)
    assert values, (
        "the tensor product of an empty family of modules is not constructed here: give at least one factor"
    )
    ring = _owned_ring(values[0].base_ring())
    assert all(_owned_ring(factor.base_ring()) == ring for factor in values), (
        f"the tensor product of {values} is not defined: the factors must all be modules over {ring}, "
        f"the base ring of the first factor"
    )

    represented_free = all(_represented_framed_free(factor) for factor in values)
    represented_presented = all(
        _represented_finite_presentation(factor) for factor in values
    )
    if not represented_free and not represented_presented:
        from sage_extensions.categories.modules.tensor_quotients import _tensor_quotient

        return _tensor_quotient(
            factors,
            extra_categories=extra_categories,
            extra_construction_data=extra_construction_data,
        )

    tensor_labels = _tensor_label_set(factors)

    if represented_free:
        construction_data = {"tensor_factors": factors}
        if extra_construction_data is not None:
            construction_data.update(extra_construction_data)
        return ring._fresh_free_module_on(
            tensor_labels,
            _extra_categories=(TensorProductModules(ring), *tuple(extra_categories)),
            _extra_construction_data=construction_data,
        )

    # R-module tensoring preserves the zero object.  A presented zero module
    # may have arbitrarily many chosen generators and relations; the tensor
    # of its presentation with another one need not be constructed to obtain
    # the zero tensor product with its universal maps.
    if represented_presented and any(factor.is_zero() is True for factor in values):
        construction_data = {"tensor_factors": factors}
        if extra_construction_data is not None:
            construction_data.update(extra_construction_data)
        return ring._fresh_free_module_on(
            Sets.Δ[-1],
            _extra_categories=(TensorProductModules(ring), *tuple(extra_categories)),
            _extra_construction_data=construction_data,
        )

    label_sets = tuple(factor.module_generating_set() for factor in values)
    if not all(labels.cardinality().is_finite() for labels in label_sets):
        raise TypeError(
            f"the tensor product of {values} is computed only for finitely generated factors, but the "
            f"generating sets have cardinalities {tuple(labels.cardinality() for labels in label_sets)}"
        )

    ranking = factors.index_set().ranking_map()
    generators = ring._fresh_free_module_on(tensor_labels)
    relations = []

    # A relation of one factor, tensored with a generator chosen in each of
    # the others, is a relation of the product; over a family of presented
    # modules those exhaust the relations of the tensor product.
    for position, factor in enumerate(values):
        elsewhere_sets = tuple(
            labels for other, labels in enumerate(label_sets) if other != position
        )
        factor_relations = factor._selected_relation_morphism()
        assert factor_relations is not None, (
            f"the tensor product of {values} needs the relations of {factor}, but they are not known explicitly"
        )
        for relation_label in factor_relations.domain().module_generating_set():
            relation = factor_relations(
                factor_relations.domain().module_generator(relation_label)
            ).to_vector()
            for elsewhere in itertools.product(*elsewhere_sets):
                coefficients = {}
                for factor_label, coefficient in (
                    relation.parent()._selected_module_coefficients(relation).items()
                ):
                    section = (
                        elsewhere[:position] + (factor_label,) + elsewhere[position:]
                    )
                    label = tensor_labels(
                        lambda place, section=section: section[int(ranking(place))]
                    )
                    coefficients[label] = coefficient
                relations.append(generators.linear_combination(coefficients))

    from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
        _morphism_on_elements,
    )

    presentation = _morphism_on_elements(generators, tuple(relations))
    result = NotImplemented
    construction_data = {"tensor_factors": factors}
    if extra_construction_data is not None:
        construction_data.update(extra_construction_data)
    for presentation_owner in values:
        result = presentation_owner._presented_module_from_relation_morphism(
            presentation,
            extra_categories=(TensorProductModules(ring), *tuple(extra_categories)),
            extra_construction_data=construction_data,
        )
        if result is not NotImplemented:
            break
    assert result is not NotImplemented, (
        f"the tensor product of the finitely presented modules {values} over {ring} has no algorithm: "
        f"no factor can construct the quotient by the tensor relations"
    )
    return result


def _biproduct_label_set(factors):
    r"""Return $\coprod_{i \in I} S_i$, the generating set of $\bigoplus_i M_i$.

    A generator of the biproduct is a generator of exactly one factor,
    remembering which; that is a point of the coproduct of the family of
    generating sets over the index set.
    """
    return Sets().coproduct(
        indexed_family(
            factors.index_set(),
            lambda index: factors.value(index).module_generating_set(),
        )
    )


def _biproduct_label(label_set, index, label):
    return label_set(index, label)


class BiproductModules(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""The biproduct of the free module of rank one with itself."""
        free = Modules(self.base_ring()).an_object()
        return Modules(self.base_ring()).biproduct((free, free))

    def _repr_object_names(self):
        return f"chosen module biproducts over {self.base_ring()}"

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.direct_sum_objects import (
            DirectSumObjects,
        )

        return [DirectSumObjects(Modules(self.base_ring()))]

    class ParentMethods:
        _derived_construction_parameters = frozenset({"summands"})

        def __init__(self, biproduct_factors, **rest) -> None:
            self._preamble_biproduct_factors = biproduct_factors
            super().__init__(summands=biproduct_factors, **rest)

        def biproduct_factors(self):
            return self._preamble_biproduct_factors

        def biproduct_factor(self, index):
            return self.biproduct_factors()[index]

        def _binary_biproduct_labels(self):
            r"""Return the first and second labels of a selected binary biproduct."""
            labels = self.biproduct_factors().index_set()
            assert labels.cardinality() == cardinal(2), (
                f"the binary left/right operations of {self} need exactly two factors, "
                f"but its factor index set {labels} has cardinality {labels.cardinality()}"
            )
            ranking = labels.ranking_map()
            return ranking.inverse()(0), ranking.inverse()(1)

        def injection(self, index):
            r"""Return \(\iota_i : M_i \to \bigoplus_{j \in I} M_j\).

            A biproduct is a coproduct, so it has one injection per index, and
            each is an arrow out of that factor itself.
            """
            summand = self.biproduct_factor(index)
            labels = self.module_generating_set()
            return summand.module_category().Mor(summand, self)(
                lambda label: self.module_generator(
                    _biproduct_label(labels, index, label)
                )
            )

        def projection(self, index):
            r"""Return \(\pi_i : \bigoplus_{j \in I} M_j \to M_i\)."""
            summand = self.biproduct_factor(index)
            place = self.module_generating_set().index_set()(index)

            def image(label):
                if label.summand_index() == place:
                    return summand.module_generator(label.summand_element())
                return summand.zero()

            return self.module_category().Mor(self, summand)(image)

        def left_inclusion(self):
            r"""Return the injection at the first selected factor."""
            left, _right = self._binary_biproduct_labels()
            return self.injection(left)

        def right_inclusion(self):
            r"""Return the injection at the second selected factor."""
            _left, right = self._binary_biproduct_labels()
            return self.injection(right)

        left_injection = left_inclusion
        right_injection = right_inclusion

        def left_projection(self):
            r"""Return the projection onto the first selected factor."""
            left, _right = self._binary_biproduct_labels()
            return self.projection(left)

        def right_projection(self):
            r"""Return the projection onto the second selected factor."""
            _left, right = self._binary_biproduct_labels()
            return self.projection(right)

        def from_coproduct_cocone(self, legs, *, codomain=None):
            r"""The unique map \(\bigoplus_i M_i \to X\) with the stated legs.

            A cocone under the biproduct is the family of legs
            \(f_i : M_i \to X\), indexed the way the factors are, so that is
            the datum this takes.  A generator of the biproduct lies in one
            factor and remembers which, so its image is the value of that
            index's leg.

            Supply ``codomain`` for an empty family, whose legs alone do
            not determine its apex.
            """
            factors = self.biproduct_factors()
            legs = _finite_factor_family(legs, name="Coproduct cocone legs")
            assert legs.index_set() == factors.index_set(), (
                f"a map out of the direct sum {self} needs one map for each summand, but the maps are indexed "
                f"by {legs.index_set()} and the summands by {factors.index_set()}"
            )
            target = codomain
            if target is None:
                if factors.index_set().cardinality() == cardinal(0):
                    raise ValueError("an empty coproduct cocone needs its codomain")
                target = legs[factors.index_set().ranking_map().inverse()(0)].codomain()
            assert all(leg.codomain() is target for leg in legs), (
                f"a map out of the direct sum {self} needs maps into one module, but the maps {legs} "
                f"do not all have codomain {target}"
            )
            assert all(
                legs.value(index).domain() is factors.value(index)
                for index in factors.index_set()
            ), (
                f"a map out of the direct sum {self} needs the map at index i to start at the i-th summand, "
                f"but the maps {legs} do not"
            )

            return self.module_category().Mor(self, target)(
                lambda label: legs.value(label.summand_index())(
                    factors.value(label.summand_index()).module_generator(
                        label.summand_element()
                    )
                )
            )

        def from_product_cone(self, legs, *, domain=None):
            r"""The unique map \(X \to \prod_i M_i\) with the stated legs.

            A cone over the biproduct is the family of legs
            \(f_i : X \to M_i\), indexed the way the factors are.  The image
            of a generator of the apex is the sum over the index set of the
            coordinates of its images, each placed at its own index.

            Supply ``domain`` for an empty family, whose legs alone do
            not determine its apex.
            """
            factors = self.biproduct_factors()
            legs = _finite_factor_family(legs, name="Product cone legs")
            assert legs.index_set() == factors.index_set(), (
                f"a map into the direct sum {self} needs one map for each summand, but the maps are indexed "
                f"by {legs.index_set()} and the summands by {factors.index_set()}"
            )
            source = domain
            if source is None:
                if factors.index_set().cardinality() == cardinal(0):
                    raise ValueError("an empty product cone needs its domain")
                source = legs[factors.index_set().ranking_map().inverse()(0)].domain()
            assert all(leg.domain() is source for leg in legs), (
                f"a map into the direct sum {self} needs maps from one module, but the maps {legs} "
                f"do not all have domain {source}"
            )
            assert all(
                legs.value(index).codomain() is factors.value(index)
                for index in factors.index_set()
            ), (
                f"a map into the direct sum {self} needs the map at index i to end at the i-th summand, "
            )
            f"but the maps {legs} do not"

            labels = self.module_generating_set()

            def image(source_label):
                generator = source.module_generator(source_label)
                coefficients = {}
                for index in factors.index_set():
                    leg_image = (
                        factors.value(index)
                        .framing_morphism()
                        .lift(legs.value(index)(generator))
                    )
                    for target_label, coefficient in (
                        leg_image.parent()
                        ._selected_module_coefficients(leg_image)
                        .items()
                    ):
                        coefficients[_biproduct_label(labels, index, target_label)] = (
                            coefficient
                        )
                return self.linear_combination(coefficients)

            return source.module_category().Mor(source, self)(image)

        def from_summands(self, left_map, right_map):
            r"""Return the unique map ``self -> X`` extending both summand maps."""
            labels = self._binary_biproduct_labels()
            legs = indexed_family(
                self.biproduct_factors().index_set(),
                lambda label: left_map if label == labels[0] else right_map,
                name="Binary coproduct cocone legs",
            )
            return self.from_coproduct_cocone(legs)

        def to_product(self, left_map, right_map):
            r"""Return the unique map ``X -> self`` with the specified projections."""
            labels = self._binary_biproduct_labels()
            legs = indexed_family(
                self.biproduct_factors().index_set(),
                lambda label: left_map if label == labels[0] else right_map,
                name="Binary product cone legs",
            )
            return self.from_product_cone(legs)


@cached_function(
    key=lambda factors, base_ring: (base_ring, factors.index_set(), tuple(factors))
)
def _module_biproduct(factors, base_ring):
    r"""Return $\bigoplus_{i \in I} M_i$ over the family's own index set."""
    return _module_biproduct_with_data(factors, base_ring=base_ring)


def _module_biproduct_with_data(
    factors,
    *,
    base_ring,
    extra_categories=(),
    extra_construction_data=None,
):
    r"""Construct a represented biproduct with additional owned structure."""
    values = tuple(factors)
    ring = _owned_ring(base_ring)
    assert all(_owned_ring(factor.base_ring()) == ring for factor in values), (
        f"the direct sum of {values} is not defined: the summands must all be modules over {ring}, "
        "the base ring of the selected module category"
    )

    if not values:
        # The zero module is both the initial and terminal object of R-Mod.
        # Its free rank-zero presentation retains the empty family as actual
        # biproduct data; no first factor exists from which to infer R.
        return ring._fresh_free_module_on(
            Sets.Δ[-1],
            _biproduct_factors=factors,
            _extra_categories=extra_categories,
            _extra_construction_data=extra_construction_data,
        )

    labels = _biproduct_label_set(factors)
    result = values[0]._free_biproduct_over(
        labels,
        factors,
        extra_categories=extra_categories,
        extra_construction_data=extra_construction_data,
    )
    if result is NotImplemented:
        for factor in values:
            result = factor._presented_biproduct_over(
                labels,
                factors,
                extra_categories=extra_categories,
                extra_construction_data=extra_construction_data,
            )
            if result is not NotImplemented:
                break
    assert result is not NotImplemented, (
        f"the direct sum of {values} over {ring} has no algorithm: the summands are neither all free "
        f"with chosen bases nor all finitely presented"
    )
    return result


def _biproduct_morphism(left_morphism, right_morphism, source=None, target=None):
    if source is None:
        source = Modules(left_morphism.domain().base_ring()).biproduct(
            (left_morphism.domain(), right_morphism.domain())
        )
    if target is None:
        target = Modules(left_morphism.codomain().base_ring()).biproduct(
            (left_morphism.codomain(), right_morphism.codomain())
        )

    source_left, source_right = source._binary_biproduct_labels()
    target_left, target_right = target._binary_biproduct_labels()
    if (
        source.biproduct_factor(source_left) is not left_morphism.domain()
        or source.biproduct_factor(source_right) is not right_morphism.domain()
    ):
        raise ValueError(
            f"the direct sum of {left_morphism} and {right_morphism} cannot start at {source}: its summands "
            f"must be {left_morphism.domain()} and {right_morphism.domain()}"
        )
    if (
        target.biproduct_factor(target_left) is not left_morphism.codomain()
        or target.biproduct_factor(target_right) is not right_morphism.codomain()
    ):
        raise ValueError(
            f"the direct sum of {left_morphism} and {right_morphism} cannot end at {target}: its summands "
            f"must be {left_morphism.codomain()} and {right_morphism.codomain()}"
        )

    # f + g = i_L f p_L + i_R g p_R, read on the biproduct's own projections and
    # injections, so it does not depend on how the source labels its generators.
    left_projection, right_projection = (
        source.projection(source_left),
        source.projection(source_right),
    )
    left_injection, right_injection = (
        target.injection(target_left),
        target.injection(target_right),
    )
    return source.module_category().Mor(source, target)(
        lambda label: (
            left_injection(
                left_morphism(left_projection(source.module_generator(label)))
            )
            + right_injection(
                right_morphism(right_projection(source.module_generator(label)))
            )
        )
    )


class MatrixSpaces(OwnedCategoryOverBaseRing):
    r"""Mor objects between finitely generated framed free ``R``-modules.

    Over noncommutative ``R`` the Hom is central-linear, not a left
    ``R``-module. For ``R=M_2(ZZ)`` the center itself is a represented
    commutative subring and determines that scalar placement.

    EXAMPLES::

        sage: from sage_extensions.categories.algebras.algebras import MatrixAlgebras
        sage: R = MatrixAlgebras(ZZ).an_object()
        sage: MatrixSpaces(R).super_categories()[0].base_ring() is R.ring_center()
        True
    """

    def an_object(self):
        r"""The one-by-one matrices over the base ring."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        match _is_group_algebra(self.base_ring()):
            case True:
                modules = OwnedCategoryOverBaseRing.__classcall__(
                    Modules, self.base_ring()
                )
                free = self.base_ring().free_module(1)
            case False:
                free = modules.an_object()
        return modules.Mor(free, free)

    def _repr_object_names(self):
        return f"matrix Mor objects over {self.base_ring()}"

    def super_categories(self):
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )

        ring = self.base_ring()
        match ring in OwnedRings().Commutative():
            case True:
                return [
                    InternalMorModules(ring),
                    FramedFreeModules(ring).FinitelyGenerated(),
                ]
            case False:
                # Hom_R(F,G) is canonically additive and central-linear,
                # not a left R-module when R is noncommutative.
                return [LinearMorModules(ring.ring_center())]

    class ParentMethods:
        def projectivity_decision(self):
            r"""Decide projectivity of ``Hom_R(F_R(S), F_R(T))`` from its endpoints.

            Over a commutative ring ``R``, the Mor object between finite
            framed free modules is free on the matrix units ``T x S``, hence
            projective.  The answer reads the base ring and the endpoints,
            never this Mor's placement.
            """
            ring = self.domain().base_ring()
            match ring.is_commutative():
                case True if _coordinate_framed_free_module(
                    self.domain(), ring
                ) and _coordinate_framed_free_module(self.codomain(), ring):
                    return True
                case _:
                    return AtomicProposition("is_projective", self)

        def row_index_set(self):
            return self.codomain().module_generating_set()

        def column_index_set(self):
            return self.domain().module_generating_set()

        def nrows(self):
            return _owned_engine_element(
                SageZZ,
                SageZZ(int(self.row_index_set().cardinality())),
            )

        def ncols(self):
            return _owned_engine_element(
                SageZZ,
                SageZZ(int(self.column_index_set().cardinality())),
            )

        def matrix_shape(self):
            integers = _owned_integers()
            return Sets().product((integers, integers))((self.nrows(), self.ncols()))

        def matrix_unit(self, row_label, column_label):
            label = self.module_generating_set()((row_label, column_label))
            return self.module_generator(label)

        def _selected_module_coefficients(self, morphism):
            r"""The entries of a linear map, keyed by the matrix units ``(t, s)``."""
            return _matrix_coefficients(self, morphism)

        def from_rows(self, rows):
            r"""Construct the matrix morphism with the stated row entries."""
            rows = tuple(tuple(row) for row in rows)
            if len(rows) != self.nrows() or any(
                len(row) != self.ncols() for row in rows
            ):
                raise ValueError(
                    f"the rows {rows} do not form a matrix in {self}: it has shape {self.matrix_shape()}"
                )
            ring = self.base_ring()
            row_labels = tuple(self.row_index_set())
            column_labels = tuple(self.column_index_set())
            images = {}
            for column_position, column_label in enumerate(column_labels):
                images[column_label] = self.codomain().linear_combination(
                    {
                        row_label: ring(rows[row_position][column_position])
                        for row_position, row_label in enumerate(row_labels)
                    }
                )
            return self(images)

        def from_tensor(self, coordinate_tensor):
            r"""Read a compatible type-``(1,1)`` tensor as this linear map.

            This is an explicit interpretation, not a second matrix object:
            the returned object is an element of this Mor object.
            """
            if coordinate_tensor.tensor_valence() != (NN**2)((1, 1)):
                raise TypeError(
                    f"{coordinate_tensor} cannot be read as a matrix in {self}: it must be a tensor of type (1,1), "
                    f"but its type is {coordinate_tensor.tensor_valence()}"
                )
            if coordinate_tensor.base_ring() is not self.base_ring():
                raise TypeError(
                    f"{coordinate_tensor} cannot be read as a matrix in {self}: it is over "
                    f"{coordinate_tensor.base_ring()}, not over {self.base_ring()}"
                )
            # A type-(1,1) tensor represents a morphism here when its
            # contravariant index has the codomain's rank and its covariant
            # index the domain's rank.
            shape = coordinate_tensor.tensor_shape()
            if shape[0] != self.nrows() or shape[1] != self.ncols():
                raise ValueError(
                    f"{coordinate_tensor} cannot be read as a matrix in {self}: its shape {shape} is not {self.matrix_shape()}"
                )
            return self.from_rows(
                tuple(
                    tuple(
                        coordinate_tensor[row, column] for column in range(self.ncols())
                    )
                    for row in range(self.nrows())
                )
            )

        def from_flat_entries(self, entries):
            entries = tuple(entries)
            expected = self.nrows() * self.ncols()
            if len(entries) != expected:
                raise ValueError(
                    f"a matrix in {self} of shape {self.matrix_shape()} has {expected} entries, but {len(entries)} were given"
                )
            return self.from_rows(
                tuple(
                    entries[row * self.ncols() : (row + 1) * self.ncols()]
                    for row in range(self.nrows())
                )
            )

    class ElementMethods:
        def matrix(self):
            r"""Return the canonical matrix Mor in the selected finite framings.

            This operation exists only on MatrixSpaces. A map between
            arbitrary structured objects does not inherit it; the coordinate
            view is the induced map between the canonical finite free framing
            sources.
            """
            source = self.domain().framing_source()
            target = self.codomain().framing_source()
            coordinate_parent = source.module_category().Mor(source, target)
            assert coordinate_parent in MatrixSpaces(self.parent().base_ring()), (
                f"the matrix of {self} is not defined: Mor({source}, {target}) between the free modules on the "
                f"generators is not a space of matrices over {self.parent().base_ring()}"
            )
            if self.parent() is coordinate_parent:
                return self
            return coordinate_parent.from_rows(
                tuple(
                    tuple(
                        self.matrix_entry(row_label, column_label)
                        for column_label in self.parent().column_index_set()
                    )
                    for row_label in self.parent().row_index_set()
                )
            )

        def nrows(self):
            return self.parent().nrows()

        def ncols(self):
            return self.parent().ncols()

        def matrix_shape(self):
            return self.parent().matrix_shape()

        def change_ring(self, ring):
            r"""Return the same finite coordinate matrix over ``ring``."""
            target = ring.matrix_space(self.parent().nrows(), self.parent().ncols())
            return target.from_rows(
                (
                    ring(self.matrix_entry(row_label, column_label))
                    for column_label in self.parent().column_index_set()
                )
                for row_label in self.parent().row_index_set()
            )

        @cached_method
        def _matrix_column_coordinates(self, column_label):
            r"""The coordinates of the image of the basis vector ``e_s``: the column ``s`` as a function of the rows."""
            column_label = _matrix_index(self.parent().column_index_set(), column_label)
            generator_image = self._generator_image
            image = (
                generator_image(column_label)
                if generator_image is not None
                else self(self.domain().module_generator(column_label))
            )
            return self.codomain()(image).to_vector()

        def matrix_entry(self, row_label, column_label):
            row_label = _matrix_index(self.parent().row_index_set(), row_label)
            column_label = _matrix_index(self.parent().column_index_set(), column_label)
            return self._matrix_column_coordinates(column_label)(row_label)

        def __getitem__(self, index):
            r"""The entry at the label pair ``(row, column)``."""
            row, column = index
            return self.matrix_entry(row, column)

        def row(self, row_label):
            row_label = _matrix_index(self.parent().row_index_set(), row_label)
            dual = self.domain().dual_module()
            return dual.linear_combination(
                {
                    column_label: self.matrix_entry(row_label, column_label)
                    for column_label in self.parent().column_index_set()
                    if self.matrix_entry(row_label, column_label)
                }
            )

        def column(self, column_label):
            column_label = _matrix_index(self.parent().column_index_set(), column_label)
            return self(self.domain().module_generator(column_label))

        def rows(self):
            return finite_indexed_family(
                self.parent().row_index_set(),
                self.row,
                name="Matrix rows",
            )

        def columns(self):
            return finite_indexed_family(
                self.parent().column_index_set(),
                self.column,
                name="Matrix columns",
            )

        def determinant(self):
            if self.parent().nrows() != self.parent().ncols():
                raise ValueError(
                    f"the determinant of {self} is not defined: the matrix has shape {self.parent().matrix_shape()}, not square"
                )
            from sage_extensions.rings.real import RR

            if self.parent().base_ring() is RR:
                return RR._matrix_determinant(
                    tuple(
                        tuple(
                            self.matrix_entry(row, column)
                            for column in self.parent().column_index_set()
                        )
                        for row in self.parent().row_index_set()
                    )
                )
            backend = _engine_matrix(self)
            return _owned_engine_element(self.parent().base_ring(), backend.det())

        det = determinant

        def multiplicative_order(self):
            r"""Return the exact multiplicative order of this square matrix when finite.

            The order is the order of the cyclic matrix group generated by this
            matrix.  Sage's raw-matrix ``multiplicative_order`` supports fewer
            coefficient rings (notably excluding rational matrices), while its
            matrix-group engine owns the corresponding group computation.
            """
            if self.parent().nrows() != self.parent().ncols():
                raise ValueError(
                    f"the multiplicative order of {self} is not defined: the matrix has shape "
                    f"{self.parent().matrix_shape()}, not square"
                )
            order = _matrix_group((_engine_matrix(self),)).order()
            from sage.rings.infinity import Infinity
            from sage.rings.integer_ring import ZZ as SageZZ

            if order == Infinity:
                return Infinity
            return _owned_engine_element(SageZZ, SageZZ(order))

        def matrix_rank(self):
            from sage.rings.integer_ring import ZZ as SageZZ

            integers = _owned_integers()
            return _owned_engine_element(integers, SageZZ(_engine_matrix(self).rank()))

        def solve_right(self, target):
            r"""Return ``x`` in the domain with ``self(x)=target``."""
            from sage.modules.free_module_element import vector as sage_vector

            target = (
                target
                if target.parent() is self.codomain()
                else self.codomain()(target)
            )
            ring = self.parent().base_ring()
            coordinates = target.to_vector()
            rhs = sage_vector(
                _linear_algebra_ring(ring),
                [
                    _linear_algebra_element(ring, coordinates(label))
                    for label in self.parent().row_index_set()
                ],
            )
            solution = _engine_matrix(self).solve_right(rhs)
            return self.domain().linear_combination(
                {
                    label: _owned_engine_element(ring, solution[position])
                    for position, label in enumerate(self.parent().column_index_set())
                }
            )

        def _kernel_spanning_family(self):
            r"""Return a private owned finite family spanning ``ker(self)``."""

            ring = self.parent().base_ring()
            if ring in LocalizationRings():
                source_ring = ring.localization_source()
                row_labels = self.parent().row_index_set()
                column_labels = self.parent().column_index_set()
                entries = tuple(
                    tuple(
                        self.matrix_entry(row_label, column_label)
                        for column_label in column_labels
                    )
                    for row_label in row_labels
                )
                fractions = tuple(
                    tuple(ring.localization_fraction_data(entry) for entry in row)
                    for row in entries
                )
                denominators = tuple(
                    denominator for row in fractions for _numerator, denominator in row
                )

                cleared_rows = []
                for row in fractions:
                    cleared_row = []
                    for numerator, denominator in row:
                        multiplier = source_ring.one()
                        skipped = False
                        for candidate in denominators:
                            if not skipped and candidate == denominator:
                                skipped = True
                                continue
                            multiplier *= candidate
                        cleared_row.append(numerator * multiplier)
                    cleared_rows.append(tuple(cleared_row))

                source_domain = source_ring._fresh_free_module_on(column_labels)
                source_codomain = source_ring._fresh_free_module_on(row_labels)
                source_map = (
                    source_domain.module_category()
                    .Mor(source_domain, source_codomain)
                    .from_rows(tuple(cleared_rows))
                )
                source_kernel = source_map.kernel()
                kernel_labels = source_kernel.module_generating_set()
                inclusion = source_kernel.inclusion()
                localized_domain = self.domain()
                localization_map = ring.localization_map()

                def localized_kernel_element(label):
                    coordinates = inclusion(
                        source_kernel.module_generator(label)
                    ).to_vector()
                    return localized_domain.linear_combination(
                        {
                            column_label: localization_map(coefficient)
                            for column_label, coefficient in coordinates.parent()
                            ._selected_module_coefficients(coordinates)
                            .items()
                        }
                    )

                return finite_indexed_family(
                    kernel_labels,
                    localized_kernel_element,
                    name=f"Localized kernel spanning family of {self}",
                )

            from sage_extensions.rings.real import RR

            if ring is RR:
                labels = tuple(self.parent().column_index_set())
                rows = tuple(
                    tuple(self.matrix_entry(row, column) for column in labels)
                    for row in self.parent().row_index_set()
                )
                reduced, pivots = _represented_real_rref(rows, len(labels), ring)
                free = tuple(
                    column for column in range(len(labels)) if column not in pivots
                )
                positions = Sets.Δ[len(free) - 1]

                def kernel_vector(position):
                    values = [ring.zero()] * len(labels)
                    column = free[int(position)]
                    values[column] = ring.one()
                    for row, pivot in enumerate(pivots):
                        values[pivot] = -reduced[row][column]
                    return self.domain().linear_combination(
                        dict(zip(labels, values, strict=True))
                    )

                return finite_indexed_family(
                    positions,
                    kernel_vector,
                    name=f"Kernel spanning family of {self}",
                )

            basis = (
                _engine_matrix(self)
                .change_ring(_linear_algebra_ring(ring))
                .right_kernel()
                .basis_matrix()
            )
            labels = self.parent().column_index_set()
            positions = Sets.Δ[int(basis.nrows()) - 1]
            return finite_indexed_family(
                positions,
                lambda position: self.domain().linear_combination(
                    {
                        label: _owned_engine_element(ring, basis[int(position), column])
                        for column, label in enumerate(labels)
                    }
                ),
                name=f"Kernel spanning family of {self}",
            )

        def symmetrized_right_multiplication(self):
            r"""Return the linear map ``X |-> X*A + (X*A).transpose()``.

            Here ``A`` is this matrix, from ``V`` to ``W``. Parameters lie
            in ``Hom(W,V)`` and values in ``End(V)``. Transpose uses the
            chosen finite framings. The base ring must be commutative.

            ``equation.solution_fibre(B)`` retains the whole affine solution
            set, its translation module and its torsor when nonempty.
            After scalar extension, ``fibre.integral_members(j)`` intersects
            that fibre with the chosen integral parameter inclusion ``j``.
            Its kernel alone supplies only the homogeneous solutions.

            This presents the linear operator used by
            ``sage-indefinite-port.indefinite.isotropic_lifts`` through
            module composition, transpose, kernel and preimage.

            EXAMPLES::

                sage: A = ZZ.matrix_space(2).from_rows(((1, 0), (0, 1)))
                sage: equation = A.symmetrized_right_multiplication()
                sage: equation.kernel().module_rank() == NN(1)
                True
                sage: B = A + A
                sage: equation(equation.preimage(B)) == B
                True
                sage: fibre = equation.solution_fibre(B)
                sage: fibre.base_point() in fibre
                True
                sage: X = A.parent().from_rows(((0, 1), (-1, 0)))
                sage: equation(X) == equation.codomain().zero()
                True
                sage: fibre.base_point() + X in fibre
                True
            """
            ring = self.parent().base_ring()
            if ring not in OwnedRings().Commutative():
                raise ValueError(
                    "symmetrized multiplication requires a commutative base ring"
                )
            modules = Modules(ring)
            parameters = modules.Mor(self.codomain(), self.domain())
            values = modules.Mor(self.domain(), self.domain())

            def image(label):
                product = parameters.module_generator(label) * self
                return product + product.transpose()

            return modules.Mor(parameters, values)(image)

        def transpose(self):

            source = self.codomain()
            codomain = self.domain()
            target = source.module_category().Mor(source, codomain)
            _require_matrix_mor(target)
            return target.from_rows(
                tuple(
                    tuple(
                        self.matrix_entry(row_label, column_label)
                        for row_label in self.parent().row_index_set()
                    )
                    for column_label in self.parent().column_index_set()
                )
            )

        T = transpose

        def inverse(self):
            r"""Return the inverse matrix morphism with reversed endpoints.

            Exact scalar comparisons and division are retained through
            the generic computation when a symbolic model is inexact.

            EXAMPLES::

                sage: from sage_extensions.rings.real import RR
                sage: V = RR ** 2
                sage: A = V.module_category().Mor(V, V).from_rows(((RR.pi(), 1), (0, 1)))
                sage: B = A.inverse()
                sage: assert B.domain() is V and B.codomain() is V
                sage: assert all(A(B(v)) == v and B(A(v)) == v for v in V.module_generators())
                sage: Z = RR ** 0
                sage: z = Z.module_category().Mor(Z, Z).from_rows(())
                sage: assert z.inverse()(Z.zero()) == Z.zero()
            """
            if self.parent().nrows() != self.parent().ncols():
                raise ValueError(
                    f"{self} has no inverse: the matrix has shape {self.parent().matrix_shape()}, not square"
                )

            ring = self.parent().base_ring()
            backend = (
                _engine_matrix(self).change_ring(_linear_algebra_ring(ring)).inverse()
            )
            source = self.codomain()
            codomain = self.domain()
            target = _require_matrix_mor(source.module_category().Mor(source, codomain))
            return target.from_rows(
                (
                    _owned_engine_element(ring, backend[row, column])
                    for column in range(target.ncols())
                )
                for row in range(target.nrows())
            )

        __invert__ = inverse

        def __matmul__(self, other):

            result = ModuleMorphism.__mul__(self, other)
            if result is NotImplemented:
                raise ValueError(
                    f"the product {self} @ {other} is not defined: {self} has shape {self.parent().matrix_shape()} "
                    f"and {other} lies in {other.parent()}"
                )
            return result

        @cached_method
        def smith_form(self):
            r"""Return the named product ``(D,U,V)`` from invariant-factor presentation normalization.

            The comparison maps belong to this fixed morphism. Retain them
            across integral-preimage requests instead of normalizing the same
            presentation for every right-hand side.
            """

            ring = self.parent().base_ring()
            assert ring in PrincipalIdealDomains(), (
                f"the Smith normal form of {self} exists only over a PID, and {ring} is not known to be one"
            )
            presented = self.codomain()._represented_cokernel_of_morphism(self)
            assert presented is not NotImplemented, (
                f"the Smith normal form of {self} over {ring} has no algorithm: its cokernel cannot be computed "
                f"from {self.codomain()}"
            )
            normalization = presented.invariant_factor_presentation()
            diagonal = normalization.codomain().arrow()
            # For a square in Arr(Mod_R), right * original = diagonal * left.
            # Thus D = right * A * left^{-1} in matrix notation.
            left_change = normalization.forward().right()
            right_change = normalization.inverse().forward().left()
            labels = finite_ordered_set(
                (
                    "diagonal",
                    "left_change",
                    "right_change",
                )
            )
            factors = {
                "diagonal": diagonal.parent(),
                "left_change": left_change.parent(),
                "right_change": right_change.parent(),
            }
            values = {
                "diagonal": diagonal,
                "left_change": left_change,
                "right_change": right_change,
            }
            product = Sets().product(
                indexed_family(labels, factors.__getitem__, name="Smith-form factors")
            )
            return product(values.__getitem__)

        def smith_normal_form(self):
            return self.smith_form()["diagonal"]

        def invariant_factors(self):
            diagonal = self.smith_normal_form()
            zero = self.parent().base_ring().zero()
            count = min(diagonal.parent().nrows(), diagonal.parent().ncols())
            positions = Sets.Δ[count - 1]
            retained = positions.filtered(
                lambda index: diagonal[int(index), int(index)] != zero,
                name="Nonzero Smith-diagonal positions",
            )
            return finite_indexed_family(
                retained,
                lambda index: diagonal[int(index), int(index)],
                name="Invariant factors indexed by Smith-diagonal position",
            )


class MatrixEndomorphismSpaces(OwnedCategoryOverBaseRing):
    r"""The matrix realization of ``End_R(F)`` as an algebra over ``Z(R)``.

    EXAMPLES::

        sage: from sage_extensions.categories.algebras.algebras import MatrixAlgebras
        sage: from sage_extensions.categories.group.additive_mors import AdditiveEndomorphismRings
        sage: R = MatrixAlgebras(ZZ).an_object()
        sage: MatrixEndomorphismSpaces(R).super_categories()[1] is AdditiveEndomorphismRings(R.ring_center())
        True
        sage: E = MatrixEndomorphismSpaces(R).an_object()
        sage: E in MatrixEndomorphismSpaces(R) and E in MatrixSpaces(R)
        True
        sage: E.domain().base_ring() is R and E.domain() is E.codomain()
        True
    """

    def an_object(self):
        r"""The endomorphisms of the free module of rank one."""
        from sage_extensions.categories.modules.pure.modules import Modules

        modules = Modules(self.base_ring())
        match _is_group_algebra(self.base_ring()):
            case True:
                modules = OwnedCategoryOverBaseRing.__classcall__(
                    Modules, self.base_ring()
                )
                free = self.base_ring().free_module(1)
            case False:
                free = modules.an_object()
        return modules.Mor(free, free)

    def _repr_object_names(self):
        return f"matrix endomorphism objects over {self.base_ring()}"

    def super_categories(self):
        from sage_extensions.categories.group.additive_mors import (
            AdditiveEndomorphismRings,
        )

        # MatrixSpaces states the entrywise/module data. Composition gives
        # the endomorphism algebra over the retained centre, including
        # when the coefficient ring itself is noncommutative.
        ring = self.base_ring()
        return [MatrixSpaces(ring), AdditiveEndomorphismRings(ring.ring_center())]

    _MorCategory = MatrixEndomorphismMorCategoryConstruction

    class ParentMethods:
        def _compose_endomorphisms(self, left, right):
            r"""Compose matrix endomorphisms as linear maps, not merely additive maps."""
            return self._compose_module_endomorphisms(left, right)

        def _owned_scalar_multiple(self, scalar, morphism):
            r"""Scale matrix endomorphisms as linear maps, not merely additive maps."""
            return self._module_scalar_multiple(scalar, morphism)

        def _commutativity_decision(self):
            r"""Return whether \(\operatorname{End}_R(F)\cong M_n(R^{op})\) commutes.

            The base is not assumed commutative here, so the answer depends on
            both the ring and the rank, and each rank is its own statement.

            Rank zero gives the zero ring, which commutes whatever \(R\) is.
            Rank one gives \(R\) acting on itself, whose endomorphisms are the
            right multiplications, so it commutes exactly when \(R\) does; a
            ring that does not decide its own commutativity leaves this
            undecided too, and says so through the answer it gives.  From rank
            two the matrix units satisfy \(e_{11}e_{12}=e_{12}\) and
            \(e_{12}e_{11}=0\), so commuting forces \(e_{12}=0\) and hence
            \(1=0\): the ring commutes exactly when \(R\) is the zero ring.
            """
            ring = self.base_ring()
            match self.nrows():
                case 0:
                    return True
                case 1:
                    return ring.is_commutative()
                case _:
                    return ring.one() == ring.zero()

        def identity_matrix(self):
            return self.identity()

        def diagonal(self, entries):
            values = tuple(entries)
            labels = tuple(self.column_index_set())
            if len(values) != len(labels):
                raise ValueError(
                    f"a diagonal matrix in {self} needs {len(labels)} entries, one for each basis element, "
                    f"but {len(values)} were given"
                )
            ring = self.base_ring()
            return self(
                {
                    label: self.codomain().scalar_multiple(
                        ring(values[position]),
                        self.codomain().module_generator(label),
                    )
                    for position, label in enumerate(labels)
                }
            )

    class ElementMethods:
        def _unit_decision(self) -> bool:
            r"""Return whether this endomorphism is invertible in \(\operatorname{End}_R(M)\).

            A unit of a ring is an element with a two-sided inverse in it, and
            an endomorphism has one in \(\operatorname{End}_R(M)\) exactly when
            it is an isomorphism of \(M\): a bijective linear map has a
            set-theoretic inverse, that inverse is linear, and the two compose
            to the identity on either side.  So this is decided as injectivity
            together with surjectivity, which are the kernel and the cokernel
            of the morphism, and not from a determinant -- that is a criterion
            for the special case of a finite free module, carrying hypotheses
            the definition of a unit does not.

            Reading the units of \(\operatorname{End}_R(M)\) is what gives
            \(\operatorname{Aut}_R(M)\) its group structure, through the unit
            group functor on the owned ring category.
            """
            return self.is_injective() and self.is_surjective()

        def trace(self):
            ring = self.parent().base_ring()
            return sum(
                (
                    self.matrix_entry(label, label)
                    for label in self.parent().row_index_set()
                ),
                ring.zero(),
            )


def _matrix_index(index_set, key):
    r"""Read a row or column key as a label of ``index_set``; a position is read through ``index_set[i]`` by the caller."""
    assert key in index_set, (
        f"{key!r} is not a label of {index_set}: matrix entries are keyed by label"
    )
    return index_set(key)


def _represented_real_rref(coefficients, column_count, ring):
    r"""Reduce owned real rows, refusing a pivot whose zero status is unknown."""
    rows = [list(row) for row in coefficients]
    pivots = []
    for column in range(column_count):
        candidates = tuple(
            row
            for row in range(len(pivots), len(rows))
            if (rows[row][column] == ring.zero()) is False
        )
        if not candidates:
            assert all(
                (rows[row][column] == ring.zero()) is True
                for row in range(len(pivots), len(rows))
            ), "the real linear-system pivot is undecided"
            continue
        pivot_row = len(pivots)
        selected = candidates[0]
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = [
            ring._divide_by_nonzero(value, pivot) for value in rows[pivot_row]
        ]
        for row in range(len(rows)):
            if row != pivot_row:
                coefficient = rows[row][column]
                rows[row] = [
                    entry - coefficient * pivot_entry
                    for entry, pivot_entry in zip(
                        rows[row], rows[pivot_row], strict=True
                    )
                ]
        pivots.append(column)
        if len(pivots) == len(rows):
            break
    return tuple(tuple(row) for row in rows), tuple(pivots)


def _engine_matrix(morphism):
    r"""Privately materialize the selected framed realization in one engine call.

    Column ``s`` is the coordinate vector of the image of ``e_s``, read once
    in row-label order; the rows of the engine matrix are read off those
    columns, so no entry is looked up by its pair of labels.
    """
    from sage.matrix.constructor import matrix as sage_matrix

    morphism = morphism._framed_coordinate_morphism()
    parent = _require_matrix_mor(morphism.parent())
    if parent not in MatrixSpaces(parent.base_ring()):
        raise TypeError(
            f"{morphism} has no matrix: it is a map in {parent}, which is not a space of matrices over "
            f"{parent.base_ring()}"
        )
    ring = parent.base_ring()
    columns = tuple(
        tuple(morphism._matrix_column_coordinates(column_label))
        for column_label in parent.column_index_set()
    )
    return sage_matrix(
        _linear_algebra_ring(ring),
        parent.nrows(),
        parent.ncols(),
        [
            _linear_algebra_element(ring, entry)
            for row in zip(*columns, strict=True)
            for entry in row
        ],
    )


def _morphism_from_engine_matrix(mor, backend):
    r"""Raise one engine matrix into the matrix Mor ``mor``.

    The raising companion of :func:`_engine_matrix`: entry ``(t, s)`` of
    ``backend`` is the coefficient of ``e_t`` in the image of ``e_s``.
    """
    mor = _require_matrix_mor(mor)
    ring = mor.base_ring()
    return mor.from_rows(
        (_owned_engine_element(ring, entry) for entry in row) for row in backend.rows()
    )


def _matrix_unit(mor, label):
    label = mor.module_generating_set()(label)
    row_label = label[0]
    column_label = label[1]
    column_labels = mor.column_index_set()
    return mor(
        {
            source_label: (
                mor.codomain().module_generator(row_label)
                if source_label == column_label
                else mor.codomain().zero()
            )
            for source_label in column_labels
        }
    )


def _matrix_coefficients(mor, morphism):

    morphism = mor(morphism)
    labels = mor.module_generating_set()
    coefficients = {}
    for column_label in mor.column_index_set():
        column = morphism._matrix_column_coordinates(column_label)
        for row_label, coefficient in (
            column.parent()._selected_module_coefficients(column).items()
        ):
            coefficients[labels((row_label, column_label))] = coefficient
    return coefficients


def _require_matrix_mor(mor):
    r"""Return the already-constructed matrix Mor for finite free endpoints."""
    ring = mor.base_ring()
    domain = mor.domain()
    codomain = mor.codomain()
    if not (
        _coordinate_framed_free_module(domain, ring)
        and _coordinate_framed_free_module(codomain, ring)
    ):
        return mor
    assert mor in MatrixSpaces(ring), (
        f"{mor} between the free modules {domain} and {codomain} with chosen bases is not a space "
        f"of matrices over {ring}"
    )
    return mor


def _coordinate_framed_free_module(module, ring) -> bool:
    r"""Whether the selected framing is a finite basis, independently of its engine.

    Freeness of the underlying module does not say that an arbitrary chosen
    generating family is a basis.  ``FramedFreeModules`` supplies that stronger
    datum; finite cardinality supplies the finite matrix calculation.
    """
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        FramedFreeModules,
    )

    return (
        module in FramedFreeModules(ring)
        and module.module_generating_set().cardinality().is_finite()
    )


def _coordinate_images(morphism):
    r"""Return the coordinates of each ``f(e_s)`` in the module generators of the codomain.

    The morphism ``f`` is applied to each module generator of its domain; no
    side of a matrix is read.  Engine adapters that take a family of
    generating vectors lower a morphism of free modules through this.
    """
    codomain_labels = tuple(morphism.codomain().module_generating_set())

    def coordinates(label):
        image = morphism(morphism.domain().module_generator(label)).to_vector()
        return tuple(image(codomain_label) for codomain_label in codomain_labels)

    return tuple(
        coordinates(label) for label in morphism.domain().module_generating_set()
    )
