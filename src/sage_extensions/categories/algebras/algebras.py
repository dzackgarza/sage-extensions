r"""Algebras over a commutative ring, their axioms, and their data subcategories.

Let \(R\) be a commutative ring.  An \(R\)-algebra is an \(R\)-module \(M\)
together with an \(R\)-bilinear multiplication, that is an \(R\)-linear map
\(m\colon M\otimes_R M\to M\) (Bourbaki, *Algebra* III §1.1).  The pair
\((M, m)\) is the whole structure.  The structure morphism \(\rho\) is the
scalar action of \(M\); associativity, a unit, commutativity and the Lie
identities are axioms above the root, and a Lie bracket is the multiplication
of its algebra.

``Algebras(R)(M, m)`` is the one entry (``CON-16``).  Every other route -- an
axiom entry, the centre, a quotient, the commutator Lie algebra, a group
algebra -- computes \((M, m)\) and reaches the same construction,
:func:`_algebra_on_module`.
"""

from __future__ import annotations

import itertools
from functools import reduce
from typing import TYPE_CHECKING

from sage.categories.category_with_axiom import all_axioms
from sage.categories.map import Map
from sage.categories.morphism import Morphism, SetMorphism
from sage.categories.rings import Rings as SageRings
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _category_mor_parent,
)
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    _fix_selected_resolution,
)
from sage_extensions.categories.abstract_categories.products import (
    _finite_factor_family,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.magmas import AdditiveGroups, Magmas
from sage_extensions.categories.modules.framed.framed_free_modules import (
    FramedFreeModules,
)
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphismMethods,
)
from sage_extensions.categories.modules.pure.modules import (
    BilinearMap,
    MatrixEndomorphismSpaces,
    Modules,
    ModulesWithChosenFinitePresentation,
    TensorProductModules,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedRings,
    PredicateSubrings,
    PrincipalIdealDomains,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_integers,
    _owned_ring,
    _OwnedRingElement,
    _OwnedRingParent,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import EnumeratedSets, OwnedSetMorphism, Sets
from sage_extensions.logic import AtomicProposition, Propositions, conjunction, negation
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.refine import RealizationHook, refine
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

if TYPE_CHECKING:
    from sage.categories.category import Category

    from sage_extensions.lexicon.category_theory import ObjectOfCategory
    from sage_extensions.owned_category import ConstructionData


if "Lie" not in all_axioms:
    all_axioms.add("Lie")

# Qualified relative properties of the algebra structure are
# distinct from the corresponding module properties.
if "ProjectiveAsAlgebra" not in all_axioms:
    all_axioms.add("ProjectiveAsAlgebra")
if "FinitelyGeneratedAsAlgebra" not in all_axioms:
    all_axioms.add("FinitelyGeneratedAsAlgebra")
if "FinitelyPresentedAsAlgebra" not in all_axioms:
    all_axioms.add("FinitelyPresentedAsAlgebra")


# ---------------------------------------------------------------------------
# The algebra Mor: linear maps preserving the multiplication.
# ---------------------------------------------------------------------------


class MultiplicativeAlgebraMorphism:
    r"""An algebra morphism: an ``R``-linear \(f\colon A\to B\) with \(f\,m_A = m_B\,(f\otimes f)\).

    The datum is the linear map, an element of the module Mor.  Construction
    stores it and stops (``OWN-22``).  The defining equation is one equation
    between two module morphisms out of \(A\otimes_R A\), asked of the module
    Mor when :meth:`is_multiplicative` is first asked: its finite generating
    data decide the equation when value equality is decided; otherwise it
    answers the proposition of the equation, the hypothesis the arrow is stated under
    (``CON-16``, ``DEV-52``).  :meth:`validate_multiplicativity` refuses a map
    for which it answers ``False``.
    """

    # A stronger algebra Mor can retain an extensionally equal arrow with a
    # different parent. Reuse the set-map owner's hash for these endpoints.
    __hash__ = OwnedSetMorphism.__hash__

    def _multiplicativity_derivation(self):
        r"""Return a construction-derived multiplicativity decision, or ``None``."""
        return None

    def __init__(self, parent, underlying_morphism) -> None:
        domain = parent.domain()
        codomain = parent.codomain()
        linear = domain.module_category().Mor(domain, codomain)(underlying_morphism)
        super().__init__(parent, linear)
        self.validate_multiplicativity(check=False)

    @RealizationHook
    def _multiplicativity_decision(self):
        r"""Supply MagmaMorphism's predicate by \(f\,m_A = m_B\,(f\otimes f)\).

        The existing construction-derived decision takes precedence. Without
        one, the module Mor compares the two linear maps and preserves any
        undecided equation as the arrow's stated multiplicativity premise.
        """
        derived = self._multiplicativity_derivation()
        if derived is not None:
            return derived
        linear = Algebras(self.domain().algebra_base_ring()).underlying_module()(self)
        return (
            linear * self.domain().multiplication_morphism()
            == self.codomain().multiplication_morphism() * linear.tensor_square_morphism()
        )

    @RealizationHook
    def _center_corestriction(self):
        r"""Supply MagmaMorphism's central-image factor with the retained laws.

        A finite chosen module generating family uses the exact algebra centre
        inclusion and the existing module factorization construction. This
        returns an R-algebra map and assumes neither ambient associativity nor
        preservation of a unit. A unital associative algebra map with chosen
        algebra generators can instead lift those generators through the
        selected centre inclusion. Endpoint objects alone never promote an
        arrow to a ring map, and another representation of the ring centre
        never replaces the retained centre endpoint.
        """
        domain = self.domain()
        codomain = self.codomain()
        algebras = Algebras(domain.algebra_base_ring())
        ordinary = algebras.Associative().Unital()
        center = codomain.center()
        if center is codomain:
            return self
        inclusion = codomain.center_inclusion()
        match self:
            case _ if (
                domain.has_selected_module_resolution()
                and domain.module_generating_set().cardinality().is_finite()
                and center in algebras
                and inclusion.parent().mor_category().is_subcategory(algebras)
            ):
                forget = algebras.underlying_module()
                factor = forget(self).factor_through(forget(inclusion))
                return algebras.Mor(domain, center)(factor)
            case _ if (
                domain in ordinary and codomain in ordinary
                and self in ordinary.Mor(domain, codomain)
                and domain.is_framed_algebra()
                and domain.algebra_generating_set().cardinality().is_finite()
            ):
                return _corestrict_algebra_morphism_to_center(self)
            case _:
                return super()._center_corestriction()

    @cached_method
    def cokernel(self):
        r"""The cokernel in the root algebra category, modulo the ideal generated by the image.

        The image of the underlying linear map need not be an ideal, which is
        the difference from the module cokernel; for Lie algebras it is the
        quotient by the Lie ideal the image generates. The root category
        permits maps that do not preserve units and has a zero object. On a
        unit-preserving arrow this operation means the cokernel after
        forgetting unit preservation: its image ideal contains 1, so the
        quotient is the zero algebra. This does not assert a categorical
        cokernel in the unital category, which generally has no zero arrows.

        The selected algorithm
        first needs a finite chosen module generating family in the source;
        ideal closure and the represented quotient then use the target's
        existing module computations.
        """
        domain = self.domain()
        assert (
            domain.has_selected_module_resolution()
            and domain.module_generating_set().cardinality().is_finite()
        ), (
            f"the algebra cokernel of {self} needs a represented image; "
            "the available image-span computation needs finitely many chosen "
            "module generators in its source"
        )
        image = ModuleMorphismMethods.image(self)
        return self.codomain().quotient_by_generated_algebra_ideal(image)

    @cached_method
    def cokernel_projection(self):
        r"""The quotient map onto the underlying root-algebra cokernel.

        The target retains the structural laws descended by the quotient
        construction. The displayed arrow is in the root algebra theory,
        where its cokernel universal property is stated; an input arrow's
        additional matrix, free or graded object datum is not asserted for
        this quotient. If the source has a unit, the quotient map preserves
        it, without claiming a unital-category cokernel.
        """
        quotient = self.cokernel()
        category = Algebras(self.codomain().algebra_base_ring())
        return category.Mor(self.codomain(), quotient)(quotient.algebra_quotient_projection())

    def __mul__(self, other):
        r"""``self . other``, admitted on the composite of the underlying linear maps.

        The forgetful functor ``U : Alg_R -> Mod_R`` preserves composition,
        so the composite of algebra maps is the algebra map whose underlying
        linear map is ``U(self) U(other)``. The module Mor owns the linear
        composition; the algebra result retains only the laws shared by both
        factors. In particular, a unit-preserving left factor cannot add
        unit preservation to a right factor admitted only in the root Mor.
        """
        if not isinstance(other, (Morphism, CategoricalArrow)) or other.codomain() is not self.domain():
            return NotImplemented
        other_parent = element_parent(other)
        if not isinstance(other_parent, CategoricalMor):
            return NotImplemented
        algebras = Algebras(self.domain().algebra_base_ring())
        left_category = self.parent().mor_category()
        right_category = other_parent.mor_category()
        if not (
            left_category.is_subcategory(algebras)
            and right_category.is_subcategory(algebras)
        ):
            return NotImplemented
        if getattr(self, "_preamble_is_identity", False):
            return other
        if getattr(other, "_preamble_is_identity", False):
            return self
        source = other.domain()
        forget = algebras.underlying_module()
        category = Cat().join((left_category, right_category))
        mor = category.Mor(source, self.codomain())
        left_linear = forget(self)
        right_linear = forget(other)
        if isinstance(mor, UnitalMultiplicativeAlgebraMor):
            equations = [self.is_multiplicative(), other.is_multiplicative()]
            if hasattr(self, "preserves_unit") and hasattr(other, "preserves_unit"):
                equations.extend((self.preserves_unit(), other.preserves_unit()))
            return mor._from_constructed_element_map(
                lambda element: self(other(element)),
                linearity_premises=(left_linear, right_linear),
                equations=equations,
            )
        # The root algebra Mor has no unital construction supplier.  Its
        # defining datum is the already-composed linear map; enter it at the
        # algebra arrow type rather than redispatching that whole module arrow
        # through the public constructor boundary.
        return mor.element_class(mor, left_linear * right_linear)


class MultiplicativeAlgebraMor(CategoricalMor):
    r"""``Hom_{R-Alg}(A, B)``: the linear maps preserving the multiplication."""

    ElementMethods = MultiplicativeAlgebraMorphism

    def _element_constructor_(self, datum):
        if isinstance(datum, Map):
            if self._already_parented_arrow(datum):
                return datum
            raise TypeError(f"{datum} is an arrow of another Mor; give defining generator data or apply the functor")
        return self.element_class(self, datum)

    @object_level
    @cached_method
    def identity(self):
        assert self.domain() is self.codomain(), (
            f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
        )
        algebra = self.domain()
        identity = self.element_class(self, algebra.module_category().Mor(algebra, algebra).identity())
        # The retained module identity proves the function is the identity.
        identity._preamble_is_identity = True
        return identity

    def _repr_(self):
        return f"Mor_Alg({self.domain()}, {self.codomain()})"


class UnitalMultiplicativeAlgebraMorphism:
    r"""A morphism of unital algebras: multiplicative and \(f(1) = 1\)."""

    @cached_method
    def _constructed_algebra_map_decision(self):
        r"""The sufficient hypotheses of the retained algebra-map construction.

        Only a decided true conjunction proves the laws of a constructed
        evaluator. A failed or undecided sufficient premise leaves its
        ordinary diagnostics in force. Transport of an actual map instead
        retains its three independent law decisions in the suppliers below.
        """
        transported = self._transported_algebra_morphism
        if transported is not None:
            return conjunction((
                transported.linearity_decision(),
                transported.is_multiplicative(),
                transported.preserves_unit(),
            ))
        if self._constructed_algebra_map_premises is None:
            return None
        maps, equations = self._constructed_algebra_map_premises
        return conjunction((
            conjunction(morphism.linearity_decision() for morphism in maps),
            conjunction(equations),
        ))

    def _elementwise_linearity_derivation(self):
        if self._transported_algebra_morphism is not None:
            return self._transported_algebra_morphism.linearity_decision()
        if self._constructed_algebra_map_decision() is True:
            return True
        return super()._elementwise_linearity_derivation()

    def _multiplicativity_derivation(self):
        if self._transported_algebra_morphism is not None:
            return self._transported_algebra_morphism.is_multiplicative()
        if self._constructed_algebra_map_decision() is True:
            return True
        return super()._multiplicativity_derivation()

    def _unit_preservation_derivation(self):
        r"""Return a construction-derived unit-preservation decision, or ``None``."""
        if self._transported_algebra_morphism is not None:
            return self._transported_algebra_morphism.preserves_unit()
        if self._constructed_algebra_map_decision() is True:
            return True
        return None

    def __init__(
        self, parent, underlying_morphism, *, _construction_premises=None,
        _transported_morphism=None,
    ) -> None:
        if (
            _transported_morphism is None
            and isinstance(underlying_morphism, UnitalMultiplicativeAlgebraMorphism)
            and underlying_morphism.domain() is parent.domain()
            and underlying_morphism.codomain() is parent.codomain()
        ):
            _transported_morphism = underlying_morphism
        if _transported_morphism is not None:
            domain = parent.domain()
            codomain = parent.codomain()
            if (
                not isinstance(_transported_morphism, UnitalMultiplicativeAlgebraMorphism)
                or _transported_morphism.codomain() is not codomain
                or (
                    _transported_morphism.domain() is not domain
                    and _transported_morphism.domain() is not domain.unformed_module()
                )
                or _transported_morphism not in Algebras(
                    domain.algebra_base_ring()
                ).Unital().Mor(_transported_morphism.domain(), codomain)
            ):
                raise ValueError(
                    f"transporting an algebra map to {domain} -> {codomain} requires "
                    "the same endpoints, or the retained same-product module domain "
                    "and unchanged codomain"
                )
        # These are the actual input maps/equations, installed before the
        # lower-arrow initialization and its deferred validators.
        self._constructed_algebra_map_premises = _construction_premises
        self._transported_algebra_morphism = _transported_morphism
        super().__init__(parent, underlying_morphism)
        self.validate_unit_preservation(check=False)

    @cached_method
    def preserves_unit(self):
        r"""The decision of the unit equation \(f(1) = 1\), or the proposition for its stated hypothesis."""
        derived = self._unit_preservation_derivation()
        if derived is not None:
            return derived
        return self(self.domain().one()) == self.codomain().one()

    def is_group_algebra_augmentation(self) -> bool:
        r"""Return whether this map is the represented augmentation ``R[G] -> R``."""
        from sage_extensions.categories.functors.group_actions import (
            _is_augmentation_of_group_algebra,
        )

        return _is_augmentation_of_group_algebra(self)

    def is_group_algebra_subgroup_inclusion(self) -> bool:
        r"""Return whether this map is ``R[H] -> R[G]`` induced by a represented subgroup inclusion."""
        from sage_extensions.categories.functors.group_induction import (
            _is_group_algebra_map_of_subgroup_inclusion,
        )

        return _is_group_algebra_map_of_subgroup_inclusion(self)

    @validator
    def validate_unit_preservation(self) -> None:
        r"""Raise ``ValueError`` when this map does not send ``1`` to ``1`` (``OWN-22``)."""
        if self.preserves_unit() is False:
            raise ValueError(
                f"{self} is not a unital algebra morphism {self.domain()} -> {self.codomain()}: "
                "it does not send 1 to 1"
            )


class UnitalMultiplicativeAlgebraMor(MultiplicativeAlgebraMor):
    r"""``Mor`` of unital algebras: the multiplicative linear maps preserving the unit."""

    ElementMethods = UnitalMultiplicativeAlgebraMorphism

    def _from_constructed_element_map(
        self, evaluator, *, linearity_premises=(), equations=(),
        transported_morphism=None,
    ):
        r"""Construct a unital algebra map from its actual construction data.

        This is the common supplier for canonical comparisons, exterior
        extensions and augmentations. The selected fixed Mor still runs its
        own whole-map constructor; a framing or presentation is not required.
        The supplied construction proves the laws when its retained linear
        maps and equations hold. Empty families mean that its formula alone
        proves them. Failed or undecided sufficient premises leave the
        ordinary evaluator diagnostics in force.

        An actual transported map retains linearity, multiplicativity and
        unit preservation independently. Equal literal endpoints support
        strengthening the arrow's category. The other permitted caller is
        the scalar-slice augmentation wrapper: its construction retains the
        old algebra as its module, with that algebra's literal multiplication
        and unit. Endpoint agreement alone does not certify a new product on
        an old module; this protected wrapper construction supplies that
        same-data relation.
        """
        if not callable(evaluator):
            raise TypeError(
                f"a morphism {self.domain()} -> {self.codomain()} needs a map on elements, "
                f"but {evaluator!r} is not callable"
            )
        linearity_premises = tuple(linearity_premises)
        linear = self.domain().module_category().Mor(
            self.domain(), self.codomain()
        )._from_constructed_element_map(
            evaluator, premises=linearity_premises
        )
        return self.element_class(
            self, linear,
            _construction_premises=(linearity_premises, tuple(equations)),
            _transported_morphism=transported_morphism,
        )

    def _repr_(self):
        return f"Mor_UnitalAlg({self.domain()}, {self.codomain()})"


def _algebra_from_native_ring(
    algebra, product, unit, scalar_action, *, module_basis=None, scalar_ring=None
):
    r"""Compute (M,m) from a native ring and enter the ordinary algebra constructor.

    The native unit is needed by the coefficient arithmetic of a self-based
    ring, so the unit owner records it before constructing its regular module.
    Modules(R) constructs the specified action and, over R itself, its actual
    rank-one framing. The tensor owner classifies the primitive bilinear
    product. Only then does _algebra_on_module construct the algebra datum.
    Nothing in this route substitutes a bare binary function for m.
    """
    from sage_extensions.categories.modules.native_modules import _RingModulePresentation

    # Some owner constructors defer their algebra category until this module
    # datum has been installed, so their category-provided algebra_base_ring
    # method is not yet present. Such owners pass the already selected scalar
    # ring explicitly; ordinary callers continue to read the retained algebra
    # level as before.
    if scalar_ring is None:
        scalar_ring = vars(algebra).get("_preamble_selected_algebra_base_ring")
    ring = (
        algebra.algebra_base_ring()
        if scalar_ring is None
        else _owned_ring(scalar_ring)
    )
    Algebras.Unital.ParentMethods._retain_unit(algebra, unit)
    presentation = _RingModulePresentation(algebra, ring, product, unit, scalar_action, basis=module_basis)
    module = Modules(ring)(presentation)
    category = Algebras(ring).Associative().Unital()
    law_decisions = {"associativity": True, "unit": True}
    # The ring's constructor placed it; its product is commutative exactly
    # when that placement says so (ARC-08, CON-07).
    match algebra:
        case _ if algebra in Magmas().Commutative():
            category = category.Commutative()
            law_decisions["commutativity"] = True
        case _:
            pass
    # The ring's own product is its algebra structure (OWN-22): no map out of
    # the tensor square is built here; `multiplication()` builds it when asked.
    Algebras.ParentMethods._retain_algebra_law_decisions(module, law_decisions)
    Algebras.Unital.ParentMethods._retain_unit(module, module(unit))
    selected_category = Cat().meet((Algebras(ring), category))
    match module in selected_category:
        case True:
            pass
        case False:
            refine(module, selected_category)
    # Keep the scalar action as defining constructor data, but do not eagerly
    # realize R -> End_Ab(U(module)) here.  The End construction can itself
    # demand module-Mor objects and recurse into this constructor.  The public
    # scalar_action() owner realizes the map on demand against the final
    # additive-group parent, preserving this exact pointwise action.
    return module


class AlgebraMorCategoryConstruction(MorCategoryConstruction):
    r"""The fixed-endpoint Mor categories of ``R``-algebras: linear maps preserving the multiplication.

    An axiom that adds no condition on morphisms -- associativity,
    commutativity, the Lie identities -- shares this Mor object.
    """

    FixedCategoryClass = MultiplicativeAlgebraMor


class UnitalAlgebraMorCategoryConstruction(MorCategoryConstruction):
    r"""The fixed-endpoint Mor categories of unital ``R``-algebras: the unit is preserved too.

    General unital algebras take linear maps preserving product and unit.
    Between associative unital algebras, the domain may instead name a
    realization on selected algebra generators or a presentation. Those
    ordinary word-evaluation constructions use associativity of both
    endpoints; they do not supply maps into a general nonassociative target.
    """

    def fixed_category_class_for(self, domain, codomain):
        ordinary = Algebras(self.base_category().base_ring()).Associative().Unital()
        match domain, codomain:
            case _ if domain in ordinary and codomain in ordinary:
                return domain._algebra_mor_class()
            case _:
                return UnitalMultiplicativeAlgebraMor


# ---------------------------------------------------------------------------
# Units and the tensor square.
# ---------------------------------------------------------------------------


def _scalar_module(ring):
    r"""\(U_R(R)\): the ring as the module over itself, the domain of every unit map."""
    ring = _owned_ring(ring)
    match ring.base_ring() is ring:
        case True:
            return ring
        case False:
            return ring.as_algebra_over(ring)


def _unit_morphism_from_element(module, unit, ring):
    r"""The linear map ``U_R(R) -> module`` determined by ``1 |-> unit``.

    The map \(r\mapsto r\cdot u\) is linear by the module axioms, so the
    construction alone gives linearity.
    """
    ring = _owned_ring(ring)
    scalar_module = _scalar_module(ring)
    return scalar_module.module_category().Mor(
        scalar_module, module
    )._from_constructed_element_map(
        lambda scalar: module.scalar_multiple(ring(scalar), unit)
    )


class _CommutativeUnitalAlgebraSubcategoryMethods:
    r"""Constructions that require commutative associative unital algebras."""

    def _selected_binary_colimit_owner(self, left, right):
        r"""Return the factor whose owned presentation realizes a binary colimit."""
        from sage_extensions.categories.algebras.free_algebras import (
            SymmetricAlgebras,
        )

        base = self.base_ring()
        match (left, right):
            case _ if (
                left in SymmetricAlgebras(base)
                or left in AlgebrasWithChosenFinitePresentation(base)
            ):
                return left
            case _ if (
                right in SymmetricAlgebras(base)
                or right in AlgebrasWithChosenFinitePresentation(base)
            ):
                return right
            case _:
                raise AssertionError(
                    "commutative-algebra binary colimits currently require a symmetric-algebra "
                    "or chosen finite-presentation factor"
                )

    def spectrum(self):
        r"""``Spec_R : CAlg_R^op -> AffSch_R``, the affine spectrum functor."""
        from sage_extensions.categories.schemes.affine_spec import (
            _affine_spec_functor,
        )

        return _affine_spec_functor(self.base_ring())

    def de_rham(self):
        r"""``DR_R : CAlg_R -> SCDGA_R``, the algebraic de Rham functor."""
        from sage_extensions.categories.functors.de_rham import (
            _de_rham_functor,
        )

        return _de_rham_functor(self.base_ring())

    def de_rham_adjunction(self):
        r"""Return the algebraic de Rham/degree-zero adjunction over this base."""
        from sage_extensions.categories.functors.de_rham import (
            _de_rham_adjunction,
        )

        return _de_rham_adjunction(self.base_ring())

    def de_rham_cohomology(self, degree):
        r"""Return ``H^degree_dR(-/R)`` on this commutative algebra category."""
        from sage_extensions.categories.functors.cohomology import (
            _de_rham_cohomology_functor,
        )

        return _de_rham_cohomology_functor(self.base_ring(), degree)

    def de_rham_cohomology_algebra(self):
        r"""Return the graded algebraic de Rham cohomology functor ``H^*_dR``."""
        from sage_extensions.categories.functors.cohomology import (
            _de_rham_cohomology_algebra_functor,
        )

        return _de_rham_cohomology_algebra_functor(self.base_ring())

    # Select the common public operation before the inherited module entry;
    # the algebra supplier below retains the tensor-product cocone.
    coproduct = Cat.ParentMethods.coproduct

    def _categorical_coproduct(self, left, right):
        owner = self._selected_binary_colimit_owner(left, right)
        return owner._commutative_algebra_coproduct(left, right)

    def _categorical_coproduct_morphism(
        self,
        left_morphism,
        right_morphism,
        source,
        target,
    ):
        return source.from_cocone(
            target.left_coproduct_map() * left_morphism,
            target.right_coproduct_map() * right_morphism,
        )

    pushout = Cat.ParentMethods.pushout

    def _categorical_pushout(self, left_morphism, right_morphism):
        left = left_morphism.codomain()
        right = right_morphism.codomain()
        owner = self._selected_binary_colimit_owner(left, right)
        return owner._commutative_algebra_pushout(left_morphism, right_morphism)


class _CommutativeUnitalAlgebraParentMethods:
    def kahler_differentials(self):
        r"""Return ``Omega^1_{A/R}`` for this commutative ``R``-algebra."""
        from sage_extensions.categories.algebras.kahler_differentials import (
            KahlerDifferentialModules,
        )

        return KahlerDifferentialModules(self)(self)

    def de_rham_algebra(self):
        r"""Return the algebraic de Rham algebra ``Omega^*_{A/R}``."""
        from sage_extensions.categories.algebras.de_rham_algebras import (
            DeRhamAlgebras,
        )

        return DeRhamAlgebras(self.base_ring())(self)

    def de_rham_cohomology(self, degree):
        r"""``H^degree_dR(A/R)``, the image of this algebra under the de Rham cohomology functor."""
        commutative_algebras = Algebras(self.base_ring()).Associative().Unital().Commutative()
        return commutative_algebras.de_rham_cohomology(degree)(self)


class _AlgebraTensorSquareFunctor(Functor):
    r"""The diagonal tensor-square endofunctor on modules over a commutative ring."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        modules = Modules(self._base_ring)
        super().__init__(modules, modules)

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, module):
        return Modules(self.base_ring()).tensor_product((module, module))

    def _apply_morphism(self, morphism):
        return morphism.tensor_product_map(
            morphism,
            source=self(morphism.domain()),
            target=self(morphism.codomain()),
        )

    def _repr_(self) -> str:
        return f"Tensor-square endofunctor on {self.domain()}"


@cached_function(key=lambda base_ring: id(_owned_ring(base_ring)))
def _algebra_tensor_square_functor(base_ring):
    ring = _owned_ring(base_ring)
    assert ring in OwnedRings().Commutative(), (
        f"the tensor square of algebras over {ring} is defined here only for a commutative ring, "
        f"but {ring} is not known to be commutative"
    )
    return _AlgebraTensorSquareFunctor(ring)


def _fix_selected_algebra_resolution(
    algebra,
    owner,
    source_factory,
    labels,
    generator_morphism,
    augmentation_factory,
) -> None:
    r"""Retain one chosen degree-zero free-algebra resolution.

    The free source and the augmentation out of it are built when the
    resolution is first asked for, as the resolution itself is: an algebra
    whose construction registers its resolution (the matrix algebra
    ``End_R(F)``) must not build a tensor algebra while it is constructed.
    ``augmentation_factory`` receives the source.
    """

    def selected_resolution():
        from sage_extensions.categories.abstract_categories.resolutions import (
            Resolutions,
        )
        from sage_extensions.categories.algebras.free_algebras import (
            SymmetricAlgebras,
        )

        ordinary = Algebras(algebra.base_ring()).Associative().Unital()
        if owner.is_subcategory(ordinary.Commutative()):
            projectives = Cat().meet((
                SymmetricAlgebras(algebra.base_ring()),
                Modules(algebra.base_ring()).Projective(),
            ))
        else:
            projectives = ordinary.ProjectiveAsAlgebra()
        source = source_factory()
        return Resolutions(
            owner, projectives, 0,
            augmentation_family=Sets().category_packet().Epis(),
        ).selected_degree_zero(
            algebra,
            source,
            augmentation_factory(source),
            generating_set=labels,
            generator_morphism=generator_morphism,
        )

    _fix_selected_resolution(algebra, owner, selected_resolution, generating_set=labels)


def _install_selected_algebra_generators(
    algebra,
    generating_family,
    *,
    source=None,
    owner=None,
) -> None:
    r"""Turn constructor-selected algebra generators into resolution data."""
    associative = Algebras(algebra.base_ring()).Associative().Unital()
    match owner:
        case None:
            match algebra in associative.Commutative():
                case True:
                    owner = associative.Commutative()
                case False:
                    owner = associative
        case _:
            pass
    labels = generating_family.index_set()
    values = generating_family.map(algebra)
    free_source_is_algebra = source is algebra
    match source:
        case None:
            module = algebra.base_ring().free_module(labels)
            match owner is associative:
                case True:
                    source = module.tensor_algebra()
                case False:
                    source = module.symmetric_algebra()
            # The free module on a label set is cached by equality of label
            # sets, so the free algebra states its maps on its own label set.
            labels = source.algebra_generating_set()
        case _:
            pass
    generator_morphism = Sets().Mor(labels, algebra)(values.value)
    _fix_selected_algebra_resolution(
        algebra,
        owner,
        lambda: source,
        labels,
        generator_morphism,
        (
            (lambda free_source: free_source.Mor(algebra).identity())
            if free_source_is_algebra
            else (lambda free_source: free_source.Mor(algebra)(generator_morphism))
        ),
    )


class _SelectedFiniteAlgebraPresentationBackend:
    r"""Computational data derived from one selected finite algebra resolution."""

    def __init__(self, presentation_ideal, lift_to_presentation, cover_map=None) -> None:
        self._presentation_ideal = presentation_ideal
        self._lift_to_presentation = lift_to_presentation
        self._cover_map = cover_map

    def presentation_ideal(self):
        return self._presentation_ideal

    def lift(self, element):
        return self._lift_to_presentation(element)

    def cover_map(self):
        return self._cover_map


def _fix_selected_algebra_presentation(
    algebra,
    presentation_ring,
    relations,
    presentation_ideal,
    lift_to_presentation,
    *,
    presentation_cover_map=None,
) -> None:
    r"""Promote a selected finite presentation in its actual algebra theory.

    A polynomial presentation on several variables has a commutative free
    degree one. Its degeneracy cannot send commuting variables to distinct
    generators of a noncommutative tensor algebra. When degree zero also
    represents an associative projective algebra, the associative diagram
    retains that stronger lifting property and its original augmentation.
    The supplying constructors fix a free presentation on these actual
    labels; projectivity alone would not justify this generator inclusion.
    """
    owner = algebra.algebra_framing_owner()
    degree_zero = algebra.selected_algebra_resolution()
    match degree_zero.truncation():
        case 0:
            pass
        case _:
            raise ValueError(
                f"{algebra} already carries a selected algebra resolution through degree "
                f"{degree_zero.truncation()}; its finite presentation cannot be fixed a second time"
            )
    match degree_zero.level(0) is presentation_ring:
        case False:
            raise ValueError(
                f"the selected presentation of {algebra} is on {presentation_ring}, but its "
                f"degree-zero free algebra is {degree_zero.level(0)}"
            )
        case True:
            pass
    labels = degree_zero.generating_set()
    if labels.is_finite() is not True or relations.index_set().is_finite() is not True:
        raise NotImplementedError(
            f"the selected finite presentation of {algebra} needs proved finite "
            "generator and relation families before its two free levels can be formed; "
            "undecided finiteness does not refute finite presentation"
        )
    relation_labels = finite_ordered_set(tuple(relations.index_set()))

    def selected_resolution():
        from sage_extensions.categories.algebras.free_algebras import (
            SymmetricAlgebras,
        )

        degree_one_labels = finite_ordered_set(
            tuple(("generator", label) for label in labels)
            + tuple(("relation", index) for index in relation_labels)
        )
        base = algebra.base_ring()
        ordinary = Algebras(base).Associative().Unital()
        if presentation_ring in ordinary.ProjectiveAsAlgebra():
            presentation_owner = ordinary
            degree_one = base.free_module(degree_one_labels).tensor_algebra()
            relation_source = base.free_module(relation_labels).tensor_algebra()
        elif presentation_ring in Cat().meet((
            SymmetricAlgebras(base), Modules(base).Projective(),
        )):
            presentation_owner = ordinary.Commutative()
            degree_one = base.free_module(degree_one_labels).symmetric_algebra()
            relation_source = base.free_module(relation_labels).symmetric_algebra()
        else:
            raise NotImplementedError(
                f"the retained presentation ring {presentation_ring} of {algebra} "
                "needs represented projectivity in its associative or commutative "
                "algebra theory before a selected projective presentation can be formed; "
                "its defining ring, relations and augmentation are retained"
            )

        def first_face_value(tagged):
            match tagged[0]:
                case "generator":
                    return presentation_ring.algebra_generator(tagged[1])
                case "relation":
                    return presentation_ring.zero()

        def second_face_value(tagged):
            match tagged[0]:
                case "generator":
                    return presentation_ring.algebra_generator(tagged[1])
                case "relation":
                    return relations.value(tagged[1])

        degree_one_generating_set = degree_one.algebra_generating_set()
        first_face = degree_one.Mor(presentation_ring)(
            Sets().Mor(degree_one_generating_set, presentation_ring)(first_face_value)
        )
        second_face = degree_one.Mor(presentation_ring)(
            Sets().Mor(degree_one_generating_set, presentation_ring)(second_face_value)
        )
        degeneracy = presentation_ring.Mor(degree_one)(
            Sets().Mor(
                labels,
                degree_one,
            )(
                lambda label: degree_one.algebra_generator(("generator", label))
            )
        )
        resolution_category = (
            presentation_owner.FinitelyPresentedAsAlgebra().resolution_category()
        )
        return resolution_category.selected_presentation(
            algebra,
            presentation_ring,
            degree_one,
            degree_zero.augmentation(),
            first_face,
            second_face,
            degeneracy,
            generating_set=labels,
            generator_morphism=degree_zero.generator_morphism(),
            relation_source=relation_source,
            relations=relations,
        )

    _fix_selected_resolution(
        algebra,
        owner,
        selected_resolution,
        replace=True,
    )
    algebra._selected_algebra_presentation_backend = (
        _SelectedFiniteAlgebraPresentationBackend(
            presentation_ideal,
            lift_to_presentation,
            presentation_cover_map,
        )
    )


# ---------------------------------------------------------------------------
# Identities of a multiplication, decided on module generators.
# ---------------------------------------------------------------------------


def _product_on(multiplication):
    r"""``(x, y) |-> m(x, y)`` for ``m`` in ``M.bilinear_forms(M)``.

    That space is ``Hom_R(M (x)_R M, M)`` where the tensor square is
    represented, whose arrows evaluate on two elements through the pure
    tensor, and the bilinear maps ``M x M -> M`` otherwise; both evaluate on
    two elements of ``M``.
    """
    return lambda left, right: multiplication(left, right)


def _decide_on_module_generators(module, identity, arity, statement):
    r"""Decide an algebra law by its determining equations on module generators.

    Associativity and Jacobi are trilinear, commutativity is bilinear, and
    the equations for a fixed unit are linear. Their equations on spanning
    generators therefore determine the law. Alternation instead uses the
    diagonal and polarized equations supplied by ``_alternation``; its
    diagonal equation is quadratic, not multilinear in the tuple arguments.

    Only literally proved finiteness permits traversal. With no selected
    determining family, the answer is ``statement``, the owned proposition
    of the law. The existing module and set suppliers retain their own
    exact-cardinality and enumeration frontiers (``DEV-52``).
    """
    ring = module.base_ring()
    match module:
        case _ if module.has_selected_module_resolution() and module.module_generating_set().cardinality().is_finite() is True:
            labels = module.module_generating_set()
            return conjunction(
                identity(*(module.module_generator(label) for label in labels_tuple))
                for labels_tuple in itertools.product(labels, repeat=arity)
            )
        case _:
            return statement


def _associativity(multiplication):
    product = _product_on(multiplication)
    return lambda x, y, z: product(product(x, y), z) == product(x, product(y, z))


def _commutativity(multiplication):
    product = _product_on(multiplication)
    return lambda x, y: product(x, y) == product(y, x)


def _alternation(multiplication):
    r"""The diagonal and polarized generator criterion for an alternating bilinear map.

    For ``x = sum_i r_i e_i``, bilinearity expands ``[x,x]`` as the sum of
    ``r_i^2 [e_i,e_i]`` and ``r_i r_j ([e_i,e_j]+[e_j,e_i])`` for ``i<j``.
    Thus both equations are needed on a spanning family, including in
    characteristic two. Skew-symmetry alone does not force the diagonal
    brackets to vanish.
    """
    product = _product_on(multiplication)
    zero = multiplication.codomain().zero()
    return lambda x, y: conjunction((
        product(x, x) == zero, product(x, y) + product(y, x) == zero,
    ))


def _jacobi_identity(multiplication):
    product = _product_on(multiplication)
    zero = multiplication.codomain().zero()
    return lambda x, y, z: product(x, product(y, z)) + product(y, product(z, x)) + product(z, product(x, y)) == zero


def _two_sided_unit(multiplication, unit):
    product = _product_on(multiplication)
    return lambda x: conjunction((product(unit, x) == x, product(x, unit) == x))


def _assert_not_refuted(held, statement, module):
    r"""Reject a disproved law; otherwise construct under the stated law.

    An axiom constructor states its identities as hypotheses on the supplied
    multiplication.  Finitary data can decide them; an undecided computation
    does not imply that the algebra has no such structure (``CON-16``).
    """
    assert held is not False, f"{statement} fails for the stated multiplication on {module}"


def _root_algebra_law_decisions(algebra):
    r"""Return the retained premises supporting the root algebra axioms of ``algebra``."""
    ring = algebra.algebra_base_ring()
    algebras = Algebras(ring)
    decisions = {}
    for category, accessors in (
        (algebras.Associative(), (("associativity", algebra.associativity_decision),)),
        (algebras.Unital(), (("unit", algebra.unit_laws_decision),)),
        (algebras.Commutative(), (("commutativity", algebra.commutativity_decision),)),
        (
            algebras.Lie(),
            (
                ("alternation", algebra.alternation_decision),
                ("jacobi", algebra.jacobi_decision),
            ),
        ),
    ):
        match algebra in category:
            case True:
                decisions.update((law, accessor()) for law, accessor in accessors)
            case False:
                pass
    return decisions



# ---------------------------------------------------------------------------
# The category of algebras.
# ---------------------------------------------------------------------------


def _algebra_structure_morphism(algebra):
    r"""Return the scalar structure map determined by an algebra's retained module action."""
    selected = algebra._selected_algebra_structure_morphism()
    if selected is not None:
        return selected
    ring = algebra.algebra_base_ring()
    if ring is algebra:
        return OwnedRings().Mor(ring, ring).identity()
    rho = algebra.scalar_action()
    match algebra:
        case _ if algebra in Algebras(ring).Associative().Unital():
            center = algebra.ring_center()
            module = algebra.unformed_module()
            unit = algebra._underlying_additive_element(algebra.one())
            return OwnedRings().Mor(ring, center)(
                lambda scalar: center(algebra(module(rho(ring(scalar))(unit)))),
            )
        case _:
            return rho


class Algebras(OwnedCategoryOverBaseRing):
    r"""Algebras over a commutative ring ``R``: an ``R``-module with an ``R``-bilinear multiplication.

    The defining datum is the pair ``(M, m)``, ``m: M (x)_R M -> M``, and
    ``Algebras(R)(M, m)`` is the one entry.  The algebra is built on the data
    of ``M``, retains ``M`` as ``unformed_module()`` and ``m`` as
    ``multiplication()``, and its elements pass to and from ``M`` by
    coercion.  A unit, associativity, commutativity and the Lie identities are
    axioms above this node.
    """

    def parameter_category(self):
        r"""The coefficient datum is a commutative unital ring."""
        return OwnedRings().Commutative()

    def an_object(self):
        r"""The coefficient ring with its identity scalar action over this base.

        A coefficient ring may already be represented as an algebra over a
        smaller ring. The regular scalar module supplies the requested
        identity action, rather than reusing that different algebra datum.
        """
        return _scalar_module(self.base_ring())

    def _repr_object_names(self):
        return f"algebras over {self.base_ring()}"

    def super_categories(self):
        return [Modules(self.base_ring()), Magmas()]

    def _categorical_coproduct(self, left, right):
        r"""Do not substitute a module direct sum for an algebra coproduct.

        The root theory has multiplicative, not necessarily unital or
        associative, arrows. The tensor coproduct supplier belongs only to
        associative unital commutative algebras; the inherited additive
        coproduct does not have the root algebra universal property.
        """
        raise NotImplementedError(
            f"a binary coproduct of {left} and {right} in root {self} "
            "requires a multiplicative universal construction; neither the "
            "module sum nor the unital commutative tensor coproduct supplies it"
        )

    def underlying_module(self):
        r"""Return the forgetful functor ``Alg_R -> Mod_R`` from this category."""
        from sage_extensions.categories.functors.algebra_modules import (
            _algebra_underlying_module_functor,
        )

        return _algebra_underlying_module_functor(self.base_ring(), self)

    class SubcategoryMethods:
        def underlying_module(self):
            r"""Return the forgetful functor from this refined algebra category."""
            from sage_extensions.categories.functors.algebra_modules import (
                _algebra_underlying_module_functor,
            )

            return _algebra_underlying_module_functor(self.base_ring(), self)

        def base_change_adjunction(self, ring_map):
            r"""Return the ambient associative-unital ``S tensor_R - -| Res_f``.

            A refinement accesses this same ambient adjunction; its returned
            functors have the full associative-unital categories as their
            domain and codomain. No restriction to the calling refinement is
            inferred from access through that category.
            """
            ordinary = Algebras(self.base_ring()).Associative().Unital()
            match self.is_subcategory(ordinary):
                case True:
                    pass
                case False:
                    assert False, (
                        f"scalar change on {self} needs a general algebra functor and arrow supplier; "
                        f"the available adjunction has the associative-unital domain {ordinary}"
                    )
            if _owned_ring(ring_map.domain()) is not self.base_ring():
                raise ValueError(
                    f"scalar change along {ring_map} for algebras over {self.base_ring()} needs a ring map "
                    f"starting at {self.base_ring()}, but it starts at {ring_map.domain()}"
                )
            from sage_extensions.categories.functors.algebra_scalar_change import (
                _algebra_base_change_adjunction,
            )

            return _algebra_base_change_adjunction(ring_map)

        def scalar_extension(self, ring_map):
            r"""Return scalar extension on the ambient associative-unital categories."""
            return self.base_change_adjunction(ring_map).left_adjoint()

        def restriction_of_scalars(self, ring_map):
            r"""Return ``Res_f: Alg_S -> Alg_R`` on associative unital algebras.

            Here ``f: R -> S`` ends at this category's base S. As with
            ``base_change_adjunction``, access through a refinement returns
            the ambient functor. General algebra objects can already call
            ``restrict_scalars``; a general functor also needs its arrow
            supplier and is not asserted by the ordinary adjunction.
            """
            ordinary = Algebras(self.base_ring()).Associative().Unital()
            match self.is_subcategory(ordinary):
                case True:
                    pass
                case False:
                    assert False, (
                        f"scalar restriction on {self} needs a general algebra functor and arrow supplier; "
                        f"the available adjunction restricts the associative-unital category {ordinary}"
                    )
            if _owned_ring(ring_map.codomain()) is not self.base_ring():
                raise ValueError(
                    f"restriction of scalars along {ring_map} from algebras over {self.base_ring()} needs a ring "
                    f"map ending at {self.base_ring()}, but it ends at {ring_map.codomain()}"
                )
            source = Algebras(ring_map.domain()).Associative().Unital()
            return source.base_change_adjunction(ring_map).right_adjoint()

        def Associative(self):
            r"""Return the refinement satisfying ``(xy)z=x(yz)``."""
            return self._with_axiom("Associative")

        def Unital(self):
            r"""Return the refinement with a two-sided unit."""
            return self._with_axiom("Unital")

        def Commutative(self):
            r"""Return the refinement satisfying ``xy=yx``."""
            return self._with_axiom("Commutative")

        def Lie(self):
            r"""Return the refinement whose multiplication is a Lie bracket."""
            return self._with_axiom("Lie")

    def Mor(self, domain, codomain):
        r"""Return the unique Mor object ``Hom_{R-Alg}(domain,codomain)``."""
        if domain not in self or codomain not in self:
            raise TypeError(
                f"a morphism of algebras in {self} needs two algebras in it, but got {domain} and {codomain}"
            )
        return self.MorCategory().Of(domain, codomain)

    _MorCategory = AlgebraMorCategoryConstruction

    def _call_(self, module, multiplication):
        r"""The algebra on ``M`` with multiplication ``m: M (x)_R M -> M``: the one entry.

        No identity of ``m`` is assumed or placed here; the axiom entries
        ``Associative()``, ``Unital()``, ``Commutative()`` and ``Lie()`` place
        an algebra on the identities they decide.
        """
        assert module.base_ring() is self.base_ring(), (
            f"an algebra over {self.base_ring()} is built on a module over {self.base_ring()}, but {module} "
            f"is a module over {module.base_ring()}"
        )
        return _algebra_on_module(module, multiplication, placement=(self,))

    class ElementMethods:
        def _mul_(self, other):
            r"""``x * y`` is the multiplication evaluated on ``x (x) y`` in the module it is stated on.

            Elements pass to that module and back by coercion.
            """
            algebra = self.parent()
            module = algebra.unformed_module()
            product = _product_on(algebra.multiplication())
            return algebra(product(module(self), module(other)))

    class ParentMethods:
        @RealizationHook
        def _cardinality_decision(self):
            r"""Return the cardinality of the module carrying this algebra."""
            module = self.unformed_module()
            match module is self:
                case True:
                    return super()._cardinality_decision()
                case False:
                    return module._cardinality_decision()

        def _specialized_algebra_with_structure(
            self,
            base_ring,
            labels,
            categories,
            construction_data,
        ):
            r"""Internal construction hook for a specialized algebra realization.

            Protected Algebras constructor contract under OWN-05.  The sole
            caller is ``_algebra_with_structure``. A specialized algebra owner may return
            the owned algebra preserving its defining representation while
            adding the requested labels, categories, and construction data;
            the default returns None.  No engine handle is exchanged.  This
            hook exists because representation-preserving reconstruction is a
            constructor responsibility, not an ordinary mathematical
            operation on an already constructed algebra.
            """
            _ = (base_ring, labels, categories, construction_data)
            return None

        def __init__(
            self,
            unformed_module=None,
            multiplication=None,
            *,
            algebra_law_decisions=None,
            algebra_generating_family=None,
            algebra_framing_source=None,
            algebra_framing_owner=None,
            _engine_product=None,
            _engine_scalar_action=None,
            _native_unit_factory=None,
            **rest,
        ) -> None:
            r"""Construct the algebra from its exact module and tensor multiplication.

            Native cooperative realizations supply primitive ring operations;
            after the lower constructor finishes they compute the same module
            and tensor datum through the owners used by every ordinary entry.
            """
            self._preamble_algebra_law_decisions = dict(
                vars(self).get("_preamble_algebra_law_decisions", {})
            )
            if algebra_law_decisions is not None:
                self._retain_algebra_law_decisions(algebra_law_decisions)
            match _engine_product:
                case None:
                    assert unformed_module is not None and multiplication is not None, (
                        "an algebra needs its module and its multiplication M (x) M -> M, but one of them is missing"
                    )
                    self._retain_algebra_datum(unformed_module, multiplication)
                    super().__init__(**rest)
                case product:
                    assert unformed_module is None and multiplication is None, (
                        "an algebra computed by a computer-algebra system cannot also be given a module and a "
                        "multiplication"
                    )
                    assert callable(product) and callable(_engine_scalar_action) and callable(_native_unit_factory)
                    super().__init__(**rest)
            match algebra_generating_family:
                case None:
                    pass
                case family:
                    _install_selected_algebra_generators(
                        self,
                        family,
                        source=algebra_framing_source,
                        owner=algebra_framing_owner,
                    )
            match _engine_product:
                case None:
                    # _OwnedAlgebraParent deliberately starts with only the
                    # minimal ring/additive placement. Its selected algebra
                    # framing is installed after this Parent initialization;
                    # constructing the native module here would ask its
                    # category hooks for that framing before it exists.
                    pass
                case product:
                    # Some algebra owners (notably _OwnedAlgebraParent) must
                    # install their selected resolution after this cooperative
                    # Parent initialization returns. Honor that owner contract
                    # rather than installing the regular module merely because
                    # the generating family is already visible: the resolution
                    # and module datum are distinct construction obligations.
                    from sage_extensions.categories.modules.pure.modules import Modules

                    defer_to_owner = getattr(
                        self, "_defer_native_algebra_construction", lambda: False
                    )()
                    if (
                        not defer_to_owner
                        and Modules.ParentMethods._native_module_presentation(self) is None
                    ):
                        _algebra_from_native_ring(
                            self,
                            product,
                            _native_unit_factory(self),
                            _engine_scalar_action,
                            module_basis=getattr(self, "_native_module_basis", None),
                            scalar_ring=vars(self).get("_preamble_selected_algebra_base_ring"),
                        )

        def _retain_algebra_law_decisions(self, decisions):
            r"""Retain the exact admission decision supporting each algebra axiom placement."""
            retained = dict(vars(self).get("_preamble_algebra_law_decisions", {}))
            for law, decision in dict(decisions).items():
                assert decision is True or decision in Propositions, (
                    f"the {law} law of an algebra is recorded only as True or as the proposition "
                    f"stating it, but got {decision}"
                )
                if retained.get(law) is not True:
                    retained[law] = decision
            self._preamble_algebra_law_decisions = retained

        def associativity_decision(self):
            r"""Return the exact associativity premise admitted with ``(M,m)``.

            This reads construction data, rather than a generic predicate of
            the magma law. An undecided admitted proposition stays that
            proposition even when the algebra is declared associative. With
            no admitted datum, return the proposition of the law on m.
            """
            return self._preamble_algebra_law_decisions.get(
                "associativity", AtomicProposition("is_associative", self.multiplication())
            )

        def unit_laws_decision(self):
            r"""Return the exact premise admitted for the selected algebra unit.

            This construction-datum accessor does not replace an undecided
            admitted proposition by True merely because a unital axiom was
            declared. With no admitted datum it returns the law proposition.
            """
            return self._preamble_algebra_law_decisions.get(
                "unit", AtomicProposition("is_two_sided_unit", self.multiplication())
            )

        def commutativity_decision(self):
            r"""Return the exact commutativity premise admitted with ``(M,m)``.

            Unlike the generic ``is_commutative`` predicate, this reads the
            constructor's original datum and retains its undecided proposition
            after axiom admission. With no datum it returns the law proposition.
            """
            return self._preamble_algebra_law_decisions.get(
                "commutativity", AtomicProposition("is_commutative", self.multiplication())
            )

        def alternation_decision(self):
            r"""Return the exact alternation premise admitted with ``(M,m)``.

            This is construction data, including an admitted undecided
            proposition, rather than a new computation of the bracket law.
            With no datum it returns the proposition of alternation on m.
            """
            return self._preamble_algebra_law_decisions.get(
                "alternation", AtomicProposition("is_alternating", self.multiplication())
            )

        def jacobi_decision(self):
            r"""Return the exact Jacobi premise admitted with ``(M,m)``.

            This construction-datum accessor keeps an admitted undecided
            proposition; it does not decide the identity from Lie placement.
            With no datum it returns the proposition of the identity on m.
            """
            return self._preamble_algebra_law_decisions.get(
                "jacobi", AtomicProposition("satisfies_jacobi_identity", self.multiplication())
            )

        def _retain_algebra_datum(self, module, multiplication):
            r"""Retain the root constructor's already validated (M,m) once.

            Called by this level's constructor and by _algebra_on_module when
            the canonical native realization is the already constructed M.
            Both callers supply an actual tensor morphism. A second product
            never mutates an existing algebra.
            """
            previous = vars(self).get("_preamble_multiplication")
            if previous is not None:
                assert previous is multiplication and self._preamble_unformed_module is module, (
                    f"the multiplication of an algebra cannot be replaced: it already has {previous} on "
                    f"{self._preamble_unformed_module}"
                )
                return
            self._preamble_unformed_module = module
            self._preamble_multiplication = multiplication

        def unformed_module(self):
            r"""The module ``M`` this algebra is built on: the ``M`` of ``Algebras(R)(M, m)``, or the algebra itself when it realizes its own module."""
            native = self._native_module_presentation()
            if native is not None:
                return native.module()
            retained = vars(self).get("_preamble_unformed_module")
            match retained:
                case _ if retained is not None:
                    return retained
                case _:
                    from sage_extensions.categories.group.additive_mors import (
                        AdditiveEndomorphismRings,
                    )

                    match self:
                        case _ if self in AdditiveEndomorphismRings(self.base_ring()):
                            return self
                        case _:
                            assert False, (
                                f"{self} was constructed as an algebra without retaining the module its "
                                "multiplication is defined on"
                            )

        def _element_of_unformed_module(self, element):
            r"""The element of :meth:`unformed_module` on the data of ``element``.

            ``Algebras(R)(M, m)`` builds on the framing of ``M`` when ``M``
            has one, so an element reads there with the same coefficients;
            otherwise it builds on the underlying additive group of ``M``, and
            an element reads there as its underlying additive element.
            """
            module = self.unformed_module()
            match self:
                case _ if self.has_selected_module_resolution():
                    coordinates = self._framing_lift(self(element))
                    return module.linear_combination(
                        coordinates.parent()._selected_module_coefficients(coordinates)
                    )
                case _:
                    return module(self._underlying_additive_element(element))

        def _element_from_unformed_module(self, element):
            r"""The element of this algebra on the data of an element of :meth:`unformed_module`."""
            module = self.unformed_module()
            match self:
                case _ if self.has_selected_module_resolution():
                    coordinates = module.framing_morphism().lift(element)
                    return self.linear_combination(
                        coordinates.parent()._selected_module_coefficients(coordinates)
                    )
                case _:
                    return self(module._underlying_additive_element(element))

        def multiplication(self):
            r"""The multiplication ``m: M (x)_R M -> M`` this algebra was stated with, an element of ``M.bilinear_forms(M)``.

            A ring that is its own algebra is stated by its product, not by a
            map out of a tensor product (``OWN-22``), so for it the map is
            built from that product here, when it is asked for.
            """
            stated = vars(self).get("_preamble_multiplication")
            if stated is not None:
                return stated
            native = self._native_module_presentation()
            match native:
                case _ if native is not None:
                    return native.multiplication()
                case _:
                    from sage_extensions.categories.group.additive_mors import (
                        AdditiveEndomorphismRings,
                    )

                    match self:
                        case _ if self in AdditiveEndomorphismRings(self.base_ring()):
                            from sage_extensions.categories.modules.native_modules import (
                                _RingModulePresentation,
                            )

                            presentation = _RingModulePresentation(
                                self,
                                self.base_ring(),
                                self._compose_endomorphisms,
                                self.identity(),
                                lambda scalar, arrow: self._owned_scalar_multiple(scalar, arrow),
                            )
                            return presentation.multiplication()
                        case _:
                            assert False, f"{self} was constructed without a multiplication"

        @cached_method
        def multiplication_morphism(self):
            r"""The linear classifier ``A tensor_R A -> A`` of the product.

            The module tensor owner supplies the universal map for both
            framed and unframed modules.  Transport of the product from the
            retained module is bilinear because the element crossings preserve
            that module's addition and scalar action.
            """
            ring = self.algebra_base_ring()
            module = self.unformed_module()
            product = _product_on(self.multiplication())
            tensor = _algebra_tensor_square_functor(ring)(self)
            return tensor.from_bilinear_map(
                self, lambda left, right: self(product(module(left), module(right))),
            )

        @RealizationHook
        def _selected_algebra_structure_morphism(self):
            r"""Supply an already retained scalar-structure map, or ``None``.

            Only the common ``algebra_structure_morphism`` construction,
            through ``_algebra_structure_morphism``, calls this protected
            datum supplier. Its value is the structure map of the actual
            retained module action: for an associative unital algebra it
            is the owned ring map from the coefficient ring to the centre.
            A completion realization supplies its retained completion map
            when that source is its coefficient ring. ``None`` selects the
            existing derivation from the module action; it does not choose
            a different coefficient ring or scalar action.
            """
            return None

        @cached_method
        def algebra_structure_morphism(self):
            r"""The structure morphism \(\rho\) of this \(R\)-algebra.

            Over commutative \(R\), \(\rho\colon R\to\operatorname{End}(A)\) is
            the scalar action of the underlying module: \(\rho(r)\) commutes
            with left and right multiplication by bilinearity, so it lies in
            the centroid of \(A\).  On a unital associative algebra the
            centroid is the centre through \(\varphi\mapsto\varphi(1)\), and
            the structure morphism is the ring map \(R\to Z(A)\),
            \(r\mapsto\rho(r)(1)\), computed here from \(\rho\).
            """
            return _algebra_structure_morphism(self)

        def _with_structure(
            self,
            categories: tuple[Category, ...],
            construction_data: dict[str, ConstructionData],
            *,
            engine: type | None = None,
        ) -> ObjectOfCategory:
            r"""Construct this algebra again with the categories and data of further levels.

            The protected construction contract of ``Objects`` (``OWN-05``,
            ``OWN-16``); its roles and the reason no public operation does
            this are stated at ``Objects.ParentMethods._with_structure``.
            A general algebra retains its original module, multiplication
            and selected laws through that fixed defining construction;
            its scalar action need not be a map into a ring. Associative
            unital algebras also admit the ring realization below through
            their central structure map. Callers are the levels that add
            structure on a received object (slices, coslices).
            """
            if self not in Algebras(self.algebra_base_ring()).Associative().Unital():
                return Objects.ParentMethods._with_structure(
                    self, categories, construction_data, engine=engine,
                )
            added_categories, added_data = self._added_structure(construction_data)
            structure_map = self.algebra_structure_morphism()
            if structure_map.codomain() is not self:
                match structure_map.codomain():
                    case center if center in PredicateSubrings():
                        center_inclusion = center.inclusion()
                    case _:
                        center_inclusion = self.center_inclusion()
                assert center_inclusion.domain() is structure_map.codomain() and center_inclusion.codomain() is self, (
                    "the centre inclusion used to retain an algebra action must end at this exact algebra"
                )
                structure_map = center_inclusion * structure_map
            return _algebra_structure_on(
                self,
                structure_map,
                categories=(*added_categories, *categories),
                construction_data=added_data,
                engine=engine,
            )

        def restrict_scalars(self, ring_map):
            r"""Return this algebra with scalars restricted along ``ring_map``."""
            from sage_extensions.categories.algebras.restricted_scalars import (
                _restrict_algebra_scalars,
            )

            return _restrict_algebra_scalars(self, ring_map)

        def derivations(self, target_module=None):
            r"""Return the R-linear maps satisfying ``D(xy)=D(x)y+xD(y)``.

            The default target is this algebra with its left and right
            multiplication. A different target needs the corresponding two
            R-bilinear actions. For a commutative unital associative algebra,
            an ordinary module supplies the symmetric actions; the existing
            Kahler-differential computation returns ``Der_R(A,M)`` as an
            A-module (Stacks, Tag 00RM). A left module alone does not supply
            both actions for an arbitrary algebra.
            """
            from sage_extensions.categories.algebras.derivations import (
                _derivations,
            )

            match self:
                case _ if self in Algebras(self.algebra_base_ring()).Associative().Unital().Commutative():
                    if target_module is None:
                        target_module = self.regular_module()
                    return _derivations(self, target_module)
                case _:
                    assert False, (
                        f"derivations of {self} require a computation of the R-linear Leibniz equations "
                        "with the target's left and right actions; the available computation uses "
                        "Kahler differentials of a commutative unital associative algebra"
                    )

        def vector_fields(self):
            r"""Return ``Der_R(self,self)`` with the two regular multiplication actions."""
            return self.derivations()

        def is_algebra(self) -> bool:
            return True

        def algebra_framing_owner(self):
            r"""Return the algebra owner relative to which the chosen resolution is stored."""
            associative = Algebras(self.base_ring()).Associative().Unital()
            commutative = associative.Commutative()
            match self.has_selected_resolution(commutative):
                case True:
                    return commutative
                case False:
                    match self.has_selected_resolution(associative):
                        case True:
                            return associative
                        case False:
                            raise ValueError(
                                f"{self} has no chosen generating resolution as an algebra"
                            )

        def is_framed_algebra(self) -> bool:
            associative = Algebras(self.base_ring()).Associative().Unital()
            return (
                self.has_selected_resolution(associative)
                or self.has_selected_resolution(associative.Commutative())
            )

        def is_finitely_generated_as_algebra(self):
            r"""Whether finitely many elements generate this ``R``-algebra.

            Generation uses the retained scalar action, addition and
            multiplication, with arbitrary parenthesization when needed.
            It is defined without associativity or a unit. Forgetting an
            existing unit preserves finite generation by adjoining that one
            element to a finite generating family.

            A finite algebra generating family or a finitely generated
            underlying module proves the property. An infinite selected
            family, failure of module finite generation, or absence of a
            selected family does not refute algebra finite generation.
            """
            ring = self.algebra_base_ring()
            match self:
                case _ if self in Algebras(ring).Associative().Unital().FinitelyGeneratedAsAlgebra():
                    return True
                case _ if (
                    self.is_framed_algebra()
                    and self.algebra_generating_set().is_finite() is True
                ):
                    return True
                case _ if self.unformed_module().is_finitely_generated() is True:
                    return True
                case _:
                    return AtomicProposition("is_finitely_generated_as_algebra", self)

        def selected_algebra_resolution(self):
            return self.selected_resolution(self.algebra_framing_owner())

        def algebra_framing_source(self):
            return self.selected_algebra_resolution().level(0)

        def algebra_framing_morphism(self):
            return self.selected_algebra_resolution().augmentation()

        def algebra_generating_set(self):
            return self.selected_resolution_generating_set(self.algebra_framing_owner())

        def algebra_generator_morphism(self):
            return self.selected_algebra_resolution().generator_morphism()

        def algebra_generator(self, label):
            return self.selected_algebra_resolution().generator(label)

        def algebra_generators(self):
            return self.selected_algebra_resolution().generators(
                name="Algebra generators"
            )

        def number_of_algebra_generators(self):
            return self.selected_algebra_resolution().generator_count()

        def finite_algebra_generators(self):
            labels = self.algebra_generating_set()
            assert labels.cardinality().is_finite() is True, (
                f"computing the selected finite algebra generators of {self} needs a known finite "
                f"chosen family; its selected label set has cardinality {labels.cardinality()}"
            )
            return FiniteOrderedSets().from_indexed(
                labels,
                self.algebra_generator,
                name=f"Selected algebra generators of {self}",
            )

        def product_on_algebra_generators(self, left, right):
            return self.algebra_generator(left) * self.algebra_generator(right)

        def _commutativity_decision(self):
            r"""Whether ``xy = yx``: decided on module generators of ``M`` against ``m``, else the proposition.

            Commutativity is a property of the multiplication before it is a
            refinement; the ``Commutative`` axiom answers ``True`` by placement.
            """
            multiplication = self.multiplication()
            return _decide_on_module_generators(
                self.unformed_module(),
                _commutativity(multiplication),
                2,
                AtomicProposition("is_commutative", multiplication),
            )

        def algebra_base_ring(self):
            r"""The scalar ring established by this algebra's module constructor."""
            return self.base_ring()

        def underlying_module(self):
            r"""This algebra under the forgetful functor ``Alg_R -> Mod_R`` of its category."""
            return Algebras(self.algebra_base_ring()).underlying_module()(self)

        def base_change(self, ring_map):
            r"""Extend scalars along the exact unital ring map ``R -> S``.

            The multiplication on ``S tensor_R A`` sends
            ``(s tensor a, t tensor b)`` to ``st tensor ab``. It is defined
            for every bilinear algebra, without associativity or a unit.
            The selected associative-unital scalar-extension functor supplies
            its represented free, polynomial-presentation, and order cases.
            Other algebras retain the general construction obligation.
            """
            base = self.algebra_base_ring()
            if ring_map.domain() is not base:
                raise ValueError(
                    f"scalar change of {self} along {ring_map} needs a ring map "
                    f"starting at its exact coefficient ring {base}"
                )
            target = _owned_ring(ring_map.codomain())
            if target not in OwnedRings().Commutative():
                raise TypeError(
                    f"scalar change of an algebra over {base} needs a commutative "
                    f"target coefficient ring, but got {target}"
                )
            ring_map = OwnedRings().Mor(base, target)(ring_map)
            ordinary = Algebras(base).Associative().Unital()
            match self:
                case _ if self in ordinary:
                    return ordinary.scalar_extension(ring_map)(self)
                case _:
                    assert False, (
                        f"scalar change of {self} along {ring_map} needs a general "
                        "bilinear-algebra scalar-extension computation; the selected "
                        "functor currently computes associative-unital algebras"
                    )



        @RealizationHook
        @cached_method
        def _center_construction(self):
            r"""Supply the inherited magma centre and its algebra inclusion.

            Associative commutative algebras and finite group algebras use
            their selected centre constructions. On a module with finitely
            many chosen generators, bilinearity makes commutation linear in
            the unknown central element and the two nucleus equations
            trilinear. Their equalizers on generators therefore compute the
            full centre. An associative ambient algebra needs only the
            commutation equalizers. The induced product on the resulting
            submodule is commutative and associative in every case.

            If only finitely many algebra generators are selected, an
            associative unital algebra retains its existing predicate ring
            centre and inclusion. This is a different available datum from a
            selected finite module centre; the richer computation above has
            precedence when that module datum is present.

            This supplies Magmas' ``_center_construction`` contract. The
            bracket-zero centre of a Lie algebra is a different construction,
            available through ``lie_center``.
            """
            ring = self.algebra_base_ring()
            from sage_extensions.categories.algebras.group_algebras import GroupAlgebras
            from sage_extensions.categories.group.groups import FiniteGroups

            match self:
                case _ if self in Algebras(ring).Associative().Commutative():
                    return self, Algebras(ring).Mor(self, self).identity()
                case _ if self in GroupAlgebras(ring) and self.group() in FiniteGroups():
                    center = self._finite_group_algebra_center()
                case _ if (
                    self.has_selected_module_resolution()
                    and self.module_generating_set().cardinality().is_finite()
                ):
                    labels = self.module_generating_set()
                    endomorphisms = self.module_category().Mor(self, self)
                    modules = Modules(ring)

                    def commutation_equalizer(label):
                        element = self.module_generator(label)
                        left = endomorphisms._from_constructed_element_map(lambda other: other * element)
                        right = endomorphisms._from_constructed_element_map(lambda other: element * other)
                        return modules.equalizer(left, right)

                    identity = endomorphisms.identity()
                    submodule = reduce(
                        lambda central, label: central.intersection(commutation_equalizer(label)),
                        labels,
                        modules.equalizer(identity, identity),
                    )
                    if self not in Algebras(ring).Associative():
                        def nucleus_equalizer(left_label, right_label):
                            left_element = self.module_generator(left_label)
                            right_element = self.module_generator(right_label)
                            product = left_element * right_element
                            left_associated = endomorphisms._from_constructed_element_map(
                                lambda other: (other * left_element) * right_element
                            )
                            left_nested = endomorphisms._from_constructed_element_map(
                                lambda other: other * product
                            )
                            right_associated = endomorphisms._from_constructed_element_map(
                                lambda other: product * other
                            )
                            right_nested = endomorphisms._from_constructed_element_map(
                                lambda other: left_element * (right_element * other)
                            )
                            return modules.equalizer(left_associated, left_nested).intersection(
                                modules.equalizer(right_associated, right_nested)
                            )

                        submodule = reduce(
                            lambda central, pair: central.intersection(nucleus_equalizer(*pair)),
                            itertools.product(labels, repeat=2),
                            submodule,
                    )
                    center = _center_algebra(self, submodule)
                case _ if (
                    self in Algebras(ring).Associative().Unital()
                    and self.is_framed_algebra()
                    and self.algebra_generating_set().cardinality().is_finite()
                ):
                    center = self.ring_center()
                    if center is self:
                        return center, OwnedRings().Mor(self, self).identity()
                    assert center in PredicateSubrings(), (
                        f"the selected ring centre of {self} needs its retained "
                        "inclusion; the available algebra-generator fallback "
                        "uses the existing predicate subring inclusion"
                    )
                    return center, center.inclusion()
                case _:
                    assert False, (
                        f"the centre of {self} needs a represented computation of its centrality "
                        "equations: the available module equalizer algorithm needs finitely many "
                        "chosen module generators for commutation and the two nucleus equations; "
                        "an associative unital algebra can also use a finite chosen algebra "
                        "generating family for its predicate ring centre"
                    )
            submodule = center.unformed_module()
            inclusion = submodule.inclusion()
            linear_inclusion = center.module_category().Mor(
                center, self
            )._from_constructed_element_map(
                lambda element: inclusion(submodule(element)),
                premises=(inclusion,),
            )
            return center, Algebras(ring).Mor(center, self)(linear_inclusion)

        def _quotient_by_algebra_elements(self, elements):
            r"""Return the quotient by the generated algebra ideal and its map.

            The two-sided ideal generated by the supplied elements is closed
            under multiplication on either side, including for a nonunital or
            nonassociative algebra.  A selected associative presentation
            retains its quotient realization; a finite module realization
            over a field uses the existing multiplication-span ideal closure.
            A bare iterable is the caller's explicitly finite list of
            relations; an owned family or set must supply decided finiteness.
            """
            from sage_extensions.categories.algebras.free_algebras import (
                SymmetricAlgebras,
                TensorAlgebras,
                _quotient_by_algebra_elements_backend,
            )

            ring = self.algebra_base_ring()
            match self:
                case _ if (
                    self in Algebras(ring).Associative().Unital()
                    and (
                        self in SymmetricAlgebras(ring)
                        or self in TensorAlgebras(ring)
                        or self in AlgebrasWithChosenFinitePresentation(ring)
                    )
                ):
                    return _quotient_by_algebra_elements_backend(self, elements)
                case _ if ring in OwnedFields() and (
                    self in FramedFreeModules(ring)
                    or self in ModulesWithChosenFinitePresentation(ring)
                ):
                    assert (
                        self.has_selected_module_resolution()
                        and self.module_generating_set().cardinality().is_finite() is True
                    ), (
                        f"the quotient of {self} by algebra elements needs a selected finite "
                        "module generating family for the multiplication-span computation"
                    )
                    match elements:
                        case IndexedFamily():
                            assert elements.cardinality().is_finite() is True, (
                                f"the selected ideal quotient of {self} needs a literally finite "
                                "relation family before computing its module span"
                            )
                            selected = elements.map(self, name="Algebra relations")
                        case tuple() | list():
                            selected = tuple(self(element) for element in elements)
                        case _ if elements in Sets():
                            assert elements.cardinality().is_finite() is True, (
                                f"the selected ideal quotient of {self} needs a known finite "
                                "owned relation set before computing its module span"
                            )
                            selected = indexed_family(
                                elements,
                                lambda element: self(element),
                                name="Algebra relations",
                            )
                        case _:
                            # Bare finite iterables are syntactic ingress,
                            # as at the existing presentation boundary.
                            selected = tuple(self(element) for element in elements)
                    quotient = self.quotient_by_generated_algebra_ideal(
                        self.subobject_on(selected)
                    )
                    projection = Algebras(ring).Mor(self, quotient)(
                        quotient.algebra_quotient_projection()
                    )
                    return quotient, projection
                case _:
                    assert False, (
                        f"the quotient of {self} by algebra elements needs a represented ideal "
                        "quotient: the available suppliers use a selected finite associative presentation "
                        "or a finite module presentation over a field"
                    )

        def quotient_by_relations(
            self,
            relations,
            *,
            _extra_categories=(),
            _extra_construction_data=None,
            _generating_module=None,
        ):
            r"""Return the quotient by the algebra ideal generated by ``relations``.

            Associativity, a unit and commutativity are not hypotheses for
            this quotient.  A selected finite associative presentation also
            retains its specified presentation and construction data.  Other
            represented algebras use the existing ideal quotient supplier on
            actual relation elements.
            """
            from sage_extensions.categories.algebras.free_algebras import (
                SymmetricAlgebras,
                TensorAlgebras,
            )

            ring = self.algebra_base_ring()
            match self:
                case _ if (
                    self in Algebras(ring).Associative().Unital()
                    and (
                        self in SymmetricAlgebras(ring)
                        or self in TensorAlgebras(ring)
                        or self in AlgebrasWithChosenFinitePresentation(ring)
                    )
                ):
                    return AlgebrasWithChosenFinitePresentation(ring)._call_(
                        self,
                        relations,
                        extra_categories=_extra_categories,
                        extra_construction_data=_extra_construction_data,
                        generating_module=_generating_module,
                    )
                case _:
                    assert (
                        not _extra_categories
                        and not _extra_construction_data
                        and _generating_module is None
                    ), (
                        f"the ideal quotient of {self} with extra presentation data needs a "
                        "represented construction retaining those data; only the selected "
                        "finite associative presentation supplies it here"
                    )
                    return self._quotient_by_algebra_elements(relations)[0]

        def algebra_ideal_generated_by(self, subobject):
            r"""The two-sided algebra ideal generated by a submodule ``I``.

            The ideal is the smallest submodule containing ``I`` and closed
            under left and right multiplication by module generators of
            \(A\).  Starting from ``I``, adjoin the products of the generators
            of the current submodule with the module generators of \(A\) on
            both sides.  Over a field a strictly ascending chain of subspaces
            of a finite-dimensional algebra has at most ``dim A`` steps, so
            the closure is reached exactly.
            """
            ring = self.algebra_base_ring()
            assert ring in OwnedFields(), (
                f"the ideal of {self} generated by {subobject} is computed here only for finite-dimensional "
                f"algebras over a field, but {ring} is not a field"
            )
            assert subobject.inclusion().codomain() is self, (
                f"the ideal of {self} generated by a submodule needs a submodule of {self}, but {subobject} "
                f"is a submodule of {subobject.inclusion().codomain()}"
            )
            assert self.has_selected_module_resolution(), (
                f"ideal closure in {self} needs a selected finite module generating family "
                "for the multiplication-span algorithm"
            )
            ambient_labels = self.module_generating_set()
            assert ambient_labels.cardinality().is_finite() is True, (
                f"the ideal of {self} generated by {subobject} needs finitely many module generators of "
                f"{self}, but it has {ambient_labels.cardinality()}"
            )
            subobjects = Modules(ring).Subobjects(self)
            current = subobject
            while True:
                inclusion = current.inclusion()
                assert current.has_selected_module_resolution(), (
                    f"ideal closure in {self} needs a selected finite generating family of {current}"
                )
                current_labels = current.module_generating_set()
                assert current_labels.cardinality().is_finite() is True, (
                    f"ideal closure in {self} needs a finite generating family of {current}; "
                    f"its selected family has cardinality {current_labels.cardinality()}"
                )
                products = tuple(
                    product
                    for ideal_label in current_labels
                    for ambient_label in ambient_labels
                    for product in (
                        self.product(self.module_generator(ambient_label), inclusion(current.module_generator(ideal_label))),
                        self.product(inclusion(current.module_generator(ideal_label)), self.module_generator(ambient_label)),
                    )
                )
                if not products:
                    return current
                enlarged = current.sum(self.subobject_on(products))
                contained = subobjects.leq(enlarged, current)
                match contained:
                    case True:
                        return current
                    case False:
                        pass
                    case _:
                        assert False, (
                            f"ideal closure in {self} needs to decide whether {enlarged} "
                            f"is contained in {current}; that submodule-containment computation "
                            "is undecided"
                        )
                current = enlarged

        def quotient_by_algebra_ideal(self, ideal):
            r"""``A/I`` for a two-sided ideal ``I`` of ``A``.

            The module cokernel of ``I -> A`` is the quotient module; it is
            presented on the module generators of ``A``, each generator of
            ``A/I`` being the image of the generator of ``A`` of the same
            name.  The product of two such images is the image of the product
            of the generators, well defined because ``I`` is an ideal.
            Associativity, commutativity, the Lie identities and a unit
            descend to quotients, so they are stated with the construction.
            """
            ring = self.algebra_base_ring()
            assert ideal.inclusion().codomain() is self, (
                f"the quotient of {self} needs an ideal of {self}, but {ideal} is an ideal of "
                f"{ideal.inclusion().codomain()}"
            )
            projection = ideal.inclusion().cokernel_projection()
            quotient_module = projection.codomain()
            multiplication = BilinearMap(
                quotient_module,
                quotient_module,
                quotient_module,
                lambda left, right: projection(
                    self.product(self.module_generator(left), self.module_generator(right))
                ),
            )
            algebras = Algebras(ring)
            descended = tuple(
                axiom
                for axiom in (algebras.Associative(), algebras.Commutative(), algebras.Lie())
                if self in axiom
            )
            law_decisions = _root_algebra_law_decisions(self)
            match self:
                case _ if self in algebras.Unital():
                    return _algebra_on_module(
                        quotient_module,
                        multiplication,
                        placement=(*descended, algebras.Unital()),
                        unit=projection(self.one()),
                        law_decisions=law_decisions,
                    )
                case _:
                    return _algebra_on_module(
                        quotient_module,
                        multiplication,
                        placement=descended,
                        law_decisions=law_decisions,
                    )

        def quotient_by_generated_algebra_ideal(self, subobject):
            r"""The quotient by the algebra ideal generated by ``subobject``."""
            ideal = self.algebra_ideal_generated_by(subobject)
            return self.quotient_by_algebra_ideal(ideal)

        def algebra_quotient_projection(self):
            r"""The projection ``A -> A/I`` of an algebra built as ``A.quotient_by_algebra_ideal(I)``, as a linear map.

            That algebra is built on the module cokernel of ``I -> A``, which
            retains its projection; the projection passes to this algebra by
            coercion.
            """
            projection = self.unformed_module().cokernel_projection()
            ambient = projection.domain()
            return ambient.module_category().Mor(
                ambient, self
            )._from_constructed_element_map(
                lambda element: self(projection(element)),
                premises=(projection,),
            )

        def algebra_quotient_ideal(self):
            r"""The ideal ``I`` of an algebra built as ``A.quotient_by_algebra_ideal(I)``: the kernel of its projection."""
            return self.unformed_module().cokernel_projection().kernel()

        def _Hom_(self, codomain, category=None):
            r"""Use the same exact algebra-arrow selection as the public Mor."""
            if category is not None and not category.is_subcategory(Algebras(self.algebra_base_ring())):
                raise TypeError(
                    f"{category} is not a category of algebras over {self.algebra_base_ring()}, so Mor({self}, "
                    f"{codomain}) cannot be formed in it"
                )
            return self.Mor(codomain, category=category)

    class Associative(CategoryWithAxiom):
        r"""Algebras whose multiplication is associative."""

        class SubcategoryMethods:
            def Unital(self):
                r"""Return the associative refinement with a two-sided unit."""
                return self._with_axiom("Unital")

            def commutator_lie_algebra(self):
                r"""Return the functor sending ``m`` to the Lie product ``m-m tau``."""
                from sage_extensions.categories.functors.commutator_lie_algebras import (
                    _commutator_lie_algebra_functor,
                )

                return _commutator_lie_algebra_functor(self.base_ring())

        @classmethod
        def _repr_object_names(cls):
            return "associative algebras"

        def _call_(self, module, multiplication):
            r"""The associative algebra on ``(M, m)``: ``(xy)z = x(yz)`` decided on module generators of ``M``."""
            associativity = _decide_on_module_generators(
                module, _associativity(multiplication), 3,
                AtomicProposition("is_associative", multiplication),
            )
            _assert_not_refuted(associativity, "associativity", module)
            return _algebra_on_module(
                module,
                multiplication,
                placement=(self,),
                law_decisions={"associativity": associativity},
            )

        class ParentMethods:
            def is_finitely_presented_as_algebra(self):
                r"""Whether this algebra has a finite associative ``R``-algebra presentation.

                The presentation theory does not require a unit. A finite
                unital presentation gives one here by adjoining ``e`` with
                ``e^2=e`` and ``e*x_i=x_i=x_i*e``, and replacing scalar
                constants ``r`` in its relations by ``r*e``. Associativity
                extends these finitely many unit equations to all words.

                A finite presentation of the retained underlying module
                also suffices: add its finitely many multiplication-table
                relations to the finite linear relations. Finite algebra
                generation alone does not prove finite presentation, and
                missing or undecided presentation data do not refute it.
                """
                ring = self.algebra_base_ring()
                match self:
                    case _ if self in Algebras(ring).Associative().Unital().FinitelyPresentedAsAlgebra():
                        return True
                    case _ if self.unformed_module().is_finitely_presented() is True:
                        return True
                    case _:
                        return AtomicProposition("is_finitely_presented_as_algebra", self)

        class Unital(CategoryWithAxiom):
            r"""Associative unital algebras: the ring objects among algebras."""

            @classmethod
            def _repr_object_names(cls):
                return "algebras"

            def extra_super_categories(self):
                return [
                    Algebras(self.base_ring()).Unital(),
                    OwnedRings(),
                ]

            _MorCategory = UnitalAlgebraMorCategoryConstruction


            @property
            def _SliceCategory(self):
                r"""Supply the algebra realization of the canonical scalar slice."""
                from sage_extensions.categories.algebras.augmented_algebras import (
                    _AugmentedAlgebraSlice,
                )

                return _AugmentedAlgebraSlice

            class SubcategoryMethods:
                def ProjectiveAsAlgebra(self):
                    r"""Return algebras projective relative to underlying surjections."""
                    return self._with_axiom("ProjectiveAsAlgebra")

                def FinitelyGeneratedAsAlgebra(self):
                    r"""Return the refinement whose objects admit finitely many algebra generators."""
                    return self._with_axiom("FinitelyGeneratedAsAlgebra")

                def FinitelyPresentedAsAlgebra(self):
                    r"""Return the refinement whose objects admit a finite algebra presentation."""
                    return self._with_axiom("FinitelyPresentedAsAlgebra")

            class ProjectiveAsAlgebra(CategoryWithAxiom):
                r"""Projective associative unital ``R``-algebras.

                For every surjective associative unital ``R``-algebra map
                ``p: B -> C``, every algebra map ``f: A -> C`` admits an
                algebra lift ``h: A -> B`` with ``p*h = f``. Surjectivity
                concerns the underlying sets; a categorical epimorphism
                alone is insufficient. This is an existence property and
                does not select a lift, generators, or a presentation.

                The inherited ``Projective()`` retains its distinct module
                meaning. For example, ``R[x,y]`` has a free underlying
                module, but need not have this associative algebra lifting
                property. Free tensor algebras do have it, as do free
                symmetric algebras on at most one generator.
                """

                @classmethod
                def _repr_object_names(cls):
                    return "projective associative unital algebras"

                def an_object(self):
                    return self.base_ring().free_module(("x",)).tensor_algebra()

            class FinitelyGeneratedAsAlgebra(CategoryWithAxiom):
                r"""Algebras that admit a finite algebra generating set."""

                @classmethod
                def _repr_object_names(cls):
                    return "finitely generated algebras"

                def an_object(self):
                    return self.base_ring().free_module(("x",)).symmetric_algebra()

                @cached_method
                def resolution_category(self):
                    r"""Return finite generating surjections from projective tensor algebras.

                    A tensor algebra with projective underlying R-module has
                    projective degree-one module, so its maps lift through
                    underlying surjections. Categorical algebra epimorphisms
                    alone need not be surjective and do not express finite
                    generation. The construction requires the stated
                    projective-module placement; it does not choose a basis
                    or decide projectivity of an unclassified realization.
                    """
                    from sage_extensions.categories.abstract_categories.resolutions import (
                        Resolutions,
                    )
                    from sage_extensions.categories.algebras.free_algebras import (
                        TensorAlgebras,
                    )

                    ordinary = Algebras(self.base_ring()).Associative().Unital()
                    projective_tensors = Cat().meet((
                        TensorAlgebras(self.base_ring()),
                        Modules(self.base_ring()).Projective(),
                    ))
                    finite_projective_tensors = Cat().meet(
                        (projective_tensors, ordinary.FinitelyGeneratedAsAlgebra())
                    )
                    return Resolutions(
                        ordinary, projective_tensors, 0, finite_projective_tensors,
                        augmentation_family=Sets().category_packet().Epis(),
                    )

                @cached_method
                def resolution_classifier(self):
                    return self.resolution_category().target_functor()

            class FinitelyPresentedAsAlgebra(CategoryWithAxiom):
                r"""Algebras that admit a finite algebra presentation.

                A property: the presentation exists and none is chosen.
                ``AlgebrasWithChosenFinitePresentation`` is the data category.
                """

                @classmethod
                def _repr_object_names(cls):
                    return "finitely presented algebras"

                def extra_super_categories(self):
                    return [
                        Algebras(self.base_ring())
                        .Associative()
                        .Unital()
                        .FinitelyGeneratedAsAlgebra()
                    ]

                class SubcategoryMethods:
                    r"""Operations of every subcategory of finitely presented algebras, the commutative ones included.

                    ``Commutative().FinitelyPresentedAsAlgebra()`` is a join, which
                    reaches only these methods; the presentation data of a
                    commutative quotient is built there.
                    """

                    @cached_method
                    def resolution_category(self):
                        r"""Return finite projective presentation data in the actual theory.

                        Associative presentations use algebra-projective
                        sources. Commutative presentations use symmetric
                        algebras with projective degree-one modules, witnessed
                        here by their projective underlying modules. Finite
                        levels and an underlying-surjective augmentation are
                        required; the reflexive coequalizer laws belong to the
                        represented presentation data. No presentation is
                        chosen by this property selector.
                        """
                        from sage_extensions.categories.abstract_categories.resolutions import (
                            Resolutions,
                        )
                        from sage_extensions.categories.algebras.free_algebras import (
                            SymmetricAlgebras,
                        )

                        ordinary = Algebras(self.base_ring()).Associative().Unital()
                        commutative = ordinary.Commutative()
                        if self.is_subcategory(commutative):
                            theory = commutative
                            projectives = Cat().meet((
                                SymmetricAlgebras(self.base_ring()),
                                Modules(self.base_ring()).Projective(),
                            ))
                        else:
                            theory = ordinary
                            projectives = ordinary.ProjectiveAsAlgebra()
                        finite_projectives = Cat().meet(
                            (projectives, ordinary.FinitelyGeneratedAsAlgebra())
                        )
                        return Resolutions(
                            theory, projectives, 1, finite_projectives,
                            augmentation_family=Sets().category_packet().Epis(),
                        )

                    @cached_method
                    def resolution_classifier(self):
                        return self.resolution_category().target_functor()

                def an_object(self):
                    r"""``R[x]/(x^2)``, the dual numbers: one generator and one relation."""
                    return _dual_numbers_example(self.base_ring())

            def _call_(self, module, multiplication, unit):
                r"""The associative unital algebra on ``(M, m)`` with unit ``1 in M``, both identities decided on module generators."""
                associativity = _decide_on_module_generators(
                    module, _associativity(multiplication), 3,
                    AtomicProposition("is_associative", multiplication),
                )
                unit_laws = _decide_on_module_generators(
                    module,
                    _two_sided_unit(multiplication, module(unit)),
                    1,
                    AtomicProposition("is_two_sided_unit", multiplication, module(unit)),
                )
                _assert_not_refuted(associativity, "associativity", module)
                _assert_not_refuted(unit_laws, "the two unit equations", module)
                return _algebra_on_module(
                    module,
                    multiplication,
                    placement=(self,),
                    unit=module(unit),
                    law_decisions={
                        "associativity": associativity,
                        "unit": unit_laws,
                    },
                )

            class Commutative(CategoryWithAxiom):
                r"""Commutative associative unital ``R``-algebras.

                A full subcategory: its arrows are the unital algebra maps,
                so it declares no Mor family of its own and inherits that of
                ``Algebras(R).Associative().Unital()``.
                """

                SubcategoryMethods = _CommutativeUnitalAlgebraSubcategoryMethods
                ParentMethods = _CommutativeUnitalAlgebraParentMethods

                @classmethod
                def _repr_object_names(cls):
                    return "commutative algebras"

                class FinitelyPresentedAsAlgebra(CategoryWithAxiom):
                    r"""Commutative ``R``-algebras ``R[x_1, ..., x_n]/(f_1, ..., f_r)``: finitely presented commutative algebras.

                    A property, as for associative unital algebras; its
                    presentation data are those of the commutative theory,
                    read by the inherited ``resolution_category``.
                    """

                    @classmethod
                    def _repr_object_names(cls):
                        return "finitely presented commutative algebras"

                def an_object(self):
                    modules = Modules(self.base_ring())
                    return modules.symmetric_algebra()(modules.an_object())

                def _call_(self, module, multiplication, unit):
                    r"""The commutative associative unital algebra on ``(M, m)`` with unit ``1 in M``, each identity decided on module generators."""
                    decisions = {
                        "associativity": _decide_on_module_generators(
                            module, _associativity(multiplication), 3,
                            AtomicProposition("is_associative", multiplication),
                        ),
                        "commutativity": _decide_on_module_generators(
                            module, _commutativity(multiplication), 2,
                            AtomicProposition("is_commutative", multiplication),
                        ),
                        "unit": _decide_on_module_generators(
                            module,
                            _two_sided_unit(multiplication, module(unit)),
                            1,
                            AtomicProposition("is_two_sided_unit", multiplication, module(unit)),
                        ),
                    }
                    for law, statement in (
                        ("associativity", "associativity"),
                        ("commutativity", "commutativity"),
                        ("unit", "the two unit equations"),
                    ):
                        held = decisions[law]
                        _assert_not_refuted(held, statement, module)
                    return _algebra_on_module(
                        module,
                        multiplication,
                        placement=(self,),
                        unit=module(unit),
                        law_decisions=decisions,
                    )

    class Lie(CategoryWithAxiom):
        r"""Algebras whose bilinear multiplication is a Lie bracket: alternating and satisfying the Jacobi identity.

        Alternation means ``[x,x]=0`` in every characteristic. Together
        with bilinearity it implies ``[x,y]=-[y,x]``; the converse need
        not hold in characteristic two. Jacobi is the cyclic sum
        ``[x,[y,z]] + [y,[z,x]] + [z,[x,y]] = 0``.

        No associativity or unit is implied: the multiplication at this node
        is the bracket itself, so the algebra Mor already has the right
        morphisms, the linear maps preserving it.
        """

        @classmethod
        def _repr_object_names(cls):
            return "Lie algebras"

        def an_object(self):
            r"""``gl_2(R)``: the two-by-two matrix algebra under the commutator."""
            ring = self.base_ring()
            return Algebras(ring).Associative().commutator_lie_algebra()(
                MatrixAlgebras(ring).an_object()
            )

        def _call_(self, module, multiplication):
            r"""Retain ``(M, m)`` under its alternation and Jacobi premises.

            The selected finite generator criteria decide the two laws
            independently. A refutation rejects the bracket; an undecided
            law remains its original owned proposition in
            ``alternation_decision()`` or ``jacobi_decision()``.
            """
            alternation = _decide_on_module_generators(
                module, _alternation(multiplication), 2,
                AtomicProposition("is_alternating", multiplication),
            )
            jacobi = _decide_on_module_generators(
                module, _jacobi_identity(multiplication), 3,
                AtomicProposition("satisfies_jacobi_identity", multiplication),
            )
            _assert_not_refuted(alternation, "alternation", module)
            _assert_not_refuted(jacobi, "the Jacobi identity", module)
            return _algebra_on_module(
                module,
                multiplication,
                placement=(self,),
                law_decisions={"alternation": alternation, "jacobi": jacobi},
            )

        class ParentMethods:
            def bracket(self, left, right):
                r"""Evaluate the defining Lie multiplication on the two elements."""
                return self.product(left, right)

            @cached_method
            def lie_center(self):
                r"""Return the submodule annihilated by every adjoint action.

                This is ``{z : [z,x] = 0 for all x}`` (Mathlib
                ``Algebra.Lie.Abelian``, ``LieAlgebra.center``). Alternation
                makes left and right annihilation equivalent in every
                characteristic. Bilinearity permits the equalizer equations
                to be checked on a finite chosen module generating family.
                The result is the underlying ``R``-submodule with its exact
                inclusion; the existing module kernels retain their own
                coefficient and presentation computation frontiers.
                The inherited ``center`` instead uses the bracket as a magma
                multiplication and includes its nucleus equations.
                """
                assert (
                    self.has_selected_module_resolution()
                    and self.module_generating_set().cardinality().is_finite()
                ), (
                    f"the Lie centre of {self} needs a represented kernel of the adjoint "
                    "action; the available equalizer algorithm needs finitely many "
                    "chosen module generators"
                )
                endomorphisms = self.module_category().Mor(self, self)
                modules = Modules(self.algebra_base_ring())
                zero = endomorphisms.zero()

                def adjoint_kernel(label):
                    element = self.module_generator(label)
                    adjoint = endomorphisms._from_constructed_element_map(lambda other: other * element)
                    return modules.equalizer(adjoint, zero)

                identity = endomorphisms.identity()
                return reduce(
                    lambda central, label: central.intersection(adjoint_kernel(label)),
                    self.module_generating_set(),
                    modules.equalizer(identity, identity),
                )

            def lie_center_inclusion(self):
                r"""Return the selected module inclusion ``lie_center() -> self``."""
                return self.lie_center().inclusion()

    class Unital(CategoryWithAxiom):
        r"""Algebras with a two-sided unit, without associativity.

        The unit is unique when it exists, so this is a property.  Its
        witness, the unit ``1`` of ``M``, is decided against the
        multiplication by the entry that states it, or supplied by the
        theorem of the construction that builds the algebra, and is retained
        by the construction.
        """

        _MorCategory = UnitalAlgebraMorCategoryConstruction

        @classmethod
        def _repr_object_names(cls):
            return "unital algebras"

        def _call_(self, module, multiplication, unit):
            r"""Retain ``(M, m, u)`` under the two equations ``m(u,x)=x=m(x,u)``.

            Each equation is linear in ``x``, so a finite selected spanning
            family suffices; neither freeness nor associativity is needed.
            A refuted equation is rejected and an undecided unit hypothesis
            remains the original owned proposition.
            """
            unit_laws = _decide_on_module_generators(
                module,
                _two_sided_unit(multiplication, module(unit)),
                1,
                AtomicProposition("is_two_sided_unit", multiplication, module(unit)),
            )
            _assert_not_refuted(unit_laws, "the two unit equations", module)
            return _algebra_on_module(
                module,
                multiplication,
                placement=(self,),
                unit=module(unit),
                law_decisions={"unit": unit_laws},
            )

        class ParentMethods:
            def __init__(self, unit=None, *, _engine_unit=None, **rest) -> None:
                match _engine_unit:
                    case None:
                        assert unit is not None, (
                            "a unital algebra needs its unit element, but none was given"
                        )
                        self._retain_unit(unit)
                        super().__init__(**rest)
                    case unit_factory:
                        assert unit is None and callable(unit_factory)
                        super().__init__(_native_unit_factory=unit_factory, **rest)

            def _retain_unit(self, unit):
                r"""The one unit datum, including self-based coefficient construction."""
                previous = vars(self).get("_preamble_algebra_unit")
                assert previous is None or previous is unit or (previous == unit) is True, (
                    f"the unit of an algebra cannot be replaced: it already has unit {previous}, not {unit}"
                )
                self._preamble_algebra_unit = unit

            @cached_method
            def one(self):
                r"""Supply the inherited unital-magma unit from the retained module datum."""
                unit = vars(self).get("_preamble_algebra_unit")
                match unit:
                    case _ if unit is not None:
                        return self(unit)
                    case _:
                        from sage_extensions.categories.group.additive_mors import (
                            AdditiveEndomorphismRings,
                        )

                        match self:
                            case _ if self in AdditiveEndomorphismRings(self.base_ring()):
                                return self.identity()
                            case _:
                                assert False, (
                                    f"{self} is a unital algebra but its construction supplied neither a "
                                    "unit element nor a represented endomorphism identity"
                                )

            @cached_method
            def unit_morphism(self):
                r"""The module arrow ``eta: U_R(R) -> A``, ``r |-> rho(r)(1)``.

                Bilinearity and the two admitted unit laws give
                ``m(eta(r),a) = rho(r)(a) = m(a,eta(r))``. These are the
                left and right module unit triangles; associativity is not
                a hypothesis of this map or these equations.
                """
                return _unit_morphism_from_element(self, self.one(), self.algebra_base_ring())

            def _element_constructor_(self, value):
                r"""Read a scalar ``r`` of the coefficient ring ``R`` as ``eta(r) = r * 1``.

                In a unital ``R``-algebra ``A`` a scalar names the image of
                ``r`` under the structure map, ``unit_morphism``
                ``r |-> rho(r)(1)``: in ``C(k, X, RR)`` the real ``2`` is the
                constant map with value ``2``.  An element of a ring that is
                contained in ``R`` and is not an ``R``-module (the integers
                inside ``RR``) is that element of ``R``.  Everything else,
                including the module ``A`` is built on, is read by the
                realization below; so is a scalar when ``A`` is built on
                ``R`` itself, where ``r`` already is the element ``r * 1``.
                """
                ring = self.algebra_base_ring()
                source = element_parent(value)
                match source:
                    case _ if self is _scalar_module(ring):
                        # U_R(R) is the domain of its own unit map r |-> r * 1.
                        return super()._element_constructor_(value)
                    case _ if source is ring and self.unformed_module() is not ring:
                        return self.unit_morphism()(value)
                    case _ if source not in Modules(ring) and source in OwnedRings() and value in ring:
                        return self.unit_morphism()(ring(value))
                    case _:
                        return super()._element_constructor_(value)

            def _algebra_mor_class(self):
                r"""Choose generator-image morphisms exactly when selected algebra resolution data exists."""
                match self.is_framed_algebra():
                    case True:
                        return AlgebraMor
                    case False:
                        return UnitalMultiplicativeAlgebraMor


    class Commutative(CategoryWithAxiom):
        r"""``R``-modules with an ``R``-bilinear commutative product.

        For the defining map ``m : M tensor_R M -> M`` and the tensor
        transposition ``tau``, the additional law is ``m = m . tau``.
        Associativity and a unit are separate hypotheses. Morphisms are
        the inherited ``R``-linear maps preserving ``m``; this object law
        adds no condition to the root algebra morphisms.
        """

        @classmethod
        def _repr_object_names(cls):
            return "commutative algebras"

        def an_object(self):
            r"""The symmetric algebra on the selected rank-one module over this base."""
            return Algebras(self.base_ring()).Associative().Unital().Commutative().an_object()

        def _call_(self, module, multiplication):
            r"""Retain ``(M, m)`` subject to ``m(x, y) = m(y, x)``.

            Bilinearity makes a selected finite spanning family sufficient
            to decide this law; no basis or finite-dimensional hypothesis
            is needed. A literal refutation is rejected. An undecided law
            remains the original owned premise, available through the
            resulting algebra's ``commutativity_decision()`` accessor.
            """
            commutativity = _decide_on_module_generators(
                module, _commutativity(multiplication), 2,
                AtomicProposition("is_commutative", multiplication),
            )
            _assert_not_refuted(commutativity, "commutativity", module)
            return _algebra_on_module(
                module,
                multiplication,
                placement=(self,),
                law_decisions={"commutativity": commutativity},
            )

# ``Lie`` is an owned algebra axiom not known to Sage's global axiom registry.
# Register the nested refinement explicitly so ``Algebras(R).Lie()`` is a
# category-with-axiom rather than an inference through Sage's built-in names.
Algebras.__dict__["Lie"]._base_category_class_and_axiom = (Algebras, "Lie")

FinitelyPresentedAlgebras = Algebras.Associative.Unital.FinitelyPresentedAsAlgebra


# ---------------------------------------------------------------------------
# The construction behind every entry.
# ---------------------------------------------------------------------------


def _algebra_on_module(
    module,
    multiplication,
    *,
    placement,
    categories=(),
    unit=None,
    construction_data=None,
    law_decisions=None,
):
    r"""Build the algebra on the data of ``M`` with multiplication ``m``: the realization of ``Algebras(R)(M, m)``.

    Declared owner: the ``Algebras(R)`` entry and its axiom entries, and the
    constructions that compute ``(M, m)`` -- the centre, quotients, the
    commutator Lie algebra, group algebras, graded algebras -- call this and
    nothing else (``OWN-13``).

    The algebra's module structure is the defining datum of ``M``, read from
    the most specific module construction ``M`` carries: a chosen finite
    presentation (a finitely generated framed free module is one), a framed
    free module on its labels, or otherwise the datum of every ``R``-module,
    its additive group with the scalar action ``rho_M``.  ``M`` is retained
    as ``unformed_module()`` and ``m`` as ``multiplication()``; elements pass
    to and from ``M`` by coercion at the module level of that construction,
    and no map identifying the two is built.

    ``placement`` lists the categories the caller established for ``(M, m)``:
    an identity an axiom entry decided, or the theorem of a construction,
    cited where it is called.  ``unit``, an element of ``M``, is required
    exactly when the placement is unital.  ``categories`` lists further
    categories, not themselves categories of algebras, whose levels add their
    own data to this algebra: a slice or coslice over a category of rings.
    ``construction_data`` carries the datum of a data category in
    ``placement`` or ``categories``.  ``law_decisions`` carries the exact
    premises supporting axiom placements: ``True``, or the proposition of a
    law stated as a hypothesis.
    """
    ring = module.base_ring()
    tensor = multiplication.domain()
    assert tensor in TensorProductModules(ring) and tensor.tensor_factors().index_set().cardinality() == 2 and all(factor is module for factor in tensor.tensor_factors()), (
        f"the multiplication of an algebra on {module} must be a linear map {module} (x) {module} -> "
        f"{module}, but {multiplication} starts at {tensor}"
    )
    assert all(category.is_subcategory(Algebras(ring)) for category in placement), (
        f"an algebra on the {ring}-module {module} must be placed in categories of algebras over "
        f"{ring}, but got {placement}"
    )
    assert multiplication.codomain() is module, (
        f"the multiplication of an algebra on {module} must end at {module}, but {multiplication} "
        f"ends at {multiplication.codomain()}"
    )
    multiplication = module.module_category().Mor(tensor, module)(multiplication)
    categories = (Algebras(ring), *placement, *categories)
    selected_category = Cat().meet(categories)
    law_decisions = dict(law_decisions or {})
    for decision in law_decisions.values():
        assert decision is True or decision in Propositions, (
            f"an algebra law is recorded only as True or as the proposition stating it, but got {decision}"
        )
    for required_category, required_laws in (
        (Algebras(ring).Associative(), ("associativity",)),
        (Algebras(ring).Unital(), ("unit",)),
        (Algebras(ring).Commutative(), ("commutativity",)),
        (Algebras(ring).Lie(), ("alternation", "jacobi")),
    ):
        match selected_category.is_subcategory(required_category):
            case True:
                missing = tuple(law for law in required_laws if law not in law_decisions)
                assert not missing, (
                    f"placing an algebra on {module} in {selected_category} needs a decision for each of the "
                    f"laws {missing}, but none was recorded"
                )
            case False:
                pass
    data = {
        "unformed_module": module,
        "multiplication": multiplication,
        "algebra_law_decisions": law_decisions,
        **(construction_data or {}),
    }
    match selected_category:
        case category if category.is_subcategory(Algebras(ring).Unital()):
            assert unit is not None, (
                f"an algebra on {module} placed in {selected_category} is unital, so it needs its unit "
                "element, but none was given"
            )
            data["unit"] = module(unit)
        case _:
            assert unit is None, (
                f"a unit {unit} was given for an algebra on {module}, but {selected_category} is not a "
                "category of unital algebras"
            )
    native = Modules.ParentMethods._native_module_presentation(module)
    if native is not None and construction_data is None and multiplication is native.multiplication():
        # This is the original ring product on its constructed module, not an
        # alternative multiplication admitted merely because M is a ring.
        Algebras.ParentMethods._retain_algebra_datum(module, module, multiplication)
        Algebras.ParentMethods._retain_algebra_law_decisions(
            module, law_decisions
        )
        if unit is not None:
            Algebras.Unital.ParentMethods._retain_unit(module, module(unit))
        assert module in selected_category, (
            "a native algebra realization must receive its algebra placement "
            "from the constructing parent"
        )
        return module
    return module._module_with_structure(categories, data)


def _center_algebra(algebra, submodule):
    r"""Build the induced algebra on a submodule known to be the magma centre.

    The commutant intersected with the nucleus is a commutative associative
    subalgebra, even when the ambient algebra is not associative, and it
    contains any two-sided unit. Its multiplication is the ambient product
    read back along the injective inclusion, so ``lift`` recovers each
    product. Associativity here follows from the centre's nucleus equations.
    """
    ring = algebra.algebra_base_ring()
    inclusion = submodule.inclusion()
    multiplication = BilinearMap(
        submodule,
        submodule,
        submodule,
        lambda left, right: inclusion.lift(
            inclusion(submodule.module_generator(left)) * inclusion(submodule.module_generator(right))
        ),
    )
    algebras = Algebras(ring)
    law_decisions = {
        "associativity": True,
        "commutativity": True,
    }
    match algebra:
        case _ if algebra in algebras.Unital():
            law_decisions["unit"] = algebra.unit_laws_decision()
            return _algebra_on_module(
                submodule,
                multiplication,
                placement=(algebras.Associative().Unital().Commutative(),),
                unit=inclusion.lift(algebra.one()),
                law_decisions=law_decisions,
            )
        case _:
            return _algebra_on_module(
                submodule,
                multiplication,
                placement=(algebras.Associative(), algebras.Commutative()),
                law_decisions=law_decisions,
            )



class MatrixAlgebras(OwnedCategoryOverBaseRing):
    r"""Finite matrix endomorphism Mor objects with their canonical algebra structure."""

    def an_object(self):
        r"""``End_R(Free_R([2]))``, the two-by-two matrix algebra."""
        from sage_extensions.categories.sets.set_categories import (
            finite_ordinal_set,
        )

        ring = self.base_ring()
        plane = Sets().free_module(ring)(finite_ordinal_set(2))
        return Modules(ring).Mor(plane, plane)

    def _repr_object_names(self):
        return f"matrix algebras over {self.base_ring()}"

    def super_categories(self):
        if self.base_ring() not in OwnedRings().Commutative():
            raise TypeError(
                f"End_R(F) is an R-algebra only for commutative R, but {self.base_ring()} is not known to be "
                "commutative"
            )
        return [
            MatrixEndomorphismSpaces(self.base_ring()),
            Algebras(self.base_ring()).Associative().Unital(),
        ]

    # M_n(R) is unital, so a morphism of matrix algebras preserves the unit.
    # The associative Mor that arrives from the endomorphism spaces below does
    # not ask that, and this says which of the two the category means.
    _MorCategory = UnitalAlgebraMorCategoryConstruction

    class ParentMethods:
        def __init_extra__(self) -> None:
            r"""Retain the canonical matrix-unit algebra framing at refinement."""
            owner = Algebras(self.base_ring()).Associative().Unital()
            if self.has_selected_resolution(owner):
                return
            labels = self.module_generating_set()
            generator_morphism = Sets().Mor(labels, self)(
                lambda label: self.matrix_unit(label[0], label[1])
            )
            base_ring = self.base_ring()
            _fix_selected_algebra_resolution(
                self,
                owner,
                lambda: base_ring.free_module(labels).tensor_algebra(),
                labels,
                generator_morphism,
                lambda source: source.Mor(self)(generator_morphism),
            )

def _require_matrix_algebra(mor):
    r"""Return a square matrix Mor after requiring constructor-time algebra placement."""

    ring = mor.base_ring()
    if mor not in MatrixEndomorphismSpaces(ring):
        return mor
    if ring not in OwnedRings().Commutative():
        return mor
    if mor not in MatrixAlgebras(ring):
        raise TypeError(
            f"End({mor.domain()}) over the commutative ring {ring} must be constructed as a matrix algebra, "
            f"but {mor} is not in {MatrixAlgebras(ring)}"
        )
    return mor


def _dual_numbers_example(base_ring):
    """The algebra R[x]/(x²) from its one-generator presentation."""
    presentation = base_ring.free_module(("x",)).symmetric_algebra()
    return presentation.quotient_by_relations(("x^2",))


class AlgebrasWithChosenFinitePresentation(OwnedCategoryOverBaseRing):
    r"""Associative unital algebras carrying one selected finite presentation.

    The selected presentation may use a free associative algebra or a
    polynomial algebra. Commutativity belongs to the actual construction,
    rather than to the presence of finite generators and relations.
    """

    def an_object(self):
        r"""``R[x]/(x^2)``, the dual numbers: one generator and one relation."""
        return _dual_numbers_example(self.base_ring())

    def _repr_object_names(self):
        return f"algebras with a chosen finite presentation over {self.base_ring()}"

    def super_categories(self):
        return [
            Algebras(self.base_ring()).Associative().Unital().FinitelyPresentedAsAlgebra(),
        ]

    def _call_(
        self,
        presentation_ring,
        relations,
        *,
        extra_categories=(),
        extra_construction_data=None,
        generating_module=None,
    ):
        r"""Construct an algebra from its selected finite associative presentation.

        Retain the exact tensor or polynomial source. The selected quotient
        computation states its own coefficient and relation hypotheses;
        finite presentation does not impose commutativity.
        """
        if presentation_ring.base_ring() is not self.base_ring():
            raise ValueError(
                f"an algebra over {self.base_ring()} given by generators and relations needs a presentation algebra "
                f"over {self.base_ring()}, but {presentation_ring} is over {presentation_ring.base_ring()}"
            )
        if presentation_ring not in Algebras(self.base_ring()).Associative().Unital():
            raise TypeError(
                f"a finite associative unital presentation over {self.base_ring()} "
                f"needs an associative unital presentation algebra, but got {presentation_ring}"
            )
        from sage_extensions.categories.algebras.free_algebras import (
            _finitely_presented_algebra_from_data,
        )

        return _finitely_presented_algebra_from_data(
            presentation_ring,
            relations,
            _extra_categories=tuple(extra_categories),
            _extra_construction_data=extra_construction_data,
            _generating_module=generating_module,
            _constructing_category=self,
        )

    class ParentMethods:
        def _algebra_mor_class(self):
            return PresentedAlgebraMor

        def selected_algebra_presentation(self):
            r"""Return the one chosen truncation-one algebra resolution."""
            selected = self.selected_algebra_resolution()
            match selected.truncation():
                case 1:
                    return selected
                case _:
                    raise TypeError(
                        f"{self} has no chosen finite algebra presentation: its selected resolution "
                        f"is truncated in degree {selected.truncation()}"
                    )

        def presentation_ring(self):
            return self.selected_algebra_presentation().level(0)

        def generating_module(self):
            r"""Return the exact module on which the selected free algebra is built."""
            generating = self.presentation_ring().generating_module()
            module_labels = generating.module_generating_set()
            algebra_labels = self.algebra_generating_set()
            assert module_labels is algebra_labels, (
                f"the generators {generating.module_generating_set()} of the presentation algebra of {self} "
                f"must use the literal index set of its chosen algebra generators {self.algebra_generating_set()}"
            )
            return generating

        def _has_selected_exact_coefficient_presentation(self) -> bool:
            return True

        def _exact_coefficient_presentation_ring(self):
            return self.presentation_ring()

        def _exact_coefficient_presentation_relations(self):
            return self.relations()

        def _lift_coefficient_to_presentation(self, value):
            return self.lift_to_presentation(self(value))

        def _descend_coefficient_from_presentation(self, value):
            return self(value)

        def relations(self):
            return self.selected_algebra_presentation().relations()

        @cached_method
        def presentation_ideal(self):
            r"""Return the owned two-sided ideal of the selected presentation.

            A commutative presentation uses its existing ideal constructor.
            In a tensor presentation the ideal is the kernel submodule of
            the actual quotient map. Its inclusion retains that exact
            ambient algebra; finite algebra relations do not assert a
            finite generating family over the coefficient ring.
            """
            presentation = self.presentation_ring()
            if presentation in OwnedRings().Commutative():
                return presentation.ideal(*self.relations())

            from sage_extensions.categories.modules.affine_fibres import (
                ModuleInverseImages,
            )

            quotient = Algebras(self.base_ring()).underlying_module()(
                self.algebra_presentation_morphism()
            )
            return ModuleInverseImages(self.base_ring())(
                quotient, self.zero_subobject().inclusion()
            )

        def presentation(self):
            labels = finite_ordered_set(("presentation_ring", "relations"))
            values = {
                "presentation_ring": self.presentation_ring(),
                "relations": self.relations(),
            }
            return indexed_family(
                labels,
                values.__getitem__,
                name="Selected finite algebra presentation data",
            )

        def _represented_structure_morphism_kernel_is_zero(self) -> bool:
            r"""Decide injectivity from the selected scalar-map construction.

            In a tensor or symmetric algebra, degree-zero augmentation is a
            left inverse of the scalar map, including when the generating
            module has torsion.  For a polynomial quotient the kernel is
            ``I cap R``.  The latter computation requires its actual native
            polynomial quotient, with the original relative variables or
            their images under the retained coefficient-preserving cover map.
            """
            from sage.rings.polynomial.multi_polynomial_ideal import MPolynomialIdeal
            from sage.rings.polynomial.multi_polynomial_ring_base import MPolynomialRing_base
            from sage.rings.polynomial.polynomial_ring import PolynomialRing_generic
            from sage.rings.quotient_ring import QuotientRing_generic

            from sage_extensions.categories.algebras.free_algebras import (
                SymmetricAlgebras,
                TensorAlgebras,
            )

            base = self.base_ring()
            presentation = self.presentation_ring()
            match self:
                case _ if self in TensorAlgebras(base) or self in SymmetricAlgebras(base):
                    return True
                case _ if presentation in SymmetricAlgebras(base):
                    pass
                case _:
                    raise AssertionError(
                        f"injectivity of the scalar map {base} -> {self} needs a selected "
                        "associative-ideal intersection computation; polynomial elimination "
                        f"does not apply to its presentation {presentation}"
                    )

            presentation_engine = _engine_ring(presentation)
            algebra_engine = _engine_ring(self)
            assert isinstance(presentation_engine, (PolynomialRing_generic, MPolynomialRing_base)), (
                f"injectivity of {base} -> {self} needs a native polynomial realization of "
                f"the selected presentation {presentation}"
            )
            assert isinstance(algebra_engine, QuotientRing_generic), (
                f"injectivity of {base} -> {self} needs the selected polynomial-quotient "
                "computation or an injectivity supplier for its retained algebra realization"
            )
            cover = algebra_engine.cover_ring()
            defining_ideal = algebra_engine.defining_ideal()
            assert isinstance(cover, MPolynomialRing_base) and isinstance(defining_ideal, MPolynomialIdeal), (
                f"injectivity of {base} -> {self} needs an ideal-intersection computation "
                f"for its cover {cover}; the available elimination supplier uses a "
                "multivariate polynomial ideal"
            )

            if cover is presentation_engine:
                algebra_variables = tuple(presentation_engine.gens())
            else:
                comparison = self._selected_algebra_presentation_backend.cover_map()
                assert comparison is not None, (
                    f"injectivity of {base} -> {self} needs the retained comparison from "
                    f"{presentation} to its computation cover {cover}"
                )
                assert comparison.domain() is presentation_engine and comparison.codomain() is cover, (
                    f"cannot decide whether {base} -> {self} is injective: its retained "
                    "presentation comparison has different computation endpoints"
                )
                algebra_variables = tuple(comparison(generator) for generator in presentation_engine.gens())

            scalar_kernel = defining_ideal.elimination_ideal(algebra_variables)
            return scalar_kernel.is_zero()

        def _torsion_freeness_decision(self):
            r"""Use the retained module or integral-algebra torsion computation.

            Over a PID, ``T(M)`` and ``Sym(M)`` for a finitely presented module
            are torsion-free exactly when ``M`` is: degree one retains ``M``,
            and a finite torsion-free PID module is free.  The input here is
            the actual construction module, not its free presentation source.

            If ``R`` and ``A`` are domains, torsion-freeness of ``A`` is instead
            equivalent to injectivity of ``R -> A``.  An undecided or refuted
            domain hypothesis proves neither answer, so the general module
            predicate remains undecided when neither construction applies.
            """
            from sage_extensions.categories.algebras.free_algebras import (
                SymmetricAlgebras,
                TensorAlgebras,
            )

            base = self.base_ring()
            if base.is_field() is True:
                return True
            assert base in PrincipalIdealDomains(), (
                f"torsion-freeness of {self} is decided here only over a principal ideal domain, but "
                f"{base} is not known to be one"
            )
            match self:
                case _ if self in FramedFreeModules(base):
                    return True
                case _ if self in TensorAlgebras(base):
                    generating = TensorAlgebras.ParentMethods.generating_module(self)
                case _ if self in SymmetricAlgebras(base):
                    generating = SymmetricAlgebras.ParentMethods.generating_module(self)
                case _ if self.is_integral_domain() is True:
                    return self._represented_structure_morphism_kernel_is_zero()
                case _:
                    return Modules.ParentMethods._torsion_freeness_decision(self)

            assert generating in ModulesWithChosenFinitePresentation(base), (
                f"torsion-freeness of {self} needs a computation for its actual generating "
                f"module {generating}; the selected PID tensor/symmetric supplier uses "
                "a chosen finite module presentation"
            )
            return generating.is_torsion_free()

        def _represented_primitive_hypersurface_relative_dimension(self) -> int:
            r"""Return the pure dimension of every nonempty polynomial fibre.

            Primitivity makes the equation nonzero over every residue field.
            A nonconstant specialization cuts out a hypersurface of dimension
            ``n - 1``; a nonzero constant specialization has empty fibre.
            Thus ``n - 1`` is the fibre dimension at every source point, as
            needed by the relative differential-rank criterion.  No assertion
            of nonempty fibres, monicity, or homogeneity is made.
            """
            from sage.rings.polynomial.multi_polynomial_ring_base import MPolynomialRing_base
            from sage.rings.polynomial.polynomial_ring import PolynomialRing_generic

            from sage_extensions.categories.algebras.free_algebras import SymmetricAlgebras

            presentation = self.presentation_ring()
            presentation_engine = _engine_ring(presentation)
            assert presentation in SymmetricAlgebras(self.base_ring()) and isinstance(
                presentation_engine, (PolynomialRing_generic, MPolynomialRing_base)
            ), (
                f"the relative dimension of {self} needs a polynomial hypersurface "
                f"presentation; its selected presentation {presentation} needs a different "
                "dimension computation"
            )

            relations = self.relations()
            assert relations.cardinality().is_finite() and int(relations.cardinality()) == 1, (
                f"the relative dimension of {self} is computed here only for one defining equation, but it has "
                f"{relations.cardinality()}"
            )
            labels = presentation.algebra_generating_set()
            assert labels.cardinality().is_finite(), (
                f"the relative dimension of {self} needs finitely many variables, but it has {labels.cardinality()}"
            )
            variable_count = int(labels.cardinality())
            assert variable_count > 0, (
                f"the relative dimension of the hypersurface {self} needs at least one variable, but it has none"
            )

            relation_index = next(iter(relations.index_set()))
            relation = relations.value(relation_index)
            backend_relation = presentation_engine(_engine_element(presentation, relation))
            coefficient_ideal = self.base_ring().ideal(*tuple(_owned_engine_element(self.base_ring(), coefficient) for coefficient in backend_relation.coefficients()))
            assert (coefficient_ideal == self.base_ring().ideal(self.base_ring().one())) is True, (
                f"the relative dimension of the hypersurface {self} is computed here only when its equation "
                f"{relation} is primitive, i.e. its coefficients generate the unit ideal of {self.base_ring()}"
            )
            return variable_count - 1

        def algebra_presentation_morphism(self):
            return self.selected_algebra_presentation().augmentation()

        def lift_to_presentation(self, element):
            return self._selected_algebra_presentation_backend.lift(element)

        def presentation_normal_form_terms(self, element):
            r"""Return the coefficients of the selected presentation representative.

            These are the existing finitely supported function on the
            presentation algebra's chosen module basis. A supported label
            ``i`` denotes ``presentation_ring().module_generator(i)``;
            evaluating the function at ``i`` gives its owned coefficient.
            The same coordinate construction handles polynomial monomials
            and ordered tensor words, after the selected quotient lift.
            """
            presentation = self.presentation_ring()
            assert presentation in FramedFreeModules(self.base_ring()), (
                f"computing normal-form coefficients for {self} needs a selected "
                f"module basis of its retained presentation algebra {presentation}"
            )
            representative = self.lift_to_presentation(self(element))
            return representative.to_vector()

        def _commutative_algebra_coproduct(self, left, right):
            r"""Evaluate the selected binary-coproduct construction on this object.

            Protected algebra-construction contract under OWN-05--07. The sole
            external caller role is ``Algebras._categorical_coproduct`` after
            it has selected one of the two operands as the construction owner.
            The installed callable returns an owned algebra and its owned
            injections; no engine algebra or presentation storage crosses this
            method.
            """
            operation = self._preamble_commutative_algebra_coproduct_backend
            assert operation is not None, (
                f"no construction of the coproduct {left} (x) {right} of commutative algebras is available for {self}"
            )
            return operation(left, right)

        def _commutative_algebra_pushout(self, left_map, right_map):
            r"""Evaluate the selected commutative-algebra pushout on this object.

            Protected algebra-construction contract under OWN-05--07. The sole
            external caller role is ``Algebras._categorical_pushout`` once an
            operand has supplied the represented construction. The result and
            its structure maps are owned algebraic objects; private
            presentation data remain inside the construction implementation.
            """
            operation = self._preamble_commutative_algebra_pushout_backend
            assert operation is not None, (
                f"no construction of the pushout of {left_map} and {right_map} in commutative algebras is "
                f"available for {self}"
            )
            return operation(left_map, right_map)


class CommutativeAlgebraCoproducts(OwnedCategoryOverBaseRing):
    r"""Commutative ``R``-algebras equipped as selected binary coproducts."""

    def an_object(self):
        r"""``R[x] \otimes_R R[y]``, the coproduct of two polynomial algebras."""

        ring = self.base_ring()
        return Algebras(ring).Associative().Unital().Commutative().coproduct((ring.free_module(("x",)).symmetric_algebra(), ring.free_module(("y",)).symmetric_algebra()))

    def super_categories(self):
        return [Algebras(self.base_ring()).Associative().Unital().Commutative()]

    class ParentMethods:
        def coproduct_factors(self):
            r"""Return the family of factors, indexed by the product's own index set."""

            return _finite_factor_family(self._preamble_coproduct_factors, name="Coproduct factors")

        tensor_factors = coproduct_factors

        @cached_method
        def coproduct_injection(self, index):
            # Indices are the actual two-point set. Converting to int first
            # would silently turn a nonintegral index such as 1/2 into 0,
            # assigning a nonexistent coproduct leg to the left factor.
            if index not in (0, 1) or index != int(index):
                raise IndexError(
                    f"a coproduct of two algebras has injections 0 and 1, but got index {index}"
                )
            index = int(index)
            factor = self.coproduct_factors()[index]
            tag = "left" if index == 0 else "right"
            return factor.Mor(self)({label: self.algebra_generator((tag, label)) for label in factor.algebra_generating_set()})

        def coproduct_injections(self):
            factors = self.coproduct_factors()
            return indexed_family(
                factors.index_set(),
                self.coproduct_injection,
                name="Coproduct injections",
            )

        def left_coproduct_map(self):
            return self.coproduct_injection(0)

        def right_coproduct_map(self):
            return self.coproduct_injection(1)

        def from_cocone(self, left_map, right_map):
            left, right = self.coproduct_factors()
            if left_map.domain() is not left or right_map.domain() is not right:
                raise ValueError(
                    f"the maps out of the coproduct {self} must start at its factors {left} and {right}, but they "
                    f"start at {left_map.domain()} and {right_map.domain()}"
                )
            if left_map.codomain() is not right_map.codomain():
                raise ValueError(
                    f"the maps out of the coproduct {self} must end at one algebra, but they end at "
                    f"{left_map.codomain()} and {right_map.codomain()}"
                )
            target = left_map.codomain()
            category = Algebras(self.base_ring()).Associative().Unital().Commutative()
            if target not in category or (
                left_map not in category.Mor(left, target)
                or right_map not in category.Mor(right, target)
            ):
                raise TypeError(
                    f"the cocone on {self} needs two actual commutative-algebra morphisms "
                    f"over {self.base_ring()}"
                )
            images = {
                **{("left", label): left_map(left.algebra_generator(label)) for label in left.algebra_generating_set()},
                **{("right", label): right_map(right.algebra_generator(label)) for label in right.algebra_generating_set()},
            }
            induced = self.Mor(target)(images)
            # A coproduct is specified by its two injections, not merely
            # by the ambient polynomial presentation. Check the defining
            # triangles in the actual Mor graph on the chosen generators;
            # these determine algebra morphisms out of either factor.
            for injection, factor_map, factor in (
                (self.left_coproduct_map(), left_map, left),
                (self.right_coproduct_map(), right_map, right),
            ):
                if any(
                    induced(injection(factor.algebra_generator(label)))
                    != factor_map(factor.algebra_generator(label))
                    for label in factor.algebra_generating_set()
                ):
                    raise ValueError("the proposed coproduct morphism does not factor the supplied cocone")
            return induced

        tensor_map = from_cocone


class CommutativeAlgebraPushouts(OwnedCategoryOverBaseRing):
    r"""Commutative ``R``-algebras equipped as selected pushouts of one span."""

    def an_object(self):
        r"""``R[x] \otimes_{R[t]} R[y]`` for ``t`` sent to ``x`` and to ``y``.

        The pushout of the span whose legs are the two isomorphisms
        \(R[t]\to R[x]\) and \(R[t]\to R[y]\).
        """

        ring = self.base_ring()
        common = ring.free_module(("t",)).symmetric_algebra()
        left = ring.free_module(("x",)).symmetric_algebra()
        right = ring.free_module(("y",)).symmetric_algebra()
        return Algebras(ring).Associative().Unital().Commutative().pushout(
            common.Mor(left)({"t": left.algebra_generator("x")}),
            common.Mor(right)({"t": right.algebra_generator("y")}),
        )

    def super_categories(self):
        return [Algebras(self.base_ring()).Associative().Unital().Commutative()]

    class ParentMethods:
        def pushout_span(self):
            return self._preamble_pushout_span

        @cached_method
        def pushout_maps(self):
            coproduct = self._preamble_pushout_coproduct
            quotient_map = coproduct.Mor(self)({label: self.algebra_generator(label) for label in coproduct.algebra_generating_set()})
            maps = coproduct.coproduct_injections().map(
                lambda injection: quotient_map * injection,
                name="Pushout structure maps",
            )
            source_map, target_map = self.pushout_span()
            common = source_map.domain()
            for label in common.algebra_generating_set():
                element = common.algebra_generator(label)
                if maps[0](source_map(element)) != maps[1](target_map(element)):
                    raise ValueError(
                        "the selected pushout structure maps do not agree on the common algebra"
                    )
            return maps

        def left_pushout_map(self):
            return self.pushout_maps()[0]

        def right_pushout_map(self):
            return self.pushout_maps()[1]

        def from_pushout_cocone(self, left_map, right_map):
            source_map, target_map = self.pushout_span()
            left_factor = source_map.codomain()
            right_factor = target_map.codomain()
            if left_map.domain() is not left_factor or right_map.domain() is not right_factor:
                raise ValueError(
                    f"the maps out of the pushout {self} must start at {left_factor} and {right_factor}, but they "
                    f"start at {left_map.domain()} and {right_map.domain()}"
                )
            if left_map.codomain() is not right_map.codomain():
                raise ValueError(
                    f"the maps out of the pushout {self} must end at one algebra, but they end at "
                    f"{left_map.codomain()} and {right_map.codomain()}"
                )
            target = left_map.codomain()
            category = Algebras(self.base_ring()).Associative().Unital().Commutative()
            if target not in category or (
                left_map not in category.Mor(left_factor, target)
                or right_map not in category.Mor(right_factor, target)
            ):
                raise TypeError(
                    f"the pushout cocone on {self} needs two actual commutative-algebra "
                    f"morphisms over {self.base_ring()}"
                )
            common_source = source_map.domain()
            for label in common_source.algebra_generating_set():
                element = common_source.algebra_generator(label)
                if (left_map(source_map(element)) == right_map(target_map(element))) is False:
                    raise ValueError(
                        f"the maps {left_map} and {right_map} do not agree on the common algebra "
                        f"{common_source}: they differ on its generator {element}"
                    )
            # The selected presentation includes these compatibility
            # relations. Its actual algebra-morphism constructor retains
            # undecided relation images rather than declaring them proved.
            images = {
                **{("left", label): left_map(left_factor.algebra_generator(label)) for label in left_factor.algebra_generating_set()},
                **{("right", label): right_map(right_factor.algebra_generator(label)) for label in right_factor.algebra_generating_set()},
            }
            induced = self.Mor(target)(images)
            # The quotient presentation alone does not establish that the
            # admitted arrow has the required composites with the selected
            # pushout legs. Check the defining triangles at the generators.
            for injection, factor_map, factor in (
                (self.left_pushout_map(), left_map, left_factor),
                (self.right_pushout_map(), right_map, right_factor),
            ):
                if any(
                    induced(injection(factor.algebra_generator(label)))
                    != factor_map(factor.algebra_generator(label))
                    for label in factor.algebra_generating_set()
                ):
                    raise ValueError("the proposed pushout morphism does not factor the supplied cocone")
            return induced


class AlgebraMorphism:
    r"""An ``R``-algebra morphism specified by the images of algebra generators."""

    def _multiplicativity_derivation(self):
        r"""Generator extension proves the law; arbitrary map ingress states it."""
        derived = super()._multiplicativity_derivation()
        if derived is not None:
            return derived
        return self._generator_extension_laws

    def _unit_preservation_derivation(self):
        derived = super()._unit_preservation_derivation()
        if derived is not None:
            return derived
        return self._generator_extension_laws

    def __init__(
        self, parent, images, *, _construction_premises=None,
        _transported_morphism=None,
    ) -> None:
        if (
            _transported_morphism is None
            and isinstance(images, UnitalMultiplicativeAlgebraMorphism)
            and images.domain() is parent.domain()
            and images.codomain() is parent.codomain()
        ):
            _transported_morphism = images
        self._generator_extension_laws = None
        domain = parent.domain()
        codomain = parent.codomain()
        framed_domain = domain.is_framed_algebra()
        self._engine_morphism = None
        self._source_element_map = None

        if isinstance(images, ModuleMorphismMethods):
            if images.domain() is not domain or images.codomain() is not codomain:
                raise ValueError(
                    f"cannot view the module map {images} as an algebra morphism {domain} -> {codomain}: it is a "
                    f"map {images.domain()} -> {images.codomain()}"
                )

            # This exact linear map is the datum. Its algebra and unit laws
            # remain admission premises until the inherited diagnostics are
            # requested; unknown equality is not Boolean-coerced here.
            self._source_element_map = images
            if framed_domain:
                algebra_labels = domain.algebra_generating_set()
                self._generator_images = indexed_family(
                    algebra_labels,
                    lambda label: codomain(images(domain.algebra_generator(label))),
                    name="Generator images",
                )
            else:
                self._generator_images = None
            linear = domain.module_category().Mor(domain, codomain)._from_constructed_element_map(
                images, premises=(images,),
            )
            super().__init__(
                parent, linear, _construction_premises=_construction_premises,
                _transported_morphism=_transported_morphism,
            )
            return
        if isinstance(images, Map):
            if images.domain() is domain and images.codomain() is codomain:
                self._source_element_map = images
                if framed_domain:
                    labels = domain.algebra_generating_set()
                    self._generator_images = indexed_family(
                        labels,
                        lambda label: codomain(images(domain.algebra_generator(label))),
                        name="Generator images",
                    )
                else:
                    self._generator_images = None
                # Matching endpoints retain this function, but do not prove
                # its R-linearity. The module owner keeps that law undecided
                # until its ordinary elementwise diagnostic is requested.
                linear = domain.module_category().Mor(
                    domain, codomain
                ).elementwise(
                    lambda element: codomain(images(domain(element)))
                )
                super().__init__(
                    parent, linear, _construction_premises=_construction_premises,
                    _transported_morphism=_transported_morphism,
                )
                return
            engine_domain = _engine_ring(domain)
            engine_codomain = _engine_ring(codomain)
            if images.domain() is not engine_domain or images.codomain() is not engine_codomain:
                raise ValueError(
                    f"cannot view {images} as an algebra morphism {domain} -> {codomain}: it is a map "
                    f"{images.domain()} -> {images.codomain()}"
                )
            self._engine_morphism = images
            if framed_domain:
                labels = domain.algebra_generating_set()
                self._generator_images = indexed_family(
                    labels,
                    lambda label: codomain(images(engine_domain(domain.algebra_generator(label)))),
                    name="Generator images",
                )
            else:
                self._generator_images = None
            # Translating native endpoints supplies no linearity proof for
            # an arbitrary Map; use the same diagnostic as an owned map.
            linear = domain.module_category().Mor(
                domain, codomain
            ).elementwise(
                lambda element: codomain(
                    images(engine_domain(domain(element)))
                )
            )
            super().__init__(
                parent, linear, _construction_premises=_construction_premises,
                _transported_morphism=_transported_morphism,
            )
            return
        engine_domain = _engine_ring(domain)
        engine_codomain = _engine_ring(codomain)
        assert framed_domain, (
            f"{domain} has no chosen algebra generators, so a morphism out of it must be given as a ring "
            f"map, not as {images!r}"
        )
        labels = domain.algebra_generating_set()
        if isinstance(images, IndexedFamily):
            source_indices = images.index_set()
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(images[source_indices(label)]),
                name="Generator images",
            )
        elif isinstance(images, dict):
            if not labels.cardinality().is_finite():
                raise TypeError(
                    f"a dictionary of generator images needs finitely many algebra generators of {domain}, but it "
                    f"has {labels.cardinality()}; give a function or an indexed family"
                )
            missing = [label for label in labels if label not in images]
            if missing:
                raise ValueError(
                    f"the images of the algebra generators of {domain} must be given for every generator, but "
                    f"{missing} are missing"
                )
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(images[label]),
                name="Generator images",
            )
        elif isinstance(images, (tuple, list)):
            size = labels.cardinality()
            if not size.is_finite():
                raise TypeError(
                    f"a list of generator images needs finitely many algebra generators of {domain}, but it has "
                    f"{size}; give a function or an indexed family"
                )
            values = tuple(images)
            if len(values) != int(size.finite_value()):
                raise ValueError(
                    f"{domain} has {size} algebra generators, but {len(values)} images were given"
                )
            if labels not in EnumeratedSets():
                raise TypeError(
                    f"a list of generator images needs the algebra generators of {domain} in a fixed order, but "
                    f"{labels} is not ordered"
                )
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(values[int(labels.ranking_map()(label))]),
                name="Generator images",
            )
        elif callable(images):
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(images(label)),
                name="Generator images",
            )
        else:
            raise TypeError(
                f"a morphism {domain} -> {codomain} of algebras is given by the images of the algebra "
                f"generators, but got {images!r}"
            )

        assert engine_domain in SageRings() and engine_codomain in SageRings(), (
            f"a morphism {domain} -> {codomain} given by generator images is computed only between rings "
            "that Sage can compute with; use the category of free algebras or of algebras given by "
            "generators and relations"
        )
        self._engine_morphism = _engine_algebra_morphism_from_generator_images(
            domain,
            codomain,
            self._generator_images,
        )
        self._generator_extension_laws = True
        linear = domain.module_category().Mor(
            domain, codomain
        )._from_constructed_element_map(
            lambda element: codomain(
                self._engine_morphism(engine_domain(domain(element)))
            )
        )
        super().__init__(
            parent, linear, _construction_premises=_construction_premises,
            _transported_morphism=_transported_morphism,
        )

    def __call__(self, element):
        r"""Apply this owned algebra morphism to an engine-backed facade element."""
        return self._call_(element)

    def _call_(self, element):
        r"""Apply the algebra map in its represented realization."""
        if self._source_element_map is not None:
            return self.codomain()(self._source_element_map(self.domain()(element)))
        engine_morphism = self._engine_morphism_crossing()
        source = _engine_ring(self.domain())
        return self.codomain()(engine_morphism(source(element)))

    def _engine_morphism_crossing(self):
        r"""Return the private engine morphism when this map has one.

        Protected contract for bridge consumers that must construct a native
        Sage object.  An algebra morphism represented entirely in the owned
        universe deliberately has no such engine morphism.
        """
        if self._engine_morphism is not None:
            return self._engine_morphism
        return _engine_algebra_morphism(self)

    def algebra_generator_morphism(self):
        assert self._generator_images is not None, (
            f"{self} has no images of algebra generators: its domain {self.domain()} has no chosen "
            "algebra generators"
        )
        return Sets().Mor(
            self.domain().algebra_generating_set(), self.codomain()
        )(self._generator_images.value)

    def algebra_generator_images(self):
        assert self._generator_images is not None, (
            f"{self} has no images of algebra generators: its domain {self.domain()} has no chosen "
            "algebra generators"
        )
        return self._generator_images

    def _richcmp_(self, other, op):
        r"""Decide equality from the source's chosen algebra generating set.

        Two algebra morphisms agree exactly when they agree on generators, so
        this is decidable when the source is framed and not otherwise.
        """
        from sage.structure.richcmp import op_EQ, op_NE

        if op not in (op_EQ, op_NE):
            return NotImplemented
        if other not in self.parent():
            return op == op_NE
        if self is other:
            return op == op_EQ
        if (
            not isinstance(other, AlgebraMorphism)
            or (
                self._generator_extension_laws is not True
                and self._constructed_algebra_map_decision() is not True
            )
            or (
                other._generator_extension_laws is not True
                and other._constructed_algebra_map_decision() is not True
            )
        ):
            forget = Algebras(self.domain().algebra_base_ring()).underlying_module()
            return ModuleMorphismMethods._richcmp_(forget(self), forget(other), op)
        domain = self.domain()
        if not domain.is_framed_algebra():
            equal = AtomicProposition("equal", self, other)
        else:
            equal = self.algebra_generator_images() == other.algebra_generator_images()
        return equal if op == op_EQ else negation(equal)

    def __mul__(self, other):
        r"""Compose the retained maps in their common scalar-algebra theory.

        Generator values alone cannot reconstruct an arbitrary whole map
        whose algebra or unit premise is still undecided. The existing
        underlying-module composition preserves its actual evaluator.
        """
        return MultiplicativeAlgebraMorphism.__mul__(self, other)


