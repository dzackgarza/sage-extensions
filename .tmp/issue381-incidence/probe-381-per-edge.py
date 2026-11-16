"""Probe: what one incidence edge costs on T_Co, in its parts.

An edge of the incidence carries a flag certificate: the flag's two terms, the
two cusp vertices, and a transporter carrying each term to its vertex.  The
certificate's construction transports each term and compares spans; this probe
times those parts at one plane of the Otilde(T_Co) row, on the tree it is run
against, so the row's floor is a number and not an inference.
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
from sage_extensions.categories.isotropic_orbits import _same_subobject, _span_key

mark = time.monotonic()


def stage(label):
    global mark
    now = time.monotonic()
    print(f"    {now - mark:8.2f} s  {label}  rss {rss_mib():7.1f} MiB", flush=True)
    mark = now


def per_call(label, count, work):
    began = time.monotonic()
    for _ in range(count):
        work()
    elapsed = (time.monotonic() - began) / count
    print(f"    {label:44s} {elapsed * 1000:9.3f} ms per call", flush=True)


lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
stage(f"Otilde and its quotient, index {quotient.index()}")
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
plane.is_parabolic_complete()
family = tuple(plane.parabolic_stabilizer_generators())
quotient.register_isotropic_lift(plane, quotient.supergroup.one(), family)
stage("plane, parabolic, registration")
splittings = quotient._iter_splitting_isometries_in_im_rho(family)
splitting = next(splittings)
stage("the walk's first splitting lift arrived")
transported = splitting.transport_isotropic_object(plane)
quotient.register_isotropic_lift(transported, splitting, family)
stage("one transported plane")
per_call("one span key", 20, lambda: _span_key(plane))
per_call("one span comparison (_same_subobject)", 10, lambda: _same_subobject(plane, transported))
per_call("one transport of a plane", 10, lambda: splitting.transport_isotropic_object(plane))
per_call("one registry lookup", 200, lambda: quotient.isotropic_lift_of(plane))
per_call("one registration", 200, lambda: quotient.register_isotropic_lift(transported, splitting, family))
stage("the parts")
