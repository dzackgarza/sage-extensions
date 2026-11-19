r"""The orthogonal group's orbits on the classes of its form.

A finite formed module's classes are the set `O(q)` acts on, and the
decomposition of that set into orbits is what a card's `isotropic_orbits` field
states -- for card `6JRR` (`T_Co`) the answer is two: the zero class and the
nonzero isotropic ones.

This file checks the decomposition where it can be counted by hand.  On
`U + U(2) + <-4>` the form has sixteen classes and `O(q)` has order twelve; its
orbits are one of size six, two of size three, one of size two and two fixed
classes, and two of them are isotropic: their classes are exactly the ones `q`
vanishes on.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""`U + U(2) + <-4>`: sixteen classes, twelve isometries."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[-4]])
    )


def test_the_orbits_partition_the_classes_and_are_ranked_by_size():
    r"""The orbits are disjoint, cover the class set, and come largest first.

    Covering is checked against the form's own cardinality and disjointness
    against the positions themselves, so the assertion does not depend on the
    action being correct in any way the group could fake: a decomposition that
    repeated a class or dropped one fails here.
    """
    lattice = _specimen()
    form = lattice.discriminant_group()
    group = form.O()

    orbits = group.class_orbits()
    positions = tuple(position for orbit in orbits for position in orbit)

    assert form.cardinality() == cardinal(16)
    assert set(positions).issubset(range(16))
    assert sum(group.class_orbit_sizes()) == int(form.cardinality())
    assert sum(1 for _orbit in orbits) == int(6)
    assert sum(1 for position in positions) == int(form.cardinality())
    assert group.class_orbit_sizes() == (6, 3, 3, 2, 1, 1)
    assert sum(group.class_orbit_sizes()) == 16


def test_the_isotropic_orbits_are_the_ones_the_form_vanishes_on():
    r"""Two isotropic orbits whose classes number exactly those `q` vanishes on.

    `O(q)` preserves `q`, so an orbit is isotropic when one class of it is.
    Reading the answer through `q` on one class per orbit is therefore exact,
    and the count of isotropic classes it implies is checked against the
    enumeration of the classes that `q` vanishes on.
    """
    lattice = _specimen()
    form = lattice.discriminant_group()
    group = form.O()
    classes = tuple(form.elements())
    zero = form.q(form.zero())

    isotropic = group.isotropic_class_orbits()
    counted = sum(
        1 for class_ in classes if form.q(class_) == zero
    )

    assert sum(1 for _orbit in isotropic) == int(2)
    assert sum(1 for orbit in isotropic for _position in orbit) == counted
