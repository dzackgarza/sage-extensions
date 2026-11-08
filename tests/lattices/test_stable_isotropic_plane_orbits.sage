r"""Stable-group isotropic plane orbits on rank-five ``6JRS``.

``6JRS`` (alias ``U + U + <-2>``) is the rank-five shadow, not Scattone's
rank-21 $\Lambda_2$.  Its orbit rows are still being certified by
lattice-database#13, so no count is used as an oracle here.  The public call is tested
for its mathematical output: primitive totally isotropic rank-two sublattices, plus the
standard $U$ witness.

The failure pinned below: the discriminant stabilizer path passes a raw GAP ``GapElement``
into ``LatticeIsometryMor`` instead of converting it through the owned row-action
conversion.  Before repair, evaluation on this specimen raises
``TypeError: cannot define a linear map ... from [ f1 ] -> [ f1 ]``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _planes_are_primitive_isotropic_rank_two_sublattices(planes, lattice) -> None:
    for plane in planes:
        assert plane.module_rank() == cardinal(2)
        assert plane.is_primitive() is True
        for left_label in plane.module_generating_set():
            for right_label in plane.module_generating_set():
                assert lattice.b(
                    plane.inclusion()(plane.module_generator(left_label)),
                    plane.inclusion()(plane.module_generator(right_label)),
                ) == ZZ(0)


def test_the_standard_u_plane_is_primitive_and_totally_isotropic() -> None:
    r"""The span of the two isotropic generators, one from each $U$, is the witness.

    In $U \oplus U$ the two isotropic lines from different planes pair to zero, so
    their span is totally isotropic; the two generators of one $U$ pair to $1$ and do
    not.  The witness is therefore the cross-plane span, primitive of rank two.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    labels = tuple(lattice.module_generating_set())
    plane = lattice.primitive_isotropic_subobject(
        lattice.module_generator(labels[0]), lattice.module_generator(labels[2])
    )
    assert plane.module_rank() == cardinal(2)
    assert plane.is_primitive() is True
    for left_label in plane.module_generating_set():
        for right_label in plane.module_generating_set():
            assert lattice.b(
                plane.inclusion()(plane.module_generator(left_label)),
                plane.inclusion()(plane.module_generator(right_label)),
            ) == ZZ(0)


def test_the_stable_plane_orbit_of_l_1() -> None:
    r"""$6JRS$: stable-group representatives are primitive rank-two isotropic planes."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    stable = lattice.stable_orthogonal_group()
    planes = stable.isotropic_orbit_representatives(2)

    assert planes.cardinality() != cardinal(0)
    _planes_are_primitive_isotropic_rank_two_sublattices(planes, lattice)


def test_stable_plus_has_the_same_l_1_plane_orbit() -> None:
    r"""$6JRS$: $\widetilde{O}^+$ plane fibres are primitive rank-two isotropic too.

    Spinor and discriminant characters are joint here, so the operation retains the
    full joint image instead of deducing coverage from a sign alone.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    stable_plus = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    planes = stable_plus.isotropic_orbit_representatives(2)

    assert planes.cardinality() != cardinal(0)
    _planes_are_primitive_isotropic_rank_two_sublattices(planes, lattice)
