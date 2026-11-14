# PATH B only: Subgroup(parent engine, gens) + Order at real size.
import time

START = time.monotonic()


def stage(label):
    print(f"[t={time.monotonic()-START:7.1f}s] {label}", flush=True)


stage("imports")
from sage_extensions.all import *
from sage.libs.gap.libgap import libgap
from sage_extensions.categories.group.groups import _gap_model, _element_to_engine

U = Lattices(ZZ)([[0, 1], [1, 0]])
U2 = Lattices(ZZ)([[0, 2], [2, 0]])
N = U + U2 + Lattices(ZZ)("E8").twist(2)
G = N.O()
gens = tuple(G.group_generators())
stage(f"{len(gens)} ambient generators")
OG = N.discriminant_group().orthogonal_group()
rho = N.discriminant_representation()
gimgs = [_element_to_engine(OG, rho(g)) for g in gens]
stage(f"{len(gimgs)} rho images")
engine = _gap_model(OG)

stage("PATH B: Subgroup(parent, gens) + Order")
sub = libgap.Subgroup(engine, gimgs)
stage("bound")
stage(f"Order(sub) = {libgap.Order(sub)}")
stage("PATH B done")
print("MEASURE_OK", flush=True)
