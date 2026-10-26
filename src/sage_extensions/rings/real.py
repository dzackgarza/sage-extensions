r"""The exact real field.

Sage's global ``RR`` is MPFR: an approximation field.  It cannot be the
mathematical real field because its arithmetic is rounded; for example the
MPFR image of ``sqrt(2)`` need not square to exactly ``2``.

This module represents exact real numbers by closed exact Sage symbolic
expressions or regular rational Cauchy sequences with a supplied error modulus.
Algebraic subproblems on symbolic expressions are delegated to ``AA`` and
inequalities/non-equality can be certified by Arb balls without ever storing
an approximation as the value.  Approximation is explicit through ``.n()``.

Equality and order are necessarily partial algorithms on a language rich
enough to contain transcendental expressions.  A relation that is not decided
immediately is returned as a predicate and can be evaluated by ``ask(...)``.
"""

from __future__ import annotations

import operator
from collections.abc import Callable

from sage.misc.latex import latex
from sage.misc.cachefunc import cached_method
from sage.misc.unknown import Unknown
from sage.categories.rings import Rings as SageRings
from sage.rings.integer_ring import ZZ
from sage.rings.qqbar import AA, QQbar
from sage.rings.rational_field import QQ
from sage.rings.real_arb import RealBall, RealBallField
from sage.rings.real_lazy import CLF, RLF, LazyFieldElement, LazyUnop
from sage.rings.real_mpfr import (
    RealField,
)
from sage.rings.real_mpfr import (
    create_RealNumber as _create_real_approximation,
)
from sage.rings.ring import Field
from sage.structure.element import FieldElement, parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.symbolic.expression import Expression
from sage.symbolic.ring import SR

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    OwnedOrderedRings,
    OwnedRings,
    _OwnedRingBootstrapParent,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import continuum
from sage_extensions.categories.sets.set_categories import NN, Sets, UncountableSets
from sage_extensions.logic import Predicate, Propositions, ask
from sage_extensions.refine import realize_owned_category


def RealApproximation(value):
    r"""Return the owned finite-precision real represented by ``value``."""
    backend = _create_real_approximation(value)

    # The approximation constructor selects its MPFR precision. Preserve that
    # defining datum through the owned field constructor rather than adopting
    # the native RealField parent by engine class.
    from sage_extensions.categories.rings.ring_foundation import (
        _owned_real_field,
    )

    parent = _owned_real_field(int(backend.parent().precision()))
    return _owned_engine_element(parent, backend)


def _cauchy_sequence_from_enclosures(enclose: Callable[[int], RealBall]) -> CategoricalArrow:
    r"""Choose regular rational midpoints from convergent real enclosures.

    The supplier encloses one fixed real value, with finite enclosures
    whose diameters tend to zero as precision increases. For term n,
    diameter <= 2^(-n-1) gives midpoint error <= 2^(-n-2).
    The triangle inequality gives the regular Cauchy bound used by
    RR.of_cauchy. Constructing the map evaluates no term.
    """
    from sage_extensions.categories.rings.ring_foundation import _owned_rationals

    rationals = _owned_rationals()

    def approximation(index):
        exponent = int(index)
        diameter = QQ(1) / ZZ(2)**(exponent + 1)
        precision = max(64, exponent + 4)
        while True:
            enclosure = enclose(precision)
            precision *= 2
            if not enclosure.is_finite():
                continue
            lower, upper = enclosure.endpoints()
            lower = lower.exact_rational()
            upper = upper.exact_rational()
            if upper - lower <= diameter:
                return _owned_engine_element(rationals, (lower + upper)/2)

    return Sets().Mor(NN, rationals)(approximation)


_RELATION_SYMBOL = {
    operator.eq: "==",
    operator.ne: "!=",
    operator.lt: "<",
    operator.le: "<=",
    operator.gt: ">",
    operator.ge: ">=",
}


def _contains_approximation(expression: Expression) -> bool:
    r"""Return whether a symbolic expression contains an inexact numeric atom."""
    operands = expression.operands()
    if operands:
        return any(_contains_approximation(SR(operand)) for operand in operands)

    try:
        atom = expression.pyobject()
    except TypeError:
        return False

    if isinstance(atom, (float, complex)):
        return True

    atom_parent = parent(atom)
    if atom_parent in SageRings():
        return not bool(atom_parent.is_exact())
    # Symbolic constants and foreign Python atoms are not approximation rings.
    return False


