r"""Function spaces \(C^k(X,Y)\), \(L^p(X,Y)\) and \(\ell^p(X,Y)\) as submodules of \(Y^X\).

A function space is the set of maps \(X\to Y\) cut out of
\(\operatorname{Hom}_{\mathbf{Set}}(X,Y)\) by a condition on the maps, with
the pointwise structure of \(Y\) (``CON-17``; owner statement 2026-10-14:
\(L^p(X,Y) := \{f\colon X\to Y \mid p\text{-integrable}\}\subseteq
\operatorname{Hom}_{\mathbf C}(X,Y)\)).  Each constructor takes both
endpoints and is spelled out every time (``OWN-02``):

- ``C(k, X, Y)``: maps of class \(C^k\), \(k\in\mathbb N\cup\{\infty\}\),
  on a \(C^k\) manifold \(X\); for \(Y=\mathbb R\) the pointwise product
  makes it a commutative unital \(\mathbb R\)-algebra.  The condition and
  the calculus are computed from a formula in one real variable, which is the
  case \(X=\mathbb R\).
- ``Lp(p, X, Y)``: the \(p\)-integrable maps \(\mathcal L^p(X,Y)\), whose
  quotient by the null maps is \(L^p\); implemented for Lebesgue measure on
  \(X=\mathbb R\) and \(Y=\mathbb R\).  For \(p=2\) it is the formed module
  with \(b(f,g)=\int fg\) on functions; the radical of \(b\) is exactly the
  null functions, and the Hilbert space \(L^2\) is the quotient by them
  (``quotient_by_null_functions``).
- ``ell(p, X, Y)``: the \(p\)-summable maps \(X\to\mathbb R\) for an
  arbitrary set \(X\) (\(\sum_{x\in X}|a(x)|^p<\infty\), counting measure;
  bounded for \(p=\infty\)); for \(p=2\) the formed module with
  \(b(a,c)=\sum_{x\in X}a(x)c(x)\).  The summation and the summability
  theorems are computed from a formula in one variable read as
  \(n\in\mathbb N\), which is the case \(X=\mathbb N\).

Each space is ``Y.function_module(X).condition_submodule(P)``: its
underlying set is a subset of ``Sets().Mor(X, Y)``, and a map enters
through that Mor's element constructor -- a callable, or a formula binding
its own variable (``f(t) = exp(-t^2)``).  No space stores a variable or
supplies a point of its domain.  Construction does not ask the condition
(``OWN-22``): ``f in space`` asks it, and the element validator
``validate_condition_membership`` raises when it is false.  The condition
is decided by theorems on a map given by a formula (the ladder below) and
is otherwise the proposition that states it.

Operations that need the formula of a map -- derivatives, integrals,
Taylor series, the forms \(\int fg\) and \(\sum a_n b_n\) -- read it through
the private formula adapter ``_map_formula``; a map given by an opaque
callable reaches the named computation assertion there.
"""

from sage.functions.error import erf
from sage.functions.hyperbolic import cosh, sech, sinh, tanh
from sage.functions.log import exp
from sage.functions.other import abs_symbolic
from sage.functions.trig import arctan, cos, sin
from sage.calculus.calculus import limit
from sage.misc.cachefunc import cached_function
from sage.misc.latex import latex
from sage.rings.infinity import Infinity
from sage.rings.integer_ring import ZZ
from sage.rings.power_series_ring import PowerSeriesRing
from sage.rings.qqbar import AA
from sage.rings.rational_field import QQ
from sage.symbolic.expression import Expression
from sage.symbolic.integration.integral import integrate
from sage.symbolic.operators import add_vararg, mul_vararg
from sage.symbolic.ring import SR

import functools
import operator as _operator

from sage_extensions.categories.algebras.algebras import Algebras, _algebra_on_module
from sage_extensions.categories.modules.framed.formed.form_modules import (
    PairedModules,
    SymmetricBilinearFormModules,
)
from sage_extensions.categories.modules.general_modules import (
    _ConditionSubmodule,
    _ConditionSubmoduleElement,
    _FunctionModuleElement,
    _PointwiseValues,
    _condition_submodule,
)
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    VectorSpaces,
    _pointwise_negative,
    _pointwise_scalar_multiple,
    _pointwise_sum,
    _pointwise_zero,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import continuum
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.logic import AtomicProposition
from sage_extensions.rings.real import RR


def _regularity(k):
    if k is Infinity or k == Infinity:
        return Infinity
    integers = _owned_integers()
    k = integers(k)
    if k < integers.zero():
        raise ValueError(f"C^k is defined for k >= 0, but k = {k}")
    return k


