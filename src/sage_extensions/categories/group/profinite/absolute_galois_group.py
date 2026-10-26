r"""The realized parent (G_K=\operatorname{Aut}_K(\bar K))."""

from typing import cast

from sage.categories.finite_fields import FiniteFields
from sage.categories.number_fields import NumberFields
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.unknown import Unknown
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.group.groups import OwnedGroups
from sage_extensions.categories.group.profinite.absolute_galois_groups import (
    AbsoluteGaloisGroups,
    AbsoluteGaloisGroupsOfFiniteFields,
    OpenAbsoluteGaloisSubgroups,
    _absolute_galois_group_category,
)
from sage_extensions.categories.group.profinite.galois_characters import (
    CyclotomicCharacter,
    QuadraticCharacter,
)
from sage_extensions.categories.group.profinite.galois_decomposition import (
    AbsoluteDecompositionGroup,
    AbsoluteInertiaGroup,
    DecompositionGroupConjugacyClass,
    FrobeniusConjugacyClass,
    InertiaGroupConjugacyClass,
)
from sage_extensions.categories.group.profinite.galois_quotient import (
    FiniteExtensionAutomorphismGroup,
    FiniteGaloisExtension,
    FiniteGaloisQuotient,
    LiftCoset,
    _galois_restriction_rule,
    _relative_degree,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    OwnedRings,
    RingMorphism,
    _engine_ring,
    _is_finite_or_number_field,
    _own_ring,
    _owned_engine_element,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.logic import AtomicProposition, Predicate, conjunction, negation
from sage_extensions.owned_category import _object_of
from sage_extensions.validation import validator


class AbsoluteGaloisGroupElement(Element):
    r"""A coherent, progressively realized automorphism of the chosen closure.

    A global exact map may be supplied directly.  A lift from a finite
    quotient instead starts with one exact finite coordinate; additional
    coordinates can be installed only after their compatibility is checked.
    A third datum is a stage rule: a function sending each finite Galois
    stage ``L`` on which it is defined to an element of ``Gal(L/K)``, with
    coherence of its values under restriction a premise of its caller.
    """

    def __init__(
        self,
        parent,
        *,
        exact_action: RingMorphism | None = None,
        coordinates=(),
        frobenius_exponent=None,
        stage_rule=None,
    ) -> None:
        Element.__init__(self, parent)
        self._exact_action = exact_action
        self._coordinates = list(coordinates)
        self._frobenius_exponent = (
            None if frobenius_exponent is None else ZZ(frobenius_exponent)
        )
        self._stage_rule = stage_rule
        self.validate_defining_datum(check=False)
        self.validate_base_fixing(check=False)

    @cached_method
    def as_morphism(self):
        field_endomorphisms = self.parent().field_automorphism_mor()
        if self._exact_action is not None:
            return field_endomorphisms(self._exact_action)
        if self._frobenius_exponent == 0:
            return field_endomorphisms.identity()
        return field_endomorphisms.elementwise(lambda element: self(element))

    def underlying_field_morphism(self, *args, **kwargs):
        return self.as_morphism(*args, **kwargs)

    def domain(self):
        return self.parent().algebraic_closure()

    def codomain(self):
        return self.parent().algebraic_closure()

    def exact_action(self):
        return self._exact_action

    def realized_stages(self):
        return finite_ordered_set(
            tuple(stage for stage, _coordinate in self._coordinates)
        )

    def restriction_coordinate(self, stage):
        if self._stage_rule is not None:
            return self._stage_rule(self.parent().extension_data(stage))
        for known_stage, coordinate in self._coordinates:
            if known_stage is stage:
                return coordinate
            if (
                known_stage.field() is stage.field()
                and known_stage.embedding() == stage.embedding()
            ):
                return coordinate
        return None

    def extend_coordinate(self, restriction_map, coordinate) -> None:
        r"""Install a higher finite coordinate after checking compatibility."""
        stage = restriction_map.extension()
        coordinate = restriction_map.codomain()(coordinate)
        for old_stage, old_coordinate in self._coordinates:
            if old_stage is stage:
                if old_coordinate != coordinate:
                    raise ValueError(
                        f"{self} already restricts to {old_coordinate} on {stage.field()}, "
                        f"not to {coordinate}"
                    )
                return
        if restriction_map(self) != coordinate:
            raise ValueError(
                f"{self} restricts to {restriction_map(self)} on {stage.field()}, "
                f"not to {coordinate}"
            )
        self._coordinates.append((stage, coordinate))

    def frobenius_exponent(self):
        if self._frobenius_exponent is None:
            return None
        return _owned_engine_element(ZZ, self._frobenius_exponent)

    def is_globally_evaluable(self) -> bool:
        return self._frobenius_exponent is not None or self._exact_action is not None

    def __call__(self, element):
        r"""Evaluate without forcing a finite-stage element through the closure facade."""
        return self._call_(element)

    def _call_(self, element):
        r"""Evaluate: a Frobenius power by its exponent, otherwise the exact action.

        An element given by its stage restrictions acts on ``Kbar`` through
        the stage containing the argument; that stage is named by
        ``restrict(stage)``, and evaluation away from a named stage is the
        assertion below.
        """
        if self._frobenius_exponent is not None:
            return self.parent()._finite_frobenius_image(
                element, self._frobenius_exponent
            )
        assert self._exact_action is not None, (
            f"evaluating {self} at {element} needs a finite Galois stage of "
            f"{self.parent().algebraic_closure()} containing {element}; this element is "
            f"given by its restrictions to finite stages, so restrict it to such a stage "
            f"first"
        )
        return self._exact_action(element)

    def fixes_base_field(self) -> bool | Predicate:
        r"""The equation ``sigma * e == e`` for the retained ``e: K -> Kbar``.

        This is a diagnostic of the admitted base-fixing premise. It uses
        the existing equality of field maps, whose selected finite
        determining data may decide the equation; otherwise the equation
        remains an owned proposition. No finite generator family is
        required of an arbitrary base field.
        """
        if self._stage_rule is not None:
            # Each value of the stage rule is an element of Gal(L/K), which
            # fixes K by construction of that quotient.
            return True
        parent = cast("_AbsoluteGaloisGroupEngine", self.parent())
        embedding = parent.base_embedding()
        return self.as_morphism() * embedding == embedding

    @validator
    def validate_defining_datum(self) -> None:
        r"""Reject a defining datum of the wrong kind (``OWN-22``: checked on request).

        One of an exact action in ``Mor(Kbar, Kbar)``, a ``q``-Frobenius
        exponent over a finite base field, or a stage rule is the datum.
        """
        parent = self.parent()
        if self._exact_action is None and self._frobenius_exponent is None and self._stage_rule is None:
            raise ValueError(
                f"an element of {parent} must be given as an automorphism of the "
                f"algebraic closure, as a power of Frobenius, or by its restrictions to "
                f"the finite Galois stages, but none was given"
            )
        if self._exact_action is not None and element_parent(self._exact_action) is not parent.field_automorphism_mor():
            raise ValueError(
                f"the exact action of an element of {parent} must lie in "
                f"{parent.field_automorphism_mor()}, but got {self._exact_action}"
            )
        if self._frobenius_exponent is not None and parent not in AbsoluteGaloisGroupsOfFiniteFields():
            raise ValueError(
                f"a q-Frobenius power requires a finite base field, but the base field "
                f"of {parent} is {parent.base_field()}"
            )

    @validator
    def validate_base_fixing(self) -> None:
        r"""Reject a proved failure of the admitted equation ``sigma e = e``.

        OWN-22 separates admission from checking, and unknown equations are
        retained. A ``K``-endomorphism of the algebraic extension ``Kbar/K``
        is an automorphism (Stacks, Lemma 9.8.11), so the base-fixing
        premise supplies the group law without an inverse computation at
        construction.
        """
        if self.fixes_base_field() is False:
            raise ValueError(
                f"{self.as_morphism()} does not fix the retained base embedding "
                f"{self.parent().base_embedding()} of {self.parent()}"
            )

    def restrict(self, stage):
        return self.parent().restriction_map(stage)(self)

    def _mul_(self, other):
        r"""``self ∘ other``; Sage's arithmetic calls this with one parent."""
        return self.parent()._compose_elements(self, other)

    def __invert__(self):
        return self.inverse()

    def inverse(self):
        return self.parent()._inverse_element(self)

    def __pow__(self, exponent):
        exponent = ZZ(exponent)
        if self._frobenius_exponent is not None:
            return FrobeniusElement(self.parent(), exponent * self._frobenius_exponent)
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = self.parent().one()
        factor = self
        while exponent:
            if exponent & 1:
                result = result * factor
            factor = factor * factor
            exponent >>= 1
        return result

    def conjugacy_class(self):
        return ElementConjugacyClass(self.parent(), self)

    def _richcmp_(self, other, op):
        r"""Compare two elements of one ``G_K``; Sage calls this with one parent.

        Only equality is defined: ``G_K`` carries no order.
        """
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        equal = self._same_automorphism(other)
        return equal if op == op_EQ else negation(equal)

    def _same_automorphism(self, other) -> bool | Predicate:
        r"""Whether ``self`` and ``other`` of the same parent are the same automorphism."""
        if self is other:
            return True
        if (
            self._frobenius_exponent is not None
            and other._frobenius_exponent is not None
        ):
            return self._frobenius_exponent == other._frobenius_exponent
        if self._stage_rule is not None or other._stage_rule is not None:
            # Agreement on finitely many stages does not decide equality in G_K.
            return AtomicProposition("equal_automorphisms", self, other)
        return self.as_morphism() == other.as_morphism()

    def __hash__(self) -> int:
        r"""Equal automorphisms can have different retained representations."""
        return hash(id(self.parent()))

    def _repr_(self) -> str:
        if self._frobenius_exponent is not None:
            parent = cast("_AbsoluteGaloisGroupEngine", self.parent())
            q = parent.base_field_order()
            return f"q-Frobenius^{self._frobenius_exponent} (q={q})"
        if self._exact_action is not None:
            return f"Element of {self.parent()} represented by {self._exact_action}"
        if self._stage_rule is not None:
            return f"Element of {self.parent()} given by its restrictions to finite Galois stages"
        fields = ", ".join(str(stage.field()) for stage, _ in self._coordinates)
        return f"Element of {self.parent()} realized on {fields}"


class FrobeniusElement(AbsoluteGaloisGroupElement):
    r"""An integral power of the canonical (q)-Frobenius."""

    def __init__(self, parent, exponent=1) -> None:
        super().__init__(parent, frobenius_exponent=ZZ(exponent))


class ArithmeticFrobeniusElement(AbsoluteGaloisGroupElement):
    r"""A Frobenius element of ``G_K`` at a prime ``p`` of a number field ``K`` and a chosen prolongation ``pbar``.

    Defining data: the base prime ``p`` and the prolongation ``pbar``, which
    assigns to each finite Galois stage ``L`` a prime of ``O_L`` above ``p``.
    At a stage unramified above ``p`` the restriction is the arithmetic
    Frobenius at the chosen prime (Mathlib ``IsArithFrobAt``,
    ``Mathlib/RingTheory/Frobenius.lean``; ``lean-categories``
    ``serreFrobeniusSubstitution``, ``LeanCategories/Algebra/ArithmeticFrobeniusData.lean``),
    which is unique there.  At a stage where ``p`` ramifies the restriction
    is a choice of inertia lift that this element does not retain, and asking
    for it asserts.
    """

    def __init__(self, parent, prime, prolongation) -> None:
        self._base_prime = prime
        self._prolongation = prolongation
        super().__init__(parent, stage_rule=self._frobenius_at_stage)

    def _frobenius_at_stage(self, stage):
        r"""The restriction to ``Gal(L/K)``.

        With a prolongation: the Frobenius at its prime of ``L``. Without one
        the element is a Frobenius at an unspecified prime of ``Kbar`` above
        ``p``, and its restriction is defined exactly when ``Gal(L/K)`` is
        abelian (and ``p`` unramified in ``L``): then the Frobenius at a prime
        above ``p`` does not depend on that prime (``lean-categories``
        ``serreArtinFamilyAtPrime_eq``, ``LeanCategories/Algebra/ArithmeticFrobeniusData.lean``:
        in an abelian invariant extension the coherent Frobenius family is
        independent of the prime above ``P``). Any prime above ``p`` serves,
        and none is stored.
        """
        quotient = self.parent().finite_quotient(stage)
        if self._prolongation is not None:
            prime_above = self._prolongation.at(stage)
        else:
            assert quotient.is_abelian() is True, (
                f"the restriction of {self} to {stage.field()} depends on the prime of "
                f"{stage.field()} above {self._base_prime}, since Gal(L/K) is not known "
                f"to be abelian; supply frobenius({self._base_prime}, prolongation=...)"
            )
            prime_above = next(iter(stage.field().primes_above(int(self._base_prime))))
        return quotient.frobenius_class(self._base_prime, prime_above).representative()

    def base_prime(self):
        return self._base_prime

    def prolongation(self):
        return self._prolongation


    def conjugacy_class(self):
        r"""The Frobenius class at ``p``: the Frobenius elements at all prolongations of ``p``."""
        return FrobeniusConjugacyClass(self.parent(), self._base_prime)

    def _repr_(self) -> str:
        if self._prolongation is None:
            return f"Frobenius at {self._base_prime} in {self.parent()}, at an unspecified prime above it"
        return f"Frobenius at {self._base_prime} in {self.parent()}, at {self._prolongation}"


class _AbsoluteElementConjugacyClassEngine:
    r"""Private realization of a represented absolute-Galois conjugacy orbit."""

    def __init__(self, representative, **rest) -> None:
        self._representative = representative
        super().__init__(**rest)

    def supergroup(self):
        return self.codomain()

    def ambient(self):
        r"""Return the ambient absolute Galois group ``G_K``."""
        return self.supergroup()

    def representative(self):
        return self._representative

    def _repr_(self) -> str:
        return f"Conjugacy class of {self._representative} in {self.supergroup()}"


def ElementConjugacyClass(supergroup, representative):
    r"""The represented conjugacy orbit of ``representative`` as a subset of ``G_K``.

    In the currently decidable absolute-Galois regime the group is abelian, so
    the orbit is the singleton ``{representative}``.  Outside that regime the
    predicate retains the existing assertion frontier rather than identifying
    conjugacy with equality.
    """
    representative = supergroup(representative)

    def is_conjugate(element):
        assert supergroup.is_abelian() is True, (
            f"conjugacy to {representative} in {supergroup} is decided only when "
            f"{supergroup} is known to be abelian, and it is not"
        )
        return supergroup(element) == representative

    inclusion = supergroup.condition_set(is_conjugate).inclusion()
    return Sets().Subobjects(supergroup).object(
        inclusion,
        _engine=_AbsoluteElementConjugacyClassEngine,
        construction_data={"representative": representative},
    )


def _as_exact_embedding(domain, codomain, embedding) -> RingMorphism:
    r"""Read ``embedding`` as an element of the ring ``Mor`` from ``domain`` to ``codomain``.

    That Mor's element constructor admits its own elements and exact Sage
    ring maps between the corresponding engine fields, and refuses a map with
    other endpoints.
    """
    return _own_ring(domain).Mor(_own_ring(codomain))(embedding)


class _AbsoluteGaloisGroupEngine:
    r"""The automorphism group of one exact extension object (K\to\bar K).

    The extension is an object of the coslice category (K/\mathbf{Fields}),
    equivalently an object of the slice of affine schemes over
    (\operatorname{Spec}K).  Elements are precisely closure automorphisms
    commuting with that structure map.
    """

    def __init__(
        self,
        field,
        *,
        closure,
        embedding,
        **rest,
    ) -> None:
        self._field = field
        self._closure = closure
        self._embedding = embedding
        super().__init__(**rest)

    def base_field(self):
        return self._field

    def algebraic_closure(self):
        return self._closure

    def base_embedding(self) -> RingMorphism:
        return self._embedding

    @cached_method
    def field_automorphism_mor(self):
        r"""The ring ``Mor(\bar K,\bar K)`` containing the exact actions of elements of ``G_K``."""
        return self.algebraic_closure().Mor(self.algebraic_closure())

    def arrow_set(self):
        r"""Return the underlying field Mor carrying these automorphisms."""
        return self.field_automorphism_mor()

    geometric_point = base_embedding

    def choice_data(self):
        r"""Return the explicit realization data retained by this parent.

        The live realization records the chosen algebraic closure and base
        embedding.  Later finite-stage embeddings and prolongations are
        supplied as explicit mathematical data at their constructors rather
        than being selected by a hidden global choice policy.
        """
        return {
            "closure": self.algebraic_closure(),
            "embedding": self.base_embedding(),
        }

    def has_canonical_realization(self) -> bool:
        r"""Return whether this realized absolute Galois group is canonical.

        For a finite field the selected profinite group is canonically
        procyclic, with the arithmetic Frobenius as its distinguished
        topological generator.  For a general field the concrete closure and
        base embedding are chosen realization data rather than canonical
        mathematical objects.
        """
        return self._is_finite_field()

    @cached_method
    def slice_category(self):
        r"""``K/Fields``, the coslice in which the chosen ``K -> Kbar`` is an object."""
        return OwnedFields().CosliceUnder(self._field)

    @cached_method
    def extension_object(self):
        r"""``Kbar`` with its chosen embedding ``K -> Kbar``, an object of ``K/Fields``."""
        return self.slice_category()(self._embedding)

    @cached_method
    def stage_category(self):
        r"""``(K/Fields)/(K -> Kbar)``, whose objects are the stages ``K -> L -> Kbar``."""
        return self.slice_category().SliceOver(self.extension_object())

    slice_object = extension_object

    def slice_automorphism(self, element):
        r"""Regard ``element`` as an isomorphism of the coslice object (K\to\bar K)."""
        element = element if element in self else self(element)
        extension = self.extension_object()
        mor = self.slice_category().Mor(extension, extension)
        identity = self.base_field().Mor(self.base_field()).identity()
        forward = mor._from_commuting_edges(identity, element.as_morphism())
        inverse = mor._from_commuting_edges(identity, element.inverse().as_morphism())
        return self.slice_category().Core().Mor(
            extension, extension
        )._from_known_inverse_pair(
            forward,
            inverse,
        )

    def _finiteness_decision(self):
        r"""Return ``False`` for a finite or number field ``K``: ``G_K`` is infinite.

        ``G_K`` surjects onto every ``Gal(L/K)`` with ``L`` finite Galois over
        ``K`` inside the chosen closure, so finite quotients of unbounded
        order make ``G_K`` infinite.  Over ``F_q`` the quotient
        ``Gal(F_{q^d}/F_q)`` has order ``d`` for every ``d``.  Over a number
        field ``K`` the quotient ``(C_2)^r`` exists for every ``r`` (see
        ``_finite_generation_decision``), of order ``2^r``.
        """
        match self:
            case _ if self._is_finite_field() or self._is_number_field():
                return False
            case _:
                return super()._finiteness_decision()

    def _finite_generation_decision(self):
        r"""Return whether this absolute Galois group is algebraically finitely generated.

        Finite-field absolute Galois groups are procyclic but not algebraically
        generated by Frobenius.  If ``K`` is a number field, then for every
        ``r`` there are multiquadratic finite Galois extensions of ``K`` with
        Galois group ``(C_2)^r``.  Hence ``G_K`` has finite quotients whose
        minimal number of generators is arbitrarily large, so no finite
        algebraic generating set of ``G_K`` can exist.  Outside these two
        represented regimes this parent does not decide the question.
        """
        if self._is_finite_field() or self._is_number_field():
            return False
        return AtomicProposition("is_finitely_generated", self)

    def _is_finite_field(self) -> bool:
        return _engine_ring(self._field) in FiniteFields()

    def _is_number_field(self) -> bool:
        computation_field = _engine_ring(self._field)
        return computation_field is SageQQ or computation_field in NumberFields()

    def base_field_order(self):
        if not self._is_finite_field():
            raise TypeError(
                f"the base field order q of {self} is defined only for a finite base "
                f"field, but the base field is {self._field}"
            )
        return _owned_engine_element(
            ZZ,
            ZZ(_engine_ring(self._field).cardinality()),
        )

    def _element_constructor_(self, datum=None, **options):
        if element_parent(datum) is self:
            return datum
        if element_parent(datum) in AbsoluteGaloisGroups():
            raise ValueError(
                f"{datum} is an element of {element_parent(datum)}, not of {self}"
            )
        if element_parent(datum) is not self.field_automorphism_mor():
            raise TypeError(
                f"an element of {self} is an automorphism of the algebraic closure "
                f"{self._closure}, an element of {self.field_automorphism_mor()}, but {datum} is not"
            )
        return AbsoluteGaloisGroupElement(self, exact_action=datum)

    def __contains__(self, element) -> bool:
        return element_parent(element) is self

    def __eq__(self, other) -> bool:
        return self is other

    def __hash__(self) -> int:
        return id(self)

    @cached_method
    def one(self):
        r"""The identity: the zeroth Frobenius power over a finite field, else the identity of the closure."""
        if self._is_finite_field():
            return FrobeniusElement(self, ZZ.zero())
        identity = self._closure.Mor(self._closure).identity()
        return AbsoluteGaloisGroupElement(self, exact_action=identity)

    def an_element(self):
        return self.frobenius() if self._is_finite_field() else self.one()

    def frobenius(self, prime=None, prolongation=None):
        r"""Return ``x -> x^q`` over a finite field, or the Frobenius element at ``prolongation``.

        Over a number field ``K`` the element is determined by a prime of
        ``Kbar`` above ``prime``, supplied as a :func:`PrimeProlongation`;
        the conjugacy class :meth:`frobenius_class` does not depend on it.
        Without ``prolongation`` the element is a Frobenius at an unspecified
        (existentially quantified) prime of ``Kbar`` above ``prime``: nothing
        is chosen, and it restricts only to abelian stages, where the
        Frobenius does not depend on the prime above ``prime``.
        """
        from sage_extensions.categories.rings.number_fields import OwnedNumberFields

        if prime is None:
            assert self in AbsoluteGaloisGroupsOfFiniteFields(), (
                f"the base field {self._field} of {self} is not finite, so a Frobenius "
                f"element exists only at a prime; give `prime` and a prime of the "
                f"algebraic closure above it"
            )
            return FrobeniusElement(self, ZZ.one())
        assert self._field in OwnedNumberFields(), (
            f"a Frobenius element at the prime {prime} is constructed here only over a "
            f"number field, but the base field of {self} is {self._field}"
        )
        if prolongation is None:
            from sage_extensions.categories.rings.ring_foundation import PrimeFields

            assert self._field in PrimeFields(), (
                f"a Frobenius element at {prime} with an unspecified prime above it is "
                f"constructed here only over QQ, where {prime} is a rational prime; over "
                f"{self._field} supply prolongation=PrimeProlongation({prime}, ...)"
            )
        return ArithmeticFrobeniusElement(self, prime, prolongation)

    def _finite_frobenius_image(self, element, exponent):
        if not self._is_finite_field():
            raise TypeError(
                f"the q-Frobenius x -> x^q exists only over a finite base field, but the "
                f"base field of {self} is {self._field}"
            )
        exponent = ZZ(exponent)
        if exponent == 0:
            return element
        q = self.base_field_order()
        if exponent > 0:
            return element ** (q**exponent)
        degree_over_prime = ZZ(int(element.minpoly().degree()))
        base_degree = ZZ(_engine_ring(self._field).degree())
        orbit_order = degree_over_prime // degree_over_prime.gcd(base_degree)
        positive_exponent = exponent % orbit_order
        return element ** (q**positive_exponent)

    def _compose_elements(self, left, right):
        if (
            left.frobenius_exponent() is not None
            and right.frobenius_exponent() is not None
        ):
            return FrobeniusElement(
                self, left.frobenius_exponent() + right.frobenius_exponent()
            )
        if not (left.is_globally_evaluable() and right.is_globally_evaluable()):
            # Restriction to a finite Galois stage is a group morphism, so the
            # composite restricts to the composite of the restrictions.
            return AbsoluteGaloisGroupElement(
                self,
                stage_rule=lambda stage: self.restriction_map(stage)(left)
                * self.restriction_map(stage)(right),
            )
        if (left == self.one()) is True:
            return right
        if (right == self.one()) is True:
            return left
        # Both admitted maps fix the same e: K -> Kbar, so their composite
        # fixes e too, independently of whether that equation is decidable.
        return self(left.as_morphism() * right.as_morphism())

    def _inverse_element(self, element):
        r"""``sigma^-1``: the negated Frobenius exponent, else the inverse of the exact action."""
        if element.frobenius_exponent() is not None:
            return FrobeniusElement(self, -element.frobenius_exponent())
        if not element.is_globally_evaluable():
            return AbsoluteGaloisGroupElement(
                self,
                stage_rule=lambda stage: self.restriction_map(stage)(element).inverse(),
            )
        if (element == self.one()) is True:
            return self.one()
        return self(element.exact_action().inverse())

    def extension_data(self, extension, *, embedding=None, base_embedding=None):
        r"""The stage ``K -> L -> Kbar`` named by a stage of this realization or by an owned field ``L``.

        For a field the embeddings are the stated ones, or the first pair of
        exact embeddings whose composite is the chosen ``K -> Kbar``.
        """
        if extension in self.stage_category():
            return extension
        extension_field = extension
        if (
            extension_field is self._field
            and embedding is None
            and base_embedding is None
        ):
            closure_candidates = (self._embedding,)
            base_candidates = (self._field.Mor(self._field).identity(),)
        else:
            closure_candidates = (
                extension_field.exact_embeddings(self._closure)
                if embedding is None
                else (_as_exact_embedding(extension_field, self._closure, embedding),)
            )
            base_candidates = (
                self._field.exact_embeddings(extension_field)
                if base_embedding is None
                else (
                    _as_exact_embedding(self._field, extension_field, base_embedding),
                )
            )
        compatible_pairs = [
            (candidate_base, candidate_closure)
            for candidate_closure in closure_candidates
            for candidate_base in base_candidates
            if candidate_closure * candidate_base == self._embedding
        ]
        if not compatible_pairs:
            raise ValueError(
                f"{extension_field} has no embeddings {self._field} -> {extension_field} -> "
                f"{self._closure} whose composite is the embedding {self._embedding} of {self}"
            )
        base_embedding, closure_embedding = compatible_pairs[0]
        return FiniteGaloisExtension(
            self._field,
            extension_field,
            base_embedding,
            self._closure,
            closure_embedding,
            extension_object=self.extension_object(),
        )

    @cached_method(key=lambda group, degree: ZZ(degree))
    def finite_extension(self, degree):
        r"""Return the canonical degree-``degree`` stage for a finite base field.

        Over ``F_q`` the unique extension of degree ``d`` inside the chosen
        closure is its subfield of order ``q^d``, so the degree is the whole
        defining datum and one degree names one stage.

        The cache key uses the same exact integer conversion as construction;
        truncating with ``int`` would admit a nonintegral degree on a cache hit.
        """
        assert self._is_finite_field(), (
            f"the extension of degree {degree} is unique only over a finite field, but "
            f"the base field of {self} is {self._field}"
        )
        degree = ZZ(degree)
        assert degree > 0, (
            f"an extension of {self._field} has positive degree, but degree = {degree}"
        )
        total_degree = ZZ(_engine_ring(self._field).degree()) * degree
        field_engine, embedding_engine = _engine_ring(self._closure).subfield(
            total_degree
        )
        # The subfield is defined by its finite-field characteristic, selected
        # variable label and exact modulus. Raise those data through the named
        # finite-field constructor rather than adopting the native parent.
        from sage_extensions.categories.rings.ring_foundation import (
            _finite_field_with_modulus,
        )

        extension_field = _finite_field_with_modulus(
            int(field_engine.characteristic()),
            field_engine.variable_name(),
            tuple(int(coefficient) for coefficient in field_engine.modulus().list()),
        )
        closure_embedding = extension_field.Mor(self._closure)(embedding_engine)
        return self.extension_data(extension_field, embedding=closure_embedding)

    def finite_quotient(self, extension):
        r"""Return ``Gal(L/K)`` for the finite stage ``L`` named by ``extension``.

        ``extension`` is a stage or a field; both name the stage
        :meth:`extension_data` selects, and the quotient is keyed on that
        stage's defining data, so equal data give one quotient.
        """
        return self._finite_quotient_of_stage(self.extension_data(extension))

    @cached_method
    def _finite_quotient_of_stage(self, stage):
        return FiniteGaloisQuotient(stage)

    def restriction_map(self, extension):
        stage = self.extension_data(extension)
        quotient = self.finite_quotient(stage)
        return self.Mor(quotient)._from_realization_rule(
            _galois_restriction_rule(stage)
        )

    def lift(self, finite_automorphism):
        quotient = finite_automorphism.parent()
        stage = self.extension_data(quotient.extension_data())
        finite_automorphism = FiniteGaloisQuotient(stage)(finite_automorphism)
        if self._is_finite_field():
            generator = stage.field().field_generators()[0]
            q = self.base_field_order()
            for exponent in range(int(stage.degree())):
                if finite_automorphism(generator) == generator ** (q**exponent):
                    return FrobeniusElement(self, exponent)
            raise ValueError(
                f"{finite_automorphism} is not a power of the q-Frobenius of "
                f"{stage.field()} over {self._field}, so it is not an automorphism of a "
                f"finite field extension"
            )
        raise ValueError(
            f"{finite_automorphism} has no canonical lift to {self} when the base field "
            f"{self._field} is not finite; lifts() gives the coset of all lifts"
        )

    def lifts(self, finite_automorphism):
        quotient = finite_automorphism.parent()
        stage = self.extension_data(quotient.extension_data())
        quotient = FiniteGaloisQuotient(stage)
        return LiftCoset(self.restriction_map(stage), quotient(finite_automorphism))

    def open_subgroup(self, extension, embedding=None):
        stage = self.extension_data(extension, embedding=embedding)
        return OpenAbsoluteGaloisSubgroup(self, stage)

    def open_subgroup_class(self, extension):
        return OpenGaloisSubgroupConjugacyClass(self, extension)

    def decomposition_group(self, prime, *, prolongation):

        return AbsoluteDecompositionGroup(self, prime, prolongation)

    def decomposition_group_class(self, prime):

        return DecompositionGroupConjugacyClass(self, prime)

    def inertia_group(self, prime, *, prolongation):

        return AbsoluteInertiaGroup(self, prime, prolongation)

    def inertia_group_class(self, prime):

        return InertiaGroupConjugacyClass(self, prime)

    def frobenius_class(self, prime):

        return FrobeniusConjugacyClass(self, prime)

    def cyclotomic_character(self, n):

        return CyclotomicCharacter(self, n)

    def quadratic_character(self, a):

        return QuadraticCharacter(self, a)

    def _repr_(self) -> str:
        return f"Aut({self._closure} / {self._field})"


def _realized_absolute_galois_group(
    field,
    *,
    closure=None,
    embedding=None,
    category=None,
    engine=_AbsoluteGaloisGroupEngine,
    **construction_data,
):
    r"""Construct one realized ``G_K`` through its owned group category."""
    field = _own_ring(field)
    if closure is None:
        closure = _engine_ring(field).algebraic_closure()
    closure = _own_ring(closure)
    if embedding is None:
        embedding = field.first_exact_embedding(closure)
    embedding = _as_exact_embedding(field, closure, embedding)
    if category is None:
        category = _absolute_galois_group_category(field)
    return _object_of(
        category,
        _engine=(OwnedGroups(), engine, AbsoluteGaloisGroupElement),
        field=field,
        closure=closure,
        embedding=embedding,
        **construction_data,
    )


@cached_function(key=lambda field: id(field))
def _canonical_absolute_galois_group(field):
    return _realized_absolute_galois_group(field)


def AbsoluteGaloisGroup(field, closure=None, embedding=None):
    r"""Return the represented absolute Galois group of ``field``.

    The canonical closure/embedding realization is one object per owned field.
    Stated realization data construct a distinct object through the same
    absolute-Galois group category entry.
    """
    field = _own_ring(field)
    if closure is None and embedding is None:
        return _canonical_absolute_galois_group(field)
    return _realized_absolute_galois_group(
        field,
        closure=closure,
        embedding=embedding,
    )


class OpenSubgroupInclusion:
    r"""The literal inclusion of a realized open subgroup into its supergroup group."""

    def __init__(self, parent) -> None:
        assert parent.domain().supergroup() is parent.codomain(), (
            f"the inclusion of {parent.domain()} must land in {parent.domain().supergroup()}, "
            f"but its codomain is {parent.codomain()}"
        )
        super().__init__(parent, self._evaluate_inclusion)

    def _evaluate_inclusion(self, element):
        subgroup = self.domain()
        element = subgroup(element)
        supergroup = self.codomain()
        exponent = element.frobenius_exponent()
        if exponent is not None:
            # A Frobenius power exists only over a finite field, where the
            # q^[E:K]-Frobenius of G_E is the [E:K]-th power of G_K's.
            return FrobeniusElement(supergroup, subgroup.index() * exponent)
        return supergroup(element.exact_action())

    def is_injective(self) -> bool:
        return True

    def is_continuous(self) -> bool:
        return True


def _open_subgroup_inclusion_rule(mor):
    r"""The group-Mor realization rule for an open absolute-Galois subgroup inclusion."""
    return mor._from_realization_engine(OpenSubgroupInclusion)


class _OpenAbsoluteGaloisSubgroupEngine(_AbsoluteGaloisGroupEngine):
    r"""The actual subgroup fixing one embedded finite extension (E/K)."""

    def __init__(self, fixed_extension, **rest) -> None:
        self._fixed_extension = fixed_extension
        super().__init__(**rest)

    def is_normal(self) -> bool:
        return self._fixed_extension.is_galois()

    def __contains__(self, element) -> bool:
        if element_parent(element) is self:
            return True
        if element not in self.supergroup():
            return False
        embedding = self.embedding()
        return all(
            element(embedding(generator)) == embedding(generator)
            for generator in self.fixed_field().field_generators()
        )

    def _element_constructor_(self, datum=None, **options):
        if element_parent(datum) is self.supergroup():
            if datum not in self:
                raise ValueError(
                    f"{datum} is not an element of {self}: it does not fix "
                    f"{self.fixed_field()}"
                )
            exponent = datum.frobenius_exponent()
            if exponent is not None and self.supergroup()._is_finite_field():
                if exponent % self.index():
                    raise ValueError(
                        f"{datum} is not an element of {self}: its Frobenius exponent "
                        f"{exponent} is not a multiple of the index {self.index()}"
                    )
                return FrobeniusElement(self, exponent // self.index())
            return super()._element_constructor_(datum.exact_action())
        return super()._element_constructor_(datum, **options)

    def conjugacy_class(self):
        return OpenGaloisSubgroupConjugacyClass(self.supergroup(), self.fixed_extension())

    def core(self):
        if self.is_normal():
            return self
        # A non-normal open subgroup occurs only over a number field, whose
        # Sage engine names the field it is defined over by base_field().
        field = _engine_ring(self.fixed_field())
        base = _engine_ring(self.supergroup().base_field())
        defining_base = field.base_field()
        assert defining_base is base or base.absolute_degree() == 1, (
            f"the core of {self} is computed only when {self.fixed_field()} is defined by a "
            f"polynomial over {self.supergroup().base_field()} or over QQ, but it is "
            f"defined over {defining_base}"
        )
        if defining_base is base:
            polynomial = field.relative_polynomial()
        else:
            polynomial = field.defining_polynomial().change_ring(base)

        from sage_extensions.categories.rings.number_fields import (
            _engine_number_field_isomorphism,
        )

        normal_engine, base_backend = polynomial.splitting_field(
            "normal_closure", map=True
        )
        from sage_extensions.categories.rings.number_fields import (
            _number_field_from_engine,
        )

        normal_field = _number_field_from_engine(normal_engine)
        # K -> N on N's own realization (generator to generator).
        base_backend = (
            _engine_number_field_isomorphism(normal_engine, _engine_ring(normal_field))
            * base_backend
        )
        base_embedding = self.supergroup().base_field().Mor(normal_field)(base_backend)
        # The embeddings N -> Kbar of the normal closure extending the chosen
        # E -> Kbar through some K-embedding E -> N.
        compatible_closure_embeddings = tuple(
            normal_to_closure
            for fixed_to_normal in self.fixed_field().exact_embeddings(normal_field)
            if all(
                fixed_to_normal(self._fixed_extension.base_embedding()(generator))
                == base_embedding(generator)
                for generator in self.supergroup().base_field().field_generators()
            )
            for normal_to_closure in normal_field.exact_embeddings(
                self.supergroup().algebraic_closure()
            )
            if all(
                normal_to_closure(fixed_to_normal(generator))
                == self.embedding()(generator)
                for generator in self.fixed_field().field_generators()
            )
        )
        if not compatible_closure_embeddings:
            raise ValueError(
                f"the normal closure {normal_field} of {self.fixed_field()} has no embedding "
                f"into {self.supergroup().algebraic_closure()} extending the embedding of "
                f"{self.fixed_field()}"
            )
        stage = self.supergroup().extension_data(
            normal_field,
            embedding=compatible_closure_embeddings[0],
            base_embedding=base_embedding,
        )
        return self.supergroup().open_subgroup(stage)

    def normalizer_quotient(self):
        r"""Return ``N_{G_K}(G_E)/G_E = Aut_K(E)`` as exact field maps.

        The infinite normalizer itself is not materialized.  The quotient is
        the finite group of exact ``K``-automorphisms of the fixed extension,
        which is canonically isomorphic to the normalizer quotient under the
        Galois correspondence.
        """
        return FiniteExtensionAutomorphismGroup(self.fixed_extension())

    def __le__(self, other) -> bool:
        if other not in OpenAbsoluteGaloisSubgroups(self.supergroup()):
            return False
        for embedding in other.fixed_field().exact_embeddings(self.fixed_field()):
            if all(
                self.embedding()(embedding(generator)) == other.embedding()(generator)
                for generator in other.fixed_field().field_generators()
            ):
                return True
        return False

    def intersection(self, other):
        if other not in OpenAbsoluteGaloisSubgroups(self.supergroup()):
            raise ValueError(
                f"cannot intersect {self} with {other}: {other} is not an open subgroup "
                f"of {self.supergroup()}"
            )
        assert _engine_ring(self.fixed_field()) in FiniteFields(), (
            f"the intersection of {self} and {other} is computed only over a finite "
            f"field, but {self.fixed_field()} is not finite"
        )
        degree = ZZ(self.index()).lcm(ZZ(other.index()))
        return self.supergroup().open_subgroup(self.supergroup().finite_extension(degree))

    def _repr_(self) -> str:
        return f"Gal({self.algebraic_closure()} / {self.fixed_field()}) inside {self.supergroup()}"


def OpenAbsoluteGaloisSubgroup(supergroup, extension):
    r"""Construct the open subgroup of ``supergroup`` fixing ``extension``."""
    return OpenAbsoluteGaloisSubgroups(supergroup)(extension)


def _same_k_extension(
    supergroup,
    left_field,
    left_base_embedding,
    right_field,
    right_base_embedding,
) -> bool | Predicate:
    r"""Whether the retained extensions ``j_E: K -> E`` and ``j_F: K -> F`` are isomorphic.

    For finite fields and number fields the selected finite embedding
    family supplies the candidates. A candidate is a ``K``-isomorphism
    exactly when ``s * j_E == j_F`` and the extension degrees agree.
    Undecided map equations remain propositions, including when both
    extensions use the same abstract field with different base maps.
    Other fields retain the isomorphism proposition without selecting an
    unavailable degree or embedding computation.
    """
    if left_field is right_field and left_base_embedding is right_base_embedding:
        return True
    if not all(
        _is_finite_or_number_field(field)
        for field in (supergroup.base_field(), left_field, right_field)
    ):
        return AtomicProposition(
            "are_isomorphic_as_extensions", left_base_embedding, right_base_embedding
        )
    if _relative_degree(supergroup.base_field(), left_field) != _relative_degree(
        supergroup.base_field(), right_field
    ):
        return False
    return negation(
        conjunction(
            negation(isomorphism * left_base_embedding == right_base_embedding)
            for isomorphism in left_field.exact_embeddings(right_field)
        )
    )


def OpenGaloisSubgroupConjugacyClass(supergroup, extension_field):
    r"""The conjugation orbit of the open subgroups ``G_E`` of ``G_K`` fixing a ``K``-extension ``E``.

    It is the orbit of one ``G_E`` in the orbit set of ``G_K`` acting by
    conjugation on its subgroups, so it forgets the embedding
    ``E -> Kbar``.  ``extension_field`` is a stage ``K -> E -> Kbar``, or an
    owned field ``E`` with exactly one embedding of ``K``.
    """
    # A stage itself also lies in Fields through its slice and coslice.
    # Its retained K -> E therefore takes precedence over bare-field data.
    if (
        extension_field not in supergroup.stage_category()
        and extension_field in OwnedRings()
    ):
        base_embeddings = supergroup.base_field().exact_embeddings(extension_field)
        if len(base_embeddings) != 1:
            raise ValueError(
                f"{extension_field} has {len(base_embeddings)} embeddings of "
                f"{supergroup.base_field()}, so its structure as an extension of "
                f"{supergroup.base_field()} is ambiguous; give it as an extension K -> L"
            )
        extension_field = supergroup.extension_data(
            extension_field, base_embedding=base_embeddings[0]
        )
    representative = supergroup.open_subgroup(extension_field)
    return supergroup.subgroup_conjugation_g_set().orbits().orbit_of(representative)



__all__ = [
    "AbsoluteGaloisGroup",
    "AbsoluteGaloisGroupElement",
    "ArithmeticFrobeniusElement",
    "ElementConjugacyClass",
    "FrobeniusElement",
    "OpenAbsoluteGaloisSubgroup",
    "OpenGaloisSubgroupConjugacyClass",
]