class PresentedAlgebraMorphism:
    r"""A map from an algebra with a chosen finite presentation.

    The map is defined on the presentation algebra; annihilation of the
    selected relations is its admitted descent premise. That premise is
    checked only when requested, and evaluation uses the chosen quotient
    representatives. No Sage target-ring protocol is involved.
    """

    def _elementwise_linearity_derivation(self):
        r"""Derive linearity from actual descent through the presentation.

        Killing the relations proves that the presentation algebra's linear
        map descends. Otherwise retain those exact descent equations and use
        the ordinary diagnostic of the chosen representative evaluator: a
        failed algebra relation alone need not refute its linearity.
        """
        if self._presentation_descent_decision() is True:
            return True
        return super()._elementwise_linearity_derivation()

    def _multiplicativity_derivation(self):
        derived = super()._multiplicativity_derivation()
        if derived is not None:
            return derived
        if self._presentation_descent_decision() is True:
            return True
        return None

    def _unit_preservation_derivation(self):
        derived = super()._unit_preservation_derivation()
        if derived is not None:
            return derived
        if self._presentation_descent_decision() is True:
            return True
        return None

    @cached_method
    def _presentation_descent_decision(self):
        r"""The actual unital-algebra-map and relation premises for descent.

        Vanishing of selected ideal generators extends to their ideal only
        when the presentation map is linear and multiplicative. The unit
        law then descends too. Keep every undecided premise; failure of this
        sufficient proof does not refute a law of the chosen representative
        evaluator, whose ordinary diagnostic remains available.

        A retained whole-algebra map is already defined on the quotient and
        has no generator-extension derivation.
        """
        if self._source_element_map is not None:
            return None
        return conjunction((
            self._presentation_map.linearity_decision(),
            self._presentation_map.is_multiplicative(),
            self._presentation_map.preserves_unit(),
            self._presentation_relations_decision(),
        ))

    @cached_method
    def _presentation_relations_decision(self):
        r"""Retain the exact equations admitting descent through this presentation.

        The callers are the construction-derived linearity and algebra-law
        suppliers and ``validate_presentation_relations``. These are equations about
        the chosen generator assignment, not a replacement for the generic
        multiplication-preservation predicate on the represented map.
        """
        if self._source_element_map is not None:
            return None
        zero = self.codomain().zero()
        return conjunction(
            self._presentation_map(relation) == zero
            for relation in self.domain().relations()
        )

    @validator
    def validate_presentation_relations(self) -> None:
        r"""Reject a generator assignment proved not to annihilate its relations.

        Unknown relation equations remain admitted premises under OWN-22.
        The validation is distinct from computing the generic algebra laws
        of the represented function on the chosen quotient representatives.
        """
        if self._presentation_relations_decision() is False:
            raise ValueError(
                f"the chosen generator images of {self.domain()} -> {self.codomain()} "
                "do not annihilate its presentation relations"
            )

    def __init__(
        self, parent, images, *, _construction_premises=None,
        _transported_morphism=None,
    ) -> None:
        if (
            _transported_morphism is None
            and isinstance(images, UnitalMultiplicativeAlgebraMorphism)
            and images.domain() is parent.domain()
            and images.codomain() is parent.codomain()
        ):
            _transported_morphism = images
        domain = parent.domain()
        codomain = parent.codomain()
        labels = domain.algebra_generating_set()
        self._source_element_map = None
        self._presentation_map = None
        if isinstance(images, (Map, ModuleMorphismMethods)):
            if images.domain() is not domain or images.codomain() is not codomain:
                raise ValueError(
                    f"the whole-algebra map for {domain} -> {codomain} has "
                    f"different endpoints {images.domain()} -> {images.codomain()}"
                )
            self._source_element_map = images
            self._generator_images = indexed_family(
                labels,
                lambda label: codomain(images(domain.algebra_generator(label))),
                name="Generator images",
            )
            linear = domain.module_category().Mor(domain, codomain)._from_constructed_element_map(
                images, premises=(images,),
            )
            super().__init__(
                parent, linear, _construction_premises=_construction_premises,
                _transported_morphism=_transported_morphism,
            )
            return
        size = labels.cardinality()
        if not size.is_finite():
            raise ValueError(
                f"an algebra given by generators and relations needs finitely many generators, but "
                f"{domain} has {size}"
            )
        if isinstance(images, IndexedFamily):
            source_indices = images.index_set()
            selected = indexed_family(
                labels,
                lambda label: codomain(images[source_indices(label)]),
                name="Generator images",
            )
        elif isinstance(images, dict):
            missing = [label for label in labels if label not in images]
            if missing:
                raise ValueError(
                    f"the images of the algebra generators of {domain} must be given for every generator, but "
                    f"{missing} are missing"
                )
            selected = indexed_family(
                labels,
                lambda label: codomain(images[label]),
                name="Generator images",
            )
        elif isinstance(images, (tuple, list)):
            values = tuple(images)
            if len(values) != int(size.finite_value()):
                raise ValueError(
                    f"{domain} has {size} algebra generators, but {len(values)} images were given"
                )
            selected = indexed_family(
                labels,
                lambda label: codomain(values[int(labels.ranking_map()(label))]),
                name="Generator images",
            )
        elif callable(images):
            selected = indexed_family(
                labels,
                lambda label: codomain(images(label)),
                name="Generator images",
            )
        else:
            raise TypeError(
                f"a morphism out of {domain} is given by the images of its algebra generators, but got {images!r}"
            )
        self._generator_images = selected
        self._presentation_map = Algebras(domain.presentation_ring().base_ring()).Associative().Unital().Mor(domain.presentation_ring(), codomain)(selected)
        linear = domain.module_category().Mor(domain, codomain).elementwise(
            lambda element: codomain(
                self._presentation_map(domain.lift_to_presentation(domain(element)))
            )
        )
        super().__init__(
            parent, linear, _construction_premises=_construction_premises,
            _transported_morphism=_transported_morphism,
        )
        self.validate_presentation_relations(check=False)

    def algebra_generator_morphism(self):
        return Sets().Mor(
            self.domain().algebra_generating_set(), self.codomain()
        )(self._generator_images.value)

    def algebra_generator_images(self):
        return self._generator_images

    def _call_(self, element):
        if self._source_element_map is not None:
            return self.codomain()(self._source_element_map(self.domain()(element)))
        return self._presentation_map(self.domain().lift_to_presentation(element))

    def __call__(self, element):
        return self._call_(element)

    def _richcmp_(self, other, op):
        r"""Decide equality on the chosen algebra generators of the source.

        A morphism out of a presented algebra is determined by the images of
        those generators: its map from the presentation algebra is determined
        there, and the quotient projection is surjective.
        """
        from sage.structure.richcmp import op_EQ, op_NE

        if op not in (op_EQ, op_NE):
            return NotImplemented
        if other not in self.parent():
            return op == op_NE
        if self is other:
            return op == op_EQ
        if (
            not isinstance(other, PresentedAlgebraMorphism)
            or self._presentation_descent_decision() is not True
            or other._presentation_descent_decision() is not True
        ):
            forget = Algebras(self.domain().algebra_base_ring()).underlying_module()
            return ModuleMorphismMethods._richcmp_(forget(self), forget(other), op)
        equal = self._generator_images == other._generator_images
        return equal if op == op_EQ else negation(equal)

    def __mul__(self, other):
        r"""Compose the actual quotient maps, retaining their law premises."""
        return MultiplicativeAlgebraMorphism.__mul__(self, other)


