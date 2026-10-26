r"""Milnor numbers and ADE types of plane curve germs over ``Q``.

The Milnor number is ``mu(f) = dim Q[x, y]/(f_x, f_y)`` and the Tjurina number
``tau(f) = dim Q[x, y]/(f, f_x, f_y)`` (localized at the origin).  Each expected value below
is a direct computation of these quotients: for ``f = x^a + y^b`` the Jacobian ideal is
``(x^{a-1}, y^{b-1})``, so ``mu = (a - 1)(b - 1)``, and ``f`` lies in it, so ``tau = mu``.
The ADE normal forms are ``A_k: x^2 + y^{k+1}``, ``D_k: x^2 y + y^{k-1}``,
``E_6: x^3 + y^4``, ``E_7: x^3 + x y^3``, ``E_8: x^3 + y^5``, each with ``mu = k``.
"""

from sage_extensions.all import *


def _plane():
    plane = QQ.polynomial_ring(("x", "y"))
    return plane, plane.algebra_generator("x"), plane.algebra_generator("y")


def test_the_ade_normal_forms_have_milnor_number_equal_to_their_index() -> None:
    r"""``mu(A_1) = 1``, ``mu(A_4) = 4``, ``mu(D_4) = 4``, ``mu(D_5) = 5``, ``mu(E_k) = k``."""
    for ade_type, milnor in (("A1", 1), ("A4", 4), ("D4", 4), ("D5", 5), ("E6", 6), ("E7", 7), ("E8", 8)):
        germ = IsolatedHypersurfaceSingularity.from_ade_type(QQ, ade_type)
        assert germ.milnor_number() == milnor


def test_the_ade_normal_forms_are_the_textbook_equations() -> None:
    r"""The ADE normal forms in the variables ``x, y``."""
    plane, x, y = _plane()
    pairs = (("A1", x**2 + y**2), ("A4", x**2 + y**5), ("D4", x**2 * y + y**3), ("D5", x**2 * y + y**4),
             ("E6", x**3 + y**4), ("E7", x**3 + x * y**3), ("E8", x**3 + y**5))
    for ade_type, equation in pairs:
        germ = IsolatedHypersurfaceSingularity.from_ade_type(QQ, ade_type)
        assert germ.equation() == equation


def test_a_normal_form_is_recognized_by_its_type() -> None:
    r"""``x^2 + y^3`` is ``A_2``, ``x^3 + y^4`` is ``E_6``, ``x^2 y + y^4`` is ``D_5``."""
    plane, x, y = _plane()

    assert IsolatedHypersurfaceSingularity(plane, x**2 + y**3).ade_normal_form_type() == ("A", 2)
    assert IsolatedHypersurfaceSingularity(plane, x**3 + y**4).ade_normal_form_type() == ("E", 6)
    assert IsolatedHypersurfaceSingularity(plane, x**2 * y + y**4).ade_normal_form_type() == ("D", 5)


def test_brieskorn_pham_curves_have_milnor_number_a_minus_one_times_b_minus_one() -> None:
    r"""``mu(x^a + y^b) = (a - 1)(b - 1)``: 2 for ``(2, 3)``, 6 for ``(3, 4)``, 12 for ``(4, 5)``."""
    plane, x, y = _plane()
    for a, b in ((2, 3), (3, 4), (4, 5)):
        assert IsolatedHypersurfaceSingularity(plane, x**a + y**b).milnor_number() == (a - 1) * (b - 1)


def test_the_jacobian_ideal_of_the_cusp_is_generated_by_its_partials() -> None:
    r"""For ``f = y^2 - x^3``: ``f_x = -3 x^2`` and ``f_y = 2 y``."""
    plane, x, y = _plane()
    cusp = IsolatedHypersurfaceSingularity(plane, y**2 - x**3)
    partials = cusp.jacobian_generators()

    assert partials["x"] == -3 * x**2
    assert partials["y"] == 2 * y
    assert cusp.milnor_number() == 2


def test_a_sheared_a2_germ_is_linearly_right_equivalent_to_the_normal_form() -> None:
    r"""``(x + y)^2 + y^3`` becomes ``x^2 + y^3`` under ``x -> x - y``, so it is an ``A_2`` germ."""
    plane, x, y = _plane()
    sheared = IsolatedHypersurfaceSingularity(plane, (x + y) ** 2 + y**3)
    normal = IsolatedHypersurfaceSingularity(plane, x**2 + y**3)

    equivalence = sheared.ade_type_via_linear_right_equivalence({"x": x - y, "y": y}, {"x": x + y, "y": y})
    explicit = sheared.linear_right_equivalence_to(normal, {"x": x - y, "y": y}, {"x": x + y, "y": y})

    assert equivalence.ade_type() == ("A", 2)
    assert equivalence.source() is sheared
    assert explicit.target() is normal
    assert sheared.milnor_number() == normal.milnor_number()


def test_quasihomogeneous_germs_have_tjurina_number_equal_to_milnor_number() -> None:
    r"""``tau(x^2 + y^3) = mu = 2`` and ``tau(x^3 + y^4) = mu = 6``: ``f`` lies in its Jacobian ideal."""
    plane, x, y = _plane()

    assert IsolatedHypersurfaceSingularity(plane, x**2 + y**3).tjurina_number() == 2
    assert IsolatedHypersurfaceSingularity(plane, x**3 + y**4).tjurina_number() == 6


def test_the_milnor_algebra_of_the_cusp_is_two_dimensional() -> None:
    r"""``f = x^2 + y^3`` has ``(f_x, f_y) = (x, y^2)``, and ``Q[x, y]/(x, y^2)`` has basis ``1, y``."""
    plane, x, y = _plane()

    assert IsolatedHypersurfaceSingularity(plane, x**2 + y**3).milnor_algebra().dimension() == 2
