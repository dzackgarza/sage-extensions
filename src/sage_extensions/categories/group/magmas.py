"""The owned operation spine below groups."""

from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_function, cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _compose_operation_preserving_mor,
)
from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoryPacketMethods,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.refine import RealizationHook
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class MagmaMorphism:
    r"""A map preserving the selected binary operation."""

    def __init__(self, parent, function) -> None:
        if not callable(function):
            raise TypeError(
                f"cannot build a morphism in {parent} from {function}: an operation-preserving "
                "morphism is given by a map on elements"
            )
        self._function = function
        super().__init__(parent, function)

    def _composition(self, right):
        return _compose_operation_preserving_mor(self, right, super()._composition)

    @RealizationHook
    def _multiplicativity_decision(self):
        r"""Supply the decision of the admitted multiplication-preservation law.

        Protected predicate contract under OWN-05. The sole caller is
        ``is_multiplicative``. A realization may derive the law from its
        construction or decide its defining equations. The default checks
        every pair in a finite enumerated source, and otherwise retains the
        proposition; admission to this Mor alone is not a computation of
        that proposition.
        """
        from sage_extensions.categories.sets.set_categories import EnumeratedSets, FiniteSets
        from sage_extensions.logic import AtomicProposition, conjunction

        domain = self.domain()
        if domain in FiniteSets() and domain in EnumeratedSets():
            return conjunction(
                self(left * right) == self(left) * self(right)
                for left in domain for right in domain
            )
        return AtomicProposition("is_multiplicative", self)

    @cached_method
    def is_multiplicative(self):
        r"""Return the decision or proposition that ``f(x*y) == f(x)*f(y)``.

        The map-on-elements datum states this law as its admission premise.
        This diagnostic can establish it, refute it, or leave it undecided;
        no addition, scalar action, associativity or unit is required.
        """
        return self._multiplicativity_decision()

    @validator
    def validate_multiplicativity(self) -> None:
        r"""Raise ``ValueError`` only when multiplication preservation is false.

        An undecided owned proposition remains the stated admission premise
        under OWN-22; validation does not turn it into a Boolean proof.
        """
        if self.is_multiplicative() is False:
            raise ValueError(
                f"{self} does not preserve the multiplication from {self.domain()} "
                f"to {self.codomain()}: f(x*y) != f(x)*f(y)"
            )

    @RealizationHook
    def _center_corestriction(self):
        r"""Supply the represented factor through the codomain's centre.

        Protected construction contract under OWN-05. The sole caller is
        ``corestrict_to_center``. A stronger arrow owner may compute a centre
        inclusion and the unique multiplication-preserving factor through it,
        or reject a decided noncentral image. When the selected centre is
        already the codomain, the original arrow is exactly that factor.
        """
        codomain = self.codomain()
        match codomain.center() is codomain:
            case True:
                return self
            case False:
                assert False, (
                    f"corestricting {self} to the centre of {codomain} needs "
                    "a selected central-image decision and a lift through "
                    "the centre inclusion"
                )

    def corestrict_to_center(self):
        r"""Factor this magma map through a represented centre of its codomain.

        This factor exists exactly when the image is central, and is unique
        because the centre inclusion is injective. Its defining triangle
        preserves multiplication without needing addition or a unit.
        """
        return self._center_corestriction()


class MagmaMor(CategoricalMor):
    r"""The fixed Mor category of operation-preserving magma maps."""

    ElementMethods = MagmaMorphism

    def _element_constructor_(self, function):
        if isinstance(function, Map):
            if function.domain() is not self.domain() or function.codomain() is not self.codomain():
                raise ValueError(
                    f"{function} is a morphism {function.domain()} -> {function.codomain()}, "
                    f"not a morphism {self.domain()} -> {self.codomain()}"
                )
            if function.parent() is self:
                return function
            raise TypeError(f"{function} belongs to another Mor; apply the functor between the categories")
        if not callable(function):
            raise TypeError(
                f"a morphism {self.domain()} -> {self.codomain()} needs a map on elements, "
                f"but got {function!r}"
            )
        return self.element_class(self, function)

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism {self.domain()} -> {self.codomain()}: the endpoints differ"
            )
        return self(lambda element: element)


class MagmaMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return MagmaMor


class UnitalMagmaMor(MagmaMor):
    r"""Maps preserving the selected binary law and its two-sided unit.

    The inherited map-on-elements constructor takes these two laws as its
    defining premises: ``f(x * y) = f(x) * f(y)`` and ``f(1) = 1``.
    It does not dynamically test them. Identity and composition preserve
    both laws and reuse the existing magma-map implementation. An already
    represented arrow is reused only through this stronger fixed-Mor graph.
    Constructing a new arrow from callable or typed-map data declares the
    target theory's laws as caller premises; it does not place the original
    weaker arrow in this Mor or infer unit preservation from multiplication.
    """


class UnitalMagmaMorCategoryConstruction(MorCategoryConstruction):
    r"""The fixed-endpoint Mor categories of owned unital magmas."""

    def fixed_category_class(self):
        return UnitalMagmaMor


class Magmas(CategoryPacketMethods, OwnedCategory):
    _MorCategory = MagmaMorCategoryConstruction

    def an_object(self):
        r"""The owned integers under multiplication."""
        from sage.rings.integer_ring import ZZ as SageZZ

        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        return _owned_integers()

    def super_categories(self):
        from sage_extensions.categories.sets.set_categories import Sets

        return [Sets()]

    class ElementMethods:
        @RealizationHook
        def _squareness_decision(self):
            r"""Return whether this element is a square in its exact parent.

            Protected predicate contract under OWN-05. ``is_square`` is the
            sole caller. An element realization may supply True, False, or
            an owned proposition for the existence of a root ``y`` in the
            same parent with ``y * y == self``. The default preserves that
            proposition without selecting a root or requiring associativity.
            """
            from sage_extensions.logic import AtomicProposition

            return AtomicProposition("is_square", self)

        def is_square(self):
            r"""Return the proposition ``exists y in this magma: y * y == self``."""
            return self._squareness_decision()

        @abstract_method
        def _mul_(self, other):
            r"""Return the value of the selected magma law on ``(self, other)``.

            ``other`` has the parent of ``self``.  ``x * y`` reaches this
            through Sage's ``Element.__mul__``, which coerces both operands
            into one parent first; an element supplies the law here, never by
            overriding the operator.
            """

        @RealizationHook
        def _regularity_decision(self):
            r"""Protected decision of two-sided cancellation by this element.

            Only is_regular calls this hook. An owned element realization or
            a more specific category may return a Boolean or the proposition
            that both translations by this element are injective. Absence of
            a decision leaves that proposition undecided.
            """
            from sage_extensions.logic import AtomicProposition

            return AtomicProposition("is_regular", self)

        def is_regular(self):
            r"""Return whether left and right multiplication are injective.

            For this element x, regularity means that xy = xz implies y = z
            and yx = zx implies y = z for all y and z in this magma. Only the
            selected multiplication and equality are needed; associativity,
            a unit, addition and commutativity are unnecessary.

            Definition: Mathlib Algebra/Regular/Defs, IsRegular.
            """
            return self._regularity_decision()

    class ParentMethods:
        def product(self, left, right):
            r"""Evaluate this magma's selected binary law on two elements."""
            return self(left) * self(right)

        @RealizationHook
        @cached_method
        def _center_construction(self):
            r"""Supply the centre and its exact inclusion as a retained pair.

            Protected construction contract under OWN-05. The only callers
            are ``center`` and ``center_inclusion``. A realization or stronger
            category supplies ``(Z, i)`` with the induced magma law on Z and
            a multiplication-preserving injection ``i: Z -> self``. Its image
            consists exactly of the elements commuting with every element
            and lying in the nucleus. The cached pair keeps both public
            operations on the same selected centre and inclusion.
            """
            assert False, (
                f"the centre of {self} needs a selected construction of the "
                "elements satisfying commutation and the left and right "
                "associator equations, together with their magma inclusion"
            )

        def center(self):
            r"""Return this magma's centre with its induced multiplication.

            An element z is central when, for every x and y,
            ``z*x == x*z``, ``(z*x)*y == z*(x*y)``, and
            ``(x*y)*z == x*(y*z)``. These equations also imply
            ``(x*z)*y == x*(z*y)``. Thus the centre is the commutant
            intersected with the nucleus; associativity and commutativity
            hold on its induced multiplication. No unit or ambient
            associativity is required (Mathlib ``Algebra.Group.Center``,
            ``Set.IsMulCentral``).
            """
            return self._center_construction()[0]

        def center_inclusion(self):
            r"""Return the selected magma inclusion ``center() -> self``."""
            return self._center_construction()[1]

        @RealizationHook
        def _commutativity_decision(self):
            r"""Supply whether the selected binary law is commutative.

            Protected predicate contract under OWN-05. The callers are
            ``is_commutative`` and ``Modules.super_categories`` when the
            latter reads a native owned ring before selecting its module
            refinement. A parent realization may return True, False,
            or the owned proposition that ``x * y == y * x`` for every pair
            in this magma. The default retains the undecided proposition.
            """
            from sage_extensions.logic import AtomicProposition

            return AtomicProposition("is_commutative", self)

        def is_commutative(self):
            r"""Return whether the magma law satisfies ``xy = yx`` for all elements."""
            if self in Magmas().Commutative():
                return True
            return self._commutativity_decision()

        @RealizationHook
        def _finite_magma_generation_decision(self):
            r"""Supply finite generation for this selected binary law.

            Only ``is_finitely_generated_as_magma`` calls this hook. A
            realization or stronger owner may decide whether some finite
            subset generates under multiplication, or retain that
            proposition. This does not select a generating family.
            """
            from sage_extensions.logic import AtomicProposition

            return AtomicProposition("is_finitely_generated_as_magma", self)

        def is_finitely_generated_as_magma(self):
            r"""Whether some finite subset generates under the binary law.

            Every finite magma is generated by its whole underlying set;
            this existence assertion requires no selected enumeration or
            equality decisions. The qualification distinguishes it from
            generation as a module, algebra or other additional structure.
            """
            if self in Magmas().FinitelyGeneratedAsMagma() or self.is_finite() is True:
                return True
            return self._finite_magma_generation_decision()

    class SubcategoryMethods:
        def Subobjects(self, base_object):
            r"""Return represented structured subobjects of ``base_object``.

            A submagma remains a magma equipped with its chosen monomorphism
            into the fixed object.  It therefore uses the generic structured
            subobject category rather than the set-specific slice realization
            inherited from ``Sets``.
            """
            from sage_extensions.categories.abstract_categories.arrow_categories import (
                SubobjectCategory,
            )

            return SubobjectCategory(self, base_object)

        def Commutative(self):
            r"""Return this category with the axiom ``xy = yx``.

            Commutativity is a property of the operation, so it is stated once
            here, at the level that introduces the operation, and every
            subcategory reaches it.
            """
            return self._with_axiom("Commutative")

        def Unital(self):
            r"""Return this category with a two-sided unit for its multiplication.

            ``lean-categories``: ``LeanCategories.Algebra.unital``, the
            classifier ``UnitalMagma -> MagmaCat`` on magmas
            (``Algebra/Concrete/Magmas.lean``).
            """
            return self._with_axiom("Unital")

        def FinitelyGeneratedAsMagma(self):
            r"""Return this category with the existence of a finite magma generating set."""
            return self._with_axiom("FinitelyGeneratedAsMagma")

    class FinitelyGeneratedAsMagma(CategoryWithAxiom):
        r"""Magmas generated under their binary law by some finite subset.

        This is an existence property, without a selected generating
        family. Its arrows remain the inherited magma maps. Stronger
        owners may retain their own finite-generation presentations.
        """

        def an_object(self):
            r"""The two-element cyclic group, whose whole finite set generates its magma."""
            from sage_extensions.categories.group.groups import OwnedGroups

            return OwnedGroups().C(2)

        @classmethod
        def _repr_object_names(cls):
            return "finitely generated magmas"

    class Commutative(CategoryWithAxiom):
        r"""Magmas whose law satisfies ``xy = yx``.

        The axiom is implemented here, at the level that introduces the law.
        ``Category._with_axiom_as_tuple`` (``sage/categories/category.py``)
        returns the category itself for an axiom no class on its path
        implements, so without this class ``Magmas().Commutative()`` would be
        ``Magmas()`` and every magma would be a commutative magma.  Sage then
        joins this class into the supercategories of every category with the
        ``Commutative`` axiom whose path reaches ``Magmas()``: commutative
        rings, commutative algebras and abelian groups are commutative magmas
        through it.
        """

        def an_object(self):
            r"""The owned integers under multiplication."""
            return Magmas().an_object()

        @classmethod
        def _repr_object_names(cls):
            return "commutative magmas"

    class Unital(CategoryWithAxiom):
        r"""Unital magmas: a magma ``(M, *)`` with an element ``1`` with ``1 * x = x = x * 1``.

        ``lean-categories``: ``UnitalMagma`` (``Algebra/Concrete/Magmas.lean``).
        The unit is introduced at this level, so its contract is stated here:
        monoids and unital algebras are unital magmas and supply it.

        Its arrows preserve both the multiplication and the unit. Mere
        multiplication preservation would also admit maps such as the
        constant-zero endomap of the multiplicative integers.
        """

        _MorCategory = UnitalMagmaMorCategoryConstruction

        @classmethod
        def _repr_object_names(cls):
            return "unital magmas"

        class ParentMethods:
            @abstract_method
            def one(self):
                r"""Return the two-sided unit of this magma."""

        class ElementMethods:
            def is_one(self):
                r"""Whether this element is the two-sided unit ``1`` of its magma."""
                return self == self.parent().one()

            @RealizationHook
            def _unit_decision(self):
                r"""Supply the existence of a two-sided inverse in this magma.

                Protected predicate contract under OWN-05. Only is_unit
                calls this hook. A more specific category or realization
                may return a Boolean or the owned proposition
                ``exists y: self * y == 1 and y * self == 1`` in this exact
                parent. This does not select an inverse or assert uniqueness.
                An undecided proposition is not a negative answer.
                """
                from sage_extensions.logic import AtomicProposition

                return AtomicProposition("is_unit", self)

            def is_unit(self):
                r"""Return whether some ``y`` satisfies ``xy = 1 = yx``.

                For monoids this is Mathlib's IsUnit by isUnit_iff_exists.
                The same existential predicate needs no associativity, but
                uniqueness of an inverse and the group of units do.
                """
                if (self == self.parent().one()) is True:
                    return True
                return self._unit_decision()


