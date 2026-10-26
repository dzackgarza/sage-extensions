r"""Absolute Galois groups of finite fields and of $\mathbb{Q}$, through finite Galois theory."""

from sage_extensions.all import *  # noqa: F401,F403


def _cubic_field(radicand):
    x = QQ.polynomial_ring("x").algebra_generator("x")
    return (x**3 - QQ(radicand)).number_field("a")


def test_the_frobenius_of_f9_raises_to_the_ninth_power_and_fixes_f9() -> None:
    r"""The arithmetic Frobenius of $G_{\mathbb{F}_9}$ is $x \mapsto x^9$, not $x \mapsto x^3$.

    On $\alpha$ generating $\mathbb{F}_{9^4}$, $\alpha^9 \ne \alpha^3$; on
    $\mathbb{F}_9$ it is the identity.
    """
    field = GF(9, "u")
    group = field.absolute_galois_group()
    frobenius = group.frobenius()
    degree_four = group.finite_extension(4)
    alpha = degree_four.embedding()(degree_four.field().field_generators()[0])
    u = group.base_embedding()(field.field_generators()[0])

    assert frobenius(alpha) == alpha**9
    assert frobenius(alpha) != alpha**3
    assert frobenius(u) == u
    assert (~frobenius * frobenius)(alpha) == alpha


def test_the_frobenius_of_f625_restricts_to_that_of_f25_with_two_extensions() -> None:
    r"""$G_{\mathbb{F}_5} \to \operatorname{Gal}(\mathbb{F}_{5^4}/\mathbb{F}_5) \cong \mathbb{Z}/4$.

    Its kernel is normal of index $4$, contains $\mathrm{Frob}^4$ and not
    $\mathrm{Frob}$; the Frobenius of $\mathbb{F}_{25}$ has exactly
    $[\mathbb{F}_{625} : \mathbb{F}_{25}] = 2$ extensions to $\mathbb{F}_{625}$,
    namely $\sigma$ and $\sigma^3$.  Source: Lang, *Algebra*, V §5.
    """
    group = GF(5).absolute_galois_group()
    frobenius = group.frobenius()
    degree_two = group.finite_extension(2)
    degree_four = group.finite_extension(4)
    restriction_two = group.restriction_map(degree_two)
    restriction_four = group.restriction_map(degree_four)
    kernel = restriction_four.kernel()
    sigma = restriction_four(frobenius)
    tau = restriction_two(frobenius)

    assert group.finite_quotient(degree_four).order() == 4
    assert restriction_four.is_surjective()
    assert kernel.index() == 4
    assert kernel.is_normal()
    assert frobenius not in kernel
    assert frobenius**4 in kernel
    assert sigma.multiplicative_order() == 4
    assert tau.multiplicative_order() == 2
    assert [k for k in range(4) if restriction_two(frobenius**k) == tau] == [1, 3]
    assert restriction_four(frobenius**3) != sigma


def test_open_subgroups_of_the_absolute_galois_group_of_f5_follow_the_degrees() -> None:
    r"""$G_{\mathbb{F}_{25}}$ has index $2$, its Frobenius is $\mathrm{Frob}_5^2$, and $G_{\mathbb{F}_{25}} \cap G_{\mathbb{F}_{125}} = G_{\mathbb{F}_{5^6}}$ has index $6$."""
    group = GF(5).absolute_galois_group()
    frobenius = group.frobenius()
    index_two = group.open_subgroup(group.finite_extension(2))
    index_three = group.open_subgroup(group.finite_extension(3))
    intersection = index_two.intersection(index_three)

    assert index_two.index() == 2
    assert frobenius not in index_two
    assert frobenius**2 in index_two
    assert index_two.inclusion()(index_two.frobenius()) == frobenius**2
    assert intersection.index() == 6
    assert intersection <= index_two
    assert intersection <= index_three


def test_the_core_of_the_subgroup_fixing_the_real_cube_root_of_two_has_index_six() -> None:
    r"""$G_{\mathbb{Q}(\sqrt[3]{2})}$ has index $3$ and is not normal; its core fixes the splitting field of $x^3 - 2$, of degree $6$."""
    group = QQ.absolute_galois_group()
    subgroup = group.open_subgroup(_cubic_field(2))
    core = subgroup.core()

    assert subgroup.index() == 3
    assert not subgroup.is_normal()
    assert core.index() == 6
    assert core.is_normal()
    assert core <= subgroup


def test_two_is_inert_in_the_field_of_root_five() -> None:
    r"""$x^2 - x - 1$ is irreducible mod $2$, so $2$ is inert in $\mathbb{Q}(\sqrt5)$.

    The decomposition group is all of $\operatorname{Gal}(\mathbb{Q}(\sqrt5)/\mathbb{Q})$,
    inertia is trivial, and $\mathrm{Frob}_2$ is the nontrivial element; the
    Frobenius class of $G_{\mathbb{Q}}$ at $2$ maps to it.  Source: Neukirch,
    *Algebraic Number Theory*, I.8.
    """
    group = QQ.absolute_galois_group()
    field = QuadraticField(5, "a")
    quotient = group.finite_quotient(group.extension_data(field))
    prime = field.primes_above(2)[0]

    assert quotient.order() == 2
    assert quotient.decomposition_group(prime).order() == 2
    assert quotient.inertia_group(prime).order() == 1
    assert quotient.frobenius_class(2, prime).representative() != quotient.one()
    assert group.frobenius_class(2).image(quotient, prime) == quotient.frobenius_class(2, prime)


def test_cyclotomic_and_kummer_characters_of_finite_fields_take_their_frobenius_values() -> None:
    r"""On $G_{\mathbb{F}_5}$: $\chi_3(\mathrm{Frob}) = 5 \equiv -1 \bmod 3$ and $\mathrm{Frob}(\sqrt2)/\sqrt2 = (2/5) = -1$.

    Both characters factor through $\mathbb{F}_{25}$ and have kernel of index
    $2$.  On $G_{\mathbb{F}_9}$, $\chi_5(\mathrm{Frob}) = 9 \equiv 4 \bmod 5$.
    """
    group = GF(5).absolute_galois_group()
    frobenius = group.frobenius()

    for character in (group.cyclotomic_character(3), group.quadratic_character(2)):
        assert character.factor_extension().degree() == 2
        assert character(frobenius**5) == character(frobenius**2) * character(frobenius**3)
        assert character(frobenius) != character.codomain().one()
        assert character.kernel().index() == 2
        assert frobenius not in character.kernel()
        assert frobenius**2 in character.kernel()

    field_nine = GF(9, "u").absolute_galois_group()
    assert field_nine.cyclotomic_character(5)(field_nine.frobenius()).value() == 4
