r"""Finite bilinear and quadratic forms, taken as discriminant forms of small lattices."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_discriminant_bilinear_form_of_two_plus_one_is_cyclic_of_order_two() -> None:
    r"""$\langle 2\rangle \oplus \langle 1\rangle$ has discriminant group $\mathbb{Z}/2$, one invariant factor $2$, $b = 1/2$.

    The invariant-factor form is isometric to the form it normalizes.
    """
    form = Lattices(ZZ)([[2, 0], [0, 1]]).discriminant_bilinear_form()
    normalized = form.invariant_factor_form().codomain()

    assert form.cardinality() == 2
    assert tuple(form.invariant_factors()) == (2,)
    assert normalized.module_generators().cardinality() == 1
    assert normalized.b(normalized.module_generator(0), normalized.module_generator(0)) == normalized.value_module()(QQ(1) / 2)
    assert normalized.is_isometric_to(form)


def test_the_discriminant_quadratic_form_of_two_plus_one_is_one_half_on_z2() -> None:
    r"""$\langle 2\rangle \oplus \langle 1\rangle$ has discriminant quadratic form $q = 1/2 \bmod 2$ on $\mathbb{Z}/2$."""
    form = Lattices(ZZ)([[2, 0], [0, 1]]).discriminant_quadratic_form()
    normalized = form.invariant_factor_form().codomain()

    assert normalized.module_generators().cardinality() == 1
    assert normalized.q(normalized.module_generator(0)) == normalized.value_module()(QQ(1) / 2)
    assert normalized.is_isometric_to(form)


def test_the_orthogonal_group_of_the_discriminant_form_of_eight_has_order_two() -> None:
    r"""$\langle 8\rangle$ has $q(g) = 1/8 \bmod 2$ on $\mathbb{Z}/8$; $O(q) = \{u : u^2 \equiv 1 \bmod 16\} = \{\pm 1\}$."""
    form = Lattices(ZZ)([[8]]).discriminant_quadratic_form()
    generator = form.module_generator(0)

    assert form.q(generator) == form.value_module()(QQ(1) / 8)
    assert form.O().order() == 2
    assert all(form.q(g(generator)) == form.q(generator) for g in form.O())


def test_the_bilinear_orthogonal_group_of_z8_is_larger_than_the_quadratic_one() -> None:
    r"""On $\mathbb{Z}/8$ with $b = 1/8 \bmod 1$, $O(b) = \{u : u^2 \equiv 1 \bmod 8\} = (\mathbb{Z}/8)^\times$ has order $4$.

    The quadratic refinement $q = 1/8 \bmod 2$ cuts this to $O(q) = \{\pm 1\}$
    of order $2$: multiplication by $3$ preserves $b$ but sends $q$ to $9/8$.
    """
    lattice = Lattices(ZZ)([[8]])

    assert lattice.discriminant_quadratic_form().O().order() == 2
    assert lattice.discriminant_bilinear_form().O().order() == 4


def test_mixed_prime_jordan_framing_is_distinct_and_has_an_explicit_isometry() -> None:
    form = (Lattices(ZZ)("A2") + Lattices(ZZ)("A1")).discriminant_quadratic_form()
    decomposition = form.p_adic_jordan_decomposition()
    normalization = form.p_adic_jordan_form()
    jordan = normalization.codomain()

    assert tuple(decomposition.index_set()) == (ZZ(2), ZZ(3))
    assert tuple(generator.additive_order() for generator in decomposition[ZZ(2)]) == (2,)
    assert tuple(generator.additive_order() for generator in decomposition[ZZ(3)]) == (3,)
    assert form.invariant_factor_form().codomain().module_generators().cardinality() == 1
    assert jordan.module_generators().cardinality() == 2
    assert jordan.cardinality() == form.cardinality() == 6
    assert all(
        left.b(right) == form.bilinear_value_module().zero()
        for left in decomposition[ZZ(2)]
        for right in decomposition[ZZ(3)]
    )
    for generator in form.module_generators():
        assert normalization.inverse()(normalization(generator)) == generator
        assert jordan.q(normalization(generator)) == form.q(generator)


def test_the_form_one_third_on_z3_is_anti_isometric_only_to_its_negative() -> None:
    r"""$b = 1/3$ on $\mathbb{Z}/3$: an anti-isometry to itself needs $u^2 \equiv -1 \bmod 3$, which has no solution."""
    form = Lattices(ZZ)([[3]]).discriminant_bilinear_form()

    assert form.b(form.module_generator(0), form.module_generator(0)) == form.value_module()(QQ(1) / 3)
    assert not form.is_anti_isometric(form)
    assert form.is_anti_isometric(form.twist(-1))


def test_bilinear_jordan_form_preserves_the_pairing() -> None:
    form = (Lattices(ZZ)("A2") + Lattices(ZZ)("A1")).discriminant_bilinear_form()
    normalization = form.p_adic_jordan_form()
    jordan = normalization.codomain()

    assert tuple(form.p_adic_jordan_decomposition().index_set()) == (ZZ(2), ZZ(3))
    for left in form.module_generators():
        for right in form.module_generators():
            assert jordan.b(normalization(left), normalization(right)) == form.b(left, right)


def test_the_bilinear_discriminant_form_of_u2_is_metabolic_with_orthogonal_group_s3() -> None:
    r"""$(\mathbb{Z}/2)^2$ with $b(e,f) = 1/2$ and $b(x,x) = 0$ for all $x$.

    Every automorphism of $(\mathbb{Z}/2)^2$ preserves $b$, so
    $O(b) = GL_2(\mathbb{F}_2) \cong S_3$ of order $6$.  The three lines are
    the Lagrangians; $O(b)$ permutes them transitively, so its orbits on
    isotropic subgroups have sizes $1$ (the zero subgroup) and $3$, and a
    metabolizer $M$ has $M^\perp / M = 0$.
    """
    form = Lattices(ZZ)("U").twist(2).discriminant_bilinear_form()
    first = form.module_generator(0)
    metabolizer = form.metabolizer()

    assert not form.is_anisotropic()
    assert form.is_metabolic()
    assert form.lagrangian_subobjects().cardinality() == 3
    assert form.O().order() == 6
    assert sorted(orbit.cardinality() for orbit in form.orbits_on_isotropic_subobjects()) == [1, 3]
    assert form.orbit(first).cardinality() == 3
    assert metabolizer.cardinality() == 2
    assert form.orthogonal_quotient(metabolizer).cardinality() == 1


def test_u2_bilinear_orthogonal_group_element_orbit() -> None:
    form = Lattices(ZZ)("U").twist(2).discriminant_bilinear_form()
    label = next(iter(form.module_generating_set()))
    element = form.module_generator(label)
    group = form.O()

    assert group.order() == 6
    assert group.orbit(element).cardinality() == 3


def test_the_discriminant_forms_of_a1_are_one_half_mod_one_and_minus_one_half_mod_two() -> None:
    r"""$A_1 = \langle -2\rangle$: $A_1^\vee / A_1 = \mathbb{Z}/2$ on $e/2$, with $b = q = -1/2$."""
    a1 = Lattices(ZZ)("A1")
    bilinear = a1.discriminant_bilinear_form()
    quadratic = a1.discriminant_quadratic_form()

    assert bilinear.cardinality() == 2
    assert quadratic.cardinality() == 2
    assert bilinear.b(bilinear.module_generator(0), bilinear.module_generator(0)) == bilinear.value_module()(QQ(-1) / 2)
    assert quadratic.q(quadratic.module_generator(0)) == quadratic.value_module()(QQ(-1) / 2)
    assert a1.correlation_morphism().cokernel().cardinality() == 2