class MonoidMorCategoryConstruction(MorCategoryConstruction):
    r"""The fixed-endpoint Mor categories of owned monoids."""

    def fixed_category_class(self):
        return MonoidMor


class Semigroups(CategoryPacketMethods, OwnedCategory):
    _MorCategory = MagmaMorCategoryConstruction

    def an_object(self):
        return Magmas().an_object()

    def super_categories(self):
        return [Magmas()]


class Monoids(CategoryPacketMethods, OwnedCategory):
    def an_object(self):
        return Magmas().an_object()

    def super_categories(self):
        r"""A monoid is a semigroup whose magma is unital (Mathlib ``Monoid.toMulOneClass``)."""
        return [Semigroups(), Magmas().Unital()]

    def unit_group(self):
        r"""Return ``M |-> M^x : Mon -> Grp``."""
        return UnitGroupFunctor()

    class ElementMethods:
        @RealizationHook
        def _unit_inverse_decision(self):
            r"""Protected computation of the inverse in this exact monoid.

            Only inverse_of_unit calls this hook. An owned element realization
            or a more specific category returns the owned two-sided inverse in
            the same parent, or None when it supplies no computation. It raises
            ZeroDivisionError only for an established nonunit. Computing an
            inverse need not require a separately decidable unit predicate.
            An applied procedure may propagate its explicit unresolved-
            computation error; that does not establish that the element is a
            nonunit.
            """
            return None

        def inverse_of_unit(self):
            r"""Return the unique two-sided inverse of this monoid unit."""
            inverse = self._unit_inverse_decision()
            assert inverse is not None, (
                f"no inverse computation is available for {self} in its ambient monoid {self.parent()}"
            )
            return inverse

        def divide_by_unit(self, other):
            r"""Return the right quotient by a unit in the same ambient monoid."""
            return self * self.parent()(other).inverse_of_unit()

        def _pow_int(self, exponent):
            r"""Integer powers by repeated squaring, from the monoid law."""
            from sage.arith.power import generic_power

            return generic_power(self, exponent)

    class ParentMethods:
        def _emptiness_decision(self) -> bool:
            r"""A monoid is not empty: it contains its unit (``Sets``' emptiness hook)."""
            return False

        @cached_method
        def unit_group(self):
            r"""Return the group of two-sided units of this exact monoid."""
            return _unit_group(self)

        def generated_submonoid(
            self, generators, *, description=None, structure_data=None
        ):
            r"""Return the represented submonoid generated by ``generators``."""
            from sage_extensions.categories.group.submonoids import (
                _generated_submonoid,
            )

            return _generated_submonoid(
                self,
                generators,
                description=description,
                structure_data=structure_data,
            )

        def predicate_submonoid(
            self, predicate, description, *, placements=(), structure_data=None
        ):
            r"""Return the represented submonoid cut out by ``predicate``.

            The caller supplies the mathematical premises that its truth set
            contains the identity and is closed under multiplication. The
            predicate is defined on this ambient monoid; its values may be
            undecided owned propositions. The constructor retains this datum
            and rejects a proved failure at the identity, without claiming
            that a one-point check establishes the submonoid laws.

            A specialized construction may supply theorem-backed stronger
            ``placements``; they are part of the object's category at
            construction rather than a later refinement.
            """
            from sage_extensions.categories.group.submonoids import (
                _predicate_submonoid,
            )

            return _predicate_submonoid(
                self,
                predicate,
                description,
                placements=placements,
                structure_data=structure_data,
            )

    _MorCategory = MonoidMorCategoryConstruction

    def Mor(self, domain, codomain):
        if domain not in self or codomain not in self:
            raise TypeError(
                f"cannot form Mor({domain}, {codomain}) in {self}: the domain and the "
                f"codomain must both be monoids"
            )
        return self.MorCategory().Of(domain, codomain)

    class Commutative(CategoryWithAxiom):
        r"""Commutative monoids, the existing associative, unital, commutative meet."""

        @classmethod
        def _repr_object_names(cls):
            return "commutative monoids"

        def an_object(self):
            r"""The multiplicative group of the two units of the integers."""
            return Monoids().an_object().unit_group()

        @cached_method
        def square_class_group(self):
            r"""Return ``M |-> M^x/(M^x)^2 : CMon -> Grp``."""
            from sage_extensions.categories.rings.square_classes import (
                SquareClassGroupFunctor,
            )

            return SquareClassGroupFunctor()

        class ParentMethods:
            @cached_method
            def square_class_group(self):
                r"""Return the cokernel of squaring on this monoid's unit group.

                The units of a commutative monoid form an abelian group, so
                their squares are a subgroup. No additive law is needed.
                """
                from sage_extensions.categories.rings.square_classes import (
                    _square_class_group,
                )

                return _square_class_group(self)


