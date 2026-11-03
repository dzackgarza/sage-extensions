from sage_extensions.all import *
import time

L = Lattices(ZZ)([[2, 0], [0, 2]])
G = L.O()
g = tuple(G.group_generators())[0]
t = g._coordinate_tensor()

print("fiber components:", len(t._flat_components()), "types:", {type(c).__name__ for c in t._flat_components()})

def timeit(f, n=200):
    t0 = time.monotonic()
    for _ in range(n):
        f()
    return (time.monotonic() - t0) / n

c = t._flat_components()[0]
print(f"hash(scalar): {timeit(lambda: hash(c))*1e6:.1f} us")
print(f"hash((valence,ranks,flat)) tensor.__hash__: {timeit(lambda: hash(t))*1e6:.1f} us")
print(f"tensor._cache_key(): {timeit(lambda: t._cache_key())*1e6:.1f} us")
print(f"str(tensor components): {timeit(lambda: repr(t))*1e6:.1f} us")
print(f"hash(mor) current: {timeit(lambda: hash(g))*1e6:.1f} us")
print("consistency check: hash(g) id-parts:", id(g.domain()), id(g.codomain()))
g2 = G(tuple(G.group_generators())[0])
print("equal g == g2:", g == g2, "| same tensor hash:", hash(g._coordinate_tensor()) == hash(g2._coordinate_tensor()))
