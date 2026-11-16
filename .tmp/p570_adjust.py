"""#570: the adjuster's own stages, on the witness the named question uses.

`_subgroup_isotropic_equivalence_witness` at the Otilde(T_Co) cusp of a plane's own
line spends its minutes in `OrthogonalCharacterQuotient.adjust_witness_into_subgroup`
(entered at 94.27 s, not returned when the 575 s cap killed the probe).  This probe
rebuilds that call's two arguments -- the ambient witness carrying the plane's line
to the cusp's line, and the parabolic family at the cusp's line -- and runs the real
adjuster with each engine call it makes wrapped, so a stage with no exit line names
the wall.
"""
import ast
import os
import time

START = time.monotonic()
DEPTH = [0]
ROW_LOG = os.environ.get("ROW_LOG", ".tmp/p570_row.log")


def rss_mib():
    for line in open(f"/proc/{os.getpid()}/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return float("nan")


def say(label):
    print(f"[t={time.monotonic() - START:8.2f}s] {'.' * DEPTH[0]} {label}  rss={rss_mib():.0f} MiB", flush=True)


from sage_extensions.all import *  # noqa: F401,F403
from sage.libs.gap.libgap import libgap
import sage_extensions.categories.orthogonal_quotients as oq
from sage_extensions.categories.lattice_morphisms import LatticeIsometryMor


def wrap_method(cls, name):
    original = getattr(cls, name)

    def timed(self, *arguments, **keywords):
        DEPTH[0] += 1
        say(f"enter {name}")
        began = time.monotonic()
        try:
            return original(self, *arguments, **keywords)
        finally:
            DEPTH[0] -= 1
            say(f"exit  {name}  {time.monotonic() - began:.2f} s")

    setattr(cls, name, timed)


def wrap_function(module, name):
    original = getattr(module, name)

    def timed(*arguments, **keywords):
        DEPTH[0] += 1
        say(f"enter {name}")
        began = time.monotonic()
        try:
            return original(*arguments, **keywords)
        finally:
            DEPTH[0] -= 1
            say(f"exit  {name}  {time.monotonic() - began:.2f} s")

    setattr(module, name, timed)


def wrap_gap(name):
    original = getattr(libgap, name)

    def timed(*arguments, **keywords):
        DEPTH[0] += 1
        say(f"enter libgap.{name}")
        began = time.monotonic()
        try:
            return original(*arguments, **keywords)
        finally:
            DEPTH[0] -= 1
            say(f"exit  libgap.{name}  {time.monotonic() - began:.2f} s")

    setattr(libgap, name, timed)


wrap_function(oq, "_double_coset_adjustment")
wrap_method(oq._GapWordSection, "letters_of_permutation")
for name in ("IsomorphismPermGroup", "Subgroup", "Image", "DoubleCoset",
             "CanonicalRightCosetElement", "Range"):
    wrap_gap(name)


def count_gap(name):
    original = getattr(libgap, name)
    seen = [0]

    def counted(*arguments, **keywords):
        seen[0] += 1
        if seen[0] in (1, 2, 10, 100, 1000) or seen[0] % 10000 == 0:
            say(f"libgap.{name} call {seen[0]}")
        return original(*arguments, **keywords)

    setattr(libgap, name, counted)


count_gap("GeneratorsOfGroup")

lattice = NamedLattices.Tco
subgroup = lattice.stable_orthogonal_group()
quotient = subgroup.finite_character_quotient()
say("Otilde(T_Co) and its quotient")
names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane = lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
)
plane_domain = plane.inclusion().domain()
first = plane.inclusion()(plane_domain.module_generator(next(iter(plane_domain.module_generating_set()))))
line = lattice.primitive_isotropic_subobject(first)
line_class = lattice.divided_discriminant_class(first)

candidate = None
for entry in open(ROW_LOG, encoding="utf-8"):
    if not entry.startswith("ROW "):
        continue
    position, rest = entry[len("ROW "):].split(" ", 1)
    readings = ast.literal_eval(rest.split(" class=")[0].strip())
    vector = lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})
    if lattice.divided_discriminant_class(vector) == line_class:
        candidate = (int(position), vector)
        break
position, vector = candidate
representative = lattice.primitive_isotropic_subobject(vector)
say(f"the cusp's own line, row position {position}")

ambient = subgroup.supergroup()
began = time.monotonic()
family = list(ambient.isotropic_stabilizer_generators(representative))
say(f"the parabolic family at the cusp's line: {len(family)} generators in {time.monotonic() - began:.2f} s")
began = time.monotonic()
witness = ambient.isotropic_equivalence_witness(line, representative)
say(f"the ambient witness carrying the plane's line to it: {time.monotonic() - began:.2f} s, found {witness is not None}")
if witness is None:
    raise SystemExit("no ambient witness")

target = quotient._gap_character_target()
say(f"the subgroup's condition S in the product: |S| = {int(libgap.Size(target))}")
say("the adjuster")
began = time.monotonic()
candidate = quotient.adjust_witness_into_subgroup(witness, tuple(family))
say(f"adjusted in {time.monotonic() - began:.2f} s: {candidate is not None}; "
    f"in the subgroup {None if candidate is None else candidate in subgroup}")
