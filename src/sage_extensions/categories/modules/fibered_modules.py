r"""Modules over varying commutative scalar rings and semilinear arrows.

For a commutative-ring morphism ``sigma : R -> S``, extension of scalars
``S tensor_R -`` is left adjoint to restriction of scalars.  Thus a
``sigma``-semilinear map ``M -> N`` is represented here by its actual additive
map, equivalently the ``R``-linear map ``M -> Res_sigma(N)``.  Its ``S``-linear
transpose ``S tensor_R M -> N`` is derived from the scalar-extension
adjunction owned by
:class:`~sage_extensions.categories.modules.pure.modules.Modules`.

This is the Grothendieck construction of the pseudofunctor
``R |-> Modules(R)`` on commutative rings: an arrow over ``R -> S`` is a map
``M -> Res_sigma(N)``, with the equivalent scalar-extended map available by
adjunction.  See the Stacks Project,
Tag 05DQ, for the scalar-extension/restriction adjunction, and Dai Tamaki,
*The Grothendieck Construction and Gradings for Enriched Categories*,
arXiv:0907.0061, for the Grothendieck construction.
"""

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoryPacketMethods,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.magmas import AdditiveGroups
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphismMethods,
    _finite_generating_elements,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import (
    CommutativeRings,
    OwnedRings,
)
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class SemilinearModuleMorphism:
    r"""A module arrow over a morphism of commutative scalar rings.

    If ``sigma : R -> S``, the defining map is the equivalent ``R``-linear map
    ``M -> Res_sigma(N)``.  The ``S``-linear transpose
    ``S tensor_R M -> N`` is derived from the scalar-extension/restriction
    adjunction when that represented scalar extension is available.
    """

    def __init__(
        self,
        parent,
        scalar_map,
        restricted_morphism=None,
        *,
        evaluator=None,
    ) -> None:
        domain = parent.domain()
        codomain = parent.codomain()
        if scalar_map.domain() is not domain.base_ring():
            raise ValueError(
                f"a semilinear map out of {domain} lies over a ring map out of its base ring "
                f"{domain.base_ring()}, but {scalar_map} starts at {scalar_map.domain()}"
            )
        if scalar_map.codomain() is not codomain.base_ring():
            raise ValueError(
                f"a semilinear map into {codomain} lies over a ring map into its base ring "
                f"{codomain.base_ring()}, but {scalar_map} ends at {scalar_map.codomain()}"
            )
        self._scalar_map = scalar_map
        self._restricted_codomain = None
        self._restricted_morphism = None
        match restricted_morphism, evaluator:
            case None, None:
                raise TypeError(
                    f"a semilinear map {domain} -> {codomain} needs its defining linear map "
                    f"{domain} -> Res_{{{scalar_map}}}({codomain}) or a construction-derived evaluator"
                )
            case None, _:
                pass
            case _, None:
                restricted = Modules(domain.base_ring()).base_change_adjunction(
                    scalar_map
                ).right_adjoint()(codomain)
                self._restricted_codomain = restricted
                linear_mor = Modules(domain.base_ring()).Mor(domain, restricted)
                self._restricted_morphism = linear_mor(restricted_morphism)
                match restricted is codomain:
                    case True:
                        evaluator = lambda element: codomain(self._restricted_morphism(element))
                    case False:
                        evaluator = lambda element: codomain(
                            self._restricted_morphism(element).underlying_element()
                        )
            case _, _:
                raise TypeError(
                    "a semilinear arrow is defined either by its restricted linear morphism "
                    "or by a construction-derived evaluator, not both"
                )
        super().__init__(parent, evaluator)

    def scalar_map(self):
        return self._scalar_map

    def source(self):
        return self.domain()

    def target(self):
        return self.codomain()

    def restricted_codomain(self):
        r"""Return ``Res_sigma(N)``, the target read in the source fibre."""
        if self._restricted_codomain is None:
            adjunction = Modules(self.domain().base_ring()).base_change_adjunction(
                self.scalar_map()
            )
            self._restricted_codomain = adjunction.right_adjoint()(self.codomain())
        return self._restricted_codomain

    @cached_method
    def restricted_morphism(self):
        r"""Return the defining ``R``-linear map ``M -> Res_sigma(N)``."""
        if self._restricted_morphism is not None:
            return self._restricted_morphism
        restricted = self.restricted_codomain()
        linear_mor = Modules(self.domain().base_ring()).Mor(self.domain(), restricted)
        # An evaluator carries no proof of semilinearity, so the linearity of
        # its restricted map is decided where decidable and otherwise is the
        # proposition ``is_linear(f)``.
        return linear_mor.elementwise(lambda element: restricted(self(element)))

    @cached_method
    def additive_map(self):
        r"""Return the underlying additive map ``M -> N`` of this semilinear arrow."""
        additive = AdditiveGroups().AdditiveCommutative().MorCategory().Of(
            self.domain(),
            self.codomain(),
        )
        return additive.elementwise(lambda element: self(element))

    @cached_method
    def linearization(self):
        r"""Return the adjoint transpose ``S tensor_R M -> N`` when represented."""
        adjunction = Modules(self.domain().base_ring()).base_change_adjunction(
            self.scalar_map()
        )
        return adjunction.mor_set_isomorphism_inverse(
            self.restricted_morphism(),
            self.codomain(),
        )

    def extended_source(self):
        return Modules(self.domain().base_ring()).base_change_adjunction(
            self.scalar_map()
        ).left_adjoint()(self.domain())

    def _richcmp_(self, other, op):
        r"""Decide equality of two semilinear arrows of one Mor.

        Arrows over ``sigma`` and ``tau`` are equal when ``sigma = tau`` and
        their additive maps are equal.  A ``sigma``-semilinear map sends
        ``sum r_i x_i`` to ``sum sigma(r_i) f(x_i)``, so on a finite spanning
        family of the source the two maps agree everywhere when they agree
        there.  Without such a family the additive maps' own comparison
        answers; no infinite family is iterated.  An undecided comparison
        answers the proposition ``equal(f, g)``.
        """
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if self is other:
            return op == op_EQ
        match self.scalar_map() == other.scalar_map():
            case True:
                pass
            case False:
                return op == op_NE
            case _:
                equal = AtomicProposition("equal", self, other)
                return equal if op == op_EQ else negation(equal)
        elements = _finite_generating_elements(self.domain())
        match elements:
            case None:
                equal = self.additive_map() == other.additive_map()
            case _:
                equal = conjunction(self(element) == other(element) for element in elements)
        return equal if op == op_EQ else negation(equal)

    def __mul__(self, other):
        match other:
            case SemilinearModuleMorphism() if other.codomain() is self.domain():
                pass
            case _:
                return NotImplemented
        source = other.domain()
        scalar_map = self.scalar_map() * other.scalar_map()
        mor = ModulesOverCommutativeRings().Mor(source, self.codomain())
        restricted = mor.restricted_codomain(scalar_map)
        linear_mor = Modules(source.base_ring()).Mor(source, restricted)
        composite = linear_mor._from_constructed_element_map(
            lambda element: restricted(self(other(element))),
            premises=(self.restricted_morphism(), other.restricted_morphism()),
        )
        return mor(scalar_map, composite)

    @classmethod
    def identity(cls, module):
        r"""The identity of ``module`` in the varying-ring module category."""
        return ModulesOverCommutativeRings().Mor(module, module).identity()

    @classmethod
    def from_linear(cls, morphism):
        r"""Regard a fixed-fiber linear map as semilinear over the identity ring map."""
        source = morphism.domain()
        target = morphism.codomain()
        if source.base_ring() is not target.base_ring():
            raise ValueError(
                f"{morphism} is not a linear map: its domain and codomain must be modules over one ring, "
                f"but they are over {source.base_ring()} and {target.base_ring()}"
            )
        morphism = Modules(source.base_ring()).Mor(source, target)(morphism)
        mor = ModulesOverCommutativeRings().Mor(source, target)
        scalar_map = source.base_ring().Mor(source.base_ring()).identity()
        restricted = mor.restricted_codomain(scalar_map)
        compatible = Modules(source.base_ring()).Mor(
            source, restricted
        )._from_constructed_element_map(
            lambda element: restricted(morphism(element)),
            premises=(morphism,),
        )
        return mor(scalar_map, compatible)


