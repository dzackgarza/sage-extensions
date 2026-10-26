r"""The universal property of ``S^{-1}R``: maps inverting ``S`` extend uniquely.

A ring map ``g: R -> T`` sending every element of ``S`` to a unit factors uniquely
through ``R -> S^{-1}R``, by ``a/s -> g(a) g(s)^{-1}``.  Evaluation
``Q[x] -> Q`` at ``x = 2`` sends ``x`` to the unit ``2``, so it extends to
``Q[x, 1/x] -> Q`` with ``1/x -> 1/2`` and ``(x + 1)/x^2 -> 3/4``.  Reduction
``Z -> F_5`` sends ``2`` to a unit, so it extends to ``Z[1/2] -> F_5`` with
``1/2 -> 3``; the two representatives ``1/2`` and ``2/4`` have the same image.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_evaluation_at_two_extends_to_the_laurent_localization() -> None:
    line = QQ["x"]
    x = line.algebra_generator("x")
    laurent = line.localization(x)
    evaluation = line.Mor(QQ)({"x": QQ(2)})
    extended = laurent.induced_morphism(evaluation)
    inverse_of_x = laurent(x).inverse_of_unit()

    assert extended(laurent(x)) == 2
    assert extended(inverse_of_x) == QQ(1) / QQ(2)
    assert extended(laurent(x + 1) * inverse_of_x * inverse_of_x) == QQ(3) / QQ(4)
    assert extended * laurent.localization_map() == evaluation


def test_reduction_modulo_five_extends_to_z_one_half() -> None:
    half = ZZ.localization(ZZ(2))
    residues = ZZ.ideal(ZZ(5)).quotient_ring()
    extended = half.induced_morphism(residues.quotient_map())

    assert extended(half.fraction(ZZ(1), ZZ(2))) == residues(3)
    assert extended(half.fraction(ZZ(2), ZZ(4))) == residues(3)
    assert extended(half.fraction(ZZ(7), ZZ(8))) == residues(4)
    assert extended(half(10)) == residues.zero()
