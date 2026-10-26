r"""Centres, finite local rings, real quadratic fields and cardinalities of the number systems."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_algebraic_reals_embed_in_the_reals_and_the_algebraic_numbers_do_not() -> None:
    r"""``AA`` is the real closure of ``QQ`` in ``RR``, so ``sqrt 2`` in ``AA`` is a
    real number squaring to ``2``; ``QQbar`` contains ``i`` with ``i^2 = -1``, which
    has no square root in the ordered field ``RR``, so there is no ring morphism
    ``QQbar -> RR``."""
    root_two = AA(2).sqrt()

    assert RR(root_two) ** 2 == RR(2)
    assert RR(root_two) > 0
    assert QQbar.Mor(RR).cardinality() == 0


def test_the_centre_of_the_two_by_two_rational_matrices_is_the_scalars() -> None:
    r"""``Z(M_2(QQ)) = QQ * I`` (Lang, *Algebra*, XVII §1): the scalars commute with
    everything, and a matrix commuting with ``E_{12}`` and ``E_{21}`` is scalar."""
    matrices = QQ.matrix_space(2)
    center = matrices.ring_center()
    e12 = matrices.matrix_unit(0, 1)
    e21 = matrices.matrix_unit(1, 0)
    e11 = matrices.matrix_unit(0, 0)

    assert center.inclusion()(center.one()) == matrices.one()
    assert 3 * matrices.one() in center
    assert e12 not in center
    assert e11 not in center
    assert e11 + 2 * (matrices.one() - e11) not in center
    assert e12 * e21 != e21 * e12
    assert center.module_rank() == 1


def test_integers_mod_eight_is_local_artinian_with_residue_field_two_and_four_is_not_prime() -> None:
    r"""``ZZ/8`` has the single prime ideal ``(2)``, which is nilpotent (``2^3 = 0``),
    so it is local Artinian with residue field ``F_2``; ``F_4`` has characteristic
    ``2`` and four elements, so it properly contains its prime field ``F_2``."""
    local = Zmod(8)
    two = local(2)

    assert local in LocalRings()
    assert local in ArtinianRings()
    assert local.residue_field().cardinality() == 2
    assert local.residue_map()(two) == local.residue_field().zero()
    assert local.residue_map()(local(3)) == local.residue_field().one()
    assert two**3 == local.zero()
    assert two**2 != local.zero()
    assert not two.is_unit()
    assert local(5).is_unit()

    extension = GF(4)
    assert GF(5) in PrimeFields()
    assert extension not in PrimeFields()
    assert extension.characteristic() == 2
    assert extension.cardinality() == 4


def test_real_and_imaginary_quadratic_fields_have_signatures_two_zero_and_zero_one() -> None:
    r"""``x^2 - 2`` has two real roots, so ``QQ(sqrt 2)`` has ``(r_1, r_2) = (2, 0)``;
    ``x^2 + 1`` has none, so ``QQ(i)`` has ``(0, 1)``; ``r_1 + 2 r_2`` is the
    degree (Neukirch, I.5).  Orders are free of finite rank over ``ZZ``, hence
    countably infinite."""
    real_quadratic = QuadraticField(2, "a")
    gaussian_field = QuadraticField(-1, "i")
    order = real_quadratic.order_generated_by(real_quadratic.primitive_element())
    gaussian = gaussian_field.ring_of_integers()

    assert real_quadratic.signature() == signature_pair(2, 0)
    assert gaussian_field.signature() == signature_pair(0, 1)
    assert order.module_rank() == 2
    assert order.cardinality() == aleph0
    assert gaussian.cardinality() == aleph0


def test_owned_ring_cardinality_distinguishes_countable_and_uncountable_infinite_rings() -> None:
    assert ZZ.cardinality() == aleph0
    assert QQ.cardinality() == aleph0
    assert QQbar.cardinality() == aleph0
    assert RR.cardinality() == continuum
    assert CC.cardinality() == continuum
    assert Zp(5).cardinality() == continuum
    assert Qp(5).cardinality() == continuum


def test_finite_owned_ring_iteration_enumerates_its_points() -> None:
    ring = GF(25)
    points = tuple(ring)

    assert Set(ring) is ring
    assert len(points) == ring.cardinality() == 25
    assert all(points[i] != points[j] for i in range(25) for j in range(i))
    assert all(point.parent() is ring for point in points)


def test_owned_algebraic_real_and_complex_closures_are_countable() -> None:
    assert AA.cardinality() == aleph0
    assert QQbar.cardinality() == aleph0
