"""Whether a plane's parabolic family is a function of the plane, and what a resumed cusp costs.

Three questions, one process, on the small lattice the row's probes use:

1. the source plane's span, and the family at the plane as drawn and at a copy
   rebuilt from the same span -- a resume replays the second, not the first;
2. the bytes a checkpoint entry needs, kept as the pair the relation reads
   (span rows and the finite element) and as the pair the split holds (span and
   the lift's word);
3. what reading a cusp back from a span costs through the subobject the span
   names, and what the cusp's own construction costs on its own.
"""

import os
import pickle
import sys
import time

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403
import sage_extensions.categories.isotropic_orbits as isotropic_orbits  # noqa: E402
import sage_extensions.categories.orthogonal_quotients as orthogonal_quotients  # noqa: E402
from sage_extensions.owned_category import _object_of  # noqa: E402

from coble_gamma_co_2_incidence_rows import _lattice_by_name, _row_subgroup  # noqa: E402

NAME = os.environ.get("PROBE_LATTICE", "U+U(2)+<-2>")
ROW = os.environ.get("PROBE_ROW", "Otilde")
REPEATS = int(os.environ.get("PROBE_REPEATS", "50"))


def mark(what):
    print(what, flush=True)


def span_rows(span):
    return span[1]


def family_at(plane):
    return tuple(plane.parabolic_stabilizer_generators())


lattice = _lattice_by_name(NAME)
subgroup = _row_subgroup(lattice, ROW)
source = tuple(lattice.Aut().isotropic_orbit_representatives(2))[0]
span = isotropic_orbits._span_key(source)
family = family_at(source)
mark(f"source span rows: {span_rows(span)}")
mark(f"family at the source as drawn: {len(family)}")

rebuilt = isotropic_orbits._subobject_of_span(lattice, span)
rebuilt_family = family_at(rebuilt)
mark(f"the copy rebuilt from that span: rows {span_rows(isotropic_orbits._span_key(rebuilt))}")
mark(f"family at the rebuilt copy: {len(rebuilt_family)}")
again = family_at(isotropic_orbits._subobject_of_span(lattice, span))
mark(f"family at a second rebuilt copy: {len(again)}")
mark(f"the same set of generators (repr, sorted): "
     f"{sorted(repr(g) for g in family) == sorted(repr(g) for g in rebuilt_family)}")
mark(f"the same order of generators (repr): "
     f"[repr(g) for g in family] == [repr(g) for g in rebuilt_family]")

# ---- what a checkpoint entry costs -------------------------------------------
quotient = subgroup.finite_character_quotient()
planes = []
for plane in orthogonal_quotients._iter_transported_planes(quotient, source, family):
    planes.append(plane)
    if len(planes) >= 4:
        break
mark(f"planes drawn for the entry measurement: {len(planes)}")
for position, plane in enumerate(planes):
    plane_span = isotropic_orbits._span_key(plane)
    record = quotient.__dict__["_isotropic_lift_registry"][plane_span]
    retained, _family, image = record
    as_read = pickle.dumps((plane_span[1], image))
    as_held = pickle.dumps((plane_span[1], tuple(retained.letters), retained.flip is not None))
    mark(f"  plane {position}: the relation's read {len(as_read)} bytes; "
         f"the split's entry {len(as_held)} bytes; word {len(retained.letters)} letters")

# ---- what reading a cusp back from a span costs -------------------------------
def timed(label, action, repeats):
    action()
    started = time.perf_counter()
    for _ in range(repeats):
        action()
    elapsed = time.perf_counter() - started
    mark(f"{label}: {elapsed / repeats * 1000:.3f} ms a call over {repeats}")
    return elapsed / repeats


timed("cusp via the subobject the span names",
      lambda: isotropic_orbits._arithmetic_cusp(
          subgroup, isotropic_orbits._subobject_of_span(lattice, isotropic_orbits._span_key(planes[0]))),
      REPEATS)
timed("cusp constructed from the span alone",
      lambda: _object_of(
          isotropic_orbits.Sets(),
          _engine=(isotropic_orbits.Sets(), isotropic_orbits._ArithmeticCuspEngine, None),
          subgroup=subgroup,
          span=isotropic_orbits._span_key(planes[0]),
          subobject_rank=planes[0].module_rank(),
      ),
      REPEATS)
