r"""Owned ring implementations and the public ring-construction surface."""

from sage_extensions.categories.rings.commutative_algebra import (
    AdicCompletions,
    DistinguishedOpenSubobjects,
    FormalPowerSeriesRings,
    GeneratedIdealView,
    PrimeLocalizations,
    PrimeSpectra,
    QuotientRings,
    ZariskiClosedSubobjects,
    Zp,
)
from sage_extensions.categories.rings.commutative_ideals import (
    CommutativeIdeals,
)
from sage_extensions.categories.rings.number_fields import (
    CyclotomicField as _CyclotomicField,
)
from sage_extensions.categories.rings.number_fields import (
    NumberFieldsWithChosenPrimitiveElement,
    OwnedNumberFields,
)
from sage_extensions.categories.rings.number_fields import (
    QuadraticField as _QuadraticField,
)
from sage_extensions.categories.rings.ring_foundation import (
    GF as _GF,
)
from sage_extensions.categories.rings.ring_foundation import (
    AdicallyCompleteRings,
    ArtinianRings,
    CommutativeRings,
    CompleteLocalRings,
    CoordinateMatrixRings,
    DivisionRings,
    Fields,
    IntegralDomains,
    LocalizationRings,
    LocalRings,
    NoetherianRings,
    OrderedRings,
    Orders,
    binomial,
    OwnedAdicallyCompleteRings,
    OwnedArtinianRings,
    OwnedCategoryOverBaseRing,
    OwnedCommutativeRings,
    OwnedCompleteLocalRings,
    OwnedDivisionRings,
    OwnedFields,
    OwnedIntegralDomains,
    OwnedLocalRings,
    OwnedNoetherianRings,
    OwnedOrderedRings,
    OwnedOrders,
    OwnedPrincipalIdealDomains,
    OwnedRings,
    OwnedRngs,
    OwnedSemirings,
    PredicateSubrings,
    PrimeFields,
    PrincipalIdealDomains,
    RingMor,
    RingMorphism,
    Rings,
    _own_ring,
    _set_owned_ring_display,
    _owned_algebraic_numbers,
    _owned_complex_double_field,
    _owned_integers,
    _owned_rationals,
    _owned_real_algebraic_numbers,
    _owned_real_double_field,
)
from sage_extensions.categories.rings.ring_foundation import (
    ComplexField as _ComplexField,
)
from sage_extensions.categories.rings.ring_foundation import (
    Qp as _Qp,
)
from sage_extensions.categories.rings.ring_foundation import (
    RealField as _RealField,
)
from sage_extensions.categories.rings.ring_foundation import (
    Zmod as _Zmod,
)
from sage_extensions.rings.nonnegative_reals import NonNegativeReals
from sage_extensions.rings.complex import (
    CC,
    ComplexRelation,
    ExactComplexField,
    ExactComplexNumber,
    I,
    cos,
    cosh,
    exp,
    log,
    sech,
    sgn,
    sin,
    sinh,
    sqrt,
    tan,
    tanh,
    zeta,
)
from sage_extensions.rings.real import (
    RR,
    e,
    pi,
    ExactRealField,
    ExactRealNumber,
    RealApproximation,
    RealNumber,
)
from sage_extensions.rings.unit_interval import UnitInterval


def _public_commutative_ring(ring):
    if ring not in OwnedRings().Commutative():
        raise TypeError(
            f"expected a commutative ring, but {ring!r} is not in the category of commutative rings"
        )
    return ring


def GF(order, name=None):
    return _public_commutative_ring(_GF(order, name))


def Zmod(modulus):
    return _public_commutative_ring(_Zmod(modulus))


def Qp(prime, precision=20):
    return _public_commutative_ring(_Qp(prime, precision))


def RealField(precision=53):
    return _public_commutative_ring(_RealField(precision))


def ComplexField(precision=53):
    return _public_commutative_ring(_ComplexField(precision))


def CyclotomicField(order, name=None):
    return _CyclotomicField(order, name)


def QuadraticField(discriminant, name="a"):
    return _QuadraticField(discriminant, name)


# The session's scalar names.  Each is the one owned object of its name, bound
# here in this module's body so that the session imports it from this module's
# ``__all__`` like every other name it publishes: a name's definition and its
# binding are the same statement, and no function of another module writes the
# session's namespace while it imports (AGENTS, §4 "One source of truth, stated
# once, inline").
ZZ = _owned_integers()
QQ = _owned_rationals()
AA = _public_commutative_ring(_owned_real_algebraic_numbers())
QQbar = _public_commutative_ring(_owned_algebraic_numbers())
RDF = _public_commutative_ring(_owned_real_double_field())
CDF = _public_commutative_ring(_owned_complex_double_field())

