r"""The Coble discriminant form's orbits are exactly its quadratic-value fibres.

``B = <1> + U + E8(-1)`` has signature ``(2, 9)``; ``T = B.twist(2)`` is the
Coble discriminant form's source and ``D = T.discriminant_quadratic_form()`` has
order ``2^11 = 2048``.  Its quadratic form takes four values in
``QQ/2ZZ`` --- ``0``, ``1/2``, ``1`` and ``3/2`` --- and the ``q = 0`` fibre is
the isotropic set, of which the research consumer independently counts 528
elements.

``O(D)`` acts on ``D`` and ``D.orbits()`` returns six orbits, of sizes
``527, 527, 496, 496, 1, 1``.  The sizes alone do not say which orbit is
isotropic: the two 527s are *not* both isotropic, because the ``q = 0`` fibre
has 528 elements in total and only one orbit can be its nonzero part.  What
separates them is the quadratic value: the ``q = 0`` fibre is the singleton
``{0}`` together with the one 527 orbit, and the other 527 orbit belongs to the
``q = 1/2`` fibre, which has 527 + 1 = 528 elements as well.  So the value
partition of ``D`` is ``528, 528, 496, 496`` over ``0, 1/2, 1, 3/2``.

That is what this file checks: every orbit is constant on ``q``, the orbits
partition ``D``, each value fibre is the union of the orbits carrying its value,
and the ``q = 0`` fibre is exactly ``D.isotropic_elements()``.  The run costs
about a minute and a half, almost all of it the one-time Oscar initialisation
behind ``O(D)``'s generators.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_coble_discriminant_orbits_are_its_quadratic_value_fibres() -> None:
    r"""``O(D)``'s six orbits split ``D`` by ``q``, not by size: the ``q = 0``
    fibre is ``{0}`` plus one 527-orbit, and the second 527-orbit carries
    ``q = 1/2``."""
    base = Lattices(ZZ)([[1]]) + Lattices(ZZ)("U") + Lattices(ZZ)("E8").twist(-1)
    form = base.twist(2).discriminant_quadratic_form()
    zero = form.zero()
    isotropic = form.isotropic_elements()
    elements = tuple(form.elements())

    assert form.cardinality() == 2048
    assert isotropic.cardinality() == 528
    assert form.q(zero) == form.value_module().zero()

    orbits = tuple(form.orbits())
    assert sorted(len(orbit) for orbit in orbits) == [1, 1, 496, 496, 527, 527]

    # Every orbit is a single quadratic-value class.
    orbit_sizes_by_value = {}
    orbit_members = []
    for orbit in orbits:
        points = tuple(orbit)
        values = [form.q(point) for point in points]
        value = values[0]
        assert all(one == value for one in values), (
            f"the orbit of size {len(points)} mixes quadratic values"
        )
        orbit_sizes_by_value.setdefault(value, []).append(len(points))
        orbit_members.append((value, points))

    # The orbits partition the module: no point repeats and every point occurs.
    seen = {}
    for value, points in orbit_members:
        for point in points:
            assert point not in seen, f"{point} lies in two orbits"
            seen[point] = value
    assert len(seen) == 2048
    assert all(point in seen for point in elements)

    # Each value fibre, read off the form itself, is the union of the orbits
    # carrying that value.
    fibre_sizes = {}
    for point in elements:
        value = form.q(point)
        fibre_sizes[value] = fibre_sizes.get(value, 0) + 1
    assert sum(fibre_sizes.values()) == 2048
    for value, sizes in orbit_sizes_by_value.items():
        assert sum(sizes) == fibre_sizes[value], (
            f"the orbits of quadratic value {value} have {sum(sizes)} points, "
            f"but the fibre has {fibre_sizes[value]}"
        )

    # The isotropic set is exactly the q = 0 fibre, checked point by point, and
    # the singleton {0} is one of its orbits, so only one 527-orbit is
    # isotropic.
    zero_value = form.q(zero)
    assert fibre_sizes[zero_value] == 528
    for point in elements:
        assert (point in isotropic) == (form.q(point) == zero_value), (
            f"the isotropic set and the q = {zero_value} fibre differ at {point}"
        )
    assert sorted(len(points) for value, points in orbit_members if value == zero_value) == [1, 527]
    assert sorted(len(points) for value, points in orbit_members if value != zero_value) == [1, 496, 496, 527]

    # Two fibres have 496 elements and two have 528: the second 527-orbit is the
    # nonzero part of a 528-element fibre that is not isotropic.
    assert sorted(fibre_sizes.values()) == [496, 496, 528, 528]
