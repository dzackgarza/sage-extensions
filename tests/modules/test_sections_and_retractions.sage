r"""Freeness of finitely presented abelian groups."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z2_mod_g_is_free_and_z2_mod_6g_is_not() -> None:
    r"""$\mathbb Z^2/(g) \cong \mathbb Z$ is free; $\mathbb Z^2/(6g) \cong \mathbb Z/6 \oplus \mathbb Z$ has
    torsion, so it is not free.

    Source: Lang, Algebra, III.7 (structure theorem over a PID).
    """
    F = ZZ**2
    g = F.module_generator(0)
    torsion_free = F / F.submodule([g])
    with_torsion = F / F.submodule([6 * g])

    assert torsion_free.is_free()
    assert torsion_free.module_rank() == 1
    assert not with_torsion.is_free()
    assert with_torsion.torsion_submodule().cardinality() == 6