class _AlgebraMorCommonMethods:
    r"""Shared equality protocol for represented algebra Mor parents."""

    def _from_engine_morphism(self, morphism):
        r"""Raise an algebra/scheme adapter's selected native algebra computation."""
        assert morphism.domain() is _engine_ring(self.domain()) and morphism.codomain() is _engine_ring(self.codomain())
        return self.element_class(self, morphism)

    def _from_degree_preserving_generator_map(self, images):
        r"""Construct from a structurally degree-preserving generator map."""
        return self(images)


def _corestrict_algebra_morphism_to_center(morphism):
    r"""Return the unique represented factor ``A -> Z(B)`` of ``morphism``.

    The map is a unital associative algebra map with a finite chosen algebra
    generating family in its source. Scalars already land centrally, so
    centrality on that family proves centrality of the whole image. A
    selected algebra centre uses the lift of its underlying module
    inclusion and returns an R-algebra map. The predicate/scalar conversion
    returns a ring map only when that ring centre is literally the selected
    centre. Thus the inclusion triangle has the actual retained endpoints
    and arrow theory, without declaring two centre constructions equal.
    """
    domain = morphism.domain()
    codomain = morphism.codomain()
    algebras = Algebras(domain.algebra_base_ring())
    ordinary = algebras.Associative().Unital()
    assert (
        domain in ordinary and codomain in ordinary
        and morphism in ordinary.Mor(domain, codomain)
    ), (
        f"the ring-centre algorithm for {morphism} needs an associative unital "
        "algebra morphism; general algebra maps use their algebra centre inclusion"
    )
    assert domain.is_framed_algebra(), (
        f"the corestriction of {morphism} to the centre of {codomain} needs chosen algebra generators "
        f"of {domain}"
    )
    labels = domain.algebra_generating_set()
    assert labels.cardinality().is_finite(), (
        f"the corestriction of {morphism} to the centre of {codomain} needs finitely many algebra "
        f"generators of {domain}, but it has {labels.cardinality()}"
    )
    center = codomain.center()
    if center is codomain:
        return morphism
    inclusion = codomain.center_inclusion()
    assert inclusion.domain() is center and inclusion.codomain() is codomain, (
        f"the retained centre inclusion of {codomain} must have the exact endpoints "
        f"{center} -> {codomain}"
    )
    algebra_inclusion = (
        center in algebras
        and inclusion.parent().mor_category().is_subcategory(algebras)
    )
    if algebra_inclusion:
        lift = algebras.underlying_module()(inclusion).lift
    else:
        assert center is codomain.ring_center(), (
            f"the ring-centre algorithm for {morphism} needs a retained comparison "
            "from its predicate or scalar centre to the exact selected magma "
            "centre and its inclusion"
        )
        lift = center
    for label in labels:
        image = morphism(domain.algebra_generator(label))
        lift(image)
    if algebra_inclusion:
        linear = domain.module_category().Mor(domain, center)._from_constructed_element_map(
            lambda element: lift(morphism(element)),
            premises=(morphism, inclusion),
        )
        return algebras.Mor(domain, center)(linear)
    return OwnedRings().Mor(domain, center)(lambda element: lift(morphism(element)))