def _integrability(p):
    r"""Normalize the positive extended-real exponent supplied at map ingress.

    The symbolic field is the private expression realization of the owned
    exact real. Rational exponents retain their integer/rational spelling;
    irrational exponents are not replaced by rational approximations.
    """
    from sage_extensions.logic import ask

    if p is Infinity:
        return Infinity
    real = RR(p)
    match ask(real > RR.zero()):
        case True:
            expression = real.expression()
            if expression in QQ:
                rational = _owned_engine_element(QQ, QQ(expression))
                integers = _owned_integers()
                return integers(rational) if rational in integers else rational
            return real
        case False:
            raise ValueError(f"L^p and ell^p are defined for p > 0, but p = {p}")
        case _:
            raise TypeError(
                f"L^p and ell^p are defined for p > 0, but it is undecided whether p = {p} is positive"
            )


def _exponent_key(exponent):
    r"""Private expression key for a normalized, possibly irrational exponent."""
    return ("infinity",) if exponent is Infinity else ("finite", RR(exponent).expression())


def _decided_nonzero(expression) -> bool:
    r"""Whether the exact real constant ``expression`` is decided to be nonzero, as an owned real."""
    from sage_extensions.logic import ask

    return ask(RR(expression) != RR.zero()) is True


def _affine_nonconstant(expression, variable) -> bool:
    r"""Whether ``expression`` is an affine polynomial with nonzero slope."""
    return (
        expression.is_polynomial(variable)
        and expression.degree(variable) == 1
        and _decided_nonzero(expression.coefficient(variable, 1))
    )


def _lebesgue_nonmembership_reason(expression, variable, exponent):
    r"""Return a theorem-backed reason that ``expression`` is not in this ``L^p``, else ``None``."""
    if expression.is_polynomial(variable) and expression.degree(variable) >= 1:
        return "a nonconstant polynomial is unbounded and has nonintegrable tails"

    if expression.operator() is exp and _affine_nonconstant(expression.operands()[0], variable):
        return "an exponential with nonzero affine exponent grows on one tail"

    if exponent is not Infinity and expression.operator() in (sin, cos):
        argument = expression.operands()[0]
        if _affine_nonconstant(argument, variable):
            return "a nonzero periodic wave has the same positive p-mass on infinitely many periods"

    return None


def _sequence_nonmembership_reason(expression, variable, exponent):
    r"""Return a theorem-backed reason that ``expression`` is not in this ``ell^p``, else ``None``."""
    if not expression.is_polynomial(variable):
        return None
    if exponent is Infinity:
        if expression.degree(variable) >= 1:
            return "a nonconstant polynomial sequence is unbounded"
        return None
    if _decided_nonzero(expression):
        return "a nonzero polynomial sequence does not tend to zero"
    return None


def _l2_real_polynomial(expression, variable):
    r"""Return ``expression`` as an exact real-algebraic polynomial, or ``None``."""
    if not expression.is_polynomial(variable):
        return None
    coefficients = expression.coefficients(variable, sparse=False)
    if not all(coefficient in AA for coefficient in coefficients):
        return None
    return AA[str(variable)](coefficients)


def _l2_rational_function(expression, variable):
    r"""Return an exact reduced real rational function ``(p,q)``, or ``None``."""
    numerator = _l2_real_polynomial(expression.numerator(), variable)
    denominator = _l2_real_polynomial(expression.denominator(), variable)
    if numerator is None or denominator is None:
        return None
    common = numerator.gcd(denominator)
    return numerator // common, denominator // common


def _l2_rational_verdict(expression, variable):
    r"""Decide square-integrability of an exact real rational function.

    In lowest terms ``p/q`` belongs to ``L^2(RR)`` exactly when ``q`` has no
    real root and ``deg(q) >= deg(p)+1``.  A real root is a genuine pole and
    the degree inequality is precisely the ``p``-test at infinity.
    """
    fraction = _l2_rational_function(expression, variable)
    if fraction is None:
        return None
    numerator, denominator = fraction
    if denominator.roots(AA):
        return False
    return denominator.degree() >= numerator.degree() + 1


def _l2_gaussian(expression, variable) -> bool:
    if expression.operator() is not exp:
        return False
    exponent = expression.operands()[0]
    return (
        exponent.is_polynomial(variable)
        and exponent.degree(variable) == 2
        and bool(exponent.coefficient(variable, 2) < 0)
    )


def _l2_polynomially_bounded(expression, variable) -> bool:
    if expression.is_polynomial(variable):
        return True
    if expression.operator() in (sin, cos):
        return expression.operands()[0].is_polynomial(variable)
    return False


def _l2_schwartz(expression, variable) -> bool:
    factors = (
        expression.operands()
        if expression.operator() is mul_vararg
        else (expression,)
    )
    return any(_l2_gaussian(factor, variable) for factor in factors) and all(
        _l2_gaussian(factor, variable)
        or _l2_polynomially_bounded(factor, variable)
        for factor in factors
    )


def _l2_bounded(expression, variable) -> bool:
    if expression.operator() in (sin, cos):
        return True
    fraction = _l2_rational_function(expression, variable)
    if fraction is None:
        return False
    numerator, denominator = fraction
    return (
        not denominator.roots(AA)
        and denominator.degree() >= numerator.degree()
    )


