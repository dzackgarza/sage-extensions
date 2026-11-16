import time
from sage_extensions.all import *

def position(cusps, cusp):
    for i, c in enumerate(cusps):
        if c is cusp or c == cusp:
            return i
    return None

def case(name, group, *extra):
    t0 = time.monotonic()
    try:
        lines = tuple(group.cusps(1)); t1 = time.monotonic()-t0
        planes = tuple(group.cusps(2)); t2 = time.monotonic()-t0
        seq = group.tits_building_incidence(); t3 = time.monotonic()-t0
        edges = tuple(seq)
    except Exception as error:
        print(f"{name}: {type(error).__name__}: {error} after {time.monotonic()-t0:.2f} s", flush=True)
        return
    pairs = [(position(lines, x.line_cusp()), position(planes, x.plane_cusp())) for x in edges]
    print(f"{name}: lines={len(lines)} planes={len(planes)} edges={len(edges)} pairs={pairs} "
          f"t_lines={t1:.2f} t_planes={t2:.2f} t_all={t3:.2f} both={extra}", flush=True)

U = lambda: Lattices(ZZ)("U")
UU = U() + U()
case("O(U+U)", UU.Aut(), UU is UU.Aut().lattice())
case("SO(U+U)", UU.SO())
UU2 = U() + U() + Lattices(ZZ)([[-2]])
case("O(U+U+<-2>)", UU2.Aut())
UU3 = U() + U() + U()
case("O(U+U+U)", UU3.Aut())
UU4 = U() + Lattices(ZZ)([[0,2],[2,0]])
case("O(U+U(2))", UU4.Aut())
