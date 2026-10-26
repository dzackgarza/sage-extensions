r"""Free resolutions of finitely generated abelian groups.

Over a principal ideal domain every submodule of a free module is free, so a
finitely generated module has a free resolution of length at most one
(Weibel, *An Introduction to Homological Algebra*, 4.1.4 and 4.1.5).
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_z_mod_6_plus_z_has_the_length_one_resolution_z_to_z2_by_6_0() -> None:
    r"""$0 \to \mathbb Z \xrightarrow{(6, 0)} \mathbb Z^2 \to \mathbb Z/6 \oplus \mathbb Z \to 0$ is exact.

    Source: Weibel 4.1.5; by hand.
    """
    F = ZZ**2
    x = F.module_generator(0)
    M = F / F.submodule([6 * x])
    resolution = M.free_resolution()

    assert resolution.is_exact()
    assert resolution.length() == 1
    assert resolution.term(0).module_rank() == 2
    assert resolution.term(1).module_rank() == 1
    assert resolution.term(2).module_rank() == 0
    d1 = resolution.differential(1)
    assert d1.is_injective()
    assert d1(resolution.term(1).module_generator(0)) in (6 * resolution.term(0).module_generator(0), -6 * resolution.term(0).module_generator(0))
    assert M.torsion_submodule().cardinality() == 6


def test_the_noninjective_presentation_2x_4x_resolves_as_z_by_2_to_z() -> None:
    r"""$\operatorname{coker}(\mathbb Z^2 \xrightarrow{(2, 4)} \mathbb Z) = \mathbb Z/2$, whose minimal
    resolution is $0 \to \mathbb Z \xrightarrow{2} \mathbb Z$; the presentation has kernel of rank one.

    Source: Weibel 4.1.5; by hand, gcd(2, 4) = 2.
    """
    F0 = ZZ**1
    x = F0.module_generator(0)
    R = ZZ**2
    presentation = R.Mor(F0)({0: 2 * x, 1: 4 * x})
    assert not presentation.is_injective()
    assert presentation.kernel().module_rank() == 1

    M = presentation.cokernel()
    assert M.cardinality() == 2
    resolution = M.free_resolution()
    assert resolution.is_exact()
    assert resolution.term(1).module_rank() == 1
    assert resolution.differential(1).is_injective()
    assert resolution.differential(1).cokernel().cardinality() == 2
