r"""Stabilizer subgroups of \(O(L)\).

A stabilizer is cut out of \(O(L)\) by its defining condition, so it is an
object for indefinite \(L\) as well, where \(O(L)\) is infinite and cannot be
enumerated.  The specimens below separate the three conditions from one
another: fixing a vector, fixing a sublattice pointwise, and carrying a
sublattice onto itself.
"""

from sage_extensions.all import *


def test_the_setwise_stabilizer_of_an_isotropic_line_holds_maps_the_pointwise_one_does_not() -> None:
    r"""\(-\mathrm{id}\) carries \(\mathbb Ze\) onto itself without fixing \(e\).

    That separates \(\operatorname{Stab}(I)\) from the pointwise stabilizer,
    so a test that confused the two would fail here.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    isotropic = lattice.basis_vector(0)
    line = isotropic.sublattice()
    embedding = line.inclusion()
    orthogonal_group = lattice.O()

    negation = orthogonal_group(lambda label: -lattice.module_generator(label))

    assert negation in orthogonal_group.setwise_stabilizer(embedding)
    assert negation not in orthogonal_group.pointwise_stabilizer(embedding)
    assert negation not in orthogonal_group.stabilizer(isotropic)
    setwise = orthogonal_group.setwise_stabilizer(embedding)
    pointwise = orthogonal_group.pointwise_stabilizer(embedding)
    assert setwise.stabilized_object() is embedding
    assert pointwise.stabilized_object() is embedding
    assert setwise.stabilizer_action() is orthogonal_group.natural_module_action_functor()
    assert pointwise.stabilizer_action() is orthogonal_group.natural_module_action_functor()
    restricted = setwise.restricted_stabilizer_action()
    assert restricted.domain() is setwise.classifying_category()
    assert restricted.codomain() is Modules(lattice.base_ring())
    point = restricted.domain().an_object()
    arrow = restricted.domain().Mor(point, point)(negation)
    assert restricted(arrow)(isotropic) == -isotropic


def test_a_transvection_moving_a_line_leaves_its_setwise_stabilizer() -> None:
    r"""\(t(e,a)\) fixes \(\mathbb Ze\) but moves \(\mathbb Zf\) off itself."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    isotropic, partner, root, _second_root = lattice.module_generators()
    transvection = lattice.eichler_transvection(isotropic, root)
    orthogonal_group = lattice.O()

    assert transvection in orthogonal_group.setwise_stabilizer(
        isotropic.sublattice().inclusion()
    )
    assert transvection not in orthogonal_group.setwise_stabilizer(
        partner.sublattice().inclusion()
    )


def test_the_stabilizer_of_a_root_holds_exactly_the_expected_involution() -> None:
    r"""In \(A_2\), \(-s_r\) fixes \(r\) while neither \(-\mathrm{id}\) nor \(s_r\) does.

    \(s_r(r)=-r\) and \(-\mathrm{id}(r)=-r\), so their product is the
    nonidentity element of \(\operatorname{Stab}_{O(A_2)}(r)\); a predicate
    that tested the line \(\mathbb Zr\) instead of the vector \(r\) would
    admit all three.
    """
    root_lattice = Lattices(ZZ)("A2")
    root = root_lattice.basis_vector(0)
    orthogonal_group = root_lattice.O()
    stabilizer = orthogonal_group.stabilizer(root)

    reflection = root_lattice.reflection(root)
    negation = orthogonal_group(
        lambda label: -root_lattice.module_generator(label)
    )

    assert reflection not in stabilizer
    assert negation not in stabilizer
    assert negation * reflection in stabilizer
    assert (negation * reflection)(root) == root
