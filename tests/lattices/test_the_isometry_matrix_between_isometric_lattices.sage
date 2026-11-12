r"""An isometry between two isometric integral lattices, returned as a matrix (sage-extensions#298).

`is_isometric_to` answers a yes/no question and keeps no witness.  Stage 2 of the Coble programme
needs the witness: the research record for the `0`-cusp chamber of the Coble lattice produces the
nine walls of `I_{1,8}` in the basis whose Gram matrix is `diag(1, -1, ..., -1)`, and the index of
the induced subgroup `rho_v(Stab_{Gamma_Co}(v)) <= O(v^perp/<v>)` needs those walls as isometries of
`T_Co` --- a matrix identifying `I_{1,8}` with `v^perp/<v>` in the coordinates of `T_Co`.

The call is `isometry_matrix_to`: for two integral lattices `L` and `L'` it returns a matrix `M` with

    M^T G_L M = G_{L'},

whose columns are the coordinates, in `L`'s selected basis, of the images of `L'`'s selected
generators --- so a vector of `L'` with coordinate column `x` has image `M x` in `L`, and the Gram
equation is exactly the statement that `x |-> M x` preserves the form.  It raises `ValueError` when
there is no isometry.  `is_isometric_to` reads the same decision (`_isometry_absent`), so the library
decides isometry in one place: the emptiness of the lattice isometry Mor, whose regimes are Sage's
PARI `qfisom` for a definite pair (The PARI Group, *PARI/GP* reference card, "Arithmetic functions on
lattices"), the genus and spinor-genus classification for an indefinite one (J. H. Conway and N. J.
A. Sloane, *Sphere packings, lattices and groups*, Ch. 15, Thms 14--15), and the port's Eichler
recursion for the indefinite witness.

The two pairs tested are the ones the issue names, and each is a pair whose Gram matrices differ, so
the matrix is not the identity and the equation is a real check:

* `U + <-1>` against `I_{1,2}`.  Both are odd unimodular of rank 3 and signature `(1, 2)`, and `U`
  is not diagonal, so the transporter has no reason to be trivial.
* `U + U + <-1>^7` against `U + I_{1,8}`.  Both are odd unimodular of rank 11 and signature
  `(2, 9)`; the second pair is the indefinite one, and its witness is the port's construction.

An odd unimodular lattice is determined by its rank and signature (Conway--Sloane, Ch. 15, §1), which
is why these pairs are isometric; the call must still *exhibit* the transporter, and the test
transports the generators to check that it does.
"""

import pytest

from sage_extensions.all import *


def _transported(target, matrix, source_labels, vector):
    r"""Return the vector of ``target`` whose coordinates are ``matrix`` times ``vector``'s.

    ``matrix`` is the return of `isometry_matrix_to`, so this is the image of a vector of the other
    lattice under the isometry it returns: the operation stage 2 needs, and the one the Gram equation
    promises preserves the form.
    """
    ring = target.base_ring()
    labels = tuple(target.module_generating_set())
    coordinates = vector.to_vector()
    coefficients = {}
    for row, label in enumerate(labels):
        total = ring.zero()
        for column, source_label in enumerate(source_labels):
            value = coordinates(source_label)
            if value:
                total += matrix[row, column] * value
        if total:
            coefficients[label] = total
    return target.linear_combination(coefficients)


def test_the_odd_unimodular_rank_three_pair_has_its_isometry_matrix() -> None:
    r"""`U + <-1>` and `I_{1,2}` are isometric, and the returned matrix satisfies the form equation.

    `U` is not diagonal and `I_{1,2}` is, so the two Gram matrices differ and the transporter is not
    the identity: the equation `M^T G_L M = G_{L'}` and the transported generators' squares are the
    evidence that the call returns an isometry rather than a change of coordinates that happens to
    match two determinants.
    """
    left = NamedLattices.U + Lattices(ZZ)([[-1]])
    right = Lattices.IPQ(1, 2)
    assert left.gram_matrix() != right.gram_matrix()

    matrix = left.isometry_matrix_to(right)
    assert matrix.transpose() * left.gram_matrix() * matrix == right.gram_matrix()
    assert matrix.determinant() * matrix.determinant() == ZZ(1)

    source_labels = tuple(right.module_generating_set())
    images = [
        _transported(left, matrix, source_labels, generator)
        for generator in right.module_generators()
    ]
    assert [left.q(image) for image in images] == [right.q(generator) for generator in right.module_generators()]
    assert left.gram_matrix(images) == right.gram_matrix()

    assert left.is_isometric_to(right) is True
    assert right.is_isometric_to(left) is True
    converse = right.isometry_matrix_to(left)
    assert converse.transpose() * right.gram_matrix() * converse == left.gram_matrix()


def test_the_indefinite_rank_eleven_pair_has_its_isometry_matrix() -> None:
    r"""`U + U + <-1>^7` and `U + I_{1,8}` are isometric, and their transporter is exhibited.

    This is the pair whose signature `(2, 9)` has positive index two, so neither Sage's `qfisom` nor
    the Lorentzian case of the port reaches it: the witness is the port's Eichler recursion
    (`sage_indefinite_port.indefinite.marked_lattices.isometry` -> `EichlerRecursion.isometry`), the
    indefinite construction the library already uses.  The Gram equation and the transported
    generators are checked on that witness, and the decision itself is the Mor's genus and
    spinor-genus route.
    """
    left = NamedLattices.U + NamedLattices.U + Lattices.IPQ(0, 7)
    right = NamedLattices.U + Lattices.IPQ(1, 8)
    assert left.gram_matrix() != right.gram_matrix()
    assert left.signature_pair() == right.signature_pair()

    matrix = left.isometry_matrix_to(right)
    assert matrix.transpose() * left.gram_matrix() * matrix == right.gram_matrix()
    assert matrix.determinant() * matrix.determinant() == ZZ(1)

    source_labels = tuple(right.module_generating_set())
    images = [
        _transported(left, matrix, source_labels, generator)
        for generator in right.module_generators()
    ]
    assert left.gram_matrix(images) == right.gram_matrix()

    assert left.is_isometric_to(right) is True


def test_a_pair_that_is_not_isometric_refuses_and_the_decision_is_the_same_question() -> None:
    r"""`<1>` and `<-1>` are not isometric: the matrix call raises and the decision answers `False`.

    The two lattices have the same rank and different signatures, so coarse invariants already
    separate them; what is tested is that the refusal is `ValueError` and that `is_isometric_to`
    reads the same question rather than a second one, so the two spellings cannot disagree.
    """
    left = Lattices(ZZ)([[1]])
    right = Lattices(ZZ)([[-1]])
    assert left.is_isometric_to(right) is False
    assert right.is_isometric_to(left) is False
    with pytest.raises(ValueError):
        left.isometry_matrix_to(right)
    with pytest.raises(ValueError):
        right.isometry_matrix_to(left)
