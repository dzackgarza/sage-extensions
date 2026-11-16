"""Probe: the per-plane cost and footprint of the kernel incidence row on T_Co.

The row walks the 189720 planes of ``Otilde(T_Co)`` and, at each, identifies the plane with a cusp
of its own row and the lines of its parabolic-covering flags with the line cusps.  The call does not
return, so this probe walks a bounded prefix of the same planes, in the row's own order, and records
for each sampled plane: the walk time, the time the registry lookup takes and the size of the
registry it scans, and the process RSS.  The cusp identification is then measured on the same row's
own cusps: one matching and one non-matching witness, and a scan over the cusp prefix.
"""
import os
import threading
import time

START = time.monotonic()


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


def sample():
    while True:
        print(f"[rss] t={time.monotonic() - START:7.1f}s rss={rss_mib():8.1f} MiB", flush=True)
        time.sleep(5)


threading.Thread(target=sample, daemon=True).start()

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp

mark = time.monotonic()


def stage(label):
    global mark
    now = time.monotonic()
    print(f"    {now - mark:8.2f} s  {label}  rss {rss_mib():7.1f} MiB", flush=True)
    mark = now


N = int(os.environ.get("PROBE_PLANES", "200"))
M = int(os.environ.get("PROBE_CUSPS", "40"))

lattice = NamedLattices.Tco
stage("lattice")
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage(f"Otilde and its quotient, index {quotient.index()}")
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
first = lattice.linear_combination(
    {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
)
plane = lattice.primitive_isotropic_subobject(first, names["ep"])
print(f"ambient plane {plane.module_rank()} primitive {plane.is_primitive()} gram {plane.gram_tensor().entries()}", flush=True)
stage("ambient plane, taken from the O(T_Co) row's own representative")
print(f"parabolic complete {plane.is_parabolic_complete()}", flush=True)
stage("is_parabolic_complete")
family = tuple(plane.parabolic_stabilizer_generators())
stage(f"parabolic generators {len(family)}")
quotient.register_isotropic_lift(plane, quotient.supergroup.one(), family)
stage(f"registered the source plane, registry {len(quotient.__dict__.get('_isotropic_lift_registry', {}))}")

splittings = quotient._iter_splitting_isometries_in_im_rho(family)
first_splitting = next(splittings)
stage("the walk's first splitting lift arrived")
planes = [plane]
mark_one = time.monotonic()
for position in range(1, N + 1):
    splitting = first_splitting if position == 1 else next(splittings)
    transported = splitting.transport_isotropic_object(plane)
    quotient.register_isotropic_lift(transported, splitting, family)
    planes.append(transported)
    if position in (1, 2, 3) or position % 20 == 0:
        span = time.monotonic() - mark_one
        mark_one = time.monotonic()
        lookup_start = time.monotonic()
        found = quotient.isotropic_lift_of(transported)
        lookup = time.monotonic() - lookup_start
        registry = len(quotient.__dict__.get("_isotropic_lift_registry", {}))
        print(
            f"  plane {position:5d}: walk+transport+register {span:7.3f} s  "
            f"registry lookup {lookup * 1000:9.3f} ms over {registry} entries  "
            f"found {found is not None}  rss {rss_mib():7.1f} MiB",
            flush=True,
        )
stage(f"walked {len(planes)} planes")

cusps = []
mark_cusp = time.monotonic()
for position, term in enumerate(planes[:M]):
    cusps.append(_arithmetic_cusp(subgroup, term))
    if position in (0, 1) or position % 10 == 0:
        span = time.monotonic() - mark_cusp
        mark_cusp = time.monotonic()
        print(f"  cusp {position:5d}: built in {span:7.3f} s  rss {rss_mib():7.1f} MiB", flush=True)
stage(f"{len(cusps)} plane cusps built")


def scan(term, over):
    tested = 0
    found = None
    began = time.monotonic()
    for candidate in over:
        tested += 1
        if term not in candidate.universe():
            continue
        if candidate.transporter_witness(term) is not None:
            found = candidate
            break
    return time.monotonic() - began, tested, found is not None


target = planes[len(cusps) - 1]
elapsed, tested, hit = scan(target, [cusps[len(cusps) - 2]])
print(f"  one non-matching caller: {elapsed * 1e6:10.1f} us, hit {hit}", flush=True)
elapsed, tested, hit = scan(target, [cusps[len(cusps) - 1]])
print(f"  one matching caller    : {elapsed * 1e6:10.1f} us, hit {hit}", flush=True)
elapsed, tested, hit = scan(target, cusps)
print(f"  a scan over {len(cusps)} cusps of this row: {elapsed:8.3f} s for {tested} callers, hit {hit}", flush=True)
if tested:
    print(f"  per caller in the scan : {elapsed / tested * 1e6:10.1f} us", flush=True)
stage("cusp identification measured")
