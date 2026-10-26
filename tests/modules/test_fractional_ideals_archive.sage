r"""Archive reconciliation for ideals and fractional ideals as modules.

The archived surface treated ``as_submodule()`` as a conversion.  The live
owner makes the stronger statement: the ideal is itself the module and carries
its canonical inclusion, so no second module object is manufactured.
"""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/modules/fractional_ideals.sage",
    "live_owner": "sage_extensions/categories/modules/fractional_ideals.py",
    "disposition": "reconciled-live-owner",
}


def test_fractional_ideal_keeps_module_generators_membership_and_inverse() -> None:
    ideal = ZZ.fractional_ideal(QQ(2) / 3)

    assert ideal in FractionalIdeals(ZZ)
    assert ideal not in CommutativeIdeals(ZZ)
    assert ideal.principal_generator() == QQ(2) / 3
    assert QQ(4) / 3 in ideal
    assert QQ(1) / 3 not in ideal

    inverse = ideal.inverse()
    assert inverse.principal_generator() == QQ(3) / 2
    assert (ideal * inverse).principal_generator() == 1


def test_the_generator_family_is_the_module_family_not_a_parallel_copy() -> None:
    ideal = ZZ.ideal(12, 18)
    assert ideal.number_of_module_generators() > 0
    assert all(generator.parent() is ideal for generator in ideal.module_generators())
    assert ideal.principal_generator() == 6