def _closed_exact_real_expression(value) -> Expression:
    r"""Return the exact closed real symbolic expression represented by ``value``."""
    if isinstance(value, ExactRealNumber):
        return value.expression()

    value_parent = parent(value)
    if value_parent in OwnedRings():
        value = _engine_element(value_parent, value)
        value_parent = parent(value)

    if isinstance(value, float):
        raise TypeError(
            f"{value!r} is a floating-point number, not an exact real number; "
            "give the exact expression it approximates"
        )

    if value_parent is QQbar:
        if value.imag() != 0:
            raise TypeError(f"{value} is algebraic but not real")
        value = AA(value.real())
    elif value_parent in (RLF, CLF):
        raise TypeError(
            f"{value} is a numerical approximation in {value_parent}, not an exact real number; "
            "give the exact expression it approximates"
        )
    elif value_parent is not SR and value_parent in SageRings():
        if not value_parent.is_exact():
            raise TypeError(
                f"{value} lies in the inexact ring {value_parent}, so it is an approximation, not an exact real number"
            )

    expression = SR(value)
    if expression.variables():
        raise TypeError(
            f"{expression} contains symbolic variables and does not name one real number"
        )
    if _contains_approximation(expression):
        raise TypeError(f"{expression} contains an inexact numeric approximation")
    if expression.is_real() is not True:
        raise TypeError(f"{expression} is not known to be a real number")
    return expression


def _simplified_difference(left: Expression, right: Expression) -> Expression:
    return (left - right).simplify_full()


def _sign_from_algebraic(expression: Expression):
    r"""Return ``-1,0,1`` when ``expression`` is algebraic, else ``None``."""
    if expression not in AA:
        return None
    value = AA(expression)
    if value == 0:
        return 0
    return -1 if value < 0 else 1


def _sign_from_ball(expression: Expression | LazyFieldElement, precision: int):
    r"""Certify the sign using an Arb enclosure, or return ``None``."""
    field = RealBallField(precision)
    # ``expression in RealBallField`` is False even for pi^2 and sqrt(2),
    # which the field encloses; a closed real expression is what it
    # converts (TRAPS.md).
    if isinstance(expression, LazyFieldElement):
        ball = expression.eval(field)
    else:
        if expression.variables() or not expression.is_real():
            return None
        ball = field(expression)
    if not ball.is_finite():
        return None
    if ball == 0:
        return 0
    if ball.contains_zero():
        return None
    return 1 if ball > 0 else -1


def _relation_from_sign(sign: int, relation) -> bool:
    if relation is operator.eq:
        return sign == 0
    if relation is operator.ne:
        return sign != 0
    if relation is operator.lt:
        return sign < 0
    if relation is operator.le:
        return sign <= 0
    if relation is operator.gt:
        return sign > 0
    if relation is operator.ge:
        return sign >= 0
    raise TypeError(
        f"{relation} is not one of the order relations <, <=, >, >=, ==, != on the real numbers"
    )


def _decide_relation(
    left: Expression | LazyFieldElement,
    right: Expression | LazyFieldElement,
    relation,
    *,
    precision: int | None,
):
    r"""Decide a real relation: exact algebra, then Arb, then symbolic normalization.

    ``AA`` decides every algebraic difference exactly and an Arb enclosure
    certifies any nonzero sign, both without Maxima; ``simplify_full`` is
    reached only for a difference neither decides, and its result is then
    decided the same way.
    """
    if left is right:
        return _relation_from_sign(0, relation)
    if isinstance(left, LazyFieldElement) or isinstance(right, LazyFieldElement):
        if precision is None:
            return None
        sign = _sign_from_ball(RLF(left) - RLF(right), precision)
        return None if sign is None else _relation_from_sign(sign, relation)
    for difference_of in (operator.sub, _simplified_difference):
        difference = difference_of(left, right)
        if difference.is_zero() is True:
            return _relation_from_sign(0, relation)
        sign = _sign_from_algebraic(difference)
        if sign is None and precision is not None:
            sign = _sign_from_ball(difference, precision)
        if sign is not None:
            return _relation_from_sign(sign, relation)
    return None


class RealRelation(Predicate):
    r"""An exact relation between two real numbers awaiting evaluation."""

    __slots__ = ("_left", "_right", "_relation")

    def __init__(self, left: ExactRealNumber, right: ExactRealNumber, relation):
        self._left = left
        self._right = right
        self._relation = relation
        super().__init__()

    def left(self) -> ExactRealNumber:
        return self._left

    def right(self) -> ExactRealNumber:
        return self._right

    def operator(self):
        return self._relation

    def _ask_(self, *, max_prec: int = 4096):
        precision = 128
        while precision <= max_prec:
            answer = _decide_relation(
                self._left._expression,
                self._right._expression,
                self._relation,
                precision=precision,
            )
            if answer is not None:
                return answer
            precision *= 2
        return Unknown

    def _repr_(self) -> str:
        symbol = _RELATION_SYMBOL[self._relation]
        return f"{self._left} {symbol} {self._right}"

    def _latex_(self) -> str:
        symbol = {
            operator.eq: "=",
            operator.ne: r"\ne",
            operator.lt: "<",
            operator.le: r"\le",
            operator.gt: ">",
            operator.ge: r"\ge",
        }[self._relation]
        return rf"{latex(self._left)} {symbol} {latex(self._right)}"


