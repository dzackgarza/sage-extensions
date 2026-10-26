r"""The orthogonal group of \(A_4\).

\(O(A_4)=W(A_4)\times\{\pm1\}\cong S_5\times C_2\) (Conway--Sloane, *SPLAG*,
ch. 4 §6.1), so its order is 240, its centre is \(\{\pm1\}\) and its derived
subgroup is \(A_5\), of order 60.
"""

from sage_extensions.all import *


def test_the_orthogonal_group_of_a4_is_s5_times_c2() -> None:
    orthogonal_group = Lattices.A4.Aut()

    assert orthogonal_group.order() == 240
    assert orthogonal_group.is_finitely_presented_as_group()
    assert not orthogonal_group.is_abelian()
    assert orthogonal_group.center().order() == 2
    assert orthogonal_group.derived_subgroup().order() == 60
