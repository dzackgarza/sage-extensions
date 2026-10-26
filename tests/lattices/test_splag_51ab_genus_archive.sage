r"""Archive reconciliation for Conway--Sloane forms (51a) and (51b).

Conway--Sloane, *Sphere Packings, Lattices and Groups*, 3rd ed., chapter 15,
section 11, places these determinant ``-128`` indefinite ternary forms in one
genus which splits into two spinor genera.  In the cited ternary case each
spinor genus is one class, so the genus has class number two.  The live
isometry decision is deliberately not used as a Boolean oracle here: its
unresolved indefinite regime remains a separate question.
"""

from sage_extensions.all import *


def test_splag_51a_and_51b_share_one_two_class_genus() -> None:
    form_51a = Lattices(ZZ)(
        [[ZZ(-1), ZZ(1), ZZ(0)], [ZZ(1), ZZ(63), ZZ(0)], [ZZ(0), ZZ(0), ZZ(2)]]
    )
    form_51b = Lattices(ZZ)(
        [[ZZ(-9), ZZ(1), ZZ(0)], [ZZ(1), ZZ(7), ZZ(0)], [ZZ(0), ZZ(0), ZZ(2)]]
    )

    assert form_51a.determinant() == ZZ(-128)
    assert form_51b.determinant() == ZZ(-128)
    assert form_51a.genus() == form_51b.genus()
    assert form_51a.genus().class_number() == ZZ(2)