class PresentedAlgebraMor(_AlgebraMorCommonMethods, UnitalMultiplicativeAlgebraMor):
    ElementMethods = PresentedAlgebraMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
        )

    def _element_constructor_(self, images):
        if isinstance(images, Map):
            if self._already_parented_arrow(images):
                return images
            raise TypeError(f"{images} is an arrow of another Mor; supply algebra-generator images or apply the functor")
        return self.element_class(self, images)

    @object_level
    @cached_method
    def identity(self):
        r"""Return the identity of this endomorphism Mor.

        The identity of an object needs no framing: an unframed algebra such as
        the integers regarded over themselves has no algebra generating set,
        and its identity is still the identity.  A Mor object has one identity,
        so this is cached.
        """
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )
        domain = self.domain()
        # The identity is already represented by the engine's identity
        # morphism.  It must not query the selected generator resolution:
        # free algebras use this morphism as the augmentation of their own
        # degree-zero resolution while that resolution is being installed.
        engine = _engine_ring(domain)
        identity = self._from_engine_morphism(engine.hom(engine))
        identity._preamble_is_identity = True
        return identity


class AlgebraMor(_AlgebraMorCommonMethods, UnitalMultiplicativeAlgebraMor):
    ElementMethods = AlgebraMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
        )

    def _element_constructor_(self, images):
        if isinstance(images, Map):
            if self._already_parented_arrow(images):
                return images
            raise TypeError(f"{images} is an arrow of another Mor; supply algebra-generator images or apply the functor")
        return self.element_class(self, images)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )
        algebra = self.domain()
        identity = self._from_constructed_element_map(lambda element: element)
        identity._preamble_is_identity = True
        return identity

    def _repr_(self):
        return f"Mor_Alg({self.domain()}, {self.codomain()})"


