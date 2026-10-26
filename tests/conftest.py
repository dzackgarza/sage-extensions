r"""Named specimens a mathematician expects a session to hold.

Each family below is the standard list of members of one class of rings, built
through the session's own constructors.  The families are written from the
mathematics: a family names what belongs to the class, not what the preamble
happens to accept today, so a member that fails to build is a finding, never a
row to drop.

The families nest as the classes do,

    fields ⊂ principal ideal domains ⊂ Dedekind domains ⊂ Noetherian domains
           ⊂ commutative rings ⊂ rings,

and the local, complete, Artinian and finite families cut across that chain.

A test names a family by its fixture name (``pid``, ``field``, ``local_ring``,
...) and receives one member per run, so a construction a mathematician
expects to work over every principal ideal domain is written once and tried
over each of them.  ``build(name)`` returns one member by its catalogue name
for the tests that state a known value about a particular ring.
"""

import builtins
import functools

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _protected_hom_notation(source, target):
    """Read the protected notebook spelling through the owned Mor operation."""
    return source.Mor(target)


builtins.Hom = _protected_hom_notation


def _polynomial_ring(ring, *names):
    return ring.polynomial_ring(names if len(names) > 1 else names[0])


def _quotient(ring, *generators):
    return ring.quotient_ring(ring.ideal(*generators))


def _rationals_cube_root_of_two():
    polynomials = _polynomial_ring(QQ, "x")
    x = polynomials.algebra_generator("x")
    return (x**3 - polynomials(2)).number_field("c")


def _cusp():
    ring = _polynomial_ring(QQ, "x", "y")
    x = ring.algebra_generator("x")
    y = ring.algebra_generator("y")
    return _quotient(ring, y**2 - x**3)


def _coordinate_axes():
    ring = _polynomial_ring(QQ, "x", "y")
    return _quotient(ring, ring.algebra_generator("x") * ring.algebra_generator("y"))


def _localized_polynomial_ring_at_origin():
    ring = _polynomial_ring(QQ, "x")
    return ring.localize_at_prime(ring.ideal(ring.algebra_generator("x")))


def _localized_plane_at_origin():
    ring = _polynomial_ring(QQ, "x", "y")
    return ring.localize_at_prime(
        ring.ideal(ring.algebra_generator("x"), ring.algebra_generator("y"))
    )


FIELDS = {
    "QQ": lambda: QQ,
    "RR": lambda: RR,
    "CC": lambda: CC,
    "AA": lambda: AA,
    "QQbar": lambda: QQbar,
    "GF(5)": lambda: GF(5),
    "GF(4)": lambda: GF(4),
    "GF(27)": lambda: GF(27),
    "QQ_3": lambda: Qp(3),
    "QQ(i)": lambda: QuadraticField(-1, "i"),
    "QQ(sqrt5)": lambda: QuadraticField(5, "s"),
    "QQ(sqrt-5)": lambda: QuadraticField(-5, "s"),
    "QQ(sqrt-23)": lambda: QuadraticField(-23, "s"),
    "QQ(zeta5)": lambda: CyclotomicField(5, "z"),
    "QQ(cbrt2)": _rationals_cube_root_of_two,
    "QQ(x)": lambda: _polynomial_ring(QQ, "x").fraction_field(),
    "GF(5)(t)": lambda: _polynomial_ring(GF(5), "t").fraction_field(),
    "QQ[x]/(x^2+1)": lambda: _quotient(
        _polynomial_ring(QQ, "x"), _polynomial_ring(QQ, "x").algebra_generator("x") ** 2 + 1
    ),
}

DISCRETE_VALUATION_RINGS = {
    "ZZ_3": lambda: Zp(3),
    "ZZ_(5)": lambda: ZZ.localize_at_prime(5),
    "QQ[[t]]": lambda: QQ.power_series_ring("t"),
    "QQ[x]_(x)": _localized_polynomial_ring_at_origin,
    "ZZ^_2": lambda: ZZ.adic_completion(ZZ.ideal(2)),
}

