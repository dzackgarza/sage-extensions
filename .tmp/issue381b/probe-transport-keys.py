"""Whether a cusp's rebuilt plane is the key the walk registered its transport datum under."""

import sys

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key  # noqa: E402

lattice = Lattices(ZZ)("U") + Lattices(ZZ)(((0, 2), (2, 0))) + Lattices(ZZ)(((-2,),))
stable = lattice.stable_orthogonal_group()
quotient = stable.finite_character_quotient()
planes = tuple(stable.cusps(2))
print(f"retained transports after the row: {quotient.retained_isotropic_transport_count()}", flush=True)
registry = quotient.__dict__.get("_transported_isotropic_objects", {})
for key, datum in registry.items():
    print(f"  registered rows: {key[1]}  lattice id {key[0]}", flush=True)
for position, cusp in enumerate(planes):
    representative = cusp.representative()
    key = _span_key(representative)
    print(f"  cusp {position} rebuilds rows {key[1]} lattice id {key[0]}", flush=True)
    print(f"    found by key: {quotient.isotropic_transport_of(representative) is not None}", flush=True)
    quotient.release_isotropic_transports((representative,))
    print(f"    after release: {quotient.retained_isotropic_transport_count()}", flush=True)
