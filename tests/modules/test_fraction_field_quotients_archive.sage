r"""The divisible groups $\mathbb Q / n\mathbb Z$ as $\mathbb Z$-modules.

Every finitely generated subgroup of $\mathbb Q / n \mathbb Z$ is cyclic, and
the class of $a/b$ in lowest terms has order $b n / \gcd(a, n)$ (for $n = 1$,
order $b$).
"""

from sage_extensions.all import *  # noqa: F401,F403


def rationals_modulo(n):
    Q = Modules(ZZ)(QQ)
    return Q / Q.submodule([Q(n)])


def test_in_q_mod_6z_the_classes_of_3_and_2_generate_subgroups_of_orders_2_and_3() -> None:
    """3 * 2 = 6 and 2 * 3 = 6 lie in 6Z, and 3, 2 are not in 6Z; 4 = 2 * 2 in <2>.

    Source: by hand.
    """
    T = rationals_modulo(6)
    order_two = T.submodule([T(3)])
    order_three = T.submodule([T(2)])
    assert order_two.cardinality() == 2
    assert order_three.cardinality() == 3

    inclusion = order_three.inclusion()
    assert inclusion(order_three.module_generator(0)) == T(2)
    assert inclusion.lift(T(4)) == 2 * order_three.module_generator(0)
    assert not order_three.inclusion().is_in_image(T(3))


def test_in_q_mod_z_the_classes_of_1_4_and_1_6_generate_the_cyclic_group_of_order_12() -> None:
    """<1/4, 1/6> = <1/12> since 1/12 = 1/4 - 1/6 and lcm(4, 6) = 12; in Q/2Z, 4/3 and 2/3
    generate the same subgroup of order 3.

    Source: by hand.
    """
    T = rationals_modulo(1)
    generated = T.submodule([T(QQ(1) / 4), T(QQ(1) / 6)])
    assert generated.cardinality() == 12
    assert generated == T.submodule([T(QQ(1) / 12)])
    assert T(QQ(1) / 12) * 12 == T.zero()
    assert 6 * T(QQ(1) / 12) != T.zero()

    T2 = rationals_modulo(2)
    assert T2.submodule([T2(QQ(4) / 3)]).cardinality() == 3
    assert T2.submodule([T2(QQ(4) / 3)]) == T2.submodule([T2(QQ(2) / 3)])


def test_archived_a2_discriminant_scales_are_value_submodules() -> None:
    bilinear = Lattices.A2.discriminant_bilinear_form()
    bilinear_scale = bilinear.scale_submodule()
    bilinear_generator = bilinear_scale.embedded_module_generators()[0]

    assert bilinear_scale.ambient_module() is bilinear.value_module()
    assert bilinear_scale.cardinality() == 3
    assert bilinear_generator == bilinear.value_module()(QQ(1) / 3)

    quadratic = Lattices.A2.discriminant_quadratic_form()
    quadratic_scale = quadratic.scale_submodule()
    quadratic_generator = quadratic_scale.embedded_module_generators()[0]

    assert quadratic.value_module().modulus() == 2
    assert quadratic_scale.ambient_module() is quadratic.value_module()
    assert quadratic_scale.cardinality() == 3
    assert quadratic_generator == quadratic.value_module()(QQ(2) / 3)