_set_owned_ring_display(ZZ, "Integer Ring")
_set_owned_ring_display(QQ, "Rational Field")
_set_owned_ring_display(AA, "Real Algebraic Field")
_set_owned_ring_display(QQbar, "Algebraic Closure of Rational Field")
_set_owned_ring_display(RDF, "Real double field", kind="real")
_set_owned_ring_display(CDF, "Complex double field", kind="complex")


def _restore_session_ring_bindings(scope: dict) -> None:
    r"""Restore public scalar names after Sage code has modified a namespace.

    This is namespace repair only: every object bound here is this module's own,
    already fully constructed owned object.  The scope a repair is asked for is
    the one a load wrote a file into; the session's own namespace is not one of
    them, because ``sage_extensions/all.py`` binds each of its names itself.
    """
    scope.update(
        ZZ=ZZ,
        QQ=QQ,
        AA=AA,
        QQbar=QQbar,
        RR=RR,
        RDF=RDF,
        CDF=CDF,
        CC=CC,
        GF=GF,
        Zmod=Zmod,
        Zp=Zp,
        Qp=Qp,
        RealField=RealField,
        ComplexField=ComplexField,
        CyclotomicField=CyclotomicField,
        QuadraticField=QuadraticField,
    )
    for name in _REMOVED_ENGINE_SPELLINGS:
        scope.pop(name, None)


# AGENTS.md, *The preamble is a universe over Sage*: "where Sage spells one
# mathematical operation several ways, the preamble picks one spelling and the
# others do not exist in the session".  The session spells F_q and ZZ/(n) as
# GF and Zmod (and the category constructor PrimeFields()(p)); Sage's other
# spellings of the same constructors -- IntegerModRing and Integers
# (sage/rings/all.py), FiniteField (sage/rings/finite_rings/all.py) -- are
# removed from a session scope that sage.all populated, not rebound to stubs.
_REMOVED_ENGINE_SPELLINGS = ("FiniteField", "IntegerModRing", "Integers")


__all__ = [
    "AA",
    "AdicCompletions",
    "AdicallyCompleteRings",
    "ArtinianRings",
    "CDF",
    "CommutativeIdeals",
    "CommutativeRings",
    "OwnedCommutativeRings",
    "CompleteLocalRings",
    "ComplexField",
    "CoordinateMatrixRings",
    "CyclotomicField",
    "DistinguishedOpenSubobjects",
    "DivisionRings",
    "ExactRealField",
    "ExactRealNumber",
    "Fields",
    "FormalPowerSeriesRings",
    "GF",
    "GeneratedIdealView",
    "IntegralDomains",
    "LocalizationRings",
    "LocalRings",
    "NoetherianRings",
    "NonNegativeReals",
    "NumberFieldsWithChosenPrimitiveElement",
    "OrderedRings",
    "Orders",
    "OwnedAdicallyCompleteRings",
    "OwnedArtinianRings",
    "OwnedCategoryOverBaseRing",
    "OwnedCompleteLocalRings",
    "OwnedDivisionRings",
    "OwnedFields",
    "OwnedIntegralDomains",
    "OwnedLocalRings",
    "OwnedNoetherianRings",
    "OwnedNumberFields",
    "OwnedOrders",
    "OwnedOrderedRings",
    "OwnedPrincipalIdealDomains",
    "OwnedRings",
    "OwnedRngs",
    "OwnedSemirings",
    "PredicateSubrings",
    "PrimeFields",
    "PrimeLocalizations",
    "PrimeSpectra",
    "PrincipalIdealDomains",
    "QQ",
    "QQbar",
    "Qp",
    "QuadraticField",
    "QuotientRings",
    "RDF",
    "RR",
    "CC",
    "ComplexRelation",
    "ExactComplexField",
    "ExactComplexNumber",
    "I",
    "binomial",
    "cos",
    "cosh",
    "e",
    "exp",
    "log",
    "pi",
    "sech",
    "sgn",
    "sin",
    "sinh",
    "sqrt",
    "tan",
    "tanh",
    "zeta",
    "RealApproximation",
    "RealField",
    "RealNumber",
    "RingMor",
    "RingMorphism",
    "Rings",
    "UnitInterval",
    "ZariskiClosedSubobjects",
    "ZZ",
    "Zmod",
    "Zp",
]
