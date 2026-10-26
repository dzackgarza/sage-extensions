r"""Conway--Sloane's split indefinite ternary genus from the archive suite.

SPLAG, chapter 15 section 11, gives two determinant ``-128`` ternary forms in
one genus that splits into two spinor genera/classes.  The live owned genus
object can carry the common genus and class number even where the pairwise
indefinite isometry decision remains ``Unknown``.
"""

from sage_extensions.all import *


def test_splag_ternary_forms_share_one_genus_of_class_number_two() -> None:
    first = Lattices(ZZ)([[-1, 1, 0], [1, 63, 0], [0, 0, 2]])
    second = Lattices(ZZ)([[-9, 1, 0], [1, 7, 0], [0, 0, 2]])

    assert first.gram_matrix().determinant() == -128
    assert second.gram_matrix().determinant() == -128
    assert first.signature_pair() == second.signature_pair()
    assert first.genus() == second.genus()
    assert first.genus().class_number() == 2