def _engine_square_integral_verdict(expression, variable):
    r"""Decide \(\int_{\mathbb R} f^2<\infty\) by Sage's symbolic integration.

    Private engine adapter (`OWN-06`).  Its one owning caller is
    :func:`_l2_symbolic_verdict`, after the exact criteria there have not
    decided the formula.  The upstream operation is
    ``sage.symbolic.integration.integral.integrate`` on \(f^2\) over
    \((-\infty,\infty)\) with its default engine.  The engine reports that it
    reached no closed answer by raising ``RuntimeError``, ``TypeError`` or
    ``ValueError``; this adapter is the one site that reads those exceptions,
    and it reads each as *undecided* (``None``), never as nonmembership.  A
    returned ``+Infinity`` is divergence (``False``), a returned numeric value
    is convergence (``True``), and any other symbolic value is undecided.
    """
    try:
        integral = integrate(expression**2, variable, -Infinity, Infinity)
    except (RuntimeError, TypeError, ValueError):
        return None
    if integral is Infinity or integral == Infinity:
        return False
    if SR(integral).is_numeric():
        return True
    return None


def _l2_symbolic_verdict(expression, variable):
    r"""Return ``True``, ``False`` or ``None`` for membership in ``L^2(RR)``.

    ``None`` means that the supported exact criteria do not decide the
    formula; construction then remains an explicit placement claim.  In
    particular, failure of symbolic integration is never interpreted as a
    proof of nonmembership.
    """
    rational = _l2_rational_verdict(expression, variable)
    if rational is not None:
        return rational

    if expression.operator() in (sin, cos):
        argument = expression.operands()[0]
        if argument.is_polynomial(variable) and argument.degree(variable) == 1:
            return False

    if _l2_schwartz(expression, variable):
        return True

    if expression.operator() is add_vararg:
        verdicts = tuple(
            _l2_symbolic_verdict(summand, variable)
            for summand in expression.operands()
        )
        if all(verdict is True for verdict in verdicts):
            return True
        if verdicts.count(False) == 1 and verdicts.count(None) == 0:
            return False

    if expression.operator() is mul_vararg:
        factors = expression.operands()
        for position, factor in enumerate(factors):
            others = factors[:position] + factors[position + 1 :]
            if all(_l2_bounded(other, variable) for other in others):
                if _l2_symbolic_verdict(factor, variable) is True:
                    return True

    if _tail_vanishes(expression, variable):
        return True
    return _engine_square_integral_verdict(expression, variable)



# The generators of the two classes of functions recognized structurally,
# each closed under the operations of _is_built_from: the first three are
# C^infinity, and all are continuous on the whole line.
_SMOOTH_FUNCTIONS = (exp, sin, cos)
_CONTINUOUS_FUNCTIONS = _SMOOTH_FUNCTIONS + (sinh, cosh, tanh, sech, arctan, erf, abs_symbolic)


def _is_built_from(expression, functions) -> bool:
    r"""Is expression a polynomial in functions and their compositions?

    Sums, products, nonnegative integer powers and compositions of
    polynomials and of the given functions preserve both \(C^\infty\) and
    continuity on \(\mathbb R\), so recognizing the class proves the
    property.  A power is admitted only for a nonnegative integer exponent.
    """
    operation = expression.operator()
    if operation is None:
        return True
    if operation in (add_vararg, mul_vararg):
        return all(_is_built_from(operand, functions) for operand in expression.operands())
    if operation is _operator.pow:
        base, exponent = expression.operands()
        return _is_built_from(base, functions) and exponent in ZZ and bool(exponent >= 0)
    if operation in functions:
        return all(_is_built_from(operand, functions) for operand in expression.operands())
    return False


def _tail_vanishes(expression, variable) -> bool:
    r"""Certify \(f\in L^2(\mathbb R)\) from \(|x|f(x)	o0\) at both ends, for continuous \(f\).

    Then \(f^2\le x^{-2}\) on both tails (the \(p\)-test) and continuity
    bounds the middle.  The limit goes to giac, which answers undef for
    an oscillating tail; a nonzero or undefined limit proves nothing.
    """
    if not _is_built_from(expression, _CONTINUOUS_FUNCTIONS):
        return False
    tails = [
        limit(abs(variable) * expression, algorithm="giac", **{str(variable): direction})
        for direction in (Infinity, -Infinity)
    ]
    return all(bool(tail == 0) for tail in tails)

def _parameter_name(value) -> str:
    if value is Infinity:
        return "Infinity"
    return str(value)


def _parameter_latex(value) -> str:
    if value is Infinity:
        return r"\infty"
    return str(latex(value))


def _space_name(space) -> str:
    if space is RR:
        return "RR"
    return repr(space)


