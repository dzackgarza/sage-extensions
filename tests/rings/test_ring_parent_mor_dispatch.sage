r"""The integers are the initial ring."""

from sage_extensions.all import *  # noqa: F401,F403


def test_there_is_exactly_one_ring_morphism_out_of_the_integers() -> None:
    r"""``ZZ`` is initial in unital rings: ``n |-> n * 1`` is the only ring
    morphism ``ZZ -> R``.  There is none ``QQ -> F_5``, since ``5`` is invertible
    in ``QQ`` and ``0`` in ``F_5`` (Lang, *Algebra*, II §1)."""
    to_rationals = ZZ.Mor(QQ)
    to_five = ZZ.Mor(GF(5))

    assert to_rationals.cardinality() == 1
    assert to_five.cardinality() == 1
    assert next(iter(to_rationals))(ZZ(7)) == QQ(7)
    assert next(iter(to_five))(ZZ(7)) == GF(5)(2)
    assert QQ.Mor(GF(5)).cardinality() == 0