PRINCIPAL_IDEAL_DOMAINS_NOT_FIELDS = {
    "ZZ": lambda: ZZ,
    "QQ[x]": lambda: _polynomial_ring(QQ, "x"),
    "GF(5)[t]": lambda: _polynomial_ring(GF(5), "t"),
    "ZZ[i]": lambda: QuadraticField(-1, "i").ring_of_integers(),
    "ZZ[phi]": lambda: QuadraticField(5, "s").ring_of_integers(),
    "ZZ[zeta5]": lambda: CyclotomicField(5, "z").ring_of_integers(),
    "ZZ[cbrt2]": lambda: _rationals_cube_root_of_two().ring_of_integers(),
    **DISCRETE_VALUATION_RINGS,
}

DEDEKIND_DOMAINS_NOT_PRINCIPAL = {
    "ZZ[sqrt-5]": lambda: QuadraticField(-5, "s").ring_of_integers(),
    "ZZ[(1+sqrt-23)/2]": lambda: QuadraticField(-23, "s").ring_of_integers(),
}

NOETHERIAN_DOMAINS_NOT_DEDEKIND = {
    "ZZ[x]": lambda: _polynomial_ring(ZZ, "x"),
    "QQ[x,y]": lambda: _polynomial_ring(QQ, "x", "y"),
    "QQ[x,y]/(y^2-x^3)": _cusp,
    "QQ[x,y]_(x,y)": _localized_plane_at_origin,
    "QQ[[x,y]]": lambda: QQ.power_series_ring(("x", "y")),
}

NON_DOMAINS = {
    "ZZ/12": lambda: Zmod(12),
    "ZZ/8": lambda: Zmod(8),
    "QQ[e]/(e^2)": lambda: QQ.dual_numbers(),
    "QQ[x]/(x^3)": lambda: _quotient(
        _polynomial_ring(QQ, "x"), _polynomial_ring(QQ, "x").algebra_generator("x") ** 3
    ),
    "GF(2)[t]/(t^2)": lambda: _quotient(
        _polynomial_ring(GF(2), "t"), _polynomial_ring(GF(2), "t").algebra_generator("t") ** 2
    ),
    "QQ[x,y]/(xy)": _coordinate_axes,
}

NONCOMMUTATIVE_RINGS = {
    "M_2(QQ)": lambda: QQ.matrix_space(2),
    "M_2(ZZ)": lambda: ZZ.matrix_space(2),
    "QQ<a,b>": lambda: QQ.free_module(("a", "b")).symmetric_algebra(),
}

PRINCIPAL_IDEAL_DOMAINS = {**FIELDS, **PRINCIPAL_IDEAL_DOMAINS_NOT_FIELDS}
DEDEKIND_DOMAINS = {**PRINCIPAL_IDEAL_DOMAINS, **DEDEKIND_DOMAINS_NOT_PRINCIPAL}
INTEGRAL_DOMAINS = {**DEDEKIND_DOMAINS, **NOETHERIAN_DOMAINS_NOT_DEDEKIND}
COMMUTATIVE_RINGS = {**INTEGRAL_DOMAINS, **NON_DOMAINS}
RINGS = {**COMMUTATIVE_RINGS, **NONCOMMUTATIVE_RINGS}

