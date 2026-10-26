r"""The free resolution of a free module, and lifts of module maps to resolutions.

A free module $F$ is its own free resolution: $0 \to F \xrightarrow{\mathrm{id}} F \to 0$, of
length $0$, with $F_1 = 0$.  By the comparison theorem a map $f: M \to N$ lifts to a chain map $\tilde f: P_\bullet \to Q_\bullet$ of
projective resolutions with $\varepsilon_Q \tilde f_0 = f \varepsilon_P$, unique up to chain homotopy;
for resolutions of length $0$ by the modules themselves, $\tilde f_0 = f$ and the homotopy between
$\tilde f$ and itself vanishes.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_free_resolution_of_z2_is_z2_in_degree_zero() -> None:
    r"""$P_0 = \mathbb Z^2$, $P_1 = 0$, $\varepsilon = \mathrm{id}$ and $d_1 = 0$."""
    plane = ZZ ^ 2
    resolution = plane.free_resolution()

    assert resolution.module() is plane
    assert resolution.term(0) is plane
    assert resolution.augmentation() == plane.End().one()
    assert resolution.differential(1).codomain() is plane


def test_the_first_term_of_the_free_resolution_of_z2_is_zero() -> None:
    r"""$P_1 = 0$ has rank $0$, and it is the domain of $d_1$."""
    resolution = (ZZ ^ 2).free_resolution()

    assert resolution.term(1).module_rank() == 0
    assert resolution.differential(1).domain().module_rank() == 0


def test_the_free_resolution_of_z2_has_length_zero() -> None:
    r"""$0 \to \mathbb Z^2 \to \mathbb Z^2 \to 0$ has length $0$."""
    assert (ZZ ^ 2).free_resolution().length() == 0


def test_the_free_resolution_of_z2_is_exact() -> None:
    r"""$0 \to \mathbb Z^2 \to \mathbb Z^2 \to 0$ with the identity augmentation is exact."""
    assert (ZZ ^ 2).free_resolution().is_exact()


def test_a_map_of_free_modules_lifts_to_itself_in_degree_zero() -> None:
    r"""$f: \mathbb Z^2 \to \mathbb Z$, $e_0 \mapsto 1$, $e_1 \mapsto 2$ lifts with $\tilde f_0 = f$."""
    plane, line = ZZ ^ 2, ZZ ^ 1
    unit = line.module_generator(0)
    f = plane.Mor(line)({0: unit, 1: 2 * unit})
    lift = plane.free_resolution().lift_morphism(f, line.free_resolution())

    assert lift.module_morphism() is f
    assert lift.component(0)(plane.module_generator(0)) == unit
    assert lift.component(0)(plane.module_generator(1)) == 2 * unit


def test_a_lift_is_homotopic_to_itself_by_the_zero_homotopy() -> None:
    r"""The chain homotopy from $\tilde f$ to $\tilde f$ is zero in degree $0$."""
    plane, line = ZZ ^ 2, ZZ ^ 1
    unit = line.module_generator(0)
    f = plane.Mor(line)({0: unit, 1: 2 * unit})
    lift = plane.free_resolution().lift_morphism(f, line.free_resolution())
    homotopy = lift.chain_homotopy_to(lift)

    assert homotopy.component(0)(plane.module_generator(0)) == homotopy.component(0).codomain().zero()
