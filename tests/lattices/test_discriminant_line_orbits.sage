r"""Line orbits through the finite discriminant stabilizer, not the integral one (issue #294).

For a primitive isotropic line $\langle v\rangle$ with $p = \operatorname{div}(v)$ and
$c = [v/p]\in A_L$, Eichler's criterion (Gritsenko--Hulek--Sankaran, Lemma 7.8, p. 503) yields,
once a lift $\gamma\mapsto g$ is chosen, a stabilizer element $kg$ with
$\mathrm{disc}(kg) = \gamma$, because $\widetilde{SO}(L)$-orbits of primitive vectors depend
only on length and class.  Hence the discriminant image of $O(L)_v$ is $\operatorname{Stab}_{O(A_L)}(c)$,
computed in the finite quadratic module $A_L$ instead of parsing any integral stabilizer.
The remaining sign character is separate and is not inferred from the discriminant one.

The three specimens are cheap enough to exercise every sign/discriminant combination: $U+U$ is
unimodular so the discriminant factor is trivial, and $U+U+\langle-2\rangle$ has $A_L = \mathbb Z/2$;
the hyperbolic plane $U\oplus U$ sum is $L_1$ of Scattone's rank-five shadow.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _lattice(d):
    r"""$U\oplus U\oplus\langle-2d\rangle$; $U\oplus U$ for $d = 0$."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    if d:
        lattice = lattice + Lattices(ZZ)([[-2 * d]])
    return lattice


def test_the_unimodular_plane_sum_has_one_line_orbit_under_every_factor() -> None:
    r"""$A_{U\oplus U}=0$, so nothing splits: the class stabilizer is trivial in each case."""
    lattice = _lattice(0)
    orthogonal = lattice.Aut()
    stable = lattice.stable_orthogonal_group()
    plus = lattice.O_plus()
    stable_plus = stable.intersection(plus)

    assert orthogonal.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    assert stable.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    assert plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    assert stable_plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)

    for representative in orthogonal.isotropic_orbit_representatives(1):
        vector = representative.inclusion()(representative.module_generator(0))
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True


def test_the_line_orbits_of_l_1_under_the_discriminant_and_sign_kernels() -> None:
    r"""$L_1 = U\oplus U\oplus\langle-2\rangle$: the class stabilizer is trivial here as well.

    $A_{L_1} = \mathbb Z/2$, and a primitive isotropic $v$ with $\operatorname{div}(v) = 1$ has
    normalized class $0$, whose stabilizer is all of $O(A_{L_1})$ -- hence no splitting.
    """
    lattice = _lattice(1)
    orthogonal = lattice.Aut()
    stable = lattice.stable_orthogonal_group()
    plus = lattice.O_plus()
    stable_plus = stable.intersection(plus)

    assert orthogonal.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    assert stable.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    assert plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    assert stable_plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)

    for representative in orthogonal.isotropic_orbit_representatives(1):
        vector = representative.inclusion()(representative.module_generator(0))
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True


def test_vectors_are_not_identified_when_a_discriminant_class_differs_from_its_negative() -> None:
    r"""$3e+3f+g$ and its negative have classes $6$ and $12$ in $\mathbb Z/18$, distinct.

    $L_9 = U + U + \langle-18\rangle$ shows the vector-versus-line distinction the lemma's
    normalized class makes: a line and its two vectors are one line, but the vectors have
    different normalized classes.  The line count the public call returns is therefore not
    the vector count.
    """
    lattice = _lattice(9)
    labels = tuple(lattice.module_generating_set())
    e, f, g = (
        lattice.module_generator(labels[0]),
        lattice.module_generator(labels[1]),
        lattice.module_generator(labels[4]),
    )
    first = 3 * e + 3 * f + g
    second = -first
    assert first.q() == ZZ(0)
    assert second.q() == ZZ(0)
    assert first.is_primitive() is True
    assert second.is_primitive() is True
    assert lattice.div(first) == ZZ(3)
    assert lattice.div(second) == ZZ(3)
    assert lattice.divided_discriminant_class(first) != lattice.divided_discriminant_class(second)

    lines = lattice.Aut().isotropic_orbit_representatives(1)
    assert lines.cardinality() == cardinal(2)
    for representative in lines:
        vector = representative.inclusion()(representative.module_generator(0))
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True

    # The subgroup route constructs ambient line classes from im(rho) acting on class
    # pairs too, so it must return two lines and not one per candidate normalized class.
    plus = lattice.O_plus()
    stable_plus = lattice.stable_orthogonal_group().intersection(plus)
    assert plus.isotropic_orbit_representatives(1).cardinality() == cardinal(2)
    assert stable_plus.isotropic_orbit_representatives(1).cardinality() == cardinal(2)
    for group in (plus, stable_plus):
        for representative in group.isotropic_orbit_representatives(1):
            vector = representative.inclusion()(representative.module_generator(0))
            assert vector.q() == ZZ(0)
            assert vector.is_primitive() is True


