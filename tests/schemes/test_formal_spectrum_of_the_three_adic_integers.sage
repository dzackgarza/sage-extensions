r"""``Spf(Z, (3))``, the formal spectrum of the integers along ``3``, as its directed system of
thickenings ``Spec Z/3 -> Spec Z/9 -> Spec Z/27 -> ...``.

Each claim is a computation in ``Z/3^n``: it has ``3^n`` elements; ``3`` is nonzero in ``Z/9``
with square ``0``; the transition ``Z/27 -> Z/9`` is reduction, sending ``10`` to ``1``; each
thickening is a zero-dimensional scheme.
"""

from sage_extensions.all import *


def test_the_formal_spectrum_remembers_its_ring_and_ideal_of_definition() -> None:
    r"""``Spf(Z, (3))`` is built from ``Z`` and ``(3)``."""
    formal = ZZ.formal_spectrum(ZZ.ideal(3))

    assert formal.source_ring() is ZZ
    assert formal.ideal_of_definition() == ZZ.ideal(3)


def test_the_second_thickening_is_z_mod_nine() -> None:
    r"""In ``Z/9`` the class of ``3`` is nonzero and squares to zero; ``Spec Z/9`` is a point."""
    formal = ZZ.formal_spectrum(ZZ.ideal(3))
    ring = formal.thickening_ring(2)

    assert ring(3) != ring.zero()
    assert ring(3) * ring(3) == ring.zero()
    assert formal.thickening(2).dimension() == 0


def test_the_transition_from_z_mod_27_to_z_mod_9_is_reduction() -> None:
    r"""``10 = 1 + 9`` reduces to ``1`` modulo ``9``."""
    formal = ZZ.formal_spectrum(ZZ.ideal(3))
    reduction = formal.transition_ring_map(3, 2)

    assert reduction(formal.thickening_ring(3)(10)) == formal.thickening_ring(2)(1)


def test_the_thickening_rings_have_three_to_the_n_elements() -> None:
    r"""``|Z/3^n| = 3^n``."""
    formal = ZZ.formal_spectrum(ZZ.ideal(3))

    assert formal.thickening_ring(2).cardinality() == 9


def test_the_first_thickening_includes_into_the_third() -> None:
    r"""``Spec Z/3 -> Spec Z/27`` is the directed-system arrow between the stages."""
    formal = ZZ.formal_spectrum(ZZ.ideal(3))
    restriction = formal.formal_restriction(3, 1)

    assert restriction.domain() is formal.thickening(1)
    assert restriction.codomain() is formal.thickening(3)


def test_the_completion_is_the_ring_of_three_adic_integers() -> None:
    r"""``lim Z/3^n = Z_3``, a complete local ring whose projection to ``Z/9`` sends ``10`` to ``1``."""
    formal = ZZ.formal_spectrum(ZZ.ideal(3))
    completion = formal.completion(5)

    assert formal.completion_projection(5, 2)(completion(10)) == formal.thickening_ring(2)(1)


def test_the_formal_spectrum_of_the_line_along_the_origin_has_the_dual_numbers_as_a_thickening() -> None:
    r"""``Spf(Q[x], (x))`` has second thickening ``Q[x]/(x^2)``, in which ``x`` is nonzero with square zero."""
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    formal = ring.formal_spectrum(ring.ideal(x))
    dual_numbers = formal.thickening_ring(2)

    assert dual_numbers(x) != dual_numbers.zero()
    assert dual_numbers(x) * dual_numbers(x) == dual_numbers.zero()
