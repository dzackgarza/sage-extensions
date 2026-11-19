r"""Membership of an integral isometry in the residue action's rational group.

The pointed residue action's rational group lives in `O(L \otimes QQ)`, and its
containment test is parent-strict: an isometry of `L` is not an element of
`O(L \otimes QQ)`'s group, so asking whether it lies in that group -- or in the
action's stabilizer -- answers `False` however the isometry acts.  The crossing
is `IntegralStructureAction.rational_image`, extension of scalars on the
framing.

What the question answers once the crossing is made, at `U(2) + <2>`:

* every generator of the radical `U_I` crosses into the group and lies in the
  action's stabilizer.  The radical is inside the group by construction and
  each of its generators fixes the marked vector, so the stabilizer of the
  residue action contains `U_I`; where that action fails to be the whole
  pointed stabilizer, the failure is on the Levi side and not in the kernel;
* a generator of the rational group is outside the stabilizer, so the answers
  above are not vacuous: the rational group is bigger than the stabilizer.
"""

from sage_extensions.all import *  # noqa: F401,F403

DIVISIBILITY_TWO = [[0, 2, 0], [2, 0, 0], [0, 0, 2]]


def _pointed_action():
    r"""The lattice, its marked vector, and the residue action at that vector."""
    lattice = Lattices(ZZ)(DIVISIBILITY_TWO)
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    subobject = lattice.primitive_isotropic_subobject(vector)
    return lattice, vector, subobject, subobject.pointed_stabilizer_action()


def test_the_radical_crosses_into_the_rational_group_and_into_its_stabilizer() -> None:
    r"""`U_I` lies in the action's stabilizer, and the crossing is what makes it askable.

    Each generator of the radical is an isometry of `L` fixing the marked
    vector; crossed into the rational group it is a member of the group and of
    the stabilizer of `L`.
    """
    _lattice, vector, subobject, action = _pointed_action()
    stabilizer = action.stabilizer()
    radical = tuple(
        subobject.isotropic_reduction().unipotent_kernel().group_generators()
    )

    assert radical
    for generator in radical:
        crossed = action.rational_image(generator)
        assert generator(vector) == vector
        assert crossed in action.rational_group()
        assert crossed in stabilizer


def test_a_generator_of_the_rational_group_is_outside_the_stabilizer() -> None:
    r"""The stabilizer is a proper subgroup of the rational group.

    The group contains rational lifts that do not preserve `L`, so the
    membership asserted above is not vacuous.
    """
    _lattice, _vector, _subobject, action = _pointed_action()
    stabilizer = action.stabilizer()

    assert any(
        generator not in stabilizer
        for generator in action.rational_group().group_generators()
    )
