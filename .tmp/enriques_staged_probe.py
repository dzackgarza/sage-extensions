"""Where does an Enriques case spend its 1 800 s: case-independent setup or the case's own work?

The acceptance case runs three things: `_gamma_h(face_polarization)` (build the group),
`image.cardinality()` on a subgroup of the discriminant orthogonal group, and `_counts(group)` (orbit
splitting for lines, planes and flags). A single 1 800 s cap tells us none of this; the stack dumps gave 26
distinct innermost frames, which is an absence of a hot spot, not an attribution.

Every stage prints BEFORE it starts, so a cap still leaves the ordered attribution. Two cases are measured,
the two the cost proxy puts first (case_3, case_1).
"""
import time

START = time.monotonic()


def stage(label):
    print(f"[t={time.monotonic() - START:8.1f}s] {label}", flush=True)


stage("imports")
from tests.acceptance.consumer import element, flag_classes, isotropic_classes, lattice, subgroup_classes
from tests.fixtures.oracle_fixtures import load_enriques_87_polarizations, load_e10_fundamental_domain

_ENRIQUES = load_enriques_87_polarizations()
_E10 = load_e10_fundamental_domain()
stage(f"fixtures loaded: {len(_ENRIQUES)} Enriques cases")
# Print actual source/provider/runtime identifiers from launch environment; retain uncertainty where historical logs do not prove a pin.
import subprocess, os
for path,label in [("/work/.git/HEAD","port /work"),("/repos/sage-extensions/.git/HEAD","provider /repos/sage-extensions")]:
    try:
        stage(f"{label} HEAD: {open(path).read().strip()}")
    except Exception as e:
        stage(f"{label} HEAD unavailable inside container: {e} (historical logs do not prove a pin)")
stage(f"runtime env: SAGE_BIN={os.environ.get('SAGE_BIN','?')}, PATH={os.environ.get('PATH','?')[:80]}")

from sage_extensions.catalogue import Involutions

stage("Involutions.I_En, primitive_extension().invariant")
involution = Involutions.I_En
invariant = involution.primitive_extension().invariant
stage(f"invariant: {invariant}")

stage("lattice(_E10['gram']).twist(2).Isom(invariant)")  # `2r` preparses to the integer 2
transport_domain = lattice(_E10["gram"]).twist(2)
stage(f"transport domain: {transport_domain}")
isom_hom = transport_domain.Isom(invariant)
stage("Isom homset built; asking an_element()")
transport = isom_hom.an_element()
stage("transport isometry found")

for case in (_ENRIQUES[2], _ENRIQUES[0]):
    label = f"case_{case['case']}"
    print(f"\n===== {label}: order {case['group_order']}, L/P/F "
          f"{case['line_orbits']}/{case['plane_orbits']}/{case['flag_orbits']} =====", flush=True)
    stage(f"{label} polarized(polarization).coinvariant_extension_subgroup()")
    polarization = invariant.inclusion()(transport(element(transport.domain(), case["face_polarization"])))
    anti_invariant_group = involution.polarized(polarization).coinvariant_extension_subgroup()
    stage(f"{label} coinvariant subgroup built")
    anti_invariant = anti_invariant_group.supergroup().domain()
    stage(f"{label} anti-invariant lattice: rank {anti_invariant.rank()}, signature {anti_invariant.signature_pair()}")
    stage(f"{label} intersection with O_plus")
    group = anti_invariant_group.intersection(anti_invariant.O_plus())
    stage(f"{label} group G_h built")

    stage(f"{label} S1: generator-family realization for G_h (first group_generators read)")
    gens = tuple(group.group_generators())
    stage(f"{label} S1 done: {len(gens)} generators realized")
    stage(f"{label} S2: discriminant-group construction (A_L = N*/N)")
    disc = anti_invariant.discriminant_group()
    stage(f"{label} S2 done: discriminant group {disc}")
    stage(f"{label} S3: discriminant orthogonal group construction O(A_L)")
    target = disc.orthogonal_group()
    stage(f"{label} S3 done: target {target}")
    stage(f"{label} S4: per-generator discriminant_morphism() (each g in G_h)")
    morphisms = []
    for i,g in enumerate(gens):
        stage(f"{label} S4.{i}: discriminant_morphism for generator {i}")
        morphisms.append(g.discriminant_morphism())
    morphisms = tuple(morphisms)
    stage(f"{label} S4 done: {len(morphisms)} morphisms")
    stage(f"{label} S5: finite-character image work (OrthogonalCharacterQuotient._gap_regular_model / finite_character_quotient().image_keys)")
    try:
        q = group.finite_character_quotient()
        stage(f"{label} S5 done: image_keys={q.image_keys().cardinality()} subgroup_keys={q.subgroup_image_keys().cardinality()}")
    except Exception as e:
        stage(f"{label} S5 skipped/failed: {e}")
    stage(f"{label} {len(morphisms)} discriminant morphisms")
    image = target.subgroup_on(morphisms)
    stage(f"{label} asking image.cardinality()")
    order = int(image.cardinality())
    stage(f"{label} image.cardinality() = {order} (published {case['group_order']})")

    for rank in (1, 2):
        stage(f"{label} isotropic_classes(rank {rank})")
        classes = isotropic_classes(anti_invariant, rank)
        stage(f"{label} isotropic_classes(rank {rank}) = {len(classes)} O(L)-orbits")
        stage(f"{label} subgroup_classes(rank {rank})")
        split = subgroup_classes(group, classes)
        stage(f"{label} subgroup_classes(rank {rank}) = {len(split)} (published "
              f"{case['line_orbits'] if rank == 1 else case['plane_orbits']})")
    stage(f"{label} flag_classes")
    flags = flag_classes(anti_invariant)
    stage(f"{label} flag_classes = {len(flags)} O(L)-orbits")
    stage(f"{label} subgroup_classes(flags)")
    split_flags = subgroup_classes(group, flags)
    stage(f"{label} subgroup_classes(flags) = {len(split_flags)} (published {case['flag_orbits']})")

print("\nPROBE_OK", flush=True)
