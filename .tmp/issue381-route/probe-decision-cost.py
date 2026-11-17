r"""Probe: what the route decision costs on T_Co's Otilde row.

`chosen_route` calls `preserves_conjugation()`, and the class route calls it
again as its own precondition.  This probe times the two calls, so the cost is
a number and not a guess.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403

lattice = NamedLattices.Tco
started = time.monotonic()
subgroup = lattice.stable_orthogonal_group()
print(f"[{time.monotonic() - started:8.1f} s] Otilde(T_Co)", flush=True)
started = time.monotonic()
quotient = subgroup.finite_character_quotient()
print(f"[{time.monotonic() - started:8.1f} s] its character quotient", flush=True)
started = time.monotonic()
order = quotient.subgroup_image_order()
print(f"[{time.monotonic() - started:8.1f} s] subgroup_image_order = {order}", flush=True)
started = time.monotonic()
first = quotient.preserves_conjugation()
print(f"[{time.monotonic() - started:8.1f} s] preserves_conjugation (first) = {first}", flush=True)
started = time.monotonic()
second = quotient.preserves_conjugation()
print(f"[{time.monotonic() - started:8.1f} s] preserves_conjugation (second) = {second}", flush=True)
