r"""Connections on a free module over a polynomial ring.

A connection $\nabla\colon M \to M \otimes_A \Omega_A$ satisfies the Leibniz
rule $\nabla(f m) = m \otimes df + f \nabla(m)$; on a rank-one free module with
$\nabla(e) = e \otimes \omega$ its curvature is $e \otimes (d\omega +
\omega \wedge \omega) = e \otimes d\omega$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_leibniz_rule_and_curvature_of_a_rank_one_connection() -> None:
    """For omega = x dy on QQ[x,y], d omega = dx ^ dy != 0, so e -> e (x) x dy is not flat.

    Source: Kobayashi–Nomizu, Foundations of Differential Geometry I, III.5 (curvature of a
    rank-one connection is d omega).
    """
    A = QQ["x,y"]
    x, y = A.algebra_generator("x"), A.algebra_generator("y")
    M = A**1
    e = M.module_generator(0)
    omega = A.kahler_differentials()
    dx = omega.differential_generator("x")
    dy = omega.differential_generator("y")
    twisted_forms = M.tensor_product(omega)

    trivial = M.connections()({0: twisted_forms.zero()})
    assert trivial(x * e) == twisted_forms.pure_tensor(e, dx)
    assert trivial(x * y * e) == twisted_forms.pure_tensor(e, y * dx + x * dy)
    assert trivial.is_flat()

    twisted = M.connections()({0: twisted_forms.pure_tensor(e, x * dy)})
    assert twisted(x * e) == twisted_forms.pure_tensor(e, dx) + twisted_forms.pure_tensor(e, x**2 * dy)
    assert not twisted.is_flat()


def test_flat_connection_gives_a_de_rham_dg_module() -> None:
    """For nabla(e) = e (x) dx on QQ[x], the de Rham DG module has d(e) = e dx, d^2 = 0 and
    d(e X) = d(e) X + e dX.

    Source: Deligne, Équations différentielles à points singuliers réguliers, I.2 (the de Rham
    complex of a flat connection).
    """
    A = QQ["x"]
    x = A.gen()
    M = A**1
    omega = A.kahler_differentials()
    dx = omega.differential_generator("x")
    connection = M.connections()({0: M.tensor_product(omega).pure_tensor(M.module_generator(0), dx)})
    assert connection.is_flat()

    complex_ = connection.de_rham_module()
    forms = A.de_rham_algebra()
    d = complex_.differential()
    e = complex_(M.module_generator(0))
    X = forms(x**2)

    assert d(e) == e * forms.differential()(forms(x))
    assert d(d(e)) == complex_.zero()
    assert d(e * X) == d(e) * X + e * forms.differential()(X)