class _OwnedAlgebraElement(_OwnedRingElement):
    r"""Engine-backed owned algebra element with ring multiplication syntax."""

    def __mul__(self, other):
        return _OwnedRingElement.__mul__(self, other)

    def __rmul__(self, other):
        return _OwnedRingElement.__rmul__(self, other)

    def _lmul_(self, scalar):
        r"""``r * a = (r * 1) a``, with ``r * 1`` given by the realization's scalar structure.

        This realizes the scalar action of the underlying module.  The
        structure morphism of the algebra is computed from that action at the
        root, so it is not read back here.
        """
        parent = self.parent()
        return parent(parent._realized_scalar_structure(parent.base_ring()(scalar))) * self


class _OwnedAlgebraParent(_OwnedRingParent):
    r"""One ring read as an algebra through one specified scalar map."""

    Element = _OwnedAlgebraElement

    def _defer_native_algebra_construction(self):
        r"""The algebra owner installs its selected resolution before its regular module."""
        return True

    def _native_scalar_action(self, scalar, element):
        r"""Apply the retained algebra structure map, not the engine's default embedding.

        An owned algebra may be presented on a ring whose native engine has a
        different ambient scalar embedding from the selected map
        ``k -> A``.  Its regular ``k``-module must use the map retained by the
        algebra owner; otherwise module construction silently changes the
        specified algebra structure while leaving the underlying ring intact.
        """
        scalar_image = self._realized_scalar_structure(self.base_ring()(scalar))
        return scalar_image * self(element)

    def __init__(
        self,
        engine,
        base_ring,
        labels,
        scalar_structure=None,
        generator_values=None,
        *,
        categories=(),
        construction_data=(),
        law_decisions=(),
        algebra_framing_source=None,
        algebra_generating_family=None,
        algebra_framing_owner=None,
        constructing_category=None,
        ring_placement=None,
    ) -> None:
        r"""Realize a ring as an algebra over ``base_ring`` on a private engine.

        Declared engine adapter (``OWN-06``) for the algebras the preamble
        adopts from Sage.  ``scalar_structure`` is the ring map
        ``base_ring -> A``, ``r |-> r * 1``, that realizes the scalar action
        of the underlying module; without one it is the engine's own map from
        its scalars.  ``ring_placement``, when the construction states one, is
        the ring placement of its result (a function returning categories);
        otherwise the placement of the engine's presenting constructor is read.
        """
        base = _owned_ring(base_ring)
        # Keep the chosen scalar ring available while category placement is
        # deferred. In that interval algebra_base_ring() is not installed by
        # the algebra category, but the native regular-module construction
        # must still use this exact base rather than infer it from the engine.
        self._preamble_selected_algebra_base_ring = base
        for name, value in construction_data:
            setattr(self, name, value)
        self._realized_scalar_structure = (lambda scalar: self(scalar)) if scalar_structure is None else scalar_structure
        if labels is None:
            selected_labels = None
        else:
            # Share the module owner's rank/cardinality/set normalization.
            # In particular an owned set is retained literally, while a rank
            # denotes the canonical ordinal rather than an ordered set built
            # by iterating the integer.
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                _module_generating_set,
            )

            selected_labels = _module_generating_set(labels)
        associative = Algebras(base).Associative().Unital()
        # A native algebra that is also a ring must retain the ring category
        # supplied by its constructor. Reading only its commutativity axiom
        # below loses inherited structure such as additive-group membership,
        # so the same object can fail the native ring-module prerequisite.
        if ring_placement is None:
            raise TypeError(
                f"{engine} has no selected ring-construction placement; "
                "an algebra adapter must retain the placement supplied by its constructor"
            )
        presented_ring = owned_category_join((OwnedRings(), *ring_placement()))
        framing_owner = (
            associative if algebra_framing_owner is None else algebra_framing_owner
        )
        # The algebra root constructs an additive-commutative group as part
        # of its underlying module.  A ring placement supplied by an engine
        # adapter need not materialize that inherited facet on the concrete
        # parent, so include the module prerequisite at this construction
        # owner rather than relying on the category join to infer it.
        placement = [associative, presented_ring, AdditiveGroups().AdditiveCommutative()]
        # The ring constructor that presents ``engine``, or a category the
        # caller selected, places the product as commutative (ARC-08).
        match (
            presented_ring.is_subcategory(OwnedRings().Commutative())
            or any(category.is_subcategory(Magmas().Commutative()) for category in categories)
        ):
            case True:
                if algebra_framing_owner is None:
                    framing_owner = associative.Commutative()
                placement.append(framing_owner)
            case False:
                pass
        # Native free-algebra constructors already own the exact generator
        # family and the category relative to which its resolution is stated.
        # Retain those data instead of rebuilding a second family from backend
        # positions or inferring the resolution owner from category inclusion.
        if algebra_generating_family is not None:
            assert selected_labels is not None, (
                "a selected algebra generating family requires its index labels"
            )
            family_labels = algebra_generating_family.index_set()
            assert family_labels is selected_labels, (
                "the selected algebra generating family must be indexed by the "
                "literal index-set object retained as the algebra framing"
            )
            if generator_values is None:
                # Retain the family as a family until the common generator
                # adapter sees it. Replacing it by its bound ``value`` method
                # here bypasses the IndexedFamily branch below, preventing
                # that owner from distinguishing matching labels from distinct
                # index sets that require ordinal transport.
                generator_values = algebra_generating_family
        placement.extend(categories)
        # Construction hooks run inside Parent.__init__. A native polynomial
        # or tensor algebra's selected generator resolution is installed only
        # after that call. Even its *ring* placement may have polynomial-ring
        # hooks which ask for the selected framing, so neither the presented
        # ring category nor the algebra categories may be exposed during the
        # first Parent initialization. Start with the minimal owned ring and
        # additive-group structure; install the complete stated placement only
        # after the selected resolution and native module datum are available.
        initial_placement = (OwnedRings(), AdditiveGroups().AdditiveCommutative())
        retained_laws = {"associativity": True, "unit": True}
        if framing_owner is not associative:
            retained_laws["commutativity"] = True
        retained_laws.update(dict(law_decisions))
        # The algebra is an object of the category its public constructor
        # was asked for (OWN-15).  A route that names none is an algebra of
        # ``Algebras(R).Associative().Unital()``; commutativity, read off the
        # engine above, is a full axiom and is not recorded (ARC-08).
        _OwnedRingParent.__init__(
            self,
            engine,
            base=base,
            # Select the full implementation type before Parent.__init__, but
            # initialize it in the minimal category until the selected algebra
            # resolution and native module datum have been installed.
            category=Cat().meet(tuple(placement)),
            initial_category=Cat().meet(initial_placement),
            constructing_category=(
                associative if constructing_category is None else constructing_category
            ),
            # The presented ring placement is included in ``placement`` and
            # refined only after native module/framing setup below. Passing it
            # as named_placement would make _OwnedRingParent reintroduce those
            # categories into its initial Parent.__init__ join.
            named_placement=None,
            _defer_construction_facets=True,
        )
        Algebras.ParentMethods._retain_algebra_law_decisions(
            self, retained_laws
        )
        from sage_extensions.categories.modules.pure.modules import Modules

        if labels is None:
            if generator_values is not None:
                raise ValueError(
                    f"the algebra {engine} over {base_ring} has no chosen generators, so it cannot be given "
                    "generator values"
                )
            # The common Parent initialization intentionally skipped the
            # native module. At this point the owner has returned from it and
            # the selected scalar base is retained, so construct the regular
            # module now, before exposing the algebra placement.
            _algebra_from_native_ring(
                self,
                lambda left, right: left * right,
                self._from_engine_element(engine.one()),
                self._native_scalar_action,
                module_basis=self._native_module_basis,
                scalar_ring=base,
            )
            refine(self, Cat().meet(tuple(placement)))
            return

        label_size = selected_labels.cardinality()
        if not label_size.is_finite():
            raise TypeError(
                f"the algebra {engine} over {base_ring} needs finitely many generators, but has {label_size}"
            )

        if generator_values is None:

            def value(label):
                position = int(selected_labels.ranking_map()(label))
                return self._from_engine_element(engine.gen(position))
        else:
            if isinstance(generator_values, IndexedFamily):
                if generator_values.cardinality() != label_size:
                    raise ValueError(
                        f"the algebra {engine} has {label_size} generators, but {generator_values.cardinality()} "
                        "generator values were given"
                    )
                family_labels = generator_values.index_set()
                # A family indexed by an equal-but-distinct set is not already
                # indexed by the selected algebra framing. Treat it as a new
                # presentation and use the explicit positional transport below.
                same_labels = family_labels is selected_labels
                if same_labels:

                    def value(label):
                        return self(generator_values.value(label))

                else:
                    # Equal cardinality does not identify two index sets.
                    # When their labels differ, the constructors' selected
                    # enumerations provide the only positional correspondence.
                    # Keep the direct label path above so a finite index set
                    # need not acquire an enumeration merely to use its own
                    # already-matching generator family.
                    enumerated = family_labels in EnumeratedSets()
                    if enumerated is not True:
                        raise TypeError(
                            f"the generator family for {engine} is indexed by {family_labels}, "
                            f"which differs from the selected algebra labels {selected_labels}; "
                            "positional transport requires a proved selected enumeration of the supplied index set"
                        )
                    family_position = family_labels.ranking_map().inverse()

                    def value(label):
                        position = selected_labels.ranking_map()(label)
                        return self(generator_values.value(family_position(position)))
            elif callable(generator_values):

                def value(label):
                    raw = generator_values(label)
                    return raw if element_parent(raw) is self else self._from_engine_element(raw)
            elif isinstance(generator_values, (tuple, list)):
                if len(generator_values) != int(label_size.finite_value()):
                    raise ValueError(
                        f"the algebra {engine} has {label_size} generators, but {len(generator_values)} generator "
                        "values were given"
                    )
                # Explicit finite ingress is parsed by position; the Python
                # sequence is not retained as the mathematical family.
                by_position = {position: generator_values[position] for position in range(len(generator_values))}

                def value(label):
                    raw = by_position[int(selected_labels.ranking_map()(label))]
                    return raw if element_parent(raw) is self else self._from_engine_element(raw)
            else:
                raise TypeError(
                    f"generator values of the algebra {engine} are given by a function, an indexed family, or a "
                    f"list, but got {generator_values!r}"
                )

        generator_morphism = Sets().Mor(selected_labels, self)(value)

        def free_source():
            if algebra_framing_source is not None:
                return algebra_framing_source
            generating_module = base.free_module(selected_labels)
            match framing_owner is associative:
                case True:
                    return generating_module.tensor_algebra()
                case False:
                    return generating_module.symmetric_algebra()

        def augmentation(source):
            # A native free algebra is its own degree-zero free source.  Its
            # augmentation is therefore the identity, not a morphism built
            # from its as-yet-uninstalled selected resolution.  Constructing
            # that latter morphism here recursively asks the source for the
            # very framing this constructor is in the process of installing.
            if source is self:
                return source.Mor(self).identity()
            return source.Mor(self)(generator_morphism)

        _fix_selected_algebra_resolution(
            self,
            framing_owner,
            free_source,
            selected_labels,
            generator_morphism,
            augmentation,
        )
        # The selected algebra resolution has just been retained. The common
        # Parent initialization skipped module construction, so install the
        # native module only now, then expose the algebra category.
        _algebra_from_native_ring(
            self,
            lambda left, right: left * right,
            self._from_engine_element(engine.one()),
            self._native_scalar_action,
            module_basis=self._native_module_basis,
            scalar_ring=base,
        )
        # Both selected framing and native module datum are now queryable by
        # the algebra realization hooks this placement introduces.
        refine(self, Cat().meet(tuple(placement)))

