r"""#381: which sign path the Otilde+ plane row of T_Co takes.

`Otilde+ = ker(rho, sn_RR)` is the index-two subgroup of `Otilde = ker rho` that
also cuts the real spinor norm (Dutour Sikiric--Hulek, arXiv:2302.01679v2, p. 2:
the reflection in a vector of length 2 in the summand U of N lies in Otilde(N)
with real spinor norm -1, and that element is what makes Otilde^+(N) the
index-two subgroup).  The splitting walk yields a second lift per double coset
exactly when its stabilizer does *not* present the sign coset
(`_stabilizer_sign_flips` false) and a kernel witness is available, so the
question the row's count turns on is which of those holds at T_Co's planes.

Nothing is introduced: `rho` is the lattice's discriminant representation, `sn_RR`
its real spinor norm (`O_plus().preimage_morphism()`), the parabolic family is
Dutour Sikiric--Hulek Thm 4.9 (printed pp. 33--34), and the double cosets are
Lemma 3.6 (printed p. 22).
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

lattice = rows._lattice_by_name("Tco")
log(f"lattice: rank {lattice.module_rank()}, signature {lattice.signature()}")
subgroup = rows._row_subgroup(lattice, "Otilde+")
log(f"subgroup: {subgroup}")
quotient = subgroup.finite_character_quotient()
log(f"quotient index: {quotient.index()}")

started = time.perf_counter()
j, sign_labels = quotient._sign_descent_rank()
log(
    f"_sign_descent_rank(): j={j}, labels={list(sign_labels)} "
    f"in {time.perf_counter() - started:.2f} s"
)

started = time.perf_counter()
ambient_group = lattice.Aut()
log(f"ambient group (the O row): {ambient_group}")
planes = tuple(ambient_group.isotropic_orbit_representatives(2))
log(f"ambient plane orbits: {len(planes)} in {time.perf_counter() - started:.2f} s")
if not planes:
    raise SystemExit("no ambient plane orbit: the Otilde+ plane row has no plane cusp")
plane = planes[0]

started = time.perf_counter()
complete = plane.is_parabolic_complete()
log(f"is_parabolic_complete(): {complete} in {time.perf_counter() - started:.2f} s")

started = time.perf_counter()
family = tuple(plane.parabolic_stabilizer_generators())
log(f"parabolic_stabilizer_generators(): {len(family)} generators in {time.perf_counter() - started:.2f} s")

started = time.perf_counter()
flips = quotient._stabilizer_sign_flips(family)
log(f"_stabilizer_sign_flips(family): {flips} in {time.perf_counter() - started:.2f} s")

started = time.perf_counter()
witness = quotient._kernel_sign_flip("spinor")
log(f"_kernel_sign_flip('spinor'): answered in {time.perf_counter() - started:.2f} s")
if witness is None:
    log("witness: None")
else:
    ring = lattice.base_ring()
    rho = lattice.discriminant_representation()
    trivial = quotient._discriminant_group.one()
    log(f"witness: {witness!r}")
    log(f"  rho(witness) is trivial: {rho(witness) == trivial}")
    log(f"  real spinor norm -1: {not lattice.O_plus().preimage_morphism()(witness).is_one()}")
    log(f"  determinant one: {ring(witness.determinant()) == ring.one()}")

lifts_per_coset = 2 if (j >= 1 and len(sign_labels) == 1 and not flips and witness is not None) else 1
log(f"the walk yields {lifts_per_coset} lift(s) per double coset at this plane")
log("done")