class AdditiveMagmas(CategoryPacketMethods, OwnedCategory):
    class _MorCategory(MorCategoryConstruction):
        def fixed_category_class(self):
            from sage_extensions.categories.group.additive_mors import (
                AdditiveMagmaMor,
            )

            return AdditiveMagmaMor

    def an_object(self):
        r"""The owned integers under addition."""
        from sage.rings.integer_ring import ZZ as SageZZ

        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        return _owned_integers()

    def super_categories(self):
        from sage_extensions.categories.sets.set_categories import Sets

        return [Sets()]

    class ElementMethods:
        @abstract_method
        def __add__(self, other):
            r"""Return the value of the selected additive magma law on ``(self, other)``."""

    class SubcategoryMethods:
        def AdditiveCommutative(self):
            r"""Return this category with the axiom ``x + y = y + x``."""
            return self._with_axiom("AdditiveCommutative")

    class AdditiveCommutative(CategoryWithAxiom):
        r"""Additive magmas whose law satisfies ``x + y = y + x``.

        The axiom is implemented here, at the level that introduces the
        additive law.  ``Category._with_axiom_as_tuple``
        (``sage/categories/category.py``) returns the category itself for an
        axiom no class on its path implements, so without this class
        ``AdditiveMagmas().AdditiveCommutative()`` would be
        ``AdditiveMagmas()`` and every additive magma, semigroup and monoid
        would be additively commutative.  Sage joins this class into the
        supercategories of every category with the ``AdditiveCommutative``
        axiom whose path reaches ``AdditiveMagmas()``.
        """

        def an_object(self):
            r"""The owned integers under addition."""
            return AdditiveMagmas().an_object()

        @classmethod
        def _repr_object_names(cls):
            return "additive commutative magmas"