@cached_function(key=lambda algebra, base_ring, labels=None, categories=(), construction_data=(), law_decisions=(), ring_placement=(): (
    algebra,
    base_ring,
    None if labels is None else id(labels),
    tuple(map(id, categories)),
    tuple((name, id(value)) for name, value in construction_data),
    tuple((name, id(value)) for name, value in law_decisions),
    tuple(map(id, ring_placement)),
))
def _owned_algebra_view(
    algebra,
    base_ring,
    labels=None,
    categories=(),
    construction_data=(),
    law_decisions=(),
    ring_placement=(),
):
    # A structure view retains its source algebra as defining data. The base
    # and labels alone do not determine that algebra or its multiplication.
    base = _owned_ring(base_ring)
    return _OwnedAlgebraParent(
        _engine_ring(algebra),
        base,
        labels,
        categories=tuple(categories),
        construction_data=tuple(construction_data),
        law_decisions=tuple(law_decisions),
        ring_placement=lambda: ring_placement,
    )


def _algebra_with_structure(
    algebra,
    base_ring,
    labels=None,
    *categories,
    construction_data=(),
):
    r"""Construct an owned algebra view with its selected categories present.

    Native representation boundary: a free polynomial/word realization
    retains its exact generating module and monomial frame when a further
    construction (for example a coproduct) adds its datum.  An unchanged
    view is the existing object.  Other scalar structures retain their own
    native algebra constructor, without assuming a monomial basis.
    """
    base = _owned_ring(base_ring)
    specialized = algebra._specialized_algebra_with_structure(
        base,
        labels,
        tuple(categories),
        tuple(construction_data),
    )
    if specialized is not None:
        return specialized
    ring_placement = tuple(
        category
        for category in algebra.category().all_super_categories()
        if category is OwnedRings()._with_axioms(category.axioms())
    )
    return _owned_algebra_view(
        algebra,
        base,
        labels,
        tuple(categories),
        tuple(construction_data),
        ring_placement=ring_placement,
    )