def _space_latex(space) -> str:
    if space is RR:
        return r"\mathbb{R}"
    return str(latex(space))


def _conjugate_exponent(p):
    r"""The Hölder conjugate: \(1/p + 1/p' = 1\)."""
    if p is Infinity:
        return _owned_integers().one()
    if p == 1:
        return Infinity
    return _integrability(p / (p - 1))


def _are_holder_conjugates(p, q) -> bool:
    return _conjugate_exponent(p) == q



# ---------------------------------------------------------------------------
# The formula adapter.
# ---------------------------------------------------------------------------


def _function_formula(function):
    r"""The symbolic formula ``(body, variable)`` of a defining function, or ``None``.

    Private computation adapter (``OWN-06``) of this module.  Its datum is
    the function a map of ``Sets().Mor(X, Y)`` was constructed from
    (``OwnedSetMorphism._defining_function``).  A Sage callable symbolic
    expression in one argument (``f(t) = exp(-t^2)``) is its own formula in
    the variable it binds.  A map assembled by the pointwise module law
    (``_PointwiseValues``) has the formula of that operation applied to its
    operands' formulas, each read in a common variable.  A map built on an
    element of a module of maps is read through that element.  Any other
    callable has no formula: ``None`` here, and the operation that needs
    one states that frontier.
    """
    match function:
        case Expression() if len(function.arguments()) == 1:
            variable = function.arguments()[0]
            return function(variable), variable
        case _FunctionModuleElement():
            return _function_formula(function.underlying_element()._defining_function())
        case _PointwiseValues():
            operands = [
                _function_formula(operand._defining_function()) for operand in function.operands()
            ]
            if any(formula is None for formula in operands):
                return None
            variable = operands[0][1] if operands else SR.var("t")
            bodies = [body.subs({own: variable}) for body, own in operands]
            operation = function.operation()
            match operation:
                case _ if operation is _pointwise_sum:
                    return bodies[0] + bodies[1], variable
                case _ if operation is _pointwise_negative:
                    return -bodies[0], variable
                case _ if operation is _pointwise_zero:
                    return SR.zero(), variable
                case functools.partial() if operation.func is _pointwise_scalar_multiple:
                    return SR(operation.args[0]) * bodies[0], variable
                case _:
                    return None
        case _:
            return None


def _map_formula(element):
    r"""The formula ``(body, variable)`` of an element of a function space, or ``None``."""
    return _function_formula(element.underlying_element().underlying_element()._defining_function())


def _required_formula(element, operation):
    formula = _map_formula(element)
    assert formula is not None, (
        f"cannot compute {operation} of {element}: the map was given by a callable, not by a "
        "symbolic formula, and no other algorithm computes it"
    )
    return formula


def _formula_map(body, variable):
    r"""The callable symbolic expression ``variable |--> body``: a map given by its formula."""
    return SR(body).function(variable)


def _pointwise_product(left, right):
    r"""The defining function of ``t |-> left(t) right(t)``, keeping a formula when both have one."""
    left_formula, right_formula = _map_formula(left), _map_formula(right)
    if left_formula is not None and right_formula is not None:
        variable = left_formula[1]
        return _formula_map(left_formula[0] * right_formula[0].subs({right_formula[1]: variable}), variable)
    return lambda point: left(point) * right(point)


def _constant_map(value):
    r"""The defining function of the constant map with value ``value``."""
    return _formula_map(SR(value), SR.var("t"))


# ---------------------------------------------------------------------------
# Conditions.
# ---------------------------------------------------------------------------


def _differentiability_condition(regularity, domain):
    r"""The condition ``f`` is of class \(C^k\) on the manifold ``domain``.

    Decided for a formula in one real variable built from polynomials, exp,
    sin and cos: such a formula is \(C^\infty\) on \(\mathbb R\).  The
    formula's variable is a point of \(\mathbb R\), so the decision applies
    to ``domain`` \(=\mathbb R\) only; on any other domain the condition is
    the proposition that states it.
    """

    def condition(point):
        undecided = AtomicProposition(f"is_of_class_C^{_parameter_name(regularity)}", point)
        if domain is not RR:
            return undecided
        formula = _function_formula(point.underlying_element()._defining_function())
        if formula is not None and _is_built_from(formula[0], _SMOOTH_FUNCTIONS):
            return True
        return undecided

    return condition


def _lebesgue_condition(exponent):
    r"""The condition ``f`` is ``p``-integrable on \(\mathbb R\), decided by the theorem ladder on formulas."""

    def condition(point):
        formula = _function_formula(point.underlying_element()._defining_function())
        undecided = AtomicProposition(f"is_{_parameter_name(exponent)}_integrable", point)
        if formula is None:
            return undecided
        body, variable = formula
        if not body.variables() and exponent is not Infinity and _decided_nonzero(body):
            return False
        if _lebesgue_nonmembership_reason(body, variable, exponent) is not None:
            return False
        if (exponent == 2) is True:
            verdict = _l2_symbolic_verdict(body, variable)
            return undecided if verdict is None else verdict
        return undecided

    return condition


