"""Issue-17: the exact order of the discriminant image of the full O(N) on the real Enriques N.

That order is the correct coset-space size for the stable kernel ker(O(N) -> O(A_N)):
G/ker(rho) is isomorphic to im(rho), so a Schreier family for the kernel is indexed by
|im rho|, not by |O(A_N)| = 46998591897600.
"""
import json, time
from sage_extensions.all import ZZ, Lattices

f = json.load(open("/work/tests/fixtures/unpolarized_enriques.json"))
N = Lattices(ZZ)([[int(x) for x in r] for r in f["lattice"]["gram"]])
print(f"N rank {N.rank()} signature {N.signature_pair()}", flush=True)

t0 = time.time()
image = N.discriminant_image()
print(f"discriminant_image built in {time.time()-t0:.1f}s", flush=True)
t0 = time.time()
card = image.cardinality()
print(f"|im rho(O(N))| = {card} in {time.time()-t0:.1f}s", flush=True)
print(f"|O(A_N)| = {N.discriminant_group().orthogonal_group().cardinality()}", flush=True)
print("IMAGE_OK", flush=True)
