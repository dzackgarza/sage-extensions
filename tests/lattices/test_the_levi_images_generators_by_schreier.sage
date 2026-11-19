r"""Generators of `M_I` by Schreier over its finite coset graph.

Membership in `M_I` is decidable: :meth:`...IsotropicReductions.ParentMethods.pointwise_levi_lift`
answers with an integral lift or with ``None``.  `M_I` contains the principal
congruence subgroup `Gamma_{K_I}(d)`, so `O(K_I)/M_I` is finite, and breadth
first from the identity class over the certified generators of `O(K_I)` with
that predicate as the class test therefore terminates.  Over the resulting
transversal the words `w_{P'}^{-1} t w_P` lie in `M_I` and generate it: each
returns from the class of `t w_P` to its representative, and a word that fixes
the identity class can be rewritten through the transversal at every step.

With the reduction that `P` is `<g_s> . U_I` exactly when the lifted set
generates `M_I`, this closes the pointed family: the lifts returned here
together with the radical's own generators generate `P`.

The specimens are the two divisibility-two lines, whose `O(K_I) = {+-1}` is
the whole image, so the family returned is that one generator.  The rank-five
proper-image lattice -- `M_I` of index two in an infinite `O(K_I)`, five
Schreier words -- is measured in the record and not asserted here: one call
takes about 28 s and the per-call ceiling is 20 s.
"""

from sage_extensions.all import *  # noqa: F401,F403

DIVISIBILITY_TWO = [[0, 2, 0], [2, 0, 0], [0, 0, 2]]
ODD_DIVISIBILITY_TWO = [[0, 2, 0], [2, 0, 0], [0, 0, 3]]


def _assert_the_image_has_lifted_generators(gram) -> None:
    r"""Each returned element is an integral isometry fixing the marked vector."""
    lattice = Lattices(ZZ)(gram)
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    reduction = lattice.primitive_isotropic_subobject(vector).isotropic_reduction()

    assert vector.q() == ZZ(0)
    assert vector.is_primitive() is True

    family = reduction.pointwise_levi_image_generators()

    assert family
    for isometry in family:
        assert isometry(vector) == vector
        assert all(
            lattice.b(isometry(left), isometry(right)) == lattice.b(left, right)
            for left in lattice.module_generators()
            for right in lattice.module_generators()
        )


def test_the_divisibility_two_line_has_its_image_generators() -> None:
    r"""`U(2) + <2>`: `O(K_I) = {+-1}` lifts, so the image is the whole quotient."""
    _assert_the_image_has_lifted_generators(DIVISIBILITY_TWO)


def test_the_odd_divisibility_two_line_has_its_image_generators() -> None:
    r"""`U(2) + <3>`: the same on an odd lattice."""
    _assert_the_image_has_lifted_generators(ODD_DIVISIBILITY_TWO)