class AdditiveSemigroups(CategoryPacketMethods, OwnedCategory):
    class _MorCategory(MorCategoryConstruction):
        def fixed_category_class(self):
            from sage_extensions.categories.group.additive_mors import (
                AdditiveMagmaMor,
            )

            return AdditiveMagmaMor

    def an_object(self):
        return AdditiveMagmas().an_object()

    def super_categories(self):
        return [AdditiveMagmas()]


class AdditiveMonoids(CategoryPacketMethods, OwnedCategory):
    class _MorCategory(MorCategoryConstruction):
        def fixed_category_class(self):
            from sage_extensions.categories.group.additive_mors import (
                AdditiveMonoidMor,
            )

            return AdditiveMonoidMor

    def an_object(self):
        return AdditiveMagmas().an_object()

    def super_categories(self):
        return [AdditiveSemigroups()]

    class ParentMethods:
        def _emptiness_decision(self) -> bool:
            r"""An additive monoid is not empty: it contains its zero (``Sets``' emptiness hook)."""
            return False

        @abstract_method
        def zero(self):
            r"""Return the identity element for the additive monoid law."""

        def monoidal_unit(self):
            return self.zero()

        def additive_submonoid(self, generators, *, description=None):
            r"""Return the additive submonoid generated by a chosen finite family.

            The empty sum is zero. The family retains its index labels and
            all chosen values; equal or undecidably equal values are not
            deduplicated. Membership beyond the supplied generators is a
            computation question, with a finite coefficient solver on NN.
            """
            from sage_extensions.categories.group.submonoids import _additive_submonoid

            return _additive_submonoid(self, generators=generators, description=description)

        def predicate_additive_submonoid(self, predicate, description):
            r"""Return the additive submonoid defined by a zero- and sum-closed predicate.

            The caller supplies those two laws as construction premises.
            A decided failure at zero is rejected; an undecided value remains
            the defining proposition. The exact predicate and ambient are
            retained, with their actual additive inclusion.
            """
            from sage_extensions.categories.group.submonoids import _additive_submonoid

            return _additive_submonoid(self, predicate=predicate, description=description)