def _summability_condition(exponent, domain):
    r"""The condition ``a`` is ``p``-summable on the set ``domain`` (bounded for \(p=\infty\)).

    The nonmembership theorems below are about sequences: a formula in one
    variable read as \(n\in\mathbb N\).  They decide the condition for
    ``domain`` \(=\mathbb N\) only; on any other set the condition is the
    proposition that states it.
    """

    def condition(point):
        undecided = AtomicProposition(f"is_{_parameter_name(exponent)}_summable", point)
        if domain is not NN:
            return undecided
        formula = _function_formula(point.underlying_element()._defining_function())
        if formula is None:
            return undecided
        if _sequence_nonmembership_reason(formula[0], formula[1], exponent) is not None:
            return False
        return undecided

    return condition


# ---------------------------------------------------------------------------
# The function-space computation classes.
# ---------------------------------------------------------------------------


class _FunctionSpaceMap(_ConditionSubmoduleElement):
    r"""A map ``X -> Y`` in a function space: an element of ``Y^X`` admitted by the space's condition."""

    def __call__(self, point):
        r"""The value at ``point``."""
        return self.underlying_element()(point)

    def evaluate_at(self, point):
        r"""The value at ``point``."""
        return self(point)


class _FunctionSpace(_ConditionSubmodule):
    r"""Private computation class (``OWN-06``) of a space of maps ``X -> Y`` cut out of ``Y^X``."""

    def domain(self):
        r"""The set ``X`` the maps start at: the domain of the maps of ``Y^X``, the codomain of the inclusion."""
        return self.unformed_module().inclusion().codomain().domain()

    def codomain(self):
        r"""The module ``Y`` the maps take values in."""
        return self.unformed_module().inclusion().codomain().codomain()

    def __contains__(self, value) -> bool:
        r"""Whether ``value`` is a map ``X -> Y`` in this space.

        The argument is arbitrary.  A map of another space or of ``Y^X``,
        or a function on points (a callable, or a formula binding its own
        variable), is read by ``Sets().Mor(X, Y)`` and asked the condition.
        """
        from sage.structure.element import parent as element_parent
        from sage.structure.parent import Parent

        if element_parent(value) is self:
            return True
        if callable(value) and not isinstance(value, Parent):
            value = self.unformed_module().inclusion().codomain()(value)
        return super().__contains__(value)

    def one(self):
        r"""The constant map with value one."""
        return self(_constant_map(self.codomain().one()))


class _DifferentiableMap(_FunctionSpaceMap):
    r"""A map of class \(C^k\), with its calculus on formulas."""

    def compose(self, other):
        r"""Return \(f\circ g\), in \(C^{\min(k,\ell)}(W,Y)\)."""
        outer = self.parent()
        inner = other.parent()
        assert inner.codomain() is outer.domain(), (
            f"cannot compose {self} after {other}: {other} takes values in {inner.codomain()}, "
            f"not in {outer.domain()}"
        )
        k = min(outer.differentiability(), inner.differentiability())
        target = C(k, inner.domain(), outer.codomain())
        outer_formula, inner_formula = _map_formula(self), _map_formula(other)
        if outer_formula is None or inner_formula is None:
            return target(lambda point: self(other(point)))
        return target(_formula_map(outer_formula[0].subs({outer_formula[1]: inner_formula[0]}), inner_formula[1]))

    def derivative(self):
        r"""Return \(f'\), in \(C^{k-1}(X,Y)\) when \(k\) is finite."""
        space = self.parent()
        k = space.differentiability()
        assert k != 0, f"{self} is only of class C^0, so it has no C^k derivative"
        assert space.domain() is RR, (
            f"cannot differentiate {self}: the derivative is computed from a formula in one real "
            f"variable, which is the derivative on the domain RR, but {space} has domain {space.domain()}"
        )
        body, variable = _required_formula(self, "the derivative")
        target = space if k is Infinity else C(k - 1, space.domain(), space.codomain())
        return target(_formula_map(body.diff(variable), variable))

    def integral_from(self, lower):
        r"""Return \(x\mapsto\int_a^x f\), in \(C^{k+1}(\mathbb R,\mathbb R)\) when \(k\) is finite."""
        space = self.parent()
        assert space.domain() is RR, (
            f"cannot integrate {self}: the antiderivative is computed from a formula in one real "
            f"variable, which is the antiderivative on the domain RR, but {space} has domain {space.domain()}"
        )
        body, variable = _required_formula(self, "an antiderivative")
        antiderivative = body.integral(variable)
        k = space.differentiability()
        target = space if k is Infinity else C(k + 1, space.domain(), space.codomain())
        return target(_formula_map(antiderivative - antiderivative.subs({variable: SR(RR(lower))}), variable))

    def taylor_series(self, centre):
        r"""The Taylor series at ``centre`` in \(t=x-a\): untruncated for \(C^\infty\), the jet of order \(k\) otherwise."""
        space = self.parent()
        assert space.domain() is RR and space.codomain() is RR, (
            f"the Taylor series is defined here for maps RR -> RR, not for {space}"
        )
        body, variable = _required_formula(self, "the Taylor series")
        shifted = body.subs({variable: SR(RR(centre)) + variable})
        k = space.differentiability()
        if k is Infinity:
            from sage.rings.lazy_series_ring import LazyPowerSeriesRing

            return LazyPowerSeriesRing(SR, "t").taylor(shifted)
        jet = shifted.taylor(variable, ZZ.zero(), k)
        return PowerSeriesRing(SR, "t")(jet.subs({variable: SR.var("t")}))

    def maclaurin_series(self):
        r"""The Taylor series at \(0\)."""
        return self.taylor_series(ZZ.zero())


