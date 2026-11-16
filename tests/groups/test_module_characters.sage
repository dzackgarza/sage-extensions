r"""Ordinary and Brauer characters of group modules.

Over a characteristic-zero field the character of a finite free module is the
trace of each group element (Serre, *Linear Representations of Finite Groups*,
§2.1 and §6.1).  In positive characteristic it is not: the Brauer character of
a $p$-modular representation lifts the eigenvalues of each $p$-regular class
through a character of the coefficient field's multiplicative group, which is
the Teichmüller lift, so it differs from the $\mathbb{F}_p$-valued trace as
soon as an eigenvalue moves into an extension field (§18.1).  Both are data of
the module, asked for once and kept.
"""

from sage_extensions.all import *


def _permutation_module_of_s3():
    r"""The permutation representation $\mathbb{Q}^3$ of $S_3$ on the three basis vectors."""
    group = Groups.S(3)
    vectors = Modules(QQ).free_module(3)

    def act(g, vector):
        return vectors.Mor(vectors)(
            {label: vectors.module_generator(int(g(label + 1)) - 1) for label in range(3)}
        )(vector)

    return group, Modules(QQ[group])(vectors, act)


def _order_three_plane_of_c6():
    r"""$\mathbb{F}_2^2$ with $g \mapsto (x \mapsto y,\ y \mapsto x + y)$ of order three, over $\mathbb{F}_2[C_6]$."""
    group = Groups.C(6)
    (g,) = group.group_generators()
    module = Modules(GF(2))(GF(2) ** 2)
    x, y = module.module_generator(0), module.module_generator(1)
    rotation = module.Aut()({0: y, 1: x + y})
    rho = group.Mor(module.Aut())({g: rotation})
    return group, Modules(GF(2)[group])(module, lambda h, vector: rho(h)(vector))


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

    # The module is placed by its construction, not by asking the coefficient
    # field's characteristic; the Brauer value is the lifted eigenvalue sum,
    # which is -1 at g^2 while the modular trace there is 1.
    assert acted not in BrauerCharacterRepresentations(GF(2)[group])
    assert brauer(group.one()) == 2
    assert brauer(g**2) == -1
    assert brauer(g**4) == -1
    assert acted.action_of(g**2).trace() == GF(2).one()


def test_a_character_is_computed_once_and_kept() -> None:
    r"""A character is a datum of the module: asking twice yields the same class function.

    The ordinary character reads one trace per conjugacy class and the Brauer
    character lifts the eigenvalues of each $p$-regular class through a private
    finite representation, so neither is recomputed on a second request; the
    values are asserted first so that an object carrying no character cannot
    pass the identity comparison.
    """
    group, representation = _permutation_module_of_s3()
    cyclic, brauer_action = _order_three_plane_of_c6()
    (generator,) = cyclic.group_generators()
    ordinary = representation.character()
    modular = brauer_action.brauer_character()

    assert ordinary(group.one()) == 3
    assert modular(cyclic.one()) == 2
    assert modular(generator**2) == -1
    assert ordinary is representation.character()
    assert modular is brauer_action.brauer_character()