class AdditiveGroups(CategoryPacketMethods, OwnedCategory):
    class _MorCategory(MorCategoryConstruction):
        def fixed_category_class(self):
            from sage_extensions.categories.group.additive_mors import (
                AdditiveMonoidMor,
            )

            return AdditiveMonoidMor

    def an_object(self):
        r"""The additive group of the owned integers."""
        from sage.rings.integer_ring import ZZ as SageZZ

        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )

        return _owned_integers()

    def super_categories(self):
        return [AdditiveMonoids()]

    class ParentMethods:
        def multiplicative_group_identification(self):
            r"""Return the set isomorphism ``a |-> exp(a)`` with ``exp(a+b)=exp(a)exp(b)``.

            Multiplicative notation exists for every additive group.  The
            selected GroupExp realization requires commutative addition.
            """
            match self:
                case _ if self in AdditiveGroups().AdditiveCommutative():
                    from sage_extensions.categories.group.groups import (
                        _additive_group_exponential,
                    )

                    return _additive_group_exponential(self)
                case _:
                    assert False, (
                        "multiplicative_group_identification cannot be computed: "
                        "no realization is selected for this additive group; "
                        "the available GroupExp realization requires commutative addition"
                    )

        def multiplicative_group(self):
            r"""Return this additive group written multiplicatively."""
            return self.multiplicative_group_identification().codomain()

    class ElementMethods:
        def _sub_(self, other):
            r"""The right difference, from addition and the additive inverse."""
            return self + (-other)

    class AdditiveCommutative(CategoryWithAxiom):
        """Additive groups whose addition is commutative."""

        class _MorCategory(MorCategoryConstruction):
            def fixed_category_class(self):
                from sage_extensions.categories.group.additive_mors import (
                    AdditiveMor,
                )

                return AdditiveMor

        @classmethod
        def _repr_object_names(cls):
            return "commutative additive groups"