class _DifferentiabilityClass(_FunctionSpace):
    r"""The differentiability class \(C^k(X,Y)\); the datum this level adds is \(k\)."""

    def differentiability(self):
        return self._condition_engine_data["regularity"]

    def _cardinality_decision(self):
        r"""\(|C^k(\mathbb R,\mathbb R)|=2^{\aleph_0}\): a continuous map is fixed by its values on \(\mathbb Q\), and the constants give at least that many."""
        if self.domain() is RR and self.codomain() is RR:
            return continuum
        return super()._cardinality_decision()

    def integral(self, integrand, lower):
        r"""The map \(x\mapsto\int_a^x f(t)\,dt\)."""
        return self(integrand).integral_from(lower)

    def _repr_(self) -> str:
        return f"C({_parameter_name(self.differentiability())}, {_space_name(self.domain())}, {_space_name(self.codomain())})"

    def _latex_(self) -> str:
        return rf"C^{{{_parameter_latex(self.differentiability())}}}({_space_latex(self.domain())}, {_space_latex(self.codomain())})"


@cached_function(key=lambda regularity, domain, codomain: (_exponent_key(regularity), id(domain), id(codomain)))
def _differentiability_class(regularity, domain, codomain):
    r"""Build \(C^k(X,Y)\) as a condition submodule of \(Y^X\); for \(Y=\mathbb R\), the algebra on it."""
    assert codomain in VectorSpaces(RR), (
        f"C^k(X, Y) is a real vector space of maps, so Y must be a real vector space, but {codomain} is not"
    )
    module = _condition_submodule(
        codomain.function_module(domain),
        _differentiability_condition(regularity, domain),
        engine=(_DifferentiabilityClass, _DifferentiableMap),
        engine_data={"regularity": regularity},
        categories=(VectorSpaces(RR),),
    )
    if codomain is not RR:
        return module
    # C^k(X, RR) is closed under the pointwise product, which is bilinear,
    # associative and commutative with the constant one as unit.
    tensor = Modules(RR).tensor_product((module, module))
    multiplication = tensor.from_bilinear_map(
        module, lambda left, right: module(_pointwise_product(left, right))
    )
    return _algebra_on_module(
        module,
        multiplication,
        placement=(Algebras(RR).Associative().Unital().Commutative(),),
        unit=module.one(),
        law_decisions={"associativity": True, "unit": True, "commutativity": True},
    )


class _DifferentiabilityClassNotation:
    r"""The notation ``C(k, X, Y)`` for \(C^k(X,Y)\); \(\infty\) is a value of \(k\).

    EXAMPLES::

        sage: from dzack_research.preamble.all import Algebras, C, RR, VectorSpaces, exp
        sage: maps = C(Infinity, RR, RR)
        sage: maps in VectorSpaces(RR) and maps in Algebras(RR)
        True
        sage: g(t) = exp(-t^2)
        sage: maps(g)(0)
        1
    """

    def __call__(self, k, domain, codomain):
        return _differentiability_class(_regularity(k), domain, codomain)

    def __repr__(self) -> str:
        return "C"

    def _latex_(self) -> str:
        return "C"


C = _DifferentiabilityClassNotation()


def _l2_pairing(left, right):
    r"""\(\int_{\mathbb R} fg\) on maps given by formulas."""
    left_body, variable = _required_formula(left, "the integral of a product")
    right_body, right_variable = _required_formula(right, "the integral of a product")
    product = left_body * right_body.subs({right_variable: variable})
    return RR(product.integrate(variable, -Infinity, Infinity))


