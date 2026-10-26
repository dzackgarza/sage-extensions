r"""Ordinary and Brauer characters of group modules."""

from sage_extensions.all import *


def test_the_character_of_sign_plus_trivial_of_s3_is_2_0_2() -> None:
    r"""$\chi = \operatorname{sgn} + 1$: $\chi(1) = 2$, $\chi((1\,2)) = -1 + 1 = 0$, $\chi((1\,2\,3)) = 1 + 1 = 2$."""
    group = Groups.S(3)
    module = Modules(ZZ)(ZZ**2)
    e0, e1 = module.module_generator(0), module.module_generator(1)

    def act(g, vector):
        return module.Mor(module)({0: g.sign() * e0, 1: e1})(vector)

    character = Modules(ZZ[group])(module, act).character()

    assert character(group.one()) == 2
    assert character(group((1, 2))) == 0
    assert character(group((1, 2, 3))) == 2


def test_the_2_modular_brauer_character_of_the_order_three_action_of_c6_on_f2_squared_is_2_minus1_minus1() -> None:
    r"""$g$ acts on $\mathbb{F}_2^2$ by $x \mapsto y,\ y \mapsto x + y$, of order 3 with eigenvalues the primitive cube roots of unity in $\mathbb{F}_4$; their Teichmüller lifts sum to $\omega + \omega^2 = -1$, while the modular trace is $1$ (Serre, *Linear representations of finite groups*, 18.1)."""
    group = Groups.C(6)
    (g,) = group.group_generators()
    module = Modules(GF(2))(GF(2) ** 2)
    x, y = module.module_generator(0), module.module_generator(1)
    rotation = module.Aut()({0: y, 1: x + y})
    rho = group.Mor(module.Aut())({g: rotation})

    acted = Modules(GF(2)[group])(module, lambda h, vector: rho(h)(vector))
    brauer = acted.brauer_character()

    assert brauer(group.one()) == 2
    assert brauer(g**2) == -1
    assert brauer(g**4) == -1
    assert acted.action_of(g**2).trace() == GF(2).one()