class _ScalarAlgebraEngine:
    r"""Element conversion for an algebra built on a scalar-action module.

    Engine adapter (``OWN-06``).  The module owner supplies all arithmetic and
    the algebra root supplies multiplication. This class retains the exact
    source ring and its optional computation realization, and translates
    elements through the module used at the algebra entry.
    """

    def __init__(self, native_ring, **rest) -> None:
        self._native_ring = native_ring
        self._preamble_engine_ring = native_ring._selected_engine_ring()
        super().__init__(**rest)

    def _element_constructor_(self, value):
        source = element_parent(value)
        if source is self:
            return value
        if source in Modules(self.base_ring()) and self._built_on_the_same_data(source):
            return self._element_on_the_same_data(source, value)
        if source is self.base_ring():
            module = self.unformed_module()
            scalar_value = module.scalar_multiple(value, module(self._native_ring.one()))
            return self._element_from_unformed_module(scalar_value)
        return super()._element_constructor_(self._native_ring(value))

    def _element_from_unformed_module(self, element):
        r"""Read retained module data without applying the coefficient map again.

        This is the existing Modules protected data-crossing contract. The
        scalar-action view and its engine-result adapter supply module data;
        a plain coefficient input instead enters through the scalar action.
        These differ when the underlying ring is also the coefficient ring
        and its selected endomorphism is not the identity.
        """
        module = self.unformed_module()
        return self._element_from_underlying_set(
            module._underlying_additive_element(module(element))
        )

    def _from_engine_element(self, value):
        return self._element_from_unformed_module(
            self.unformed_module()(_owned_engine_element(self._native_ring, value))
        )

    def _selected_engine_ring(self):
        r"""Return this view's retained ring realization, or ``None``."""
        return self._preamble_engine_ring

    def _engine_element(self, value):
        module_element = self.unformed_module()(self(value))
        return _engine_element(self._native_ring, module_element.underlying_element())

    def _repr_(self):
        return f"{self._native_ring} as an algebra over {self.base_ring()}"


