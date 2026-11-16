r"""Invertible sheaf classes and Cartier section classes hash by their equality.

Two isomorphism classes of invertible sheaves of one scheme are equal exactly
when they retain one sheaf, and two Cartier sections of one scheme are equal
exactly when the group decides they are: ``D + E = E + D``, and the negation of
the zero divisor is the zero divisor although it is presented as a negation.
Each class therefore hashes the data its own owner compares, and equal classes
hash alike, which is the rule of :class:`Sets`.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _affine_line():
    r"""``A^1_Q`` as the spectrum of ``QQ[x]``, with its coordinate."""
    ring = QQ['x']
    return ring, ring('x'), ring.affine_spectrum()


def test_two_classes_of_one_invertible_sheaf_are_one_point() -> None:
    r"""``Pic(A^1_Q)`` is trivial, and ``[O]`` named twice is one class.

    The structure sheaf is the tensor unit; a class retains the sheaf it was
    built from, so the two classes of ``O`` are equal, and the affine line being
    a spectrum, the Picard group is the represented set of classes.
    """
    _ring, _x, scheme = _affine_line()
    classes = scheme.picard_group().underlying_set()
    structure = scheme.structure_sheaf()
    first = classes(structure)
    second = classes(structure)

    assert first == second
    assert hash(first) == hash(second)
    assert FiniteOrderedSets()((first, second)).cardinality() == 1
    assert FiniteOrderedSets()((first,)).cardinality() == 1


def test_the_negation_of_the_zero_cartier_divisor_is_the_zero_divisor() -> None:
    r"""``-0 = 0`` in ``CDiv(P^1_Q)``, and it is one point of a finite ordered set.

    The quotient sheaf ``K^*/O^*`` is a sheaf of groups in additive notation,
    so the negation of the zero section is the zero section.  Its presentation
    is a negation node and the zero's is the zero node, so the two are equal
    classes with different defining data.
    """
    line = ProjectiveSpaces(QQ)(1)
    sections = CartierDivisorGroups().of_scheme(line).underlying_set()
    zero = sections.zero()
    negated = sections.negate(zero)

    assert negated == zero
    assert hash(negated) == hash(zero)
    assert FiniteOrderedSets()((zero, negated)).cardinality() == 1
