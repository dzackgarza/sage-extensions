"""What the registry holds before the relation is asked, for the small lattice's row."""

import sys

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403

lattice = Lattices(ZZ)("U") + Lattices(ZZ)(((0, 2), (2, 0))) + Lattices(ZZ)(((-2,),))
stable = lattice.stable_orthogonal_group()
quotient = stable.finite_character_quotient()
print(f"quotient index: {quotient.index()}", flush=True)
lines = tuple(stable.cusps(1))
planes = tuple(stable.cusps(2))
registry = quotient.__dict__.get("_isotropic_lift_registry", {})
print(f"after the cusp rows: {len(registry)} registered lifts, {len(planes)} plane cusps", flush=True)
for position, cusp in enumerate(planes):
    representative = cusp.representative()
    registered = quotient.registered_isotropic_lift(representative)
    print(f"  plane {position}: registered {registered is not None}", flush=True)
    print(f"    cusp span:    {cusp.span()[1]}", flush=True)
    print(f"    rebuilt span: {quotient and __import__('sage_extensions.categories.isotropic_orbits', fromlist=['_span_key'])._span_key(representative)[1]}", flush=True)
print(f"line cusps: {[cusp.span()[1] for cusp in lines]}", flush=True)
