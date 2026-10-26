r"""Lebesgue classes of real integrable maps modulo null functions.

The quotient relation is equality off a Lebesgue-null subset of R.  This
is the relation on MeasureTheory.AEEqFun underlying MeasureTheory.Lp; see
Mathlib/MeasureTheory/Function/AEEqFun and Function/LpSpace/Basic.  The map
space retains point evaluation; the quotient does not inherit it.
"""

from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.unknown import Unknown
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.modules.general_modules import GeneralModules
from sage_extensions.categories.modules.pure.modules import Modules, VectorSpaces
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of
from sage_extensions.logic import Predicate, ask, negation
from sage_extensions.rings.real import RR


def _symbolic_ae_equality(left, right):
    r"""Decide nullity of the nonzero locus by the maintained symbolic set solver.

    Declared private engine adapter (``OWN-06``): SymPy ``solveset`` returns the full solution set
    (including ConditionSet for unresolved parts), not a list of found roots.
    Set.measure is its Lebesgue measure.  Only a decided zero/positive measure
    of the complement settles equality.  No point sample disproves a.e.
    equality, and failed symbolic computations return Unknown.

    Sources: docs.sympy.org/latest/modules/solvers/solveset.html and
    docs.sympy.org/latest/modules/sets.html, Set.measure.
    """
    import sympy

    if left is right:
        return True
    from sage_extensions.categories.functions.real_functions import _map_formula

    left_formula, right_formula = _map_formula(left), _map_formula(right)
    if left_formula is None or right_formula is None:
        return Unknown
    try:
        x = sympy.Symbol("x", real=True)
        f = left_formula[0]._sympy_().subs(left_formula[1]._sympy_(), x)
        g = right_formula[0]._sympy_().subs(right_formula[1]._sympy_(), x)
        difference = sympy.piecewise_fold((f - g).rewrite(sympy.Piecewise))
        zeros = sympy.solveset(difference, x, domain=sympy.S.Reals)
        measure = (sympy.S.Reals - zeros).measure
        match (measure.is_zero, measure.is_positive, measure == sympy.oo):
            case (True, _, _):
                return True
            case (_, True, _) | (_, _, True):
                return False
            case _:
                return Unknown
    except (NotImplementedError, TypeError, ValueError, AttributeError):
        return Unknown


class AlmostEverywhereEquality(Predicate):
    r"""The proposition that two represented measurable real maps agree a.e."""

    def __init__(self, left, right):
        assert left.parent().domain() is RR and right.parent().domain() is RR
        assert left.parent().codomain() is RR and right.parent().codomain() is RR
        self._left = left
        self._right = right
        super().__init__()

    def left(self):
        return self._left

    def right(self):
        return self._right

    def _ask_(self, *, max_prec=4096):
        return _symbolic_ae_equality(self.left(), self.right())

    def _repr_(self):
        return f"{self.left()} = {self.right()} almost everywhere on R"


class _AEClass:
    def __init__(self, parent, representative):
        self._representative = parent.map_space()(representative)
        super().__init__(parent)

    def representative(self):
        return self._representative

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        statement = AlmostEverywhereEquality(self.representative(), other.representative())
        decision = ask(statement)
        equal = statement if decision is Unknown else decision
        return equal if op == op_EQ else negation(equal)

    __hash__ = None

    def _repr_(self):
        return f"[{self.representative()}] a.e."


class _AEClasses:
    def __init__(self, map_space, **rest):
        self._map_space = map_space
        super().__init__(**rest)

    def map_space(self):
        return self._map_space

    def __call__(self, value):
        if element_parent(value) is self:
            return value
        return self.element_class(self, self.map_space()(value))

    def __contains__(self, value):
        return element_parent(value) is self

    def zero(self):
        return self(self.map_space().zero())

    an_element = zero

    def add(self, left, right):
        return self(self(left).representative() + self(right).representative())

    def negate(self, value):
        return self(-self(value).representative())

    def scale(self, scalar, value):
        return self(self.map_space().scalar_multiple(scalar, self(value).representative()))


@cached_function(key=id)
def _ae_class_set(space):
    return _object_of(Sets(), _engine=(Sets(), _AEClasses, _AEClass), map_space=space)


class _LebesgueClassElement:
    def representative(self):
        r"""The selected map representing this class, not an evaluation of the class."""
        return self.underlying_element().representative()

    def almost_everywhere_equal(self, other):
        return AlmostEverywhereEquality(self.representative(), self.parent()(other).representative())


class _LebesgueQuotient:
    def __init__(self, map_space, **rest):
        self._map_space = map_space
        classes = _ae_class_set(map_space)
        super().__init__(
            underlying_set=classes, addition=classes.add, zero=classes.zero(),
            negation=classes.negate, scalar_action=classes.scale, **rest,
        )

    def map_space(self):
        return self._map_space

    def integrability_exponent(self):
        return self.map_space().integrability_exponent()

    def _element_constructor_(self, value):
        source = element_parent(value)
        if source is self or source in Modules(RR) and self._built_on_the_same_data(source):
            return super()._element_constructor_(value)
        if source is self.underlying_set():
            return super()._element_constructor_(value)
        return super()._element_constructor_(self.underlying_set()(self.map_space()(value)))

    def _module_with_structure(self, categories, construction_data):
        return _quotient_with_structure(self.map_space(), categories, construction_data)

    def convolution_pairing(self, other):
        r"""The Young pairing on these two quotient spaces, with its exact target."""
        from sage_extensions.categories.functions.convolution import _convolution_pairing

        return _convolution_pairing(self, other)

    @cached_method
    def quotient_projection(self):
        r"""The linear quotient map from integrable maps to their a.e. classes."""
        return Modules(RR).Mor(self.map_space(), self)._from_constructed_element_map(self)

    @cached_method
    def integration_morphism(self):
        r"""The integral descends because integrable null functions have integral zero."""
        integration = self.map_space().integration_morphism()
        return Modules(RR).Mor(self, RR)._from_constructed_element_map(
            lambda element: integration(self(element).representative()),
            premises=(integration,),
        )

    def _repr_(self):
        return f"L^{self.integrability_exponent()}(R), modulo almost-everywhere equality"


def _quotient_with_structure(space, categories=(), construction_data=None):
    category = Cat().meet((GeneralModules(RR), VectorSpaces(RR), *categories))
    return _object_of(
        category, _engine=(GeneralModules(RR), _LebesgueQuotient, _LebesgueClassElement),
        base_ring=RR, map_space=space, **(construction_data or {}),
    )


@cached_function(key=id)
def _lebesgue_quotient(space):
    return _quotient_with_structure(space)


def _is_lebesgue_quotient(space):
    r"""Recognize the private Lebesgue quotient realization at literal ingress.

    Declared engine adapter (``OWN-06``): the quotient is mathematically placed
    in its module/vector-space categories; this predicate distinguishes its
    private representative engine only where the element constructor must
    decode literal quotient data.
    """
    return isinstance(space, _LebesgueQuotient)
