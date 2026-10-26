r"""The Legendre family `y^2 z = x (x - z)(x - \lambda z)` and its monodromy around `\lambda = 0`."""

from sage_extensions.all import *


def test_legendre_fiber_over_zero_is_a_nodal_cubic_and_nearby_fibers_are_elliptic() -> None:
    r"""At `\lambda = 0` the fiber is `y^2 z = x^2 (x - z)`, a cubic with one node and
    geometric genus 0; at `\lambda = 1/2` it is smooth of genus 1."""
    family = LegendreMonodromyFamily()
    singular = family.fiber(0)
    smooth = family.fiber(1 / 2)

    assert singular.singular_locus().point_count() == 1
    assert singular.geometric_genus() == 0
    assert smooth.singular_locus().is_empty()
    assert smooth.genus() == 1


def test_monodromy_around_zero_is_the_square_of_a_picard_lefschetz_transvection() -> None:
    r"""With `\alpha` the vanishing cycle and `\langle \alpha, \beta \rangle = 1`,
    the monodromy of `R^1` around `\lambda = 0` is `\beta \mapsto \beta + 2\alpha`,
    fixing `\alpha` and preserving the pairing.

    Derivation: the discriminant of `x(x-1)(x-\lambda)` is `\lambda^2(\lambda-1)^2`,
    vanishing to order 2 at `\lambda = 0`, so the local monodromy is the square of the
    Picard--Lefschetz transvection of the one node.
    """
    family = LegendreMonodromyFamily()
    cohomology = family.fiber_cohomology(family.base_point())
    alpha, beta = tuple(cohomology.module_generators())
    loop = family.pointed_fundamental_group().positive_loop_generator()
    monodromy = family.monodromy_representation()(loop)

    assert cohomology.pairing(alpha, beta) == 1
    assert monodromy(alpha) == alpha
    assert monodromy(beta) == beta + 2 * alpha
    assert cohomology.pairing(monodromy(alpha), monodromy(beta)) == 1
