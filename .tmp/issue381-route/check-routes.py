r"""Probe: the route each T_Co row takes under ``auto``, and the reason it gives."""
import sys

sys.path.insert(0, "tests")

from sage_extensions.all import *  # noqa: F401,F403

from coble_gamma_co_2_incidence_rows import ROW_ROUTES, chosen_route

print(f"[probe] the routes: {ROW_ROUTES}", flush=True)
lattice = NamedLattices.Tco
stable = lattice.stable_orthogonal_group()
for label, subgroup in (
    ("O", lattice.Aut()),
    ("Otilde", stable),
    # Otilde+ is the intersection of the kernel with the spinor kernel; building
    # it on T_Co is a per-row cost of the driver and not part of this probe.
):
    print(f"[probe] {label:8s} auto -> {chosen_route(subgroup, 'auto')}", flush=True)
    print(f"[probe] {label:8s} asked divided-class -> {chosen_route(subgroup, 'divided-class')}", flush=True)
    print(f"[probe] {label:8s} asked certificate   -> {chosen_route(subgroup, 'certificate')}", flush=True)
