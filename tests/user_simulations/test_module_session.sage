r"""A session in module theory over a principal ideal domain.

Free modules, submodules by generators, quotients and their invariant
factors, Hom and tensor, localization, base change, resolutions, and a
short cochain complex with its cohomology, typed as into a notebook.
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
    "ZZ": lambda: ZZ,
    "QQ[x]": lambda: QQ.polynomial_ring("x"),
    "GF(5)[t]": lambda: GF(5).polynomial_ring("t"),
    "ZZ[i]": lambda: QuadraticField(-1, "i").ring_of_integers(),
    "ZZ_3": lambda: Zp(3),
    "ZZ_(5)": lambda: ZZ.localize_at_prime(5),
}


@pytest.mark.parametrize("name", sorted(DOMAINS))
def test_a_module_session_over_a_principal_ideal_domain(name) -> None:
    ring = DOMAINS[name]()
    rendered(ring)
    fractions = ring.fraction_field()

    # A free module, elements, a submodule spanned by three vectors.
    module = ring.free_module(3)
    rendered(module)
    e0, e1, e2 = module.module_generator(0), module.module_generator(1), module.module_generator(2)
    v = 2 * e0 + 4 * e1
    w = 6 * e1 + 2 * e2
    u = 4 * e0 + 8 * e1
    rendered(v)
    assert module in FreeModules(ring)
    assert module in FinitelyGeneratedFreeModules(ring)
    assert module.module_rank() == cardinal(3)
    submodule = module.subobject_on([v, w, u])
    rendered(submodule)
    assert submodule in ModuleSubobjects(ring)
    assert submodule.module_rank() == cardinal(2)
    assert submodule.inclusion().is_injective()
    assert v in submodule
    assert submodule.is_saturated() == ring(2).is_unit()
    saturation = submodule.saturation()
    rendered(saturation)
    assert saturation.module_rank() == cardinal(2)
    assert saturation.is_saturated()

    # The quotient, its torsion, its annihilator.
    quotient = submodule.inclusion().cokernel()
    rendered(quotient)
    assert quotient in FinitelyPresentedModules(ring)
    assert quotient in Modules(ring)
    assert quotient.module_rank() == cardinal(1)
    torsion = quotient.torsion_submodule()
    rendered(torsion)
    assert torsion in TorsionModules(ring)
    assert torsion.cardinality() == cardinal(ring.quotient_ring(ring.ideal(ring(2))).cardinality() ** 2)
    assert quotient.annihilator() == ring.ideal(ring.zero())
    presented = (submodule.inclusion()).cokernel()
    rendered(presented)
    assert presented.module_rank() == cardinal(1)
    invariant_factors = presented.invariant_factors()
    rendered(invariant_factors)
    assert (ring(2) in invariant_factors) == (not ring(2).is_unit())

    # Hom and tensor.
    homs = module.Mor(module)
    rendered(homs)
    assert homs.module_rank() == cardinal(9)
    tensor = module.tensor_product(quotient)
    rendered(tensor)
    assert tensor in Modules(ring)
    assert tensor.module_rank() == cardinal(3)
    dual = module.dual_module()
    assert dual.module_rank() == cardinal(3)
    assert quotient.Mor(ring.regular_module()).module_rank() == cardinal(1)

    # A morphism, its kernel, image and cokernel; the rank–nullity relation.
    morphism = module.Mor(module)({0: e1, 1: e2, 2: 2 * e0})
    rendered(morphism)
    assert morphism.is_injective()
    assert morphism.is_surjective() == ring(2).is_unit()
    assert morphism.kernel().module_rank() == cardinal(0)
    assert morphism.image().module_rank() == cardinal(3)
    assert morphism.cokernel().cardinality() == ring.quotient_ring(ring.ideal(ring(2))).cardinality()
    assert (morphism * morphism)(e0) == e2
    assert morphism.kernel().module_rank() + morphism.image().module_rank() == cardinal(3)

    # Base change to the fraction field, and localization where it applies.
    extended = quotient.base_change(ring.Mor(fractions)(lambda element: fractions(element)))
    rendered(extended)
    assert extended in VectorSpaces(fractions)
    assert extended.module_rank() == cardinal(1)
    two_ideal = ring.ideal(ring(2))
    prime = ring.spectrum()(two_ideal) if ring(2) != ring.zero() and not ring(2).is_unit() and two_ideal.is_prime() else None
    if prime is not None:
        localized = quotient.localize_at_prime(prime)
        rendered(localized)
        assert localized in Modules(prime.local_ring())
        assert localized.module_rank() == cardinal(1)

    # A free resolution of the quotient.
    resolution = quotient.free_resolution()
    rendered(resolution)
    assert resolution.is_exact()
    assert resolution.term(0).module_rank() == cardinal(3)
    assert resolution.term(1).module_rank() == cardinal(2)
    assert resolution.term(2).module_rank() == cardinal(0)

    # A short cochain complex 0 -> R -> R^2 -> R -> 0 and its cohomology.
    line = ring.free_module(1)
    plane = ring.free_module(2)
    d0 = line.Mor(plane)({0: 2 * plane.module_generator(0) + 2 * plane.module_generator(1)})
    d1 = plane.Mor(line)({0: line.module_generator(0), 1: -line.module_generator(0)})
    complex_ = CochainComplexes(ring)({0: line, 1: plane, 2: line}, {0: d0, 1: d1})
    rendered(complex_)
    assert complex_ in CochainComplexes(ring)
    assert (d1 * d0)(line.module_generator(0)) == line.zero()
    assert complex_.cohomology(0).cardinality() == cardinal(1)
    assert complex_.cohomology(1).cardinality() == ring.quotient_ring(ring.ideal(ring(2))).cardinality()
    assert complex_.cohomology(2).cardinality() == cardinal(1)
    for degree in (0, 1, 2):
        rendered(complex_.cohomology(degree))