class SemilinearModuleMor(CategoricalMor):
    r"""All semilinear arrows between two modules over commutative rings."""

    ElementMethods = SemilinearModuleMorphism

    def _validate_scalar_map(self, scalar_map) -> None:
        source_ring = self.domain().base_ring()
        target_ring = self.codomain().base_ring()
        if scalar_map not in CommutativeRings().Mor(source_ring, target_ring):
            raise TypeError(
                f"a semilinear map {self.domain()} -> {self.codomain()} lies over a morphism of commutative "
                f"rings {source_ring} -> {target_ring}, but {scalar_map} is not one"
            )

    @cached_method(key=lambda self, scalar_map: id(scalar_map))
    def base_change_adjunction(self, scalar_map):
        r"""Return the one scalar-extension/restriction adjunction for ``scalar_map``."""
        self._validate_scalar_map(scalar_map)
        return Modules(self.domain().base_ring()).base_change_adjunction(scalar_map)

    def extended_domain(self, scalar_map):
        return self.base_change_adjunction(scalar_map).left_adjoint()(self.domain())

    def restricted_codomain(self, scalar_map):
        r"""Return ``Res_sigma(N)`` in the source module fibre."""
        return self.base_change_adjunction(scalar_map).right_adjoint()(self.codomain())

    def compatible_mor(self, scalar_map):
        r"""Return ``Hom_R(M, Res_sigma(N))`` classifying these semilinear arrows."""
        restricted = self.restricted_codomain(scalar_map)
        return Modules(self.domain().base_ring()).Mor(self.domain(), restricted)

    def _element_constructor_(self, scalar_map, compatible_map=None):
        if compatible_map is None and isinstance(scalar_map, SemilinearModuleMorphism):
            if scalar_map.parent() is self:
                return scalar_map
            raise TypeError(f"{scalar_map} belongs to another Mor; give the scalar map and compatible linear map")
        self._validate_scalar_map(scalar_map)
        restricted = self.restricted_codomain(scalar_map)
        compatible_mor = self.compatible_mor(scalar_map)
        compatible_map = compatible_mor(compatible_map)
        return self.element_class(self, scalar_map, compatible_map)

    def _from_linearization(self, scalar_map, linearization):
        r"""Construct from the equivalent target-fibre map ``S tensor_R M -> N``."""
        self._validate_scalar_map(scalar_map)
        extended = self.extended_domain(scalar_map)
        linear_mor = Modules(self.codomain().base_ring()).Mor(
            extended,
            self.codomain(),
        )
        linearization = linear_mor(linearization)
        adjunction = self.base_change_adjunction(scalar_map)
        compatible = adjunction.mor_set_isomorphism_forward(
            linearization,
            self.domain(),
        )
        return self.element_class(self, scalar_map, compatible)

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"{self} has no identity: an identity map needs domain = codomain, but these are "
                f"{self.domain()} and {self.codomain()}"
            )
        module = self.domain()
        ring = module.base_ring()
        scalar_map = ring.Mor(ring).identity()
        restricted = self.restricted_codomain(scalar_map)
        compatible = Modules(ring).Mor(module, restricted)._from_constructed_element_map(
            lambda element: restricted(module(element)),
        )
        return self(scalar_map, compatible)


