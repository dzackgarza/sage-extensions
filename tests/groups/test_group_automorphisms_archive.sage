r"""Literature-backed automorphism groups retained from the archive gap map.

Dummit--Foote, *Abstract Algebra*, 3rd ed., section 4.4 gives
``Aut(C_8) ~= C_2 x C_2``, ``Aut(V_4) ~= S_3``, ``Aut(Q_8) ~= S_4``, and
``Aut(S_n)=Inn(S_n)`` except at ``n=6``, where the inner subgroup has index
``2``.  These are assertions on the live owned automorphism groups rather than
on private GAP parents.
"""

from sage_extensions.all import *


def test_aut_c8_is_the_klein_four_group() -> None:
    automorphisms = Groups.C(8).Aut()
    elements = tuple(automorphisms)

    assert automorphisms.order() == 4
    identity = automorphisms.one()
    assert all(element * element == identity for element in elements)


def test_aut_v4_and_aut_q8_have_the_literature_orders() -> None:
    assert Groups.V4().Aut().order() == 6
    assert Groups.Q().Aut().order() == 24


def test_conjugation_realizes_all_automorphisms_of_s3() -> None:
    group = Groups.S(3)
    conjugation = group.conjugation_morphism()

    assert conjugation.kernel().order() == 1
    assert conjugation.image().order() == 6
    assert group.Aut().order() == 6


def test_s6_has_outer_automorphisms_of_index_two() -> None:
    group = Groups.S(6)
    conjugation = group.conjugation_morphism()

    assert conjugation.kernel().order() == 1
    assert conjugation.image().order() == 720
    assert group.Aut().order() == 1440
