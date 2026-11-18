"""Whether a row's own anchor is reproduced by a second process.

A row is a walk from one isotropic orbit representative over the parabolic
family at it (`_iter_transported_planes`).  A run that resumes at a mark skips
the walk's first k steps, which is only the same walk if a second process draws
the same representative and the same family in the same order.  This prints the
anchor and two digests: one of the family's members, and one of them in the
order the walk iterates.
"""

import hashlib
import os
import sys

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key  # noqa: E402

from coble_gamma_co_2_incidence_rows import _lattice_by_name, _row_subgroup  # noqa: E402

NAME = os.environ.get("PROBE_LATTICE", "U+U(2)+<-2>")
ROW = os.environ.get("PROBE_ROW", "Otilde")


def digest(rows):
    return hashlib.sha256(repr(rows).encode()).hexdigest()[:16]


lattice = _lattice_by_name(NAME)
subgroup = _row_subgroup(lattice, ROW)
print(f"row {ROW} of {NAME}; subgroup {subgroup}", flush=True)
representatives = tuple(lattice.Aut().isotropic_orbit_representatives(2))
print(f"plane orbit representatives: {len(representatives)}", flush=True)
for position, representative in enumerate(representatives):
    print(f"  representative {position} span rows: {_span_key(representative)[1]}", flush=True)
source = representatives[0]
family = tuple(source.parabolic_stabilizer_generators())
print(f"the source's parabolic family: {len(family)} generators", flush=True)


def matrix_rows(generator):
    try:
        return tuple(tuple(int(entry) for entry in row) for row in generator.matrix().rows())
    except Exception as failure:  # noqa: BLE001 - the digest falls back to the rendering
        print(f"  (no matrix: {type(failure).__name__})", flush=True)
        return ((repr(generator),),)


as_drawn = tuple(matrix_rows(generator) for generator in family)
print(f"family digest, in the walk's order: {digest(as_drawn)}", flush=True)
print(f"family digest, sorted         : {digest(sorted(as_drawn))}", flush=True)
for position, rows in enumerate(as_drawn):
    print(f"  generator {position}: {digest(rows)}", flush=True)