ARTINIAN_LOCAL_RINGS = {
    name: NON_DOMAINS[name]
    for name in ("ZZ/8", "QQ[e]/(e^2)", "QQ[x]/(x^3)", "GF(2)[t]/(t^2)")
}
ARTINIAN_RINGS = {**FIELDS, **ARTINIAN_LOCAL_RINGS, "ZZ/12": NON_DOMAINS["ZZ/12"]}
LOCAL_RINGS = {
    **FIELDS,
    **DISCRETE_VALUATION_RINGS,
    **ARTINIAN_LOCAL_RINGS,
    "QQ[x,y]_(x,y)": NOETHERIAN_DOMAINS_NOT_DEDEKIND["QQ[x,y]_(x,y)"],
    "QQ[[x,y]]": NOETHERIAN_DOMAINS_NOT_DEDEKIND["QQ[[x,y]]"],
}
COMPLETE_LOCAL_RINGS = {
    **FIELDS,
    **ARTINIAN_LOCAL_RINGS,
    "ZZ_3": DISCRETE_VALUATION_RINGS["ZZ_3"],
    "QQ[[t]]": DISCRETE_VALUATION_RINGS["QQ[[t]]"],
    "ZZ^_2": DISCRETE_VALUATION_RINGS["ZZ^_2"],
    "QQ[[x,y]]": NOETHERIAN_DOMAINS_NOT_DEDEKIND["QQ[[x,y]]"],
}
FINITE_FIELDS = {name: FIELDS[name] for name in ("GF(5)", "GF(4)", "GF(27)")}
FINITE_RINGS = {
    **FINITE_FIELDS,
    "ZZ/12": NON_DOMAINS["ZZ/12"],
    "ZZ/8": NON_DOMAINS["ZZ/8"],
    "GF(2)[t]/(t^2)": NON_DOMAINS["GF(2)[t]/(t^2)"],
}
NUMBER_FIELDS = {
    name: FIELDS[name]
    for name in ("QQ", "QQ(i)", "QQ(sqrt5)", "QQ(sqrt-5)", "QQ(sqrt-23)", "QQ(zeta5)", "QQ(cbrt2)")
}
MAXIMAL_ORDERS = {
    "ZZ": PRINCIPAL_IDEAL_DOMAINS["ZZ"],
    "ZZ[i]": PRINCIPAL_IDEAL_DOMAINS["ZZ[i]"],
    "ZZ[phi]": PRINCIPAL_IDEAL_DOMAINS["ZZ[phi]"],
    "ZZ[zeta5]": PRINCIPAL_IDEAL_DOMAINS["ZZ[zeta5]"],
    "ZZ[cbrt2]": PRINCIPAL_IDEAL_DOMAINS["ZZ[cbrt2]"],
    **DEDEKIND_DOMAINS_NOT_PRINCIPAL,
}

FAMILIES = {
    "ring": RINGS,
    "commutative_ring": COMMUTATIVE_RINGS,
    "integral_domain": INTEGRAL_DOMAINS,
    "dedekind_domain": DEDEKIND_DOMAINS,
    "pid": PRINCIPAL_IDEAL_DOMAINS,
    "field": FIELDS,
    "finite_field": FINITE_FIELDS,
    "finite_ring": FINITE_RINGS,
    "number_field": NUMBER_FIELDS,
    "maximal_order": MAXIMAL_ORDERS,
    "local_ring": LOCAL_RINGS,
    "complete_local_ring": COMPLETE_LOCAL_RINGS,
    "artinian_ring": ARTINIAN_RINGS,
    "discrete_valuation_ring": DISCRETE_VALUATION_RINGS,
}


@functools.cache
def specimen(name: str):
    r"""Return the catalogue member called ``name``, built at most once."""
    return RINGS[name]()


def pytest_generate_tests(metafunc) -> None:
    r"""A test asking for a family fixture runs once per member of that family."""
    for fixture_name, family in FAMILIES.items():
        if fixture_name in metafunc.fixturenames:
            metafunc.parametrize(fixture_name, sorted(family), ids=str, indirect=True)


def _member(request):
    return specimen(request.param)


# One fixture per family, each returning the member ``pytest_generate_tests``
# selected; a family fixture is the family's name.
for _fixture_name in FAMILIES:
    globals()[_fixture_name] = pytest.fixture(name=_fixture_name)(_member)


@pytest.fixture
def build():
    r"""``build("ZZ[i]")``: one catalogue member by name, for tests stating a known value."""
    return specimen
