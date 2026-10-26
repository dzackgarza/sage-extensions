r"""An algebraist's session on a plane curve: ideals, quotients, localization, differentials.

One long session per base field, typed as into a notebook: the polynomial
ring in two variables, the cusp $y^2 = x^3$, its coordinate ring, spectrum,
local rings, Kähler differentials and de Rham complex.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


FIELDS = {
    "QQ": lambda: QQ,
    "GF(5)": lambda: GF(5),
    "GF(4)": lambda: GF(4),
    "QQ(i)": lambda: QuadraticField(-1, "i"),
}


@pytest.mark.parametrize("name", sorted(FIELDS))
def test_a_plane_curve_session(name) -> None:
    field = FIELDS[name]()
    rendered(field)

    # The polynomial ring and a few ideals.
    plane = field.polynomial_ring(("x", "y"))
    rendered(plane)
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    assert plane in Algebras(field).Associative().Unital().Commutative()
    assert plane in IntegralDomains()
    assert plane in NoetherianRings()
    assert plane not in PrincipalIdealDomains()
    assert plane.krull_dimension() == 2

    cusp_ideal = plane.ideal(y**2 - x**3)
    origin = plane.ideal(x, y)
    axes = plane.ideal(x * y)
    fat_point = plane.ideal(x**2, x * y, y**2)
    for ideal in (cusp_ideal, origin, axes, fat_point):
        rendered(ideal)
        assert ideal in CommutativeIdeals(plane)
    assert cusp_ideal.is_prime()
    assert not cusp_ideal.is_maximal()
    assert origin.is_maximal()
    assert not axes.is_prime()
    assert axes.radical() == axes
    assert fat_point.radical() == origin
    assert not axes.intersection(cusp_ideal).is_prime()
    assert cusp_ideal.sum(origin) == origin
    assert origin.power(2) == fat_point
    assert axes.primary_decomposition().cardinality() == cardinal(2)
    assert axes.associated_primes().cardinality() == cardinal(2)
    assert origin.quotient_ring() in Fields()

    # The coordinate ring of the cusp.
    cusp = (plane).quotient_by_relations([y**2 - x**3])
    rendered(cusp)
    xbar = cusp.algebra_generator("x")
    ybar = cusp.algebra_generator("y")
    assert cusp in Algebras(field).Associative().Unital().Commutative()
    assert cusp in IntegralDomains()
    assert cusp in NoetherianRings()
    assert cusp.krull_dimension() == 1
    assert ybar**2 == xbar**3
    assert ybar != xbar
    assert cusp.cardinality() == cardinal(max(field.cardinality(), aleph0))
    fractions = cusp.fraction_field()
    rendered(fractions)
    assert fractions in Fields()
    t = fractions(ybar) / fractions(xbar)
    assert t * t == fractions(xbar)
    assert t**3 == fractions(ybar)

    # Its spectrum: generic point, the origin, the local ring there.
    spectrum = cusp.spectrum()
    rendered(spectrum)
    generic = spectrum.generic_point()
    singular = spectrum(cusp.ideal(xbar, ybar))
    smooth_point = spectrum(cusp.ideal(xbar - cusp.one(), ybar - cusp.one()))
    rendered(singular)
    assert generic.specializes_to(singular)
    assert generic.specializes_to(smooth_point)
    assert not singular.specializes_to(smooth_point)
    assert generic.residue_field() is fractions
    assert singular.residue_field() in Fields()
    assert singular.residue_field().characteristic() == field.characteristic()
    local = singular.local_ring()
    rendered(local)
    assert local in LocalRings()
    assert local in NoetherianRings()
    assert local.krull_dimension() == 1
    assert local not in PrincipalIdealDomains()
    assert smooth_point.local_ring() in PrincipalIdealDomains()
    assert local.maximal_ideal().is_maximal()
    completion = cusp.adic_completion(cusp.ideal(xbar, ybar))
    rendered(completion)
    assert completion in CompleteLocalRings()
    assert completion.residue_field().characteristic() == field.characteristic()

    # The curve as a scheme.
    affine = AffineSpaces(field)(2, names=("x", "y"))
    curve = affine.closed_subscheme(affine.coordinate_ring().algebra_generator("y") ** 2 - affine.coordinate_ring().algebra_generator("x") ** 3)
    rendered(curve)
    assert curve in Curves(field)
    assert curve in IntegralSchemes(field)
    assert curve not in SmoothSchemes(field)
    assert curve not in NormalSchemes(field)
    assert curve.dimension() == 1
    assert (cusp).affine_spectrum() in AffineSchemes(field)
    assert (cusp).affine_spectrum().relative_dimension() == 1
    assert curve.coordinate_ring().Mor(cusp).cardinality() >= cardinal(1)

    # Kähler differentials and the de Rham complex of the cusp.
    omega = cusp.kahler_differentials()
    rendered(omega)
    d = omega.universal_derivation()
    dx = omega.differential_generator("x")
    dy = omega.differential_generator("y")
    assert d(xbar) == dx
    assert d(ybar**2) == d(xbar**3)
    assert omega.scalar_multiple(2 * ybar, dy) == omega.scalar_multiple(3 * xbar**2, dx)
    assert dx != omega.zero()
    assert omega.generic_rank() == 1
    de_rham = cusp.de_rham_algebra()
    rendered(de_rham)
    assert de_rham.differential()(de_rham(xbar)) == de_rham(dx)
    assert de_rham.cohomology(0).module_rank() == cardinal(1)
    rendered(de_rham.cohomology(1))

    # Over the smooth affine line the Poincaré lemma holds in characteristic zero.
    line = field.polynomial_ring("t")
    line_de_rham = line.de_rham_algebra()
    rendered(line_de_rham)
    if field.characteristic() == 0:
        assert line_de_rham.cohomology(1).cardinality() == cardinal(1)
    else:
        assert line_de_rham.cohomology(1).cardinality() != cardinal(1)
