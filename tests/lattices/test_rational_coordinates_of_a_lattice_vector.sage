r"""The rational coordinates of a vector in a lattice, and the integrality they decide.

`Modules.ParentMethods.rational_coordinates` is the owner of the lattice's ambient
coordinates: an element of `L tensor QQ` goes to its coordinates in the selected framing
of `L`, as a Sage column matrix over `QQ`.  The coefficients are the lift through the
degree-zero augmentation, so they are unique; the map is what decides whether a rational
vector lies in the integral lattice, which is the condition the Eichler transvection
formula turns into an isometry (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
(4)--(5)).

The specimen is `U + <2>` in its named basis `e_0, e_1, e_2`, whose Gram matrix is known
entry by entry, so the coordinates can be read off by hand: `e_0` is the first basis
vector, and `(1/2) e_0 + e_2` is not a vector of the lattice -- its `e_0` coefficient is a
half, and `(1/2)e_0` is in the dual lattice `L^vee` outside `L`.

Every expected value below is built inside the coordinate matrix's own field, because the
matrix is a Sage matrix over `QQ` while the session's `ZZ` is a different parent: a
session integer is not equal to a Sage rational, and the comparison has to be made where
the coordinates live.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""``U + <2>``, and its base change to ``QQ``: the lattice and its rational model."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[2]])
    rational = lattice.base_change(lattice.base_ring().fraction_field_map())
    labels = tuple(rational.module_generating_set())
    return lattice, rational, labels


def _column(space, field, entries):
    r"""The one-column matrix of ``entries`` in the coordinate matrix's own space."""
    return space(entries)


def test_a_vector_of_the_lattice_has_integer_coordinates() -> None:
    r"""Each basis vector of `U + <2>` has a single one in its own coordinate, and no other."""
    _lattice, rational, labels = _specimen()
    for position, label in enumerate(labels):
        coordinates = rational.rational_coordinates(rational.module_generator(label))
        field = coordinates.parent().base_ring()
        one, zero = field.one(), field.zero()
        expected = tuple(
            one if other == position else zero for other in range(coordinates.nrows())
        )
        assert coordinates == _column(coordinates.parent(), field, expected)


def test_a_dual_vector_outside_the_lattice_has_a_noninteger_coordinate() -> None:
    r"""`(1/2) e_0 + e_2` lies in `L^vee` and not in `L`, and the coordinates say exactly that."""
    _lattice, rational, labels = _specimen()
    half = rational.scalar_multiple(ZZ(1) / ZZ(2), rational.module_generator(labels[0]))
    vector = half + rational.module_generator(labels[2])

    coordinates = rational.rational_coordinates(vector)
    field = coordinates.parent().base_ring()
    one, zero = field.one(), field.zero()
    two = one + one
    one_half = one / two

    assert coordinates == _column(coordinates.parent(), field, (one_half, zero, one))
    # The coordinate is one half: it is not zero, and twice it is one.  That is the whole
    # content of the reading -- a rational vector is a lattice vector exactly when every
    # coordinate is an integer -- and doubling the vector clears the denominators.
    assert coordinates[0, 0] != zero
    assert coordinates[0, 0] * two == one
    doubled = rational.rational_coordinates(rational.scalar_multiple(ZZ(2), vector))
    doubled_field = doubled.parent().base_ring()
    assert doubled == _column(
        doubled.parent(), doubled_field, (doubled_field.one(), doubled_field.zero(), doubled_field.one() + doubled_field.one())
    )
