r"""#381: the index per finite class, computed after the theorem that makes it an answer.

Theorem.  Let G = O(L), chi a finite character, Gamma = ker chi, F = chi(G), P a
primitive isotropic plane, F_P = chi(Stab_G(P)), and c the divided class pair of
a line of P.  D. Dutour Sikiric and K. Hulek, arXiv:2302.01679v2, Lemma 3.6,
printed p. 22, give that the Gamma-orbits in G.P correspond to the cosets F/F_P;
the class map x |-> chi(x)(c) is F-equivariant, so the cusps over c are the
cosets gF_P with g.c = c.  If F_P <= Stab_F(c) then gF_P maps to c exactly when
g in Stab_F(c), so the fibre over c is a torsor under Stab_F(c)/F_P and

    #{Gamma-orbits of planes with class c} = [Stab_F(c) : F_P],

which is the "index per finite class" the issue asks the call to return.

Computation.  At T_Co, for Otilde: check F_P <= Stab_F(c) for the classes of the
ambiguous buckets, then compute [Stab_F(c) : F_P] and compare it with the bucket
size the cusp row printed.  The computation answers the issue's question only
through the theorem above and names it.
"""

import importlib.util
import sys
import time

sys.path.insert(0, "tests")
START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


spec = importlib.util.spec_from_file_location("rows", "tests/coble_gamma_co_2_incidence_rows.py")
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)

from sage.libs.gap.libgap import libgap
from sage_extensions.categories.group.groups import _element_to_engine
from sage_extensions.categories.orthogonal_quotients import (
    _isotropic_line_class_points,
    _isotropic_line_image_key,
)

lattice = rows._lattice_by_name("Tco")
subgroup = rows._row_subgroup(lattice, "Otilde")
log(f"subgroup: {subgroup}")
quotient = subgroup.finite_character_quotient()
log(f"quotient index: {quotient.index()}")

engine, im_rho, _section, ambient = quotient._im_rho_engine_and_section()
log(f"im rho order: {libgap.Order(im_rho)}")

started = time.perf_counter()
planes = tuple(lattice.Aut().isotropic_orbit_representatives(2))
plane = planes[0]
family = tuple(plane.parabolic_stabilizer_generators())
log(f"parabolic family: {len(family)} generators in {time.perf_counter() - started:.2f} s")

rho = lattice.discriminant_representation()
images = [_element_to_engine(quotient._discriminant_group, rho(s)) for s in family]
F_P = libgap.Subgroup(im_rho, images)
log(f"|F_P| = {libgap.Order(F_P)}")

line_cusps = tuple(subgroup.cusps(1))
buckets = {}
for cusp in line_cusps:
    key = _isotropic_line_image_key(quotient, cusp.representative())
    buckets.setdefault(key, []).append(cusp)
log(f"line cusps {len(line_cusps)}, keys {len(buckets)}")

ambiguous = [(key, bucket) for key, bucket in buckets.items() if len(bucket) > 1]
ambiguous.sort(key=lambda item: len(item[1]))
log(f"ambiguous buckets: {len(ambiguous)}; sizes {[len(b) for _, b in ambiguous]}")

for key, bucket in ambiguous[:4]:
    line = bucket[0].representative()
    point = _isotropic_line_class_points(lattice, line)
    log(f"bucket of {len(bucket)}: key {_isotropic_line_image_key(quotient, line)}")
    started = time.perf_counter()
    fixes = all(
        bool(point == point ^ image)
        for image in images
    )
    log(f"  F_P acts trivially on the key: {fixes} ({time.perf_counter() - started:.2f} s)")
    started = time.perf_counter()
    stabilizer = libgap.Stabilizer(im_rho, point)
    log(f"  |Stab_F(c)| = {libgap.Order(stabilizer)} in {time.perf_counter() - started:.2f} s")
    started = time.perf_counter()
    index = int(libgap.Index(stabilizer, F_P)) if fixes else None
    log(f"  [Stab_F(c) : F_P] = {index} ({time.perf_counter() - started:.2f} s); bucket {len(bucket)}")
log("done")