class SemilinearModuleMorCategoryConstruction(MorCategoryConstruction):
    r"""The Mor family of the Grothendieck category of modules over rings."""

    def fixed_category_class(self):
        return SemilinearModuleMor


class ModuleBaseRingProjection(Functor):
    r"""The projection ``(R,M) |-> R`` from modules over varying rings."""

    def __init__(self) -> None:
        super().__init__(ModulesOverCommutativeRings(), CommutativeRings())

    def _apply_object(self, module):
        return module.base_ring()

    def _apply_morphism(self, morphism):
        return morphism.scalar_map()

    def _repr_(self):
        return "Base-ring projection from modules over commutative rings"


class ModulesOverCommutativeRings(CategoryPacketMethods, OwnedCategory):
    r"""The Grothendieck category of ``R |-> Modules(R)`` on commutative rings.

    Objects are modules ``M`` together with their commutative scalar ring
    ``R = M.base_ring()``.  An arrow ``M/R -> N/S`` lies over a ring map
    ``sigma : R -> S`` and retains the compatible additive map as the
    ``R``-linear arrow ``M -> Res_sigma(N)``.  Scalar extension and restriction
    give the cocartesian/cartesian transports of the represented fibration.
    """

    _MorCategory = SemilinearModuleMorCategoryConstruction

    def an_object(self):
        return CommutativeRings().an_object().free_module(1)

    def super_categories(self):
        return [AdditiveGroups().AdditiveCommutative()]

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"{self}.Mor({domain}, {codomain}) needs two modules over commutative rings, but {domain} "
                f"is in {domain.category()} and {codomain} is in {codomain.category()}"
            )
        return self.MorCategory().Of(domain, codomain)

    def fiber(self, ring):
        r"""Return the fixed-base fibre ``Modules(R)`` over a commutative ring ``R``."""
        if ring not in CommutativeRings():
            raise TypeError(
                f"{self} has fibres Modules(R) only over commutative rings R, but {ring} is in {ring.category()}"
            )
        return Modules(ring)

    def cocartesian_transport(self, ring_map):
        r"""Return scalar extension ``S tensor_R -`` along ``R -> S``."""
        source, target = ring_map.domain(), ring_map.codomain()
        if ring_map not in CommutativeRings().Mor(source, target):
            raise TypeError(
                f"scalar extension along {ring_map} is not defined: it needs a morphism of commutative rings, "
                f"but {ring_map} is not in CommutativeRings().Mor({source}, {target})"
            )
        return self.base_change_adjunction(ring_map).left_adjoint()

    def cartesian_transport(self, ring_map):
        r"""Return restriction of scalars ``Res_f : Modules(S) -> Modules(R)``."""
        source, target = ring_map.domain(), ring_map.codomain()
        if ring_map not in CommutativeRings().Mor(source, target):
            raise TypeError(
                f"restriction of scalars along {ring_map} is not defined: it needs a morphism of commutative rings, "
                f"but {ring_map} is not in CommutativeRings().Mor({source}, {target})"
            )
        return self.base_change_adjunction(ring_map).right_adjoint()

    def base_change_adjunction(self, ring_map):
        r"""Return the existing ``S tensor_R - dashv Res_f`` transport adjunction."""
        source, target = ring_map.domain(), ring_map.codomain()
        if ring_map not in CommutativeRings().Mor(source, target):
            raise TypeError(
                f"the base-change adjunction along {ring_map} is not defined: it needs a morphism of commutative rings, "
                f"but {ring_map} is not in CommutativeRings().Mor({source}, {target})"
            )
        return self.fiber(source).base_change_adjunction(ring_map)

    def projection(self):
        return ModuleBaseRingProjection()

    @classmethod
    def _repr_object_names(cls):
        return "modules over commutative rings"


__all__ = [
    "ModuleBaseRingProjection",
    "ModulesOverCommutativeRings",
    "SemilinearModuleMor",
    "SemilinearModuleMorphism",
]