class _CauchyRealComputation(LazyFieldElement):
    r"""Private lazy evaluation of a regular rational Cauchy sequence.

    The input is an owned map a: NN -> QQ satisfying
    |a(m)-a(n)| <= 2^(-n) for m >= n. Passing to the limit gives
    |lim a-a(n)| <= 2^(-n). Sage's lazy arithmetic composes evaluations
    of this primitive in interval and ball fields; its comparisons are
    never used to decide owned real relations.
    """

    def __init__(self, sequence: CategoricalArrow) -> None:
        self._sequence = sequence
        FieldElement.__init__(self, RLF)

    def depth(self) -> int:
        return 0

    def eval(self, field):
        if field.is_exact():
            raise NotImplementedError(
                "a general Cauchy limit has no supplied exact symbolic or algebraic expression"
            )
        exponent = int(field.precision()) + 4
        rationals = self._sequence.codomain()
        center = _engine_element(rationals, self._sequence(NN(exponent)))
        radius = QQ(1) / ZZ(2)**exponent
        enclosure = RealBallField(exponent)(center, rad=radius)
        return field(enclosure)

    def _repr_(self) -> str:
        return f"Limit of {self._sequence}"

    def __reduce__(self):
        return (_CauchyRealComputation, (self._sequence,))


class ExactRealNumber(FieldElement):
    r"""An exact, explicitly real number."""

    __hash__ = None

    def __init__(self, parent: ExactRealField, expression: Expression | LazyFieldElement) -> None:
        self._expression = expression
        if isinstance(expression, LazyFieldElement):
            self._cache_token = object()
        FieldElement.__init__(self, parent)

    def expression(self) -> Expression:
        r"""Return the exact symbolic expression representing this real."""
        if not isinstance(self._expression, Expression):
            raise NotImplementedError(
                "this real is presented by a Cauchy computation, not a symbolic expression"
            )
        return self._expression

    def _cache_key(self):
        r"""Supply Sage's cache key for this immutable real presentation.

        Real equality remains partial, so this element stays unhashable.
        Sage's cached constructions can instead use the parent and the
        exact stored expression, or a retained identity token for a lazy
        computation. Distinct presentations denoting the same real may
        occupy separate cache entries; a cache hit establishes
        neither a new equality decision nor a normal form for real values.
        """
        if isinstance(self._expression, Expression):
            return self.parent(), "symbolic", self._expression
        return self.parent(), "lazy", self._cache_token

    def _from_computation(self, value):
        r"""Raise an exact expression or an owned arithmetic lazy result."""
        if isinstance(value, LazyFieldElement):
            return self.parent().element_class(self.parent(), value)
        return self.parent()(value)

    def _arithmetic_values(self, other):
        if isinstance(self._expression, LazyFieldElement) or isinstance(other._expression, LazyFieldElement):
            return RLF(self._expression), RLF(other._expression)
        return self._expression, other._expression

    @cached_method
    def cauchy_sequence(self) -> CategoricalArrow:
        r"""Return a chosen regular rational Cauchy presentation of this value.

        An originally supplied sequence is retained literally. Otherwise
        Arb supplies rational midpoints with error at most 2^(-n-2).
        For m >= n the triangle inequality gives a difference at most
        2^(-m-2)+2^(-n-2) <= 2^(-n-1), hence the regularity bound used
        by of_cauchy. Convergent enclosure evaluation is required.
        The returned object is the actual map NN -> QQ; constructing
        that map evaluates no term and decides no real equality.
        """
        if isinstance(self._expression, _CauchyRealComputation):
            return self._expression._sequence
        return _cauchy_sequence_from_enclosures(
            lambda precision: self._arb_(RealBallField(precision))
        )

    def is_real(self) -> bool:
        return True

    def is_unit(self) -> bool | Predicate:
        r"""Return the field's nonzero predicate, without forcing a decision.

        EXAMPLES::

            sage: assert RR.one().is_unit() is True
            sage: assert RR.zero().is_unit() is False
            sage: from sage_extensions.categories.sets.set_categories import NN, Sets
            sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
            sage: from sage_extensions.logic import Predicate
            sage: Q = _owned_rationals()
            sage: a = Sets().Mor(NN, Q)(lambda n: Q(1)/Q(2)**int(n))
            sage: z = RR.of_cauchy(a)
            sage: assert isinstance(z.is_unit(), Predicate)
        """
        return self != self.parent().zero()

    def _repr_(self) -> str:
        return repr(self._expression)

    def __reduce__(self):
        return (_restore_exact_real, (self._expression,))

    def _latex_(self) -> str:
        return str(latex(self._expression))

    def _symbolic_(self, symbolic_ring):
        return symbolic_ring(self.expression())

    def _sympy_(self):
        return self.expression()._sympy_()

    def _integer_(self, integer_ring):
        return integer_ring(self._rational_())

    def _rational_(self):
        # The symbolic ring keeps distinct square roots apart, so
        # sqrt(6)*sqrt(3)*sqrt(2) is no numeric rational to it. AA decides an
        # algebraic value exactly, as the relations of this field already do.
        if isinstance(self._expression, Expression) and self._expression in AA:
            return QQ(AA(self._expression))
        return QQ(self.expression())

    def _algebraic_(self, algebraic_field):
        return algebraic_field(self.expression())

    def _mpfr_(self, field):
        if isinstance(self._expression, LazyFieldElement):
            return field(self._arb_(RealBallField(field.precision())).mid())
        return field(self._expression)

    def _arb_(self, field):
        r"""Enclose this exact real through its expression or Cauchy computation.

        This is Sage's designated real-ball conversion protocol. The
        exact expression is evaluated directly with outward error bounds;
        an MPFR approximation must not stand in for that enclosure.

        EXAMPLES::

            sage: from sage.rings.real_arb import RealBallField
            sage: B = RealBallField(128)
            sage: ball = B(RR.pi())
            sage: assert ball.lower().exact_rational() > 3
            sage: assert ball.upper().exact_rational() < 22/7
            sage: assert (B(RR(2).sqrt())**2).contains(2)
            sage: assert B(RR.zero()).is_zero()
        """
        if isinstance(self._expression, LazyFieldElement):
            return self._expression.eval(field)
        return field(self._expression)

    def _real_double_(self, field):
        if isinstance(self._expression, LazyFieldElement):
            return field(self._arb_(RealBallField(53)).mid())
        return field(self._expression)

    def n(self, prec: int = 53, digits: int | None = None, **kwds):
        r"""Return an explicit floating-point approximation of ``self``."""
        if isinstance(self._expression, LazyFieldElement):
            if kwds:
                raise TypeError("Cauchy real approximation accepts only prec and digits")
            return self._mpfr_(RealField(prec if digits is None else 4*int(digits)))
        if digits is not None:
            return self._expression.n(digits=digits, **kwds)
        return RealField(prec)(self._expression)

    numerical_approx = n

    def __float__(self) -> float:
        return float(self.n())

    def _add_(self, other):
        left, right = self._arithmetic_values(other)
        return self._from_computation(left + right)

    def _sub_(self, other):
        left, right = self._arithmetic_values(other)
        return self._from_computation(left - right)

    def _mul_(self, other):
        left, right = self._arithmetic_values(other)
        return self._from_computation(left * right)

    def __mul__(self, other):
        r"""Use the exact scalar engine, or the action on an owned module.

        The coefficient product cannot call the algebra tensor classifier
        whose own linear evaluation uses these coefficients.
        """
        ring = self.parent()
        source = parent(other)
        if source is ring:
            return ExactRealNumber._mul_(self, other)
        from sage_extensions.categories.modules.pure.modules import Modules

        if source in Modules(ring):
            return source.scalar_multiple(self, other)
        try:
            return ExactRealNumber._mul_(self, ring(other))
        except (TypeError, ValueError):
            return NotImplemented

    def __rmul__(self, other):
        return ExactRealNumber.__mul__(self, other)

    def _div_(self, other):
        nonzero = self.parent().relation(other, self.parent().zero(), operator.ne)

        decision = ask(nonzero) if nonzero in Propositions else nonzero
        if decision is False:
            raise ZeroDivisionError(f"cannot divide {self} by {other}: the denominator is zero")
        if decision is Unknown:
            raise ValueError(
                f"cannot divide {self} by {other}: it is undecided whether {other} is zero"
            )
        return self.parent()._divide_by_nonzero(self, other)

    def _neg_(self):
        return self._from_computation(-self._expression)

    def __invert__(self):
        return self.parent().one() / self

    def _unit_inverse_decision(self):
        r"""``x^{-1}``: every nonzero real number is a unit."""
        return ~self

    def __pow__(self, exponent, modulus=None):
        if modulus is not None:
            raise TypeError(
                f"cannot compute {self}^{exponent} mod {modulus}: modular exponentiation is not defined "
                "on the real numbers"
            )
        exponent = self.parent()(exponent)
        left, right = self._arithmetic_values(exponent)
        if isinstance(left, LazyFieldElement):
            integer_power = (
                isinstance(exponent._expression, Expression)
                and exponent._expression in ZZ
            )
            if integer_power:
                if ZZ(exponent._expression) < 0 and ask(self != self.parent().zero()) is not True:
                    raise ValueError("a negative real power needs a decided nonzero base")
            elif ask(self > self.parent().zero()) is not True:
                raise ValueError("this general real power needs a decided positive base")
        return self._from_computation(left ** right)

    def __rpow__(self, base):
        return self.parent()(base) ** self

    def sqrt(self):
        if isinstance(self._expression, LazyFieldElement) and ask(self >= self.parent().zero()) is not True:
            raise ValueError("the real square root needs a decided nonnegative input")
        return self._from_computation(self._expression.sqrt())

    def exp(self):
        return self._from_computation(self._expression.exp())

    def log(self, base=None):
        if isinstance(self._expression, LazyFieldElement) and ask(self > self.parent().zero()) is not True:
            raise ValueError("the real logarithm needs a decided positive input")
        if base is None:
            return self._from_computation(self._expression.log())
        base = self.parent()(base)
        if isinstance(self._expression, LazyFieldElement) or isinstance(base._expression, LazyFieldElement):
            if (ask(self > self.parent().zero()) is not True
                    or ask(base > self.parent().zero()) is not True
                    or ask(base != self.parent().one()) is not True):
                raise ValueError("a real logarithm base must be decided positive and different from one")
        left, right = self._arithmetic_values(base)
        return self._from_computation(left.log() / right.log())

    def sin(self):
        return self._from_computation(self._expression.sin())

    def cos(self):
        return self._from_computation(self._expression.cos())

    def tan(self):
        if (isinstance(self._expression, LazyFieldElement)
                and ask(self.cos() != self.parent().zero()) is not True):
            raise ValueError("the real tangent needs a decided nonzero cosine")
        return self._from_computation(self._expression.tan())

    def sinh(self):
        return self._from_computation(self._expression.sinh())

    def cosh(self):
        return self._from_computation(self._expression.cosh())

    def tanh(self):
        return self._from_computation(self._expression.tanh())

    def sech(self):
        from sage.functions.hyperbolic import sech

        if isinstance(self._expression, LazyFieldElement):
            return self._from_computation(LazyUnop(RLF, self._expression, sech))
        return self.parent()(sech(self._expression))

    def zeta(self):
        r"""The Riemann zeta function at this real number, which must exceed 1."""
        from sage.functions.transcendental import zeta

        assert self > 1, f"zeta(s) is computed here only for real s > 1, but s = {self} is not > 1"
        if isinstance(self._expression, LazyFieldElement):
            return self._from_computation(LazyUnop(RLF, self._expression, zeta))
        return self.parent()(zeta(self._expression))

    def sgn(self):
        r"""The sign of this real number, in the integers: \(1\), \(0\) or \(-1\)."""
        integers = _owned_integers()
        if self.is_zero() is True:
            return integers(0)
        positive = self.is_positive()
        assert positive is True or positive is False, (
            f"the sign of the real number {self} is undecided: it is not decided whether {self} > 0"
        )
        return integers(1 if positive else -1)

    def __abs__(self):
        return self._from_computation(abs(self._expression))

    def _coerce_for_relation(self, other):
        try:
            return self.parent()(other)
        except (TypeError, ValueError):
            return None

    def __eq__(self, other):
        other = self._coerce_for_relation(other)
        if other is None:
            return False
        return self.parent().relation(self, other, operator.eq)

    def __ne__(self, other):
        other = self._coerce_for_relation(other)
        if other is None:
            return True
        return self.parent().relation(self, other, operator.ne)

    def __lt__(self, other):
        other = self._coerce_for_relation(other)
        if other is None:
            raise TypeError(
                f"cannot compare the real number {self} by <: the other argument is not a real number"
            )
        return self.parent().relation(self, other, operator.lt)

    def __le__(self, other):
        other = self._coerce_for_relation(other)
        if other is None:
            raise TypeError(
                f"cannot compare the real number {self} by <=: the other argument is not a real number"
            )
        return self.parent().relation(self, other, operator.le)

    def __gt__(self, other):
        other = self._coerce_for_relation(other)
        if other is None:
            raise TypeError(
                f"cannot compare the real number {self} by >: the other argument is not a real number"
            )
        return self.parent().relation(self, other, operator.gt)

    def __ge__(self, other):
        other = self._coerce_for_relation(other)
        if other is None:
            raise TypeError(
                f"cannot compare the real number {self} by >=: the other argument is not a real number"
            )
        return self.parent().relation(self, other, operator.ge)

    def is_zero(self):
        return self == self.parent().zero()

    def is_one(self):
        return self == self.parent().one()

    def is_positive(self):
        return self > self.parent().zero()

    def is_negative(self):
        return self < self.parent().zero()

    def _squareness_decision(self):
        r"""Whether this is ``y^2`` for a real ``y``: exactly when it is nonnegative.

        A nonnegative real has the real square root :meth:`sqrt`, and a square
        is nonnegative. The exact sign relation may remain undecided and is
        returned as that proposition to the magma squareness owner.
        """
        return self >= self.parent().zero()

    def __bool__(self):
        relation = self != self.parent().zero()
        if relation is True or relation is False:
            return relation
        raise TypeError(
            f"the truth value of {self} is undecided: it is not decided whether {self} != 0; "
            "use ask(x != 0)"
        )


