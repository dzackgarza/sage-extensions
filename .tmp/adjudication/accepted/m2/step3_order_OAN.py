"""Step 3 -- the finite group O(A_N): Arf type of A_N = A_{U(2)} + A_{E8(-2)}, order check,
verification of the order formula on 4-dimensional models, and the generator count 4n."""
from fractions import Fraction
from itertools import product
import sys
sys.path.insert(0, "scripts")
from lat import Lat, U, U2, mul

# ---------------- E8 Cartan matrix, then E8(-2) = -2 * Cartan ----------------
C8 = [[2, -1, 0, 0, 0, 0, 0, 0],
      [-1, 2, -1, 0, 0, 0, 0, 0],
      [0, -1, 2, -1, 0, 0, 0, -1],
      [0, 0, -1, 2, -1, 0, 0, 0],
      [0, 0, 0, -1, 2, -1, 0, 0],
      [0, 0, 0, 0, -1, 2, -1, 0],
      [0, 0, 0, 0, 0, -1, 2, 0],
      [0, 0, -1, 0, 0, 0, 0, 2]]
print("Cartan(E8) det =", Lat(C8).det, " even =", Lat(C8).even())
E8m2 = [[-2 * x for x in row] for row in C8]
L8 = Lat(E8m2, "E8(-2)")
print("E8(-2): det =", L8.det, " even =", L8.even())

cls8 = L8.classes()
print("|A_{E8(-2)}| =", len(cls8))
from collections import Counter
c8 = Counter(str(L8.qA(y)) for y in cls8)
print("  distribution of q on A_{E8(-2)} (values in Q/2Z):", dict(c8))

# ---------------- A_{U(2)} ----------------
L2 = Lat(U2, "U(2)")
cls2 = L2.classes()
print("|A_{U(2)}| =", len(cls2), " q values:", {str(L2.qA(y)) for y in cls2})

# ---------------- A_N = A_{U(2)} + A_{E8(-2)} ----------------
A = [(a, b) for a in cls2 for b in cls8]
print("|A_N| =", len(A))
qz = Counter()
for a, b in A:
    v = (L2.qA(a) + L8.qA(b)) % 2
    qz[str(v)] += 1
print("  q_A_N distribution:", dict(qz))
zeros = qz["0"]
m = 5
print(f"  #zeros = {zeros};  plus type predicts 2^9+2^4 = {2**9 + 2**4},"
      f" minus type predicts 2^9-2^4 = {2**9 - 2**4}")
typ = "+" if zeros == 2**9 + 2**4 else ("-" if zeros == 2**9 - 2**4 else "?")
print("  ==> A_N is 2-elementary of dimension 10, type q_10^%s" % typ)


def order_O(m, eps=1):
    """|O^eps(2m,2)| = 2 * q^{m(m-1)} * (q^m - eps) * prod_{i=1}^{m-1} (q^{2i}-1), q=2."""
    o = 2 * 2**(m * (m - 1)) * (2**m - eps)
    for i in range(1, m):
        o *= (2**(2 * i) - 1)
    return o


print("  |O^+(10,2)| =", order_O(5, +1))
print("  2^21*3^5*5^2*7*17*31 =", 2**21 * 3**5 * 5**2 * 7 * 17 * 31)
print("  equal:", order_O(5, +1) == 2**21 * 3**5 * 5**2 * 7 * 17 * 31 == 46998591897600)


# -------- verification of the order formula by brute force in dimension 4 --------
def brute_order(G, n=4):
    """count isometries of the F2-quadratic form with Gram G (mod 2) by enumeration."""
    def q(x):
        return sum(x[i] * G[i][j] * x[j] for i in range(n) for j in range(n)) % 2
    cnt = 0
    for rows in product(list(product([0, 1], repeat=n)), repeat=n):
        M = [list(r) for r in rows]
        # invertible?
        d = (M[0][0] * (M[1][1] * (M[2][2] * M[3][3] - M[2][3] * M[3][2])
                        - M[1][2] * (M[2][1] * M[3][3] - M[2][3] * M[3][1])
                        + M[1][3] * (M[2][1] * M[3][2] - M[2][2] * M[3][1]))
             - M[0][1] * (M[1][0] * (M[2][2] * M[3][3] - M[2][3] * M[3][2])
                          - M[1][2] * (M[2][0] * M[3][3] - M[2][3] * M[3][0])
                          + M[1][3] * (M[2][0] * M[3][2] - M[2][2] * M[3][0]))
             + M[0][2] * (M[1][0] * (M[2][1] * M[3][3] - M[2][3] * M[3][1])
                          - M[1][1] * (M[2][0] * M[3][3] - M[2][3] * M[3][0])
                          + M[1][3] * (M[2][0] * M[3][1] - M[2][1] * M[3][0]))
             - M[0][3] * (M[1][0] * (M[2][1] * M[3][2] - M[2][2] * M[3][1])
                          - M[1][1] * (M[2][0] * M[3][2] - M[2][2] * M[3][0])
                          + M[1][2] * (M[2][0] * M[3][1] - M[2][1] * M[3][0]))) % 2
        if d == 0:
            continue
        ok = True
        for i, j in product(range(n), repeat=2):
            # compute (Mx)_i (Mx)_j pairing: check q(Mx) = q(x) for all x
            pass
        for x in product([0, 1], repeat=n):
            y = [sum(M[i][j] * x[j] for j in range(n)) % 2 for i in range(n)]
            if q(y) != q(x):
                ok = False
                break
        if ok:
            cnt += 1
    return cnt


print("\nBrute-force check of the order formula in dimension 4:")
G_plus = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]      # U + U, Arf 0
G_minus = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]     # U + (A1+A1 style, Arf 1)
print("  |O^+(4,2)| brute =", brute_order(G_plus), " formula =", order_O(2, +1))
print("  |O^-(4,2)| brute =", brute_order(G_minus), " formula =", order_O(2, -1))

print("\nGenerator count of the quoted construction (line 1450): 4*SL2 + 4(n-1) transvections = 4n")
for n in (12,):
    print(f"  n = dim(U+U+L) = {n}: 4 + 4*(n-1) = {4 + 4 * (n - 1)} generators")