def _card_lattice(k):
    r"""$\Lambda_{2k}$ from the corrected card: $U^2 \oplus E_8(-1)^2 \oplus \langle-2k\rangle$.

    ``Lattices(ZZ)("E8")`` is already negative definite (signature $(0,8)$, root scale $-1$),
    so this has rank $21$ and signature $(2,19)$, not the rank-five $U^2 \oplus \langle-2k\rangle$
    shadow.  Groups below are asked about this lattice, never about the shadow.
    """
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)([[-2 * k]])
    )


# Card objects are deliberately shared: their discriminant module and class data are
# expensive to build once at this rank, so the separate O-, stable- and spinor-positive
# comparisons must read that same retained lattice rather than authenticating by repetition.
_CARD_BY_TAG = {1: _card_lattice(1), 2: _card_lattice(2)}


def test_the_scattone_card_input_is_the_published_lattice() -> None:
    r"""The input is $\Lambda_2$ and $\Lambda_4$ (rank 21, signature $(2,19)$), not a proxy.

    These are the invariants the corrected cards themselves state (rank, signature, determinant,
    parity, and their Conway--Sloane genus symbol).  Their presence is deliberate: a helper that
    silently shrank the lattice to its rank-five shadow would fail here.
    """
    for tag, k, determinant, genus in (
        ("6JRX", 1, ZZ(-2), "II_{2,19} (2: 1^20 [2^1]_7)"),
        ("6JRY", 2, ZZ(-4), "II_{2,19} (2: 1^20:[4^1]_7)"),
    ):
        lattice = _CARD_BY_TAG[k]
        assert lattice.module_rank() == cardinal(21)
        signature = lattice.signature_pair()
        assert signature.first() == cardinal(2)
        assert signature.second() == cardinal(19)
        assert lattice.determinant() == determinant
        assert lattice.is_even() is True
        assert lattice.conway_sloane_genus_symbol() == genus


def test_6jrx_has_one_line_orbit_under_o_plus() -> None:
    r"""``6JRX`` (rank $21$, signature $(2,19)$): one primitive isotropic line orbit under $O^+(L)$.

    The corrected card's row is ``O+ -> constant: 1`` (§ 6, p. 94 with § 1, p. 3).  Both
    hyperbolic planes are present, so Eichler's criterion applies and the discriminant
    image of the line stabilizer stabilizes the class set $\{c,-c\}$ inside $\im\rho$.
    """
    lattice = _CARD_BY_TAG[1]
    plus = lattice.O_plus()
    assert plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    for representative in plus.isotropic_orbit_representatives(1):
        vector = representative.inclusion()(representative.module_generator(0))
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True


def test_6jry_has_one_line_orbit_under_o_plus() -> None:
    r"""``6JRY`` (rank $21$, signature $(2,19)$, $\det -4$): the same row under $O^+(L)$."""
    lattice = _CARD_BY_TAG[2]
    plus = lattice.O_plus()
    assert plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    for representative in plus.isotropic_orbit_representatives(1):
        vector = representative.inclusion()(representative.module_generator(0))
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True


def test_6jrx_has_one_line_orbit_under_otilde_plus() -> None:
    r"""``6JRX``'s other line row: ``Otilde+ -> constant: 1`` (Theorem 4.0.1, p. 55).

    This row must be computed by the public call too; its expected value is the card's,
    not a derivation.  The joint discriminant/sign kernel asks for the ambient selected
    finite generating family of this rank-21 group's Eichler construction.
    """
    lattice = _CARD_BY_TAG[1]
    stable_plus = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    assert stable_plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)


def test_6jry_has_one_line_orbit_under_otilde_plus() -> None:
    r"""``6JRY``'s other line row: ``Otilde+ -> constant: 1`` (Theorem 4.0.1, p. 55).
    """
    lattice = _CARD_BY_TAG[2]
    stable_plus = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    assert stable_plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
    lattice = _CARD_BY_TAG[2]
    stable_plus = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    assert stable_plus.isotropic_orbit_representatives(1).cardinality() == cardinal(1)
