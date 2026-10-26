r"""Archive reconciliation for formed-object constructor obligations."""

from sage_extensions.all import *






def test_archived_scale_submodule_is_the_ideal_generated_by_pairing_values() -> None:
    lattice = Lattices(ZZ)("A2")
    scale = lattice.scale_submodule()
    twisted_scale = lattice.twist(3).scale_submodule()

    assert scale.ring() is ZZ
    assert twisted_scale.ring() is ZZ
    assert scale == ZZ.ideal(1)
    assert twisted_scale == ZZ.ideal(3)