RealNumber = ExactRealNumber


class ExactRealField(UniqueRepresentation, Field):
    r"""The exact real field with symbolic and regular Cauchy presentations."""

    Element = ExactRealNumber
    _preamble_owned_ring_parent = True

    def __init__(self) -> None:
        from sage_extensions.categories.algebras.algebras import Algebras
        from sage_extensions.categories.modules.pure.modules import (
            FinitelyGeneratedFreeModules,
        )

        # The constructing category is construction data (OWN-15): a field is
        # built by the ring route, as every owned ring is.
        self._constructing_category = OwnedRings()
        regular_algebra = Algebras(self).Associative().Unital().Commutative()
        Field.__init__(
            self,
            self,
            category=Cat().meet(
                (
                    OwnedFields(),
                    OwnedOrderedRings(),
                    UncountableSets(),
                    regular_algebra,
                    FinitelyGeneratedFreeModules(self),
                )
            ),
        )
        realize_owned_category(self)
        from sage_extensions.categories.algebras.algebras import _algebra_from_native_ring

        _algebra_from_native_ring(self, lambda left, right: ExactRealNumber._mul_(left, right),
            ExactRealField.one(self), lambda scalar, element: ExactRealNumber._mul_(self(scalar), self(element)))


    def is_commutative(self) -> bool:
        r"""A field is commutative; answered by the class so ``Modules(RR)`` can place itself during construction."""
        return True

    def _refine_category_(self, category) -> None:
        r"""Keep the category fixed at construction.

        A Sage membership test such as ``RR in Fields()`` asks Sage's
        ``_refine_category_`` to add Sage's ``Fields()`` as a cached answer.
        Placement comes only from construction: the field is already in the
        owned fields and the owned uncountable sets, and an engine's answer
        never changes the category or the operations it selects.
        """

    def _selected_engine_ring(self):
        r"""Select SR for consumers that explicitly need symbolic serialization.

        Generic linear algebra uses the shared exact scalar protocol
        instead. A general Cauchy limit has no supplied SR expression and
        refuses this serialization rather than substituting an approximation.
        """
        return SR

    def _engine_element(self, element):
        r"""Serialize a real with an available exact symbolic expression."""
        return self(element).expression()

    def _from_engine_element(self, element) -> ExactRealNumber:
        r"""Raise a result of generic exact real scalar computation."""
        if isinstance(element, ExactRealNumber) and element.parent() is self:
            return element
        return self(element)

    def _sign_of_nonzero(self, value) -> int:
        r"""Determine the sign under a supplied nonzero hypothesis.

        Convergent enclosures eventually lie on one side of zero. This
        protected computation is not a decision procedure for arbitrary
        real inputs: a zero input violates its hypothesis.
        """
        value = self(value)
        precision = 128
        while True:
            enclosure = value._arb_(RealBallField(precision))
            if enclosure.is_finite():
                if enclosure > enclosure.parent().zero():
                    return 1
                if enclosure < enclosure.parent().zero():
                    return -1
            precision *= 2

    def _sqrt_of_positive(self, value) -> ExactRealNumber:
        r"""Compute the positive root under an established positivity hypothesis.

        The maintained symbolic or lazy real arithmetic supplies the root.
        Its reality follows from the caller's hypothesis, without another
        bounded predicate query.
        """
        value = self(value)
        return self.element_class(self, value._expression.sqrt())

    def _divide_by_nonzero(self, numerator, denominator) -> ExactRealNumber:
        r"""Compute a quotient whose denominator is already known nonzero.

        Protected arithmetic contract: callers are checked scalar division
        and the nonsingular congruence computation after an Arb enclosure
        excludes zero for that actual pivot. This performs no new zero
        decision and does not turn an undecided predicate into a proof.
        """
        numerator, denominator = self(numerator), self(denominator)
        left, right = numerator._arithmetic_values(denominator)
        # Field closure under division by this known nonzero real supplies
        # reality; a symbolic engine need not re-decide that hypothesis.
        return self.element_class(self, left / right)

    def _matrix_determinant(self, components) -> ExactRealNumber:
        r"""Sage determinant protocol for the existing real presentations.

        Accept a Sage matrix or nested scalar rows. Closed expressions use
        symbolic division-free arithmetic. General
        Cauchy coefficients use the same maintained division-free routine
        over Arb balls and a regular rational Cauchy presentation of its
        constant coefficient. The input scalars are snapshotted so later
        matrix mutation cannot change the returned real value.

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
            sage: Q = _owned_rationals()
            sage: a = Sets().Mor(NN, Q)(lambda n: Q(1) + Q(1)/Q(2)**int(n))
            sage: x = RR.of_cauchy(a)
            sage: L = Lattices(RR)([[x,0,0,0], [0,-x,0,0], [0,0,1,0], [0,0,0,-1]])
            sage: d = L.determinant()
            sage: assert RealBallField(128)(d).contains(1)
            sage: assert ask(d > RR(1)/RR(2)) is True
            sage: assert L.signature_pair().first().finite_value() == 2
            sage: assert L.signature_pair().second().finite_value() == 2
            sage: z = RR.of_cauchy(Sets().Mor(NN, Q)(lambda n: Q(1)/Q(2)**int(n)))
            sage: S = Lattices(RR)([[z,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
            sage: assert RealBallField(128)(S.determinant()).contains(0)
            sage: assert isinstance(S.is_nondegenerate(), Predicate)
            sage: C = Lattices(RR)([[1,0,0,0], [0,-1,0,0], [0,0,1,0], [0,0,0,-1]])
            sage: assert C.determinant() == RR.one()
        """
        from sage.matrix.constructor import matrix
        from sage.matrix.matrix2 import Matrix as SageMatrix

        if isinstance(components, (tuple, list)):
            size = len(components)
            assert all(len(row) == size for row in components), "a determinant requires a square matrix"
            entries = tuple(tuple(self(value) for value in row) for row in components)
        else:
            size = components.nrows()
            assert components.ncols() == size, "a determinant requires a square matrix"
            entries = tuple(
                tuple(self(components[i, j]) for j in range(size))
                for i in range(size)
            )
        if all(isinstance(entry._expression, Expression) for row in entries for entry in row):
            symbolic = matrix(SR, size, size, [entry.expression() for row in entries for entry in row])
            constant = SageMatrix.charpoly(symbolic, algorithm="df")[0]
            return self(-constant if size % 2 else constant)

        def enclose(precision: int) -> RealBall:
            field = RealBallField(precision)
            balls = matrix(field, size, size, [entry._arb_(field) for row in entries for entry in row])
            constant = SageMatrix.charpoly(balls, algorithm="df")[0]
            return -constant if size % 2 else constant

        return self.of_cauchy(_cauchy_sequence_from_enclosures(enclose))

    def _repr_(self) -> str:
        return "Real Field"

    def _latex_(self) -> str:
        return r"\mathbb{R}"

    def _element_constructor_(self, value) -> ExactRealNumber:
        if isinstance(value, ExactRealNumber) and value.parent() is self:
            return value
        from sage_extensions.categories.modules.pure.modules import Modules

        source = parent(value)
        if source in Modules(self) and source.unformed_module() is self:
            return source._element_of_unformed_module(value)
        return self.element_class(self, _closed_exact_real_expression(value))

    def _from_engine_expression(self, value) -> ExactRealNumber:
        r"""Cross a private exact expression; implementation endpoint for the protected dispatcher."""
        return self.element_class(self, _closed_exact_real_expression(value))

    def of_cauchy(self, sequence: CategoricalArrow) -> ExactRealNumber:
        r"""Return the real limit of a regular rational Cauchy sequence.

        The supplied map a: NN -> QQ must satisfy
        |a(m)-a(n)| <= 2^(-n) for every m >= n. This is a mathematical
        hypothesis on the supplied infinite sequence, not a property
        established by checking a finite prefix. It implies convergence
        and |lim a-a(n)| <= 2^(-n). The owned map is retained, with its
        actual source and rational-value target.

        This is the real Cauchy-limit construction of Mathlib's
        Real.ofCauchy, with the stated effective error modulus. The result
        belongs to this same real field, not a new approximation field.
        Arithmetic is lazy and exact; explicit ball conversion encloses
        its value. Equality and order may remain propositions.

        EXAMPLES::

            sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
            sage: Q = _owned_rationals()
            sage: a = Sets().Mor(NN, Q)(lambda n: Q(1) + Q(1)/Q(2)**int(n))
            sage: x = RR.of_cauchy(a)
            sage: assert x.parent() is RR
            sage: assert RR in OwnedOrderedRings()
            sage: assert x.cauchy_sequence() is a
            sage: assert ask(x > RR(0)) is True
            sage: assert ask(x < RR(2)) is True
            sage: from sage.rings.real_arb import RealBallField
            sage: B = RealBallField(128)
            sage: assert B(x).contains(1)
            sage: assert B(x + RR(2)).contains(3)
            sage: assert B(RR(2) * x).contains(2)
            sage: assert B(x.sqrt()).contains(1)
            sage: assert B(RR(3)/x).contains(3)
            sage: assert B(x - x).contains(0)
            sage: from sage_extensions.categories.lattices import Lattices
            sage: z = RR.of_cauchy(Sets().Mor(NN, Q)(lambda n: Q(1)/Q(2)**int(n)))
            sage: Z = Lattices(RR)([[z]])
            sage: assert isinstance(Z.is_nondegenerate(), Predicate)
            sage: b = RR(2).sqrt().cauchy_sequence()
            sage: assert b.domain() is NN and b.codomain() is Q
            sage: assert abs(RR(b(NN(8))) - RR(2).sqrt()) < RR(1)/RR(2)**10
        """
        from sage_extensions.categories.rings.ring_foundation import _owned_rationals

        assert sequence.domain() is NN and sequence.codomain() is _owned_rationals(), (
            "a regular rational Cauchy presentation needs an owned map NN -> QQ"
        )
        sequence = Sets().Mor(NN, _owned_rationals())(sequence)
        return self.element_class(self, _CauchyRealComputation(sequence))

    def __contains__(self, value) -> bool:
        r"""Return whether ``value`` canonically names an exact real number."""
        try:
            self(value)
        except (TypeError, ValueError):
            return False
        return True

    def _coerce_map_from_(self, source):
        # A coercion into a ring is a ring morphism, so only a ring has one.
        match source:
            case _ if source in OwnedRings() or source in SageRings():
                pass
            case _:
                return None
        computation_source = _engine_ring(source)
        if computation_source in (ZZ, QQ, AA):
            return True
        if computation_source not in SageRings():
            return None
        if AA.has_coerce_map_from(computation_source):
            return True
        return None

    def relation(self, left: ExactRealNumber, right: ExactRealNumber, relation):
        r"""Return a decided Boolean or an exact real relation predicate."""
        left = self(left)
        right = self(right)
        answer = _decide_relation(
            left._expression,
            right._expression,
            relation,
            precision=128,
        )
        if answer is not None:
            return answer
        return RealRelation(left, right, relation)

    def zero(self) -> ExactRealNumber:
        return self(ZZ.zero())

    def one(self) -> ExactRealNumber:
        return self(ZZ.one())

    def _characteristic_decision(self):
        return _owned_integers().zero()

    def is_exact(self) -> bool:
        return True

    def is_finite(self) -> bool:
        return False

    def _cardinality_decision(self):
        r"""Supply the cardinality of the real numbers at the set owner."""
        return continuum

    def identity_chart(self):
        r"""The coordinate chart of the real line on this exact field."""
        pass

    def standard_topological_atlas(self):
        r"""The real-line atlas on this exact underlying set."""
        pass

    def standard_smooth_atlas(self):
        r"""The smooth atlas generated by the identity chart on this field."""
        pass

    def fraction_field(self):
        return self

    def _an_element_(self):
        from sage.symbolic.constants import pi

        return self(pi)

    def pi(self) -> ExactRealNumber:
        from sage.symbolic.constants import pi

        return self(pi)

    def e(self) -> ExactRealNumber:
        from sage.symbolic.constants import e

        return self(e)


_OwnedRingBootstrapParent.register(ExactRealField)


RR = ExactRealField()


pi = RR.pi()
e = RR.e()


def _owned_real_from_engine_expression(value) -> ExactRealNumber:
    r"""Raise a private exact symbolic expression into the owned real field.

    Protected exact-real contract (\`OWN-05\`--\`OWN-07\`).  Permitted
    callers are exact symbolic computation adapters for definite-lattice
    invariants and convolution evaluation.  They produce a closed exact
    expression and immediately raise it here; the symbolic engine value never
    becomes public mathematical storage.
    """
    return RR._from_engine_expression(value)


def _restore_exact_real(expression: Expression | LazyFieldElement) -> ExactRealNumber:
    if isinstance(expression, LazyFieldElement):
        return RR.element_class(RR, expression)
    return RR(expression)


__all__ = [
    "e",
    "pi",
    "ExactRealField",
    "ExactRealNumber",
    "RR",
    "RealApproximation",
    "RealNumber",
    "RealRelation",
]
