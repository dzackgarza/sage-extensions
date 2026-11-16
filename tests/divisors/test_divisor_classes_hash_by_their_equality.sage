r"""Invertible sheaf classes and Cartier section classes hash by their equality.

An isomorphism class of invertible sheaves of one scheme is a class of
``Pic(X)``, whose equality is its group's: two classes are equal when the
sheaves they retain are isomorphic, which is a decision the group makes and not
the identity of a retained sheaf, so the class hashes the group.  Two Cartier
sections of one scheme are equal exactly when the group decides they are:
``D + E = E + D``, and the negation of the zero divisor is the zero divisor
although it is presented as a negation.  Each class therefore hashes data its
own owner's equality is a relation on, and equal classes hash alike, which is
the rule of :class:`Sets`.
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


def test_a_picard_class_hashes_the_group_that_decides_its_equality() -> None:
    r"""``[L]`` is a class of ``Pic(X)``, so the class hashes the group.

    ``Pic(X).equal`` answers ``isomorphic(L, M)`` for two classes retaining
    different sheaves, so the retained sheaf is not what the equality is a
    relation on and a hash may not read it: every class of one ``Pic(X)``
    hashes alike, which is the hash of the group it is a class of.  The
    structure sheaf of the affine line carries no tensor power here, so the
    test states the coarseness on the group itself rather than on two
    distinct sheaves of one class.
    """
    _ring, _x, scheme = _affine_line()
    classes = scheme.picard_group().underlying_set()
    structure_class = classes(scheme.structure_sheaf())

    assert structure_class == classes.zero()
    assert hash(structure_class) == hash(classes.zero())
    assert hash(structure_class) == hash(classes)
    assert FiniteOrderedSets()((structure_class,)).cardinality() == 1


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