@cached_function
def _scalar_algebra_engine(engine):
    r"""The computation class of an algebra view, with a caller's ``engine`` before it.

    Engine adapter (``OWN-06``).  ``_ScalarAlgebraEngine`` translates elements
    between the view and its native ring; a caller that adds structure to the
    view (a slice or coslice level) may supply further computation, which
    precedes that translation.
    """
    from sage.structure.dynamic_class import dynamic_class

    if engine is None:
        return _ScalarAlgebraEngine
    return dynamic_class(engine.__name__, (engine, _ScalarAlgebraEngine))


@cached_function(key=lambda ring, structure_map: (id(ring), id(structure_map)))
def _algebra_structure_view(ring, structure_map):
    r"""The R-algebra defined by the central ring map ``R -> ring``, once for each map."""
    return _algebra_structure_on(ring, structure_map)


def _algebra_structure_on(
    ring,
    structure_map,
    *,
    categories=(),
    construction_data=None,
    engine=None,
):
    r"""The R-algebra defined by the central ring map ``R -> ring``, with the data of further levels.

    First construct its R-module from the additive group and the given scalar
    action.  The product of the original ring is R-bilinear because the scalar
    image is central.  Classify it at the tensor owner and supply that module,
    classifier and unit to the single algebra entry.  Native conversion is a
    private realization of this result, not a second algebra constructor.

    ``categories`` and ``construction_data`` are the categories and data of
    the levels a caller adds on the data of ``ring`` (``OWN-16``), and
    ``engine`` is that caller's private computation class.  Every call
    constructs a new object: two slice objects on one ring are distinct.

    The incoming map is retained by the module action on the literal ring.
    The intrinsic structure map of the resulting view is separately derived
    at the algebra owner and ends in the centre of that new view. Only actual
    source ring axioms and size properties are retained as placements; old
    coefficient/framing data and the properties of a larger private engine
    are not properties of this newly selected scalar structure.
    """
    selected_ring = _own_ring(ring)
    assert structure_map.codomain() is selected_ring, (
        f"the structure map R -> A of an algebra must end at A = {selected_ring}, but {structure_map} "
        f"ends at {structure_map.codomain()}"
    )
    base = _owned_ring(structure_map.domain())
    assert base in OwnedRings().Commutative(), (
        f"{selected_ring} is an algebra over {base} through {structure_map} only if {base} is "
        "commutative, and it is not known to be"
    )
    assert structure_map in OwnedRings().Mor(base, selected_ring), (
        "the scalar structure of an associative unital algebra must be an owned unital ring map"
    )
    central_by_structure = selected_ring in OwnedRings().Commutative() or base is _owned_integers()
    center = None if central_by_structure else selected_ring.ring_center()

    def scalar_action(scalar, element):
        central_scalar = structure_map(base(scalar))
        if center is not None:
            central_scalar = center(central_scalar)
        return selected_ring(central_scalar) * selected_ring(element)

    additive_group = selected_ring
    additive_endomorphisms = AdditiveGroups().AdditiveCommutative().End(additive_group)
    rho = OwnedRings().Mor(base, additive_endomorphisms)(
        lambda scalar: additive_endomorphisms.elementwise(
            lambda element: scalar_action(scalar, element)
        )
    )
    module = Modules(base)(rho)
    tensor = Modules(base).tensor_product((module, module))
    multiplication = tensor.from_bilinear_map(
        module, lambda left, right: module(left.underlying_element() * right.underlying_element()),
    )
    algebras = Algebras(base).Associative().Unital()
    law_decisions = {"associativity": True, "unit": True}
    if selected_ring in OwnedRings().Commutative():
        algebras = algebras.Commutative()
        law_decisions["commutativity"] = True
    retained_categories = tuple(
        category for category in selected_ring.category().all_super_categories()
        if category is OwnedRings()._with_axioms(category.axioms())
        or category is Sets()._with_axioms(category.axioms())
    )
    category = Cat().meet((algebras, *retained_categories))
    # Conversion specializes both the algebra's data crossing and the
    # actual module realization's element ingress. Their relative sibling
    # order is not a semantic priority; stronger algebra laws stay above
    # this private adapter at their own providers.
    engine_owner = Cat().meet((Algebras(base), module.category()))
    return _algebra_on_module(
        module, multiplication, placement=(category,), categories=categories,
        unit=module(selected_ring.one()),
        construction_data={
            "_engine": (engine_owner, _scalar_algebra_engine(engine), None),
            "native_ring": selected_ring,
            **dict(construction_data or {}),
        },
        law_decisions=law_decisions,
    )


def _unit_from_multiplication(multiplication):
    from sage.matrix.constructor import matrix as sage_matrix
    from sage.modules.free_module_element import vector as sage_vector

    module = multiplication.codomain()
    tensor_square = multiplication.domain()
    labels = module.module_generating_set()
    size = labels.cardinality()
    if not size.is_finite():
        raise TypeError(
            f"the unit of the algebra with multiplication {multiplication} is computed from finitely many "
            f"module generators of {module}, but it has {size}"
        )
    ring = module.base_ring()
    engine = _engine_ring(ring)
    rank = int(size.finite_value())

    # Private finite linear-system serialization.  The mathematical basis stays
    # the owned ordered framing ``labels``; only this backend array is concrete.
    system_entries = [[engine.zero() for _ in range(rank)] for _ in range(rank * rank)]
    target_entries = [engine.zero() for _ in range(rank * rank)]
    for right_index in range(rank):
        right_label = labels[right_index]
        target_entries[right_index * rank + right_index] = engine.one()
        for left_index in range(rank):
            left_label = labels[left_index]
            product = multiplication(
                tensor_square.pure_tensor(
                    module.module_generator(left_label),
                    module.module_generator(right_label),
                )
            )
            coordinates = module.framing_morphism().lift(product)
            for out_index in range(rank):
                out_label = labels[out_index]
                system_entries[right_index * rank + out_index][left_index] = _engine_element(ring, coordinates(out_label))
    system = sage_matrix(engine, rank * rank, rank, system_entries)
    target = sage_vector(engine, target_entries)
    coefficients = system.solve_right(target)
    unit = module.linear_combination({labels[index]: _owned_engine_element(ring, engine(coefficients[index])) for index in range(rank) if coefficients[index]})
    for label in labels:
        generator = module.module_generator(label)
        if multiplication(tensor_square.pure_tensor(generator, unit)) != generator:
            raise TypeError(
                f"the multiplication {multiplication} on {module} has no two-sided unit: the left unit {unit} "
                f"fails on the generator {generator}"
            )
    return unit


def _own_algebra(structure_map):
    r"""Read a central ring map as its algebra, preserving the exact selected map.

    The view cache is keyed by map identity and retains that map in its
    module action. No outer equality cache may identify different supplied
    actions, and an identity shortcut needs no cache because it returns its
    literal ring.
    """
    base = _owned_ring(structure_map.domain())
    target = _owned_ring(structure_map.codomain())
    assert base in OwnedRings().Commutative(), (
        "an algebra requires a commutative coefficient ring; a noncommutative ring's identity is not central"
    )
    assert structure_map in OwnedRings().Mor(base, target), (
        "an algebra's selected central map must be an owned unital ring morphism"
    )
    if (
        target is base
        and base.base_ring() is base
        and structure_map.is_identity() is True
    ):
        # The existing regular scalar structure is literally id_R.  Creating
        # another engine view here would replace its exact ring endpoint.
        placement = Algebras(base).Associative().Unital().Commutative()
        assert base in placement, (
            "the regular algebra structure of a self-based owned ring is fixed "
            "by its ring constructor"
        )
        return base
    return _algebra_structure_view(target, structure_map)


def _engine_algebra_morphism_from_generator_images(domain, codomain, generator_images):
    r"""Realize a framed owned algebra map in Sage when both engines exist.

    This is a private bridge boundary.  The mathematical datum is the owned
    generator map; Sage receives only engine endpoints and engine elements.
    """
    engine_domain = _engine_ring(domain)
    engine_codomain = _engine_ring(codomain)
    assert engine_domain in SageRings() and engine_codomain in SageRings(), (
        f"a morphism {domain} -> {codomain} given by generator images is computed only between rings "
        "Sage can compute with"
    )
    labels = domain.algebra_generating_set()
    assert labels.cardinality().is_finite(), (
        f"a morphism out of {domain} given by generator images needs finitely many algebra generators, "
        f"but it has {labels.cardinality()}"
    )

    base = domain.base_ring()
    engine_base = _engine_ring(base)
    target_structure = codomain.algebra_structure_morphism()

    def engine_base_image(scalar):
        owned_scalar = _owned_engine_element(base, engine_base(scalar))
        return _engine_element(codomain, target_structure(owned_scalar))

    if codomain is base and engine_codomain is engine_base:
        # An R-algebra morphism A -> R is over the literal identity of R.
        # Keep that theorem visible to Sage's quotient-Hom verifier instead of
        # wrapping id_R as an opaque set map whose multiplicativity Sage cannot
        # certify when checking the defining relations.
        base_map = engine_base.hom(engine_base)
    else:
        native_base_map = engine_codomain.coerce_map_from(engine_base)
        # Sanctioned foreign-engine capability probe at this private bridge:
        # absence uses the owned base map; failures from a present API propagate.
        engine_generators = getattr(engine_base, "gens", None)
        if native_base_map is not None and callable(engine_generators):
            determining_scalars = (
                engine_base.one(),
                *tuple(engine_generators()),
            )
            native_matches_owned = all(
                native_base_map(scalar) == engine_base_image(scalar)
                for scalar in determining_scalars
            )
        else:
            native_matches_owned = False
        base_map = (
            native_base_map
            if native_matches_owned
            else SetMorphism(
                engine_base.Hom(engine_codomain),
                engine_base_image,
            )
        )
    engine_generator_images = {label: _engine_element(codomain, codomain(image)) for label, image in generator_images.items()}

    from sage_extensions.categories.algebras.restricted_scalars import (
        RestrictedScalarsAlgebras,
    )

    if domain in RestrictedScalarsAlgebras(base):
        scalar_labels = tuple(domain.restricted_scalar_generator_labels())
        algebra_labels = tuple(domain.restricted_algebra_generator_labels())
        extension_engine = _engine_ring(domain.extension_ring())
        extension_map = _engine_morphism_from_generator_images(
            extension_engine,
            engine_codomain,
            [engine_generator_images[labels(0, label)] for label in scalar_labels],
            base_map,
        )
        return _engine_morphism_from_generator_images(
            engine_domain,
            engine_codomain,
            [engine_generator_images[labels(1, label)] for label in algebra_labels],
            extension_map,
        )

    if domain in AlgebrasWithChosenFinitePresentation(base):
        engine_labels = tuple(engine_domain.gens())
        selected_size = int(labels.cardinality().finite_value())
        if engine_labels and len(engine_labels) != selected_size:
            # A maintained private realization may introduce coefficient or
            # inverse variables that are not algebra generators of the owned
            # presentation.  Recover the image of each such engine generator
            # by lifting it through the selected presentation and evaluating
            # that lift under the actual R-algebra map.  This preserves the
            # chosen presentation while supplying Sage the complete generator
            # family its quotient engine requires.
            presentation = domain.presentation_ring()
            presentation_engine = _engine_ring(presentation)
            presentation_map = _engine_morphism_from_generator_images(
                presentation_engine,
                engine_codomain,
                [engine_generator_images[label] for label in labels],
                base_map,
            )
            private_images = []
            for engine_generator in engine_labels:
                owned_generator = _owned_engine_element(domain, engine_generator)
                selected_lift = domain.lift_to_presentation(owned_generator)
                private_images.append(presentation_map(_engine_element(presentation, selected_lift)))
            return engine_domain.hom(
                private_images,
                engine_codomain,
            )

    return _engine_morphism_from_generator_images(
        engine_domain,
        engine_codomain,
        [engine_generator_images[label] for label in labels],
        base_map,
    )


def _engine_algebra_morphism(morphism):
    r"""Return a private Sage realization of an owned algebra morphism.

    Bridge consumers such as affine ``Spec`` use this function.  It is not a
    public method on the mathematical morphism.
    """
    domain = morphism.domain()
    if not domain.is_framed_algebra():
        return morphism._engine_morphism_crossing()
    assert domain.is_framed_algebra(), (
        f"cannot compute with the algebra morphism {morphism}: its domain {domain} has no chosen "
        "algebra generators"
    )
    images = {label: morphism(domain.algebra_generator(label)) for label in domain.algebra_generating_set()}
    return _engine_algebra_morphism_from_generator_images(domain, morphism.codomain(), images)


def _engine_morphism_from_generator_images(engine_domain, engine_codomain, images, base_map):
    r"""Construct a native Sage ring morphism at the engine boundary."""
    assert engine_domain in SageRings() and engine_codomain in SageRings(), (
        f"a ring morphism given by generator images needs rings Sage can compute with, but got "
        f"{engine_domain} and {engine_codomain}"
    )
    return engine_domain.hom(
        [engine_codomain(image) for image in images],
        engine_codomain,
        base_map=base_map,
    )


__all__ = [
    "AlgebraMor",
    "AlgebraMorphism",
    "Algebras",
    "AlgebrasWithChosenFinitePresentation",
    "CommutativeAlgebraCoproducts",
    "CommutativeAlgebraPushouts",
    "FinitelyPresentedAlgebras",
    "MatrixAlgebras",
    "MultiplicativeAlgebraMor",
    "UnitalMultiplicativeAlgebraMor",
]
