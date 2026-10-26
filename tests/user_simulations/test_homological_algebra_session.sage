r"""A session in homological algebra over a principal ideal domain.

Free resolutions, dualizing and tensoring a resolution to compute
$\operatorname{Ext}^1$ and $\operatorname{Tor}_1$ as cohomology of the
resulting complexes, the Koszul complex, and exactness checks, typed as
into a notebook with only complexes, Homs and tensor products.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


DOMAINS = {
    "ZZ": (lambda: ZZ, 6, 4, 2),
    "QQ[x]": (lambda: QQ.polynomial_ring("x"), None, None, None),
    "ZZ[i]": (lambda: QuadraticField(-1, "i").ring_of_integers(), 6, 4, 2),
    "GF(5)[t]": (lambda: GF(5).polynomial_ring("t"), None, None, None),
}


@pytest.mark.parametrize("name", sorted(DOMAINS))
def test_a_homological_algebra_session(name) -> None:
    build, n, m, g = DOMAINS[name]
    ring = build()
    rendered(ring)
    if n is None:
        t = ring.algebra_generator(ring.variable_names()[0])
        n, m, g = t**2 * (t + ring.one()), t**2, t**2

    # A cyclic torsion module and its free resolution.
    torsion = FinitelyPresentedTorsionModules(ring).direct_sum_of_cyclics((ring(n),))
    rendered(torsion)
    assert torsion.annihilator() == ring.ideal(ring(n))
    resolution = torsion.free_resolution()
    rendered(resolution)
    assert resolution.is_exact()
    assert resolution.term(0).module_rank() == cardinal(1)
    assert resolution.term(1).module_rank() == cardinal(1)
    assert resolution.term(2).module_rank() == cardinal(0)
    multiplication = resolution.differential(1)
    assert multiplication.is_injective()
    assert multiplication(resolution.term(1).module_generator(0)) == ring(n) * resolution.term(0).module_generator(0)

    # Ext^1(R/n, R) = R/n, by dualizing the resolution.
    dualize = Modules(ring).dualization()
    dual_map = dualize(multiplication)
    rendered(dual_map)
    assert dual_map.domain() == dualize(resolution.term(0))
    assert dual_map.codomain() == dualize(resolution.term(1))
    dual_complex = CochainComplexes(ring)({0: dual_map.domain(), 1: dual_map.codomain()}, {0: dual_map})
    rendered(dual_complex)
    assert dual_complex.cohomology(0).cardinality() == cardinal(1)
    ext = dual_complex.cohomology(1)
    rendered(ext)
    assert ext.cardinality() == torsion.cardinality()
    assert ext.annihilator() == ring.ideal(ring(n))
    assert torsion.Mor(ring.regular_module()).cardinality() == cardinal(1)

    # Tor_1(R/n, R/m) = R/gcd(n, m), by tensoring the resolution with R/m.
    other = FinitelyPresentedTorsionModules(ring).direct_sum_of_cyclics((ring(m),))
    tensored_map = resolution.term(1).tensor_product(other).Mor(resolution.term(0).tensor_product(other))(
        {0: resolution.term(0).tensor_product(other).pure_tensor(ring(n) * resolution.term(0).module_generator(0), other.module_generator(0))}
    )
    tensored_complex = CochainComplexes(ring)({0: tensored_map.domain(), 1: tensored_map.codomain()}, {0: tensored_map})
    rendered(tensored_complex)
    tor = tensored_complex.cohomology(0)
    rendered(tor)
    assert tor.cardinality() == ring.quotient_ring(ring.ideal(ring(g))).cardinality()
    assert tensored_complex.cohomology(1).cardinality() == ring.quotient_ring(ring.ideal(ring(g))).cardinality()
    assert torsion.tensor_product(other).cardinality() == ring.quotient_ring(ring.ideal(ring(g))).cardinality()

    # A three-term complex with known cohomology.
    line = ring.free_module(1)
    plane = ring.free_module(2)
    inclusion = line.Mor(plane)({0: ring(n) * plane.module_generator(0)})
    projection = plane.Mor(line)({0: line.zero(), 1: line.module_generator(0)})
    complex_ = CochainComplexes(ring)({0: line, 1: plane, 2: line}, {0: inclusion, 1: projection})
    rendered(complex_)
    assert complex_.cohomology(0).cardinality() == cardinal(1)
    assert complex_.cohomology(1).cardinality() == torsion.cardinality()
    assert complex_.cohomology(2).cardinality() == cardinal(1)
    assert (projection * inclusion)(line.module_generator(0)) == line.zero()
