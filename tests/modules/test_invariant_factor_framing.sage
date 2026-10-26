r"""Invariant factors of finitely generated abelian groups and of discriminant groups."""

from sage_extensions.all import *  # noqa: F401,F403


def test_z2_mod_x_is_free_of_rank_one_and_z2_mod_2x_is_not_projective() -> None:
    r"""$\mathbb Z^2/(x) \cong \mathbb Z$ is free of rank one, hence projective and locally free;
    $\mathbb Z^2/(2x) \cong \mathbb Z/2 \oplus \mathbb Z$ has torsion, so it is neither projective
    nor locally free (over a PID, projective = free = torsion-free for f.g. modules).

    Source: Lang, Algebra, III.7 (structure theorem over a PID).
    """
    F = ZZ**2
    x = F.module_generator(0)
    free_quotient = F / F.submodule([x])
    assert free_quotient.is_torsion_free()
    assert free_quotient.is_free()
    assert free_quotient.is_projective()
    assert free_quotient.is_locally_free()
    assert free_quotient.module_rank() == 1
    assert free_quotient.finite_free_trivialization().is_isomorphism()
    local = free_quotient.local_free_trivialization(ZZ.spectrum()(ZZ.ideal(5)))
    assert local.is_isomorphism()

    torsion_quotient = F / F.submodule([2 * x])
    assert not torsion_quotient.is_torsion_free()
    assert not torsion_quotient.is_projective()
    assert not torsion_quotient.is_locally_free()
    assert torsion_quotient.torsion_submodule().cardinality() == 2


def test_the_hyperbolic_plane_is_unimodular_so_its_discriminant_group_is_zero() -> None:
    """det U = -1, so U^vee / U = 0. Source: Nikulin, Integral symmetric bilinear forms, 1.2."""
    discriminant = Lattices(ZZ)("U").discriminant_module()
    assert discriminant.is_zero()
    assert discriminant.cardinality() == 1
    assert discriminant.invariant_factor_form().codomain().is_zero()


def test_u2_has_discriminant_group_z_mod_2_squared_generated_by_the_half_basis_classes() -> None:
    r"""$U(2)^\vee = \tfrac12 U(2)$, so $U(2)^\vee/U(2) = (\mathbb Z/2)^2$ with generators $e/2, f/2$.

    Source: Nikulin 1.2; by hand, det U(2) = -4.
    """
    discriminant = Lattices(ZZ)([[0, 2], [2, 0]]).discriminant_module()
    assert discriminant.cardinality() == 4
    assert tuple(discriminant.invariant_factor_form().codomain().invariant_factors()) == (2, 2)
    assert all(generator.additive_order() == 2 for generator in discriminant.module_generators())
    assert discriminant.invariant_factor_form().is_isomorphism()


def test_the_a2_discriminant_quadratic_form_lives_on_z_mod_3_and_normalization_preserves_q() -> None:
    """det A2 = 3, so A2^vee/A2 = Z/3; the invariant-factor normalization is an isometry of q.

    Source: Conway–Sloane, SPLAG, 4.6.1 (A_n^* / A_n = Z/(n+1)).
    """
    discriminant = Lattices(ZZ)("A2").discriminant_quadratic_form()
    normalization = discriminant.invariant_factor_form()
    normalized = normalization.codomain()
    generator = discriminant.module_generator(0)
    assert discriminant.cardinality() == 3
    assert generator.q() == discriminant.value_module()(QQ(4) / 3)
    assert tuple(normalized.invariant_factors()) == (3,)
    assert normalization.is_isomorphism()
    for generator in discriminant.module_generators():
        assert normalized.q(normalization(generator)) == discriminant.q(generator)


def test_the_odd_unimodular_lattice_i2_has_zero_discriminant_group() -> None:
    """det I_2 = 1. Source: Nikulin 1.2."""
    discriminant = Lattices(ZZ)([[1, 0], [0, 1]]).discriminant_bilinear_form()
    assert discriminant.is_zero()
    assert discriminant.invariant_factor_form().codomain().is_zero()
