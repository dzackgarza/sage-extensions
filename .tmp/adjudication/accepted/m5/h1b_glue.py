"""H1 (second half): the dual-lattice / discriminant map for  N subset M, index 2.

Fact (standard; proved in the report): if N subset M are even lattices of finite index, then
   phi : A_M = M^v/M -> A_N = N^v/N ,  [y] |-> [y]
is injective, q_N o phi = q_M (the same formula q([y]) = (y,y) mod 2 defines both), and
phi(A_M) = H^perp/H for H = M/N (because b_N(M^v, M) subset Z).
We check the cardinalities and the formula numerically, without enumerating any group.
"""
import io, contextlib, runpy
with contextlib.redirect_stdout(io.StringIO()):
    ns = runpy.run_path('h1_embed.py')
F = ns['F']; GN = ns['GN']; GM = ns['GM']; Tmat = ns['Tmat']
qfun = ns['qfun']; inv = ns['inv']; det = ns['det']
GNi, GMi, Ti = inv(GN), inv(GM), inv(Tmat)

def mod1(v): return [x - int(x) for x in v]

print("|A_M| = det M =", det(GM), "   |A_N| = det N =", det(GN))
print("H = M/N has order", det(Tmat), ";  |H^perp| = |A_N|/2 =", det(GN) // 2,
      ";  |H^perp/H| =", det(GN) // 4, "= |A_M| :", det(GN) // 4 == det(GM))

h = [F(0)] * 12; h[2] = F(1, 2)          # h = class of a/2 = p_2 in A_N
print("h = [a/2] = [p_2] in A_N : q(h) =", qfun(GN, mod1(h)), " (0 => clean gluing)")

ok, inper = True, True
for j in range(12):
    lab = mod1([GMi[i][j] for i in range(12)])       # class of G_M^{-1} e_j in A_M
    z = [Tmat[k][j] for k in range(12)]              # T^t e_j
    c = [sum(GNi[i][k] * z[k] for k in range(12)) for i in range(12)]   # c = G_N^{-1} T^t e_j
    qN = qfun(GN, mod1(c)); qM = qfun(GM, lab)
    if qN != qM:
        ok = False; print("   q mismatch at j =", j, qN, qM)
    bb = sum(mod1(c)[i] * GN[i][k] * mod1(h)[k] for i in range(12) for k in range(12))
    if bb % 1 != 0:
        inper = False; print("   not in H^perp at j =", j, bb)
print("q_N(phi(z)) = q_M(z) for the 12 spanning classes of A_M:", ok)
print("phi(A_M) subset H^perp :", inper)
print()
print("Injectivity: y in M^v with y in N implies y in M (N subset M), so [y] = 0 in A_M.")
print("Conclusion (H1): A_M = A_{E8(-2)} = (Z/2)^8 -> H^perp/H is an isometry of discriminant")
print("forms; A_N = (Z/2)^10 = (H^perp/H) + <h>, <h> the U(2)-part, q(h) = 0.")
