r"""The Young-admissible family of convolution pairings on Lebesgue classes.

For p,q,r>=1 and 1/p+1/q=1+1/r, Young gives Lp tensor Lq -> Lr.
For finite r the proof is Holder on
 (|f|^p |g|^q)^(1/r) |f|^(1-p/r) |g|^(1-q/r), followed by Tonelli;
raising to r and integrating gives ||f*g||_r^r <= ||f||_p^r ||g||_q^r.
The conjugate (r=infinity) case is Holder directly, and p=q=r=1 is
Tonelli. Null changes do not affect convolution (Mathlib Analysis/Convolution,
convolution_congr). Thus these are well-defined bilinear maps on the quotients.
They are not one total product on the sum of every Lp.
"""

from sage.misc.cachefunc import cached_function
from sage.rings.infinity import Infinity
from sage.symbolic.ring import SR

from sage_extensions.categories.algebras.algebras import Algebras, _algebra_on_module
from sage_extensions.categories.functions.real_functions import Lp
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.rings.real import RR, _owned_real_from_engine_expression
from sage_extensions.rings.unit_interval import UnitInterval


def _holder_degree(space):
    exponent = space.integrability_exponent()
    return UnitInterval.zero() if exponent is Infinity else UnitInterval(RR.one() / RR(exponent))


def _space_at_degree(degree):
    value = degree.as_extended_real()
    exponent = Infinity if (value == RR.zero()) is True else RR.one() / value
    return Lp(exponent, RR, RR).quotient_by_null_functions()


@cached_function(key=lambda left, right: (id(left), id(right)))
def _symbolic_convolution(left, right):
    r"""Private SymPy integral of the existing representative formulas.

    Declared private engine adapter (``OWN-06``).  SymPy may signal that its
    exact integrator has no implementation for the supplied expression by
    raising ``NotImplementedError`` or ``ValueError``; the mathematical result
    is then the exact unevaluated ``Integral``, not a failed convolution.

    Uses integrate over the full real line, not quadrature or finite samples.
    A remaining Integral is retained as an unevaluated exact expression.
    Opaque callable representatives keep their integral definition but have
    no symbolic evaluator in this adapter.
    """
    import sympy

    from sage_extensions.categories.functions.real_functions import _map_formula

    left_formula, right_formula = _map_formula(left), _map_formula(right)
    if left_formula is None or right_formula is None:
        return None
    x = sympy.Symbol("x", real=True)
    t = sympy.Dummy("t", real=True)
    f = left_formula[0]._sympy_().subs(left_formula[1]._sympy_(), t)
    g = right_formula[0]._sympy_().subs(right_formula[1]._sympy_(), x - t)
    integrand = sympy.piecewise_fold((f * g).rewrite(sympy.Piecewise))
    try:
        expression = sympy.integrate(integrand, (t, -sympy.oo, sympy.oo))
    except (NotImplementedError, ValueError):
        expression = sympy.Integral(integrand, (t, -sympy.oo, sympy.oo))
    return expression, x


def _engine_global_continuous_formula(expression, variable):
    r"""Return whether SymPy proves this exact expression continuous on ``RR``.

    Declared private engine adapter (``OWN-06``).  ``continuous_domain`` may
    raise when its protocol cannot decide a symbolic domain.  That engine
    failure means only that no display formula is selected; point evaluation
    continues through the exact integral expression.
    """
    import sympy
    from sympy.calculus.util import continuous_domain

    try:
        return (
            not expression.has(sympy.Integral)
            and continuous_domain(expression, variable, sympy.S.Reals)
            == sympy.S.Reals
        )
    except (NotImplementedError, TypeError, ValueError):
        return False


def _convolution_representative(space, left, right):
    r"""The integral representative, zero at exceptional nonintegrable points.

    This is the second declared SymPy boundary (``OWN-06``): it asks the
    maintained ``continuous_domain`` operation whether a closed formula is
    globally represented before crossing it into the owned function space.
    Young's hypotheses guarantee those exceptions form a null set. This
    convention never supplies a product for an inadmissible exponent pair.
    The symbolic adapter may leave exact evaluations undecided; that is not
    evidence of divergence and must not be turned into zero.
    """
    import sympy

    symbolic = _symbolic_convolution(left, right)
    formula = None
    if symbolic is not None:
        expression, variable = symbolic
        assert expression not in (sympy.oo, -sympy.oo, sympy.zoo, sympy.nan), (
            f"the convolution {left} * {right} is infinite ({expression}): the two functions do not satisfy "
            "the integrability hypotheses of Young's inequality"
        )
        if _engine_global_continuous_formula(expression, variable):
            point = SR.var("x")
            formula = SR(expression).subs({SR(str(variable)): point}).function(point)

    def evaluate(point):
        assert symbolic is not None, (
            f"cannot evaluate the convolution {left} * {right} at {point}: both functions must be given by "
            "formulas"
        )
        expression, variable = symbolic
        value = expression.subs(variable, RR(point).expression()._sympy_()).doit()
        if value in (sympy.oo, -sympy.oo, sympy.zoo, sympy.nan):
            return RR.zero()
        assert not value.has(sympy.Integral), (
            f"cannot evaluate the convolution {left} * {right} at {point}: the integral {value} has no "
            "closed form"
        )
        return _owned_real_from_engine_expression(SR(value))

    return space(evaluate if formula is None else formula)


@cached_function(key=lambda left, right: (id(left), id(right)))
def _convolution_pairing(left, right):
    r"""The linear classifier Lp tensor_R Lq -> Lr on a Young-admissible pair."""
    s, t = _holder_degree(left), _holder_degree(right)
    pair = UnitInterval.degree_pairs()(lambda index: s if int(index) == 0 else t)
    degree = UnitInterval.young_degree_map()(pair)
    target = _space_at_degree(degree)
    tensor = Modules(RR).tensor_product((left, right))

    def product(f, g):
        f, g = left(f), right(g)
        return target(_convolution_representative(target.map_space(), f.representative(), g.representative()))

    return tensor.from_bilinear_map(target, product)


@cached_function
def _convolution_pairing_family():
    return indexed_family(UnitInterval.young_pairs(), lambda pair:
        _convolution_pairing(_space_at_degree(pair.component(0)), _space_at_degree(pair.component(1))))


@cached_function
def _convolution_algebra():
    r"""The total L1 convolution algebra, within the full Young family.

    Fubini gives associativity and integral(f*g)=integral(f)integral(g).
    Substitution gives commutativity. The family for other exponents remains
    separately available; L-infinity is not silently included in this algebra.
    """
    module = Lp(1, RR, RR).quotient_by_null_functions()
    multiplication = module.convolution_pairing(module)
    return _algebra_on_module(
        module,
        multiplication,
        placement=(Algebras(RR).Associative(), Algebras(RR).Commutative()),
        law_decisions={"associativity": True, "commutativity": True},
    )
