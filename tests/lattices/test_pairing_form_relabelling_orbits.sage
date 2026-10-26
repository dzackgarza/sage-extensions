r"""A3 pairing forms have one least representative under reindexing.

The negative A3 Cartan matrix has diagonal -2, adjacent entries 1 and
nonadjacent entries 0. Its lexicographically least reindexing puts the
two nonadjacent vertices first, giving the displayed matrix. This is
the minimum of a finite orbit in a total order, independent of its seed.
The construction uses the symmetric-group set of forms and the existing
finite-orbit and ordered-minimum constructions.
"""

from sage_extensions.all import *


def test_relabelling_the_a3_root_family_keeps_its_canonical_pairing_form():
    lattice = Lattices(ZZ)("A3")
    indices = Sets.Δ[2]
    free = ZZ.free_module(indices)
    roots = tuple(lattice.module_generators())
    first = Modules(ZZ).Mor(free, lattice)({label: roots[int(label)] for label in indices})
    second = Modules(ZZ).Mor(free, lattice)({label: roots[(1, 0, 2)[int(label)]] for label in indices})
    gram = lattice.gram_tensor().pullback(first)
    relabelled = lattice.gram_tensor().pullback(second)
    symmetric = SymmetricGroups()(indices)

    def reindex(permutation, form):
        inverse = ~permutation
        linear = free.Aut()({label: free.module_generator(inverse(label)) for label in indices})
        return form.pullback(linear)

    action = GObjects(symmetric, Sets()).on_set(gram.parent(), reindex)
    orbits = action.orbits()

    def entries(form):
        return tuple(form[int(i), int(j)] for i in indices for j in indices)

    def least_form(orbit):
        points = FiniteGSets(symmetric).from_finite_orbits((orbit.representative(),), action.act).point_set()
        return PartiallyOrderedSets()(points, lambda left, right: entries(left) <= entries(right)).minimum()

    section = Sets().Mor(orbits, gram.parent())(least_form)
    first_orbit, second_orbit = orbits.orbit_of(gram), orbits.orbit_of(relabelled)

    assert entries(gram) != entries(relabelled)
    assert entries(section(first_orbit)) == (-2, 0, 1, 0, -2, 1, 1, 1, -2)
    assert section(first_orbit) == section(second_orbit)
    assert orbits.projection()(section(first_orbit)) == first_orbit