def _ell2_pairing(left, right):
    r"""\(\sum_{x\in X} a(x)b(x)\), computed as \(\sum_{n=0}^\infty a_n b_n\) on formulas.

    The sum runs over \(n=0,1,2,\dots\) in the formula's variable, which is
    the sum over \(X\) exactly when \(X=\mathbb N\); that is this
    computation's hypothesis, asserted here and not at the space.
    """
    domain = left.parent().domain()
    assert domain is NN, (
        f"cannot sum a({domain}) b({domain}) over {domain}: the sum is computed as sum_(n=0)^oo in the "
        f"formula's variable, which is the sum over the domain only when the domain is NN"
    )
    left_body, variable = _required_formula(left, "the sum of a product")
    right_body, right_variable = _required_formula(right, "the sum of a product")
    product = left_body * right_body.subs({right_variable: variable})
    return RR(product.sum(variable, ZZ.zero(), Infinity))


@cached_function
def _lebesgue_pairing_module(left, right):
    r"""The pairing \(\int fg\colon L^p\otimes L^{p'}\to\mathbb R\)."""
    if left is right:
        return left
    return PairedModules(RR)(left.pairings_with(right, RR)(_l2_pairing))


@cached_function
def _sequence_pairing_module(left, right):
    r"""The pairing \(\sum a_n b_n\colon \ell^p\otimes\ell^{p'}\to\mathbb R\)."""
    if left is right:
        return left
    return PairedModules(RR)(left.pairings_with(right, RR)(_ell2_pairing))


class _LebesgueSpace(_FunctionSpace):
    r"""\(\mathcal L^p(\mathbb R,\mathbb R)\); the datum this level adds is \(p\in(0,\infty]\).

    Its quotient by the maps vanishing almost everywhere is \(L^p\)
    (``quotient_by_null_functions``).  For \(p=2\) the object is the formed
    module with \(b(f,g)=\int fg\).  The form lives on functions, not on
    classes: \(b(f,f)=\int f^2\) vanishes exactly when \(f\) is null, so the
    radical of \(b\) is exactly the null functions and \(b\) is degenerate on
    \(\mathcal L^2\).  The Hilbert space \(L^2\) is the quotient of this
    formed module by its null functions, ``quotient_by_null_functions()``.
    A general \(\mathcal L^p\) is paired with \(\mathcal L^{p'}\) by Hölder,
    ``Lp(p, RR, RR) * Lp(p', RR, RR)``.
    """

    def integrability_exponent(self):
        return self._condition_engine_data["exponent"]

    def quotient_by_null_functions(self):
        r"""The Lebesgue space proper: these maps modulo equality almost everywhere."""
        from sage_extensions.categories.functions.lebesgue_quotients import _lebesgue_quotient

        return _lebesgue_quotient(self)

    def almost_everywhere_equal(self, left, right):
        r"""The proposition that the two integrable maps agree outside a null set."""
        from sage_extensions.categories.functions.lebesgue_quotients import AlmostEverywhereEquality

        return AlmostEverywhereEquality(self(left), self(right))

    def conjugate_lebesgue_space(self):
        r"""\(L^{p'}\) with \(1/p+1/p'=1\)."""
        return Lp(_conjugate_exponent(self.integrability_exponent()), self.domain(), self.codomain())

    def integration_morphism(self):
        r"""Integration \(L^1(\mathbb R)\to\mathbb R\), linear by the linearity of the Lebesgue integral."""
        if self.integrability_exponent() != 1:
            raise TypeError(
                f"integration is a linear functional on L^1(RR), but {self} has p = {self.integrability_exponent()}"
            )

        def evaluate(function, space=self):
            body, variable = _required_formula(space(function), "the integral")
            return RR(body.integrate(variable, -Infinity, Infinity))

        return Modules(RR).Mor(self, RR)._from_constructed_element_map(evaluate)

    def pairing_module(self):
        r"""The Hölder pairing module \(L^p\otimes L^{p'}\to\mathbb R\); for \(p=2\), \(L^2\) itself."""
        return self * self.conjugate_lebesgue_space()

    def __mul__(self, other):
        if not (_is_lebesgue_space(other) and _are_holder_conjugates(
            self.integrability_exponent(), other.integrability_exponent()
        )):
            raise TypeError(
                f"{self} (x) {other} -> RR is a pairing only of Lebesgue spaces with 1/p + 1/q = 1"
            )
        return _lebesgue_pairing_module(self, other)

    def _repr_(self) -> str:
        return f"L^{_parameter_name(self.integrability_exponent())}(RR, RR)"

    def _latex_(self) -> str:
        return rf"L^{{{_parameter_latex(self.integrability_exponent())}}}(\mathbb{{R}}, \mathbb{{R}})"


