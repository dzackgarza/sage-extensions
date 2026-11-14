"""Embedded staged measurement: the atomized stage-B hypotheses at case_3.

Direct-gram measurements now on record (4edd9bed): ambient
`O(N).group_generators()` = 407 s on a construction-free model;
O_plus + spinor morphism 0.1 s; per-generator character image ~0.28 s each.
This probe measures the SAME atoms inside the Enriques process itself,
so ambient-work and target-work inside stage B are separated rather than
inferred.  Every atom prints BEFORE it starts; a cap leaves ordered
attribution; each number is the answer, never a cut.  One heavy job.

Atoms (each names its hypothesis):
  A1 rebuild G_h (span known: 189 - 207 s at 4b8eb75+ / fd5ab11+)
  A2 enumerate the ambient generators of O(N), timed PER GENERATOR
     (h-ambient: selection cost inside the Enriques process)
  A3 per-generator character image construction, timed PER GENERATOR
     (h-pergen: the 221-generator, ~0.28 s each line of stage B)
  A4 joint image quotient infrastructure built UNDER THE HOOD:
     `group.finite_character_quotient()` only (no `index()`), timed
     (h-quotient-infrastructure: _gap_product/_image_section/_gap_subgroup,
     i.e. pre-chains)
  A5 `quotient.index()` — measured GAP orders of Q and S and their
     division (h-no-order-estimate: this was never seen complete)
"""
import time

START = time.monotonic()


def stage(label):
    print(f"[t={time.monotonic() - START:8.1f}s] {label}", flush=True)


stage("imports")
from tests.acceptance.consumer import element, lattice
from tests.fixtures.oracle_fixtures import load_enriques_87_polarizations, load_e10_fundamental_domain
_ENRIQUES = load_enriques_87_polarizations()
_E10 = load_e10_fundamental_domain()
case = _ENRIQUES[2]
stage(f"fixtures loaded: case_{case['case']} order {case['group_order']}, L/P/F "
      f"{case['line_orbits']}/{case['plane_orbits']}/{case['flag_orbits']}")


def resolved_head(git_dir):
    head = open(git_dir + "/.git/HEAD").read().strip()
    if head.startswith("ref:"):
        ref = head.split(None, 1)[1].strip()
        host = git_dir
        import os
        if git_dir.endswith("/.git") or git_dir + "/.git" in git_dir:
            pass
        try:
            return open(git_dir + "/" + ref).read().strip()
        except OSError:
            import subprocess
            try:
                return subprocess.check_output(["git", "-C", git_dir, "rev-parse", ref]).decode().strip()
            except Exception:
                raise
    return head


try:
    stage(f"port /work HEAD: {resolved_head('/work/.git')}")
    stage(f"provider /repos/sage-extensions HEAD: {resolved_head('/repos/sage-extensions/.git')}")
except Exception as e:
    stage(f"HEAD resolution unavailable: {e}; use host-side pins in the launch record")

from sage_extensions.catalogue import Involutions

stage("A1: rebuild case_3 involution, invariant, transport")
involution = Involutions.I_En
invariant = involution.primitive_extension().invariant
transport = lattice(_E10["gram"]).twist(2).Isom(invariant).an_element()
stage(f"A1: polarization transport, coinvariant_extension_subgroup()")
polarization = invariant.inclusion()(transport(element(transport.domain(), case["face_polarization"])))
anti_invariant_group = involution.polarized(polarization).coinvariant_extension_subgroup()
stage("A1: coinvariant subgroup built")
anti_invariant = anti_invariant_group.supergroup().domain()
group = anti_invariant_group.intersection(anti_invariant.O_plus())
stage("A1: group G_h constructed (construction only)")

stage("A2: ambient O(N) generating family, named per generator")
G = anti_invariant.O()
count = 0
for i, g in enumerate(G.group_generators()):
    count += 1
    stage(f"A2.{count}: ambient generator {count} (materialized)")
stage(f"A2: ambient family complete: {count} generators (span measured)")

stage("A3: per-generator character-image equipments, timed")
import sys
spinor_morphism = anti_invariant.O_plus().preimage_morphism()
for i, g in enumerate(G.group_generators()):
    stage(f"A3.{i+1}/{count}: discriminant_morphism()")
    morphism = g.discriminant_morphism()
    sign = spinor_morphism(g)
    stage(f"A3.{i+1}/{count}: spinor done (is_one={sign.is_one()})")
stage("A3: per-generator character images complete")

stage("A4: quotient infrastructure (finite_character_quotient object only)")
quotient = group.finite_character_quotient()
stage("A4: quotient object constructed (no order, no index yet)")
stage("A4b: joint character image check — product factors, model order")
image_space = quotient.image_space()
stage(f"A4b: factors in the joint character image: {image_space}")

stage("A5: quotient.index() — GAP orders of joint Q and S, then division")
index = quotient.index()
stage(f"A5: quotient.index() = {index}")
stage("A5: index obligation answered")

print("PROBE_OK", flush=True)
