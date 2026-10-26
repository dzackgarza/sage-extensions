r"""Cohomology is a functor: on cochain complexes and, through de Rham, on algebras."""

from sage_extensions.all import *


def test_multiplication_by_three_induces_the_identity_on_H1_of_ZZ_times_two_ZZ() -> None:
    r"""\(H^1(\mathbb Z \xrightarrow{2} \mathbb Z) = \mathbb Z/2\), on which \(3 \equiv 1\)."""
    degree_zero = Modules(ZZ)(ZZ**1)
    degree_one = Modules(ZZ)(ZZ**1)
    (e,) = degree_zero.module_generators()
    (f,) = degree_one.module_generators()
    complex_ = CochainComplexes(ZZ)(
        {0: degree_zero, 1: degree_one},
        {0: degree_zero.Mor(degree_one)({e: 2 * f})},
    )
    times_three = CochainComplexes(ZZ).Mor(complex_, complex_)(
        {
            0: degree_zero.Mor(degree_zero)({e: 3 * e}),
            1: degree_one.Mor(degree_one)({f: 3 * f}),
        }
    )

    functor = CochainComplexes(ZZ).cohomology(1)
    h1 = functor(complex_)
    generator = h1.class_of_cycle(f)

    assert generator != h1.zero()
    assert functor(times_three)(generator) == generator


def _dual_numbers_over_F2():
    r"""\(A = \mathbb F_2[x]/(x^2)\) and the algebra map \(x \mapsto 0\)."""
    polynomials = GF(2)["x"]
    x = polynomials.gen()
    algebra = polynomials.quotient(x**2)
    xbar = algebra(x)
    collapse = algebra.Mor(algebra)({xbar: algebra.zero()})
    return algebra, xbar, collapse


def test_x_dx_is_a_nonzero_de_rham_class_of_F2_dual_numbers_killed_by_x_to_zero() -> None:
    r"""In characteristic \(2\), \(d(x^2) = 2x\,dx = 0\), so \(\Omega_A = A\,dx\) is free on
    \(dx\) with \(\mathbb F_2\)-basis \(dx, x\,dx\), while \(dA = \mathbb F_2\,dx\); hence
    \(H^1_{dR}(A) = \mathbb F_2 [x\,dx] \ne 0\), and \(x \mapsto 0\) sends \(x\,dx\) to \(0\)."""
    algebra, xbar, collapse = _dual_numbers_over_F2()
    functor = Algebras(GF(2)).Associative().Unital().Commutative().de_rham_cohomology(1)
    h1 = functor(algebra)
    de_rham = algebra.de_rham_algebra()
    x_form = de_rham(xbar)
    x_dx = x_form * de_rham.d(x_form)

    alpha = h1.class_of_cycle(x_dx)

    assert alpha != h1.zero()
    assert h1.class_of_cycle(de_rham.d(x_form)) == h1.zero()
    assert functor(collapse)(alpha) == h1.zero()


def test_de_rham_cohomology_of_F2_dual_numbers_is_a_ring_functor_under_x_to_zero() -> None:
    r"""The induced map on \(H^*_{dR}(A)\) is a ring map: \(1 \mapsto 1\), \([x\,dx] \mapsto 0\),
    and \([1]\cdot[x\,dx] = [x\,dx]\) is sent to \(1 \cdot 0 = 0\)."""
    algebra, xbar, collapse = _dual_numbers_over_F2()
    functor = Algebras(GF(2)).Associative().Unital().Commutative().de_rham_cohomology_algebra()
    cohomology = functor(algebra)
    de_rham = algebra.de_rham_algebra()
    x_form = de_rham(xbar)
    alpha = cohomology.from_component(
        1, cohomology.graded_piece(1).class_of_cycle(x_form * de_rham.d(x_form))
    )
    induced = functor(collapse)

    assert alpha != cohomology.zero()
    assert cohomology.one() * alpha == alpha
    assert induced(cohomology.one()) == cohomology.one()
    assert induced(alpha) == cohomology.zero()
    assert induced(cohomology.one() * alpha) == induced(cohomology.one()) * induced(alpha)