class MonoidMorphism:
    """A morphism in the owned category of monoids.

    The inclusion ``S -> M`` of a submonoid sends ``s`` to ``s``.  Its
    construction gives two premises, which are stored and never checked:
    the arrow is injective (``injectivity_decision``), and its image is the
    domain ``S`` itself (``submonoid_of_codomain``).
    """

    def __init__(self, parent, function, *, injectivity_decision=None, submonoid_of_codomain=False) -> None:
        self._injectivity_premise = injectivity_decision
        self._submonoid_premise = submonoid_of_codomain
        super().__init__(parent, function)

    def is_injective(self):
        assert self._injectivity_premise is not None, (
            f"whether {self} is injective is defined for every monoid morphism, but the current "
            "preamble answers it only for the inclusion of a submonoid"
        )
        return self._injectivity_premise

    def image(self):
        r"""``f(S)``; the image of the inclusion of a submonoid ``S`` is ``S``."""
        assert self._submonoid_premise, (
            f"the image of {self} is defined for every monoid morphism, but the current preamble "
            "constructs it only for the inclusion of a submonoid"
        )
        return self.domain()

    def factor_through_or_none(self, target_inclusion):
        r"""The factor ``k`` with ``n . k = m`` of this inclusion ``m`` through ``n``, or None.

        It exists exactly when the image of ``m`` lies in the image of
        ``n``; containment is decided on the monoid generators of the
        domain.
        """
        if target_inclusion.codomain() is not self.codomain():
            raise ValueError(
                f"cannot factor {self} through {target_inclusion}: their codomains {self.codomain()} "
                f"and {target_inclusion.codomain()} differ"
            )
        source = self.domain()
        target = target_inclusion.domain()
        if target_inclusion is self:
            return Monoids().Mor(source, source).identity()
        from sage_extensions.categories.group.submonoids import _submonoid_generator_containment

        contained = _submonoid_generator_containment(self, target_inclusion, source.monoid_generators())
        if contained is False:
            return None
        assert contained is True, (
            f"cannot factor {self} through {target_inclusion}: containment of the chosen monoid "
            "generators remains undecided"
        )
        return Monoids().Mor(source, target)(lambda element: target(self(element)))

    def factor_through(self, target_inclusion):
        factor = self.factor_through_or_none(target_inclusion)
        if factor is None:
            raise ValueError(
                f"{self} does not factor through {target_inclusion}: some monoid generator of "
                f"{self.domain()} does not map into {target_inclusion.domain()}"
            )
        return factor


class MonoidMor(CategoricalMor):
    r"""The owned fixed Mor category ``Mor_Mon(A,B)``."""

    ElementMethods = MonoidMorphism

    def __init__(self, family, domain, codomain) -> None:
        super().__init__(family, domain, codomain)

    def _element_constructor_(self, function):
        if isinstance(function, Map):
            if function.domain() is not self.domain() or function.codomain() is not self.codomain():
                raise ValueError(
                    f"{function} is a monoid morphism {function.domain()} -> "
                    f"{function.codomain()}, not a morphism {self.domain()} -> {self.codomain()}"
                )
            if function.parent() is self:
                return function
            raise TypeError(f"{function} belongs to another Mor; apply the functor between the categories")
        return self.element_class(self, function)

    @cached_method
    def _from_submonoid_inclusion(self):
        r"""The inclusion ``S -> M`` of the domain, a submonoid of the codomain, sending ``s`` to ``s``.

        The construction gives the arrow's injectivity and its image ``S``
        as premises; neither is checked.
        """
        return self.element_class(
            self,
            lambda element: element,
            injectivity_decision=True,
            submonoid_of_codomain=True,
        )

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism {self.domain()} -> {self.codomain()}: an "
                f"identity exists only when the domain and codomain are the same monoid"
            )
        return self(lambda element: element)


