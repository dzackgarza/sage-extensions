r"""An algebra given by generators and relations keeps its presentation.

For ``A = Q[x, y]/(x^2 - y^3)`` the presentation is the polynomial ring
``Q[x, y]`` with the single relation ``x^2 - y^3``; the presentation map sends
``x`` to the class of ``x``, and a lift of ``xy`` is ``xy``.  The generating module is
the free module on the two letters.  Over a field every algebra is torsion-free.

Over ``Z``: ``Z[t]/(t^2 + 1) = Z[i]`` is free of rank two, hence torsion-free, and
``Z -> Z[i]`` is injective; ``Z[t]/(2t)`` is not torsion-free, since ``2 t = 0``
while ``t`` is not zero there.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_cusp_retains_its_presentation() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_by_relations([x**2 - y**3])
    xbar = cusp.algebra_generator("x")
    ybar = cusp.algebra_generator("y")
    presentation = cusp.algebra_presentation_morphism()

    assert cusp.presentation_ring() is plane
    assert presentation(x) == xbar
    assert presentation(x**2 - y**3) == cusp.zero()
    assert presentation(cusp.lift_to_presentation(xbar * ybar)) == xbar * ybar
    assert cusp.lift_to_presentation(xbar * ybar) == x * y


def test_an_algebra_over_a_field_is_torsion_free() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")

    assert plane.quotient_by_relations([x**2 - y**3]).is_torsion_free()
    assert plane.quotient_by_relations([x * y]).is_torsion_free()


def test_the_gaussian_integers_are_torsion_free_over_z() -> None:
    t = ZZ["t"].algebra_generator("t")
    gaussian = ZZ["t"].quotient_by_relations([t**2 + 1])

    assert gaussian.algebra_generator("t") ** 2 == -gaussian.one()
    assert gaussian.is_torsion_free()


def test_z_t_mod_two_t_has_two_torsion() -> None:
    t = ZZ["t"].algebra_generator("t")
    algebra = ZZ["t"].quotient_by_relations([2 * t])

    assert 2 * algebra.algebra_generator("t") == algebra.zero()
    assert algebra.algebra_generator("t") != algebra.zero()
    assert not algebra.is_torsion_free()


def test_the_presentation_ideal_of_the_cusp_contains_its_relation() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_by_relations([x**2 - y**3])

    assert x**2 - y**3 in cusp.presentation_ideal()
    assert x not in cusp.presentation_ideal()


def test_the_cusp_is_generated_as_an_algebra_by_a_module_of_rank_two() -> None:
    plane = QQ["x, y"]
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")

    assert plane.quotient_by_relations([x**2 - y**3]).generating_module().module_rank() == 2
