r"""The ten null rays of the split rank-six cell have stabilizer W(D5).

Write a_i=e_i+f and b_i=sum_{j!=i} e_j+2f in I_{5,1}.
Distinct pairings are -1 except b(a_i,b_i)=-2. Thus every pairing
permutation permutes five pairs and exchanges selected pairs. The five
orthogonal vectors a_i-b_i have square 4; their reflections exchange the
respective pairs. Each vector is congruent to sum(e_i)+f modulo 2, so
exactly the products of an even number of these half-integral reflections
are integral. Hence the lattice stabilizer is (C2)^4 semidirect S5,
of order 16*120=1920. It preserves every one of the ten given positions.
"""

from sage_extensions.all import *


def test_the_ten_null_rays_have_the_integral_even_signed_permutation_stabilizer():
    lattice = Lattices(ZZ)([[ZZ(i == j) * (-1 if i == 5 else 1) for j in range(6)] for i in range(6)])
    basis = tuple(lattice.module_generators())
    positive, negative = basis[:5], basis[5]
    rays = (
        *(vector + negative for vector in positive),
        *(sum((vector for j, vector in enumerate(positive) if j != i), lattice.zero()) + 2 * negative for i in range(5)),
    )
    indices = Sets.Δ[9]
    family = Sets().Mor(indices, lattice)(lambda index: rays[int(index)])

    stabilizer = lattice.O().stabilizer(family)

    assert stabilizer.cardinality() == 1920
    assert all(Set(isometry(ray) for ray in rays) == Set(rays) for isometry in stabilizer.group_generators())