@cached_function(key=lambda monoid: id(monoid))
def _unit_group(monoid):
    r"""Return the existing predicate submonoid of two-sided units of ``monoid``.

    Protected constructor under OWN-05. ``Monoids.ParentMethods.unit_group``
    supplies the owned monoid. Its units contain one, are closed under
    products, and have inverses within the same monoid; these are the premises
    of the group placement. A commutative ambient monoid supplies the abelian
    placement too. The facade and its literal ambient inclusion are retained.

    A facade element can belong to a larger monoid as well. Its element-level
    unit decision is used only for its literal parent; otherwise an undecided
    proposition refers to the selected monoid. This does not confuse a unit
    in a larger ambient monoid with a unit of this submonoid.
    """
    from sage.structure.element import parent

    from sage_extensions.categories.group.groups import AbelianGroups, OwnedGroups
    from sage_extensions.logic import AtomicProposition

    assert monoid in Monoids(), (
        f"the unit group needs an owned monoid, but {monoid!r} is not one"
    )

    def unit_predicate(element):
        if monoid in OwnedGroups() or (element == monoid.one()) is True:
            return True
        if parent(element) is monoid:
            return element.is_unit()
        return AtomicProposition("is_unit", monoid, element)

    placement = (
        AbelianGroups() if monoid in Monoids().Commutative() else OwnedGroups()
    )
    return Monoids.ParentMethods.predicate_submonoid(
        monoid,
        unit_predicate,
        f"{monoid}^×",
        placements=(placement,),
    )


class _UnitGroupMorphism:
    r"""The restriction of one retained monoid arrow to its unit groups.

    Private realization at the existing GroupMor owner. UnitGroupFunctor
    supplies the actual monoid arrow and its literal unit-group endpoints.
    For an admitted source unit, the image is a target unit by preservation
    of multiplication and one. Its facade representative is therefore
    already the output; re-admitting it through an undecided target unit
    predicate would discard the premise of this restriction construction.
    """

    def __init__(self, parent, monoid_morphism):
        assert parent.domain().ambient_monoid() is monoid_morphism.domain(), (
            "the unit-map source must be the retained source monoid's unit group"
        )
        assert parent.codomain().ambient_monoid() is monoid_morphism.codomain(), (
            "the unit-map target must be the retained target monoid's unit group"
        )
        self._monoid_morphism = monoid_morphism
        super().__init__(parent, monoid_morphism)

    def __call__(self, unit):
        r"""Apply the restriction to a unit of its declared source group.

        The fixed group-arrow input contract supplies source-unit membership.
        The retained monoid arrow performs the ordinary ambient ingress. A
        fresh source unit-group admission would discard this premise when
        ``unit`` is the image of an earlier induced unit map and its ambient
        unit predicate remains undecided.
        """
        return self._monoid_morphism(unit)

    def _composition(self, right):
        r"""Compose two restrictions through their retained monoid arrows."""
        if isinstance(right, _UnitGroupMorphism):
            return UnitGroupFunctor()(
                self._monoid_morphism * right._monoid_morphism
            )
        return super()._composition(right)


class UnitGroupFunctor(Functor):
    r"""Send a monoid to its units and a monoid map to its restriction.

    A map preserving products and one carries a two-sided inverse to a
    two-sided inverse. The restriction therefore lands in the target unit
    group without requiring another decision of the target unit predicate.
    Ring morphisms enter through their inherited monoid Mor, with their
    original endpoints and element map.
    """

    def __init__(self) -> None:
        from sage_extensions.categories.group.groups import OwnedGroups

        super().__init__(Monoids(), OwnedGroups())

    def _apply_object(self, monoid):
        return monoid.unit_group()

    def _apply_morphism(self, morphism):
        from sage_extensions.categories.group.groups import OwnedGroups

        source = self.object_image(morphism.domain())
        target = self.object_image(morphism.codomain())
        return OwnedGroups().Mor(source, target)._from_realization_engine(
            _UnitGroupMorphism, morphism
        )

    def _repr_(self):
        return "Unit group functor"
