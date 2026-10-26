r"""Modules over varying commutative rings, and semilinear maps over $\iota: \mathbb Z \to \mathbb Q$.

The modules over all commutative rings form the Grothendieck construction of
$R \mapsto R\text{-Mod}$: the projection $(R, M) \mapsto R$ has fibre $R\text{-Mod}$ over $R$; along
$\sigma: R \to S$ the cocartesian transport is extension of scalars $S \otimes_R -$ and the cartesian
transport is restriction of scalars.  An arrow $M \to N$ over $\sigma$ is a $\sigma$-semilinear map
$f(rm) = \sigma(r) f(m)$, equivalently an $R$-linear map $M \to \operatorname{Res}_\sigma N$, by the definitions.  So
$\mathbb Q \otimes_{\mathbb Z} \mathbb Z^2 = \mathbb Q^2$, and $\operatorname{Res}_\iota \mathbb Q^2$ is a
$\mathbb Z$-module.  Identities are semilinear over identities, and composing with them changes nothing.
"""

from sage_extensions.all import *  # noqa: F401,F403


def inclusion():
    return ZZ.Mor(QQ)(lambda n: QQ(n))


def test_the_fibre_over_z_and_the_projection_to_rings() -> None:
    r"""The fibre over $\mathbb Z$ is $\mathbb Z\text{-Mod}$, and $\mathbb Z^2$ projects to $\mathbb Z$."""
    modules = ModulesOverCommutativeRings()

    assert modules.fiber(ZZ) == Modules(ZZ)
    assert ModuleBaseRingProjection()(ZZ ^ 2) is ZZ


def test_extension_of_scalars_along_iota_is_over_q_and_restriction_is_over_z() -> None:
    r"""$\mathbb Q \otimes_{\mathbb Z} \mathbb Z^2$ is a $\mathbb Q$-module; $\operatorname{Res}_\iota \mathbb Q^2$ a
    $\mathbb Z$-module."""
    modules = ModulesOverCommutativeRings()

    assert modules.cocartesian_transport(inclusion())(ZZ ^ 2).base_ring() is QQ
    assert modules.cartesian_transport(inclusion())(QQ ^ 2).base_ring() is ZZ


def test_extension_of_scalars_of_z2_along_iota_has_rank_two() -> None:
    r"""$\mathbb Q \otimes_{\mathbb Z} \mathbb Z^2 \cong \mathbb Q^2$."""
    extension = ModulesOverCommutativeRings().cocartesian_transport(inclusion())

    assert extension(ZZ ^ 2).module_rank() == 2


def test_a_semilinear_map_over_iota_is_determined_by_its_generator_images() -> None:
    r"""$s(e_0) = w_0$, $s(e_1) = 2w_1$ over $\iota$: $s(3e_0) = \iota(3) w_0 = 3w_0$ and
    $s(e_0 - e_1) = w_0 - 2w_1$."""
    lattice, space = ZZ ^ 2, QQ ^ 2
    e0, e1 = lattice.module_generator(0), lattice.module_generator(1)
    w0, w1 = space.module_generator(0), space.module_generator(1)
    maps = ModulesOverCommutativeRings().Mor(lattice, space)
    iota = inclusion()
    semilinear = maps(iota, maps.compatible_mor(iota)({0: w0, 1: 2 * w1}))

    assert semilinear.scalar_map() is iota
    assert semilinear(e1) == 2 * w1
    assert semilinear(3 * e0) == 3 * w0
    assert semilinear(e0 - e1) == w0 - 2 * w1


def test_the_identity_of_z2_is_semilinear_over_the_identity_of_z() -> None:
    r"""$\mathrm{id}_{\mathbb Z^2}$ lies over $\mathrm{id}_{\mathbb Z}$ and fixes $e_0$."""
    lattice = ZZ ^ 2
    identity = ModulesOverCommutativeRings().Mor(lattice, lattice).identity()

    assert identity(lattice.module_generator(0)) == lattice.module_generator(0)


def test_composing_with_the_identity_of_q2_changes_nothing() -> None:
    r"""$\mathrm{id}_{\mathbb Q^2} \circ s = s$ for $s$ over $\iota$."""
    lattice, space = ZZ ^ 2, QQ ^ 2
    w0, w1 = space.module_generator(0), space.module_generator(1)
    maps = ModulesOverCommutativeRings().Mor(lattice, space)
    iota = inclusion()
    semilinear = maps(iota, maps.compatible_mor(iota)({0: w0, 1: 2 * w1}))
    identity = ModulesOverCommutativeRings().Mor(space, space).identity()

    assert identity * semilinear == semilinear