@cached_function(key=lambda exponent, domain, codomain: (_exponent_key(exponent), id(domain), id(codomain)))
def _lebesgue_space(exponent, domain, codomain):
    r"""Build \(\mathcal L^p(\mathbb R,\mathbb R)\) in \(\mathbb R^{\mathbb R}\); for \(p=2\), equipped with \(\int fg\).

    The \(p=2\) form is on functions; its radical is the null functions,
    and \(L^2\) is ``quotient_by_null_functions()`` of the result.
    """
    assert domain is RR and codomain is RR, (
        f"L^p(X, Y) is implemented for Lebesgue measure on X = RR and Y = RR, not for X = {domain}, Y = {codomain}"
    )
    module = _condition_submodule(
        RR.function_module(RR),
        _lebesgue_condition(exponent),
        engine=(_LebesgueSpace, _FunctionSpaceMap),
        engine_data={"exponent": exponent},
        categories=(VectorSpaces(RR),),
    )
    if (exponent == 2) is not True:
        return module
    return SymmetricBilinearFormModules(RR)(module.bilinear_forms(RR)(_l2_pairing))


def Lp(p, domain, codomain):
    r"""The space \(\mathcal L^p(X,Y)\) of \(p\)-integrable maps \(X\to Y\)."""
    return _lebesgue_space(_integrability(p), domain, codomain)


class _SequenceSpace(_FunctionSpace):
    r"""\(\ell^p(X,\mathbb R)\) for a set \(X\); the datum this level adds is \(p\in(0,\infty]\).

    The \(p\)-summable maps for counting measure on \(X\): \(\sum_{x\in X}|a(x)|^p<\infty\),
    bounded maps for \(p=\infty\).  For \(p=2\) the object is the formed
    module with \(b(a,c)=\sum_{x\in X}a(x)c(x)\) on functions.  Counting
    measure has no nonempty null set, so \(b(a,a)=\sum_x a(x)^2\) vanishes
    only at \(a=0\): the radical of \(b\) is zero, and no quotient is taken.
    """

    def integrability_exponent(self):
        return self._condition_engine_data["exponent"]

    def conjugate_sequence_space(self):
        r"""\(\ell^{p'}\) with \(1/p+1/p'=1\)."""
        return ell(_conjugate_exponent(self.integrability_exponent()), self.domain(), self.codomain())

    def pairing_module(self):
        return self * self.conjugate_sequence_space()

    def __mul__(self, other):
        if not (_is_sequence_space(other) and _are_holder_conjugates(
            self.integrability_exponent(), other.integrability_exponent()
        )):
            raise TypeError(
                f"{self} (x) {other} -> RR is a pairing only of sequence spaces with 1/p + 1/q = 1"
            )
        return _sequence_pairing_module(self, other)

    def _repr_(self) -> str:
        return f"ell^{_parameter_name(self.integrability_exponent())}({_space_name(self.domain())}, RR)"

    def _latex_(self) -> str:
        return rf"\ell^{{{_parameter_latex(self.integrability_exponent())}}}({_space_latex(self.domain())}, \mathbb{{R}})"


@cached_function(key=lambda exponent, domain, codomain: (_exponent_key(exponent), id(domain), id(codomain)))
def _sequence_space(exponent, domain, codomain):
    r"""Build \(\ell^p(X,\mathbb R)\) in \(\mathbb R^X\) for a set \(X\); for \(p=2\), equipped with \(\sum_x a(x)c(x)\)."""
    assert codomain is RR, (
        f"ell^p(X, Y) is implemented for real-valued sequences, Y = RR, not for Y = {codomain}"
    )
    module = _condition_submodule(
        RR.function_module(domain),
        _summability_condition(exponent, domain),
        engine=(_SequenceSpace, _FunctionSpaceMap),
        engine_data={"exponent": exponent},
        categories=(VectorSpaces(RR),),
    )
    if (exponent == 2) is not True:
        return module
    return SymmetricBilinearFormModules(RR)(module.bilinear_forms(RR)(_ell2_pairing))


class _SequenceSpaceNotation:
    r"""The notation ``ell(p, X, Y)`` for \(\ell^p(X,Y)\), \(X\) any set."""

    def __call__(self, p, domain, codomain):
        return _sequence_space(_integrability(p), domain, codomain)

    def __repr__(self) -> str:
        return "ell"

    def _latex_(self) -> str:
        return r"\ell"


ell = _SequenceSpaceNotation()


def _is_function_space(space) -> bool:
    r"""Declared engine adapter (``OWN-06``): whether ``space`` is realized by :class:`_FunctionSpace`."""
    return isinstance(space, _FunctionSpace)


def _is_differentiability_class(space) -> bool:
    r"""Declared engine adapter (``OWN-06``): whether ``space`` is a \(C^k(X,Y)\) realized here."""
    return isinstance(space, _DifferentiabilityClass)


def _is_lebesgue_space(space) -> bool:
    r"""Declared engine adapter (``OWN-06``): whether ``space`` is an \(\mathcal L^p\) realized here.

    Its callers are the Hölder product and the graded Lebesgue modules.
    """
    return isinstance(space, _LebesgueSpace)


def _is_sequence_space(space) -> bool:
    r"""Declared engine adapter (``OWN-06``): whether ``space`` is an \(\ell^p\) realized here."""
    return isinstance(space, _SequenceSpace)
