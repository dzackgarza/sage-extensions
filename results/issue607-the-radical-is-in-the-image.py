r"""The Eichler transvections of a T_Co plane fill the radical of Stab(J) mod 2.

P = <ep, 2h + a_i + a_j> on T_Co.  For e in P and a in P^perp (both in L, L even)
the Eichler transvection

    t(e, a)(v) = v - (a, v) e + (e, v) a - (1/2)(a, a)(e, v) e

is an integral isometry of L (V. Gritsenko, K. Hulek, G. Sankaran,
*Abelianisation of orthogonal groups and the fundamental group of modular
varieties*, arXiv:0810.1614, section 3.1, equation (4), printed p. 8; integral
on an even lattice by equation (10), printed p. 9).  It fixes P pointwise
((e, v) = (a, v) = 0 for v in P), so it lies in Stab_{O(L)}(P).

The probe computes rho of t(e, a) for e in a basis of P and a in a Z-basis of
P^perp, generates their image T in O(q), and compares T with
U = the kernel of the action of S = Stab_{O(q)}(J) on J and on J^perp/J.
It also checks |S / U| = |GL(J)| * |O(J^perp/J)| = 6 * 40320.
"""
import sys, time
sys.path.insert(0, "tests")
from sage.all import *  # noqa
from sage_extensions.all import *  # noqa
from sage.libs.gap.libgap import libgap
import coble_gamma_co_2_incidence_rows as driver
from sage.matrix.constructor import matrix
from sage.matrix.special import identity_matrix
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ
from sage.modules.free_module_element import vector

t0 = time.monotonic()
def log(m): print(f"[{time.monotonic()-t0:7.1f}s] {m}", flush=True)

L = NamedLattices.Tco
labels = tuple(L.module_generating_set())
gen = {l: L.module_generator(l) for l in labels}
Gram = matrix(ZZ, [[L.pairing(gen[x], gen[y]) for y in labels] for x in labels])
A = L.discriminant_group()
Oq = A.orthogonal_group()
elements = tuple(A.elements())
rank = A.elements().ranking_map()
def idx(e): return int(rank(e)) + 1
def perm(g): return libgap.PermList([idx(g(e)) for e in elements])
G = libgap.Group(*[perm(g) for g in Oq.group_generators()])
log(f"|O(q)| = {G.Size()}")

n = len(labels)
unit = identity_matrix(ZZ, n)
e1 = unit[labels.index("ep")]
e8 = [unit[labels.index(f"a{i}")] for i in range(1, 9)]
r = next(a + b for i, a in enumerate(e8) for b in e8[i + 1:] if (a + b) * Gram * (a + b) == -8)
e2 = 2 * unit[labels.index("h")] + r
assert e1 * Gram * e1 == 0 and e2 * Gram * e2 == 0 and e1 * Gram * e2 == 0
plane = L.primitive_isotropic_subobject(
    sum(c * gen[l] for c, l in zip(e1, labels)), sum(c * gen[l] for c, l in zip(e2, labels))
)
perp = matrix(ZZ, [Gram * e1, Gram * e2]).right_kernel().basis()
log(f"P^perp has a Z-basis of {len(perp)} vectors")

def transvection(e, a):
    rows = []
    for i in range(n):
        v = unit[i]
        ev, av = e * Gram * v, a * Gram * v
        rows.append(v - av * e + ev * a - (a * Gram * a) / 2 * ev * e)
    M = matrix(QQ, rows)
    assert M * Gram * M.transpose() == Gram
    return M

# A_L = L^#/L in pairing coordinates: y in L^# is z = ((y, b_j))_j in Z^n, and
# Gram = 2 * Gram0 with Gram0 unimodular (T_Co is 2-elementary of this shape),
# so A_L = Z^n / Gram Z^n = (Z/2)^n by z mod 2.  The library's class of
# primitive_dual(b_i) = b_i / 2 has z = Gram0 e_i, so the class with z = e_j is
# sum_i (Gram0^{-1})_{ij} [b_i / 2] mod 2.  An isometry M (rows the images of the
# basis) acts on z by z -> Gram M^T Gram^{-1} z.
Gram0 = Gram / 2
assert Gram0.base_ring() is ZZ or all(x in ZZ for x in Gram0.list())
Gram0 = matrix(ZZ, Gram0)
assert Gram0.det().abs() == 1
inverse0 = Gram0.inverse()
primitive = [L.discriminant_class(L.primitive_dual(gen[l])) for l in labels]
unit_class = [sum((int(inverse0[i, j]) % 2) * primitive[i] for i in range(n)) for j in range(n)]
index_of = {}
frontier = {(0,) * n: A.zero()}
for j in range(n):
    frontier.update({tuple((k[t] + (t == j)) % 2 for t in range(n)): c + unit_class[j]
                     for k, c in list(frontier.items())})
for key, element in frontier.items():
    index_of[key] = idx(element)
assert len(set(index_of.values())) == 2 ** n == len(elements)
keys = list(index_of)

def discriminant_permutation(M):
    N = Gram * M.transpose() * Gram.inverse()
    N = matrix(ZZ, N)
    images = [0] * len(elements)
    for key in keys:
        image = tuple(int(x) % 2 for x in N * vector(ZZ, key))
        images[index_of[key] - 1] = index_of[image]
    return libgap.PermList(images)

rho = L.discriminant_representation()
# a = Gram^{-1} z ranges over L^# cap P^perp: z in Z^n with z . e1 = z . e2 = 0.
dual_perp = [Gram.inverse() * z for z in matrix(ZZ, [e1, e2]).right_kernel().basis()]
candidates = dual_perp + [x + y for i, x in enumerate(dual_perp) for y in dual_perp[i + 1:]]
integral = []
for e in (e1, e2, e1 + e2):
    for a in candidates:
        M = transvection(e, a)
        if all(x in ZZ for x in M.list()):
            integral.append(matrix(ZZ, M))
log(f"{len(integral)} of {3 * len(candidates)} transvections t(e, a), e in P, a in L^# cap P^perp, are integral")
images = [discriminant_permutation(M) for M in integral]
T = libgap.Group(*images)
log(f"|T| = |<rho t(e, a)>| = {T.Size()}")

Jset = driver._plane_class_set(L, plane)
J = libgap.Set([idx(x) for x in Jset])
Jnz = [x for x in Jset if x != A.zero()]
b0 = A.b(A.zero(), A.zero())
Jperp = [x for x in elements if all(A.b(x, j) == b0 for j in Jnz)]
cosets = sorted({tuple(sorted(idx(x + j) for j in Jset)) for x in Jperp})
blocks = libgap([list(c) for c in cosets])
S = libgap.Stabilizer(G, J, libgap.OnSets)
on_blocks = libgap.ActionHomomorphism(S, blocks, libgap.OnSets)
on_J = libgap.ActionHomomorphism(S, [idx(j) for j in Jnz])
U = libgap.Intersection(libgap.Kernel(on_blocks), libgap.Kernel(on_J))
K0 = libgap.Kernel(on_blocks)
log(f"|S| = {S.Size()}, |K_0| = {K0.Size()}, |U| = {U.Size()}, "
    f"|S/U| = {S.Size() / U.Size()}, image on J: {libgap.Image(on_J).Size()}, "
    f"on J^perp/J: {libgap.Image(on_blocks).Size()}")
log(f"U is O_2(S): {U == libgap.PCore(S, 2)}")
log(f"T is inside S: {libgap.IsSubgroup(S, T)}; T = U: {T == U}")
log(f"K_0 / U acts on J as GL(J): {libgap.Image(on_J, K0).Size()}")
