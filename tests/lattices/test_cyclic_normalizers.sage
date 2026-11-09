r"""Normalizers of finite cyclic subgroups, checked by hand.

Z^3 with the three-cycle f: O(Z^3) is the signed permutations. A signed permutation
normalizing <f> has a uniform sign, or the conjugate of f has signs. So the normalizer is
+-S_3, of order 12, with centralizer +-<f> of order 6.

U + A2 with f a rotation of A2: the reflection in a root inverts f, so (Z/3)^x is realized.
Mod 2, O(A2) acts through S_3 on A2/2A2 with kernel +-1, and every element inverting f is a
reflection up to sign, which is a transposition in S_3. So if Gamma is the preimage of the
three-cycles' subgroup, Gamma contains f and no inverter: the realized image shrinks.

Z[i]^2 with h = [[5, 2 + i], [2 - i, 6]] and f = i: the trace form has O(L) of order 4,
containing f of order 4, so O(L) = <f> is abelian and no element inverts f. Chirality.

H = even sign changes on Z^3: H is normal in O(Z^3) of order 48, the centralizer is the 8
diagonal signs, and S_3 = Aut(C_2^2) is realized. On diag(1, 1, 2) the third coordinate
is fixed by isometries up to sign, so O has order 16, the image has order 2 only.
"""

from sage_extensions.all import *
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.finite_rings.finite_field_constructor import GF as SageGF
from sage_extensions.categories.lattice_centralizers import finite_preimage_generators, finite_subgroup_normalizer


def _closure(generators, one):
    known = [one]
    frontier = [one]
    while frontier:
        current = frontier.pop()
        for g in generators:
            image = current * g
            if all(image != k for k in known):
                known.append(image)
                frontier.append(image)
    return known


def _mod_two(g):
    lattice = g.domain()
    columns = [list(g(v)) for v in lattice.module_generators()]
    return sage_matrix(SageGF(int(2)), [[int(c) % int(2) for c in column] for column in columns])


def test_three_cycle_on_z3_has_normalizer_of_order_twelve():
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    labels = lattice.module_generating_set()
    first, second, third = lattice.module_generators()
    f = lattice.O()({labels[0]: second, labels[1]: third, labels[2]: first})
    decomposition = f.cyclotomic_decomposition(3)
    generators, realized = decomposition.cyclic_normalizer()
    assert sorted(int(a) for a in realized) == [int(1), int(2)]
    assert realized[int(2)] * f * ~realized[int(2)] == f * f
    assert len(_closure(generators, lattice.O().one())) == int(12)


def test_order_two_subgroup_has_normalizer_equal_to_centralizer():
    lattice = Lattices(ZZ)("U")
    labels = lattice.module_generating_set()
    first, second = lattice.module_generators()
    swap = lattice.O()({labels[0]: second, labels[1]: first})
    _generators, realized = swap.cyclotomic_decomposition(2).cyclic_normalizer()
    assert [int(a) for a in realized] == [int(1)]


def test_trivial_subgroup_has_normalizer_the_whole_group():
    lattice = Lattices(ZZ)("U")
    one = lattice.O().one()
    generators, realized = one.cyclotomic_decomposition(1).cyclic_normalizer()
    assert [int(a) for a in realized] == [int(1)]
    assert len(_closure(generators, one)) == int(4)


def test_rotation_on_a2_is_inverted_and_restricted_gamma_loses_inversion():
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    vectors = tuple(lattice.module_generators())
    reflection = lattice.reflection(vectors[2])
    f = reflection * lattice.reflection(vectors[3])
    assert f * f * f == lattice.O().one() and f != lattice.O().one()
    assert reflection * f * ~reflection == f * f
    assert reflection * f != f * reflection
    decomposition = f.cyclotomic_decomposition(3)
    generators, realized = decomposition.cyclic_normalizer()
    assert sorted(int(a) for a in realized) == [int(1), int(2)]
    assert realized[int(2)] * f * ~realized[int(2)] == f * f
    rotations = [_mod_two(lattice.O().one()), _mod_two(f), _mod_two(f * f)]
    restricted, index = finite_preimage_generators(generators, _mod_two, lambda m: m in rotations)
    assert restricted and int(index) > int(1)
    assert all(_mod_two(g) in rotations for g in restricted)
    assert not any(g * f == f * f * g for g in restricted)


def test_chiral_hermitian_lattice_has_no_inverter():
    lattice = Lattices(ZZ)([[10, 0, 4, 2], [0, 10, -2, 4], [4, -2, 12, 0], [2, 4, 0, 12]])
    labels = lattice.module_generating_set()
    e = tuple(lattice.module_generators())
    f = lattice.O()({labels[0]: e[1], labels[1]: -e[0], labels[2]: e[3], labels[3]: -e[2]})
    assert lattice.O().cardinality() == 4
    decomposition = f.cyclotomic_decomposition(4)
    assert decomposition.twisted_transporter(3) is None
    assert decomposition.twisted_transporter(1) is not None


def _even_signs(lattice):
    e = tuple(lattice.module_generators())
    labels = lattice.module_generating_set()
    return [
        lattice.O()({labels[0]: -e[0], labels[1]: -e[1], labels[2]: e[2]}),
        lattice.O()({labels[0]: e[0], labels[1]: -e[1], labels[2]: -e[2]}),
    ]


def test_finite_subgroup_normalizer_realizes_full_automorphisms_on_z3():
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    normalizer, centralizer = finite_subgroup_normalizer(lattice, _even_signs(lattice))
    assert (len(normalizer), len(centralizer)) == (int(48), int(8))


def test_finite_subgroup_normalizer_image_shrinks_on_nonisometric_eigenspaces():
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, 2]])
    normalizer, centralizer = finite_subgroup_normalizer(lattice, _even_signs(lattice))
    assert (len(normalizer), len(centralizer)) == (int(16), int(8))
