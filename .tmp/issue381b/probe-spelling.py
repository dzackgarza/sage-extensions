"""Every registered spelling of a small kernel plane row spells the lift registered with it.

For each plane cusp of both kernel rows of ``U + U(2) + <-2>``: the lift the registry answers
is an isometry of the lattice, and its character image is the finite element registered beside
it -- the check that fails if a word spells something other than its lift.  The sign sheet's
entries (a word multiplied by a kernel witness) are counted, so the flip of a spelling is
known to be exercised or known not to be.
"""

import sys

sys.path.insert(0, "/repos/sage-extensions/tests")

from sage_extensions.all import *  # noqa: F401,F403

import os  # noqa: E402

from coble_gamma_co_2_incidence_rows import _lattice_by_name, _row_subgroup  # noqa: E402

lattice = _lattice_by_name(os.environ.get("PROBE_LATTICE", "U+U(2)+<-2>"))
for label in ("Otilde", "Otilde+"):
    subgroup = _row_subgroup(lattice, label)
    quotient = subgroup.finite_character_quotient()
    plane_cusps = subgroup.cusps(2)
    checked = 0
    flipped = 0
    for cusp in plane_cusps:
        answered = quotient.registered_isotropic_lift_of_span(cusp.span())
        lift, finite_element = answered
        assert lift.domain() is lattice
        assert quotient.image(lift)["discriminant"] == finite_element, (
            f"{label}: the lift a word spelled is not the lift its finite element is the image of"
        )
        checked += 1
    for retained, family, image in quotient.__dict__.get("_isotropic_lift_registry", {}).values():
        if getattr(retained, "flip", None) is not None:
            flipped += 1
    print(
        f"{label}: {checked} plane cusps answer a spelled lift, "
        f"{flipped} registry entries are a sign sheet's",
        flush=True,
    )
print("done", flush=True)
