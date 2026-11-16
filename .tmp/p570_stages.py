"""#570 triage: where the exact line-stabilizer image of T_Co spends its time.

One call on T_Co at the named cusp -- the line the Otilde(T_Co) cusp at position
215 of 527 is the orbit of, which is one of a plane's own lines -- split into
construction and computation, every stage timed and capped.

The stages are the ones `exact_isotropic_stabilizer_generators` itself performs,
called in its own order from the same objects it reads, so each number belongs to
that call and not to a reimplementation.  The row that would build all 527 line
representatives is not repeated here: on this machine under load it does not
return inside 300 s (`.tmp/p570_stages.log`, first run), and the question at the
named cusp is a question about this line.
"""
import os
import signal
import time

START = time.monotonic()
CAP = float(os.environ.get("STAGE_CAP", "150"))
COSETS = int(os.environ.get("PROBE_COSETS", "4"))


class StageTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise StageTimeout


signal.signal(signal.SIGALRM, _alarm)


def rss_mib():
    for line in open(f"/proc/{os.getpid()}/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return float("nan")


LAST = [START]


def stage(label, detail=""):
    now = time.monotonic()
    print(f"[t={now - START:8.2f}s | {now - LAST[0]:8.2f}s] {label}{detail}  rss={rss_mib():.0f} MiB", flush=True)
    LAST[0] = now


def capped(label, fn, cap=None):
    """Run one stage under its own cap; the cap cannot interrupt a libgap call,
    so a stage that overruns prints its entry time and a TIMED OUT marker only
    after the call returns."""
    signal.setitimer(signal.ITIMER_REAL, cap or CAP)
    began = time.monotonic()
    try:
        value, out = fn(), False
    except StageTimeout:
        value, out = None, True
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    stage(label + (" [TIMED OUT]" if out else ""), f"  {time.monotonic() - began:.2f} s")
    return value, time.monotonic() - began, out


from sage_extensions.all import *  # noqa: F401,F403
from sage.libs.gap.libgap import libgap
from sage_extensions.categories.orthogonal_quotients import _isotropic_divided_class_set

lattice = NamedLattices.Tco
stage("lattice", f" {lattice} rank {lattice.module_rank()}")

subgroup, _, _ = capped("construction: Otilde(T_Co) = stable_orthogonal_group()",
                        lambda: lattice.stable_orthogonal_group())
quotient, _, _ = capped("construction: finite_character_quotient()",
                        subgroup.finite_character_quotient)
stage("quotient data", f" has_discriminant={quotient._has_discriminant} "
                       f"det_kernel={quotient.determinant_kernel} spinor_kernel={quotient.spinor_kernel}")

names = {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}
plane, _, _ = capped("construction: the plane", lambda: lattice.primitive_isotropic_subobject(
    lattice.linear_combination(
        {"h": 2, "a1": -1, "a2": -1, "a3": -2, "a4": -2, "a5": -2, "a6": -2, "a7": -2, "a8": -2}
    ),
    names["ep"],
))
plane_domain = plane.inclusion().domain()
plane_labels = tuple(plane_domain.module_generating_set())
plane_first = plane.inclusion()(plane_domain.module_generator(plane_labels[0]))
plane_line_class, _, _ = capped("construction: the plane line's divided class",
                                lambda: lattice.divided_discriminant_class(plane_first))

# The named specimen: the row representative whose divided class is the plane's own
# line's.  It is rebuilt from the coordinates `.tmp/p570_row.log` recorded, so the
# 179.7 s row is not paid for again; the class comparison is the lattice's own, not a
# reading of the printed form.
import ast as _ast

ROW_LOG = os.environ.get("ROW_LOG", ".tmp/p570_row.log")


def row_specimen():
    found = []
    for entry in open(ROW_LOG, encoding="utf-8"):
        if not entry.startswith("ROW "):
            continue
        position, rest = entry[len("ROW "):].split(" ", 1)
        readings = _ast.literal_eval(rest.split(" class=")[0].strip())
        vector = lattice.linear_combination({label: ZZ(value) for label, value in readings.items()})
        if lattice.divided_discriminant_class(vector) == plane_line_class:
            found.append((int(position), vector))
    if len(found) != 1:
        raise SystemExit(f"the row has {len(found)} representatives of the plane line's class, not one")
    return found[0]


(position, vector), _, _ = capped("construction: the named row representative, from its recorded coordinates",
                                  row_specimen)
line, _, _ = capped("construction: that line", lambda: lattice.primitive_isotropic_subobject(vector))
stage("the named specimen",
      f" row position {position} of 527, divided class {lattice.divided_discriminant_class(vector)}, "
      f"primitive {line.is_primitive()}, equal to the plane's own line {vector == plane_first}")

# `isotropic_line_stabilizer_image` is the route this call is entered *instead* of,
# and it is not part of it.  On this line it raises AssertionError from
# `_engine_two_primary_odd_orthogonal_generators` (via the complement lattice's
# `discriminant_image`), which is a different defect and is recorded separately.

family, _, _ = capped("computation: ambient.isotropic_stabilizer_generators(line)",
                      lambda: list(subgroup.supergroup().isotropic_stabilizer_generators(line)))
if family is None:
    raise SystemExit("the parabolic family did not return inside its cap")
stage("family", f" {len(family)} generators")

section_tuple, _, _ = capped("computation: _image_section()", quotient._image_section)
image, _, _ = capped("computation: _gap_image()", quotient._gap_image)
product_tuple, _, _ = capped("computation: _gap_product()", quotient._gap_product)
factors, product, embeddings, projections = product_tuple
stage("finite model", f" factors={[label for label, _ in factors]} product={type(product).__name__}")

position = next(i for i, (label, _) in enumerate(factors) if label == "discriminant")
projection = libgap.RestrictedMapping(projections[position], image)
discriminant_image = libgap.Image(projection)
stage("discriminant image built")

divided = _isotropic_divided_class_set(lattice, line)
finite_orthogonal = quotient._discriminant_group
data = libgap([libgap.Set([finite_orthogonal._engine_abelian_element(c) for c in divided])])
termwise_action = libgap.function_factory(
    "function(x, g) return List(x, part -> Set(List(part, y -> ImageElm(g, y)))); end")
stage("divided class data", f" D(W) has {len(divided)} classes")

image_generators = list(libgap.GeneratorsOfGroup(discriminant_image))
stage("image generators", f" {len(image_generators)} generators")


def data_orbit():
    seen = {str(data)}
    frontier = [data]
    steps = 0
    while frontier:
        following = []
        for reached in frontier:
            for generator in image_generators:
                steps += 1
                moved = termwise_action(reached, generator)
                marker = str(moved)
                if marker in seen:
                    continue
                seen.add(marker)
                following.append(moved)
        frontier = following
    print(f"    the walk applied {steps} generator images", flush=True)
    return seen


orbit, _, _ = capped("computation: the orbit of the divided data under rho(O(L))", data_orbit)
if orbit is not None:
    stage("orbit", f" |orbit|={len(orbit)}")

group_order, _, _ = capped("computation: Size(discriminant_image) = |rho(O(L))|",
                           lambda: int(libgap.Size(discriminant_image)))
if group_order is not None and orbit is not None:
    stage("orbit-stabilizer upper bound",
          f" |image|={group_order} |image|/|orbit|={group_order // len(orbit)}")

owned_image, _, _ = capped(
    "computation: line.stabilizer_discriminant_image()",
    lambda: line.stabilizer_discriminant_image())
if owned_image is not None:
    owned_order, _, _ = capped(
        "computation: its cardinality()",
        lambda: int(owned_image.cardinality()))
    stage("the owned stabilizer image", f" |rho(Stab(line))| = {owned_order}")

stabilizer, _, _ = capped("computation: Stabilizer(discriminant_image, data)",
                          lambda: libgap.Stabilizer(discriminant_image, data, termwise_action))
upper, _, _ = capped("computation: PreImages(projection, Stabilizer)",
                     lambda: libgap.PreImages(projection, stabilizer))
if upper is not None:
    bound, _, _ = capped("computation: Size(upper)", lambda: int(libgap.Size(upper)))
    stage("the GAP upper bound", f" |upper|={bound}")

lower, _, _ = capped("computation: Subgroup(product, images of the family)",
                     lambda: libgap.Subgroup(product, [quotient._gap_of_key(quotient.image(g))
                                                       for g in family]))
if lower is None:
    raise SystemExit("the lower bound did not return inside its cap")
lower_size, _, _ = capped("computation: Size(lower)", lambda: int(libgap.Size(lower)))
stage("the lower bound", f" |lower|={lower_size}")

if upper is not None:
    subset, _, _ = capped("computation: IsSubset(upper, lower)",
                          lambda: bool(libgap.IsSubset(upper, lower)))
    stage("containment", f" lower <= upper: {subset}")

# The loop itself, one element at a time, so the growth with the elements already
# processed is measured rather than inferred.
tested = 0
target = bound if upper is not None else None
if target is not None and lower_size is not None and lower_size < target:
    while lower_size < target and tested < COSETS:
        transversal, _, timed_out = capped(
            f"RightTransversal pass, lower of order {lower_size}",
            lambda: libgap.AsList(libgap.RightTransversal(upper, lower)))
        if timed_out:
            break
        stage("transversal", f" pass length {len(transversal)}")
        for coset in transversal:
            if tested >= COSETS:
                break
            began = time.monotonic()
            lift_t, _, out_l = capped("  lift", lambda: quotient._checked_lift(
                quotient._key_of_gap(coset), section_tuple[2].letters_of(coset)))
            if out_l:
                break
            moved_t, _, out_m = capped("  transport",
                                       lambda: lift_t.transport_isotropic_object(line))
            if out_m:
                break
            witness_t, _, out_w = capped(
                "  ambient.isotropic_equivalence_witness(moved, line)",
                lambda: subgroup.supergroup.isotropic_equivalence_witness(moved_t, line))
            if out_w or witness_t is None:
                print("    no witness / timed out here", flush=True)
                break
            element = witness_t * lift_t
            key = quotient._gap_of_key(quotient.image(element))
            closed, _, out_c = capped("  ClosureGroup(lower, key)",
                                      lambda: libgap.ClosureGroup(lower, key))
            if out_c:
                break
            grew = int(libgap.Size(closed)) > lower_size
            print(f"    coset {tested}: total {time.monotonic() - began:7.2f} s  |lower| {lower_size} -> "
                  f"{int(libgap.Size(closed))}  grew={grew}", flush=True)
            tested += 1
            if grew:
                lower = closed
                lower_size = int(libgap.Size(closed))
    stage("the loop sample", f" {tested} cosets processed, |lower|={lower_size} of |upper|={target}")
else:
    stage("the loop", f" not entered: |lower|={lower_size}, |upper|={target}")

print(f"total {time.monotonic() - START:.1f} s, rss {rss_mib():.0f} MiB", flush=True)
