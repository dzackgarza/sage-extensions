"""Constructive validation of the Enriques downstream obligations at 4a73ccd.

Hypothesis (demonstrated, not time-extended): with the generated character
model the image and orbit obligations of case_3 are computable WITHOUT
materializing the selected Schreier family of |generator words| ~
2*|gens(O(N))|*[O+(N):Gamma_h] (~2*10^7), which is the S1 wall measured at
38523e1/dbb1eafa (620 s cap, 5416 MiB).  Every stage prints BEFORE it starts,
so a cap retains ordered attribution; each stage asks a question whose answer
is published (image order 92897280; orbit counts 5/10/19).  The S1
per-generator enumeration is NOT run: that obligation stays open explicitly,
and nothing in this file substitutes for it.

Stages:
  A  rebuild G_h (identical construction; expected ~210 s)
  B  exact index of the retained character quotient (GAP orders only)
  C  the image obligation: group.discriminant_image().cardinality()
  D  the orbit obligations: _counts(group)  (lines, planes, flags)
"""
import time

START = time.monotonic()


def stage(label):
    print(f"[t={time.monotonic() - START:8.1f}s] {label}", flush=True)


stage("imports")
from tests.acceptance.consumer import element, lattice, subgroup_classes, isotropic_classes, flag_classes
from tests.fixtures.oracle_fixtures import load_enriques_87_polarizations, load_e10_fundamental_domain

_ENRIQUES = load_enriques_87_polarizations()
_E10 = load_e10_fundamental_domain()
case = _ENRIQUES[2]
stage(f"fixtures loaded; case_{case['case']}: order {case['group_order']}, L/P/F "
      f"{case['line_orbits']}/{case['plane_orbits']}/{case['flag_orbits']}")


def resolved_head(git_dir):
    head = open(git_dir + "/.git/HEAD").read().strip()
    if head.startswith("ref:"):
        ref = head.split(None, 1)[1].strip()
        try:
            return open(git_dir + "/" + ref).read().strip()
        except OSError:
            for line in open(git_dir + "/.git/packed-refs"):
                if line.strip().endswith(ref):
                    return line.split(None, 1)[0].strip()
    return head


try:
    stage(f"port /work HEAD: {resolved_head('/work')}")
    stage(f"provider /repos/sage-extensions HEAD: {resolved_head('/repos/sage-extensions')}")
except Exception as e:
    stage(f"HEAD resolution failed: {e}")

from sage_extensions.catalogue import Involutions

stage("A: involution, invariant, transport")
involution = Involutions.I_En
invariant = involution.primitive_extension().invariant
transport = lattice(_E10["gram"]).twist(2).Isom(invariant).an_element()
polarization = invariant.inclusion()(transport(element(transport.domain(), case["face_polarization"])))
stage("A: coinvariant_extension_subgroup()")
anti_invariant_group = involution.polarized(polarization).coinvariant_extension_subgroup()
stage("A: coinvariant subgroup built")
anti_invariant = anti_invariant_group.supergroup().domain()
stage(f"A: anti-invariant lattice rank {anti_invariant.rank()}, signature {anti_invariant.signature_pair()}")
group = anti_invariant_group.intersection(anti_invariant.O_plus())
stage("A: group G_h built (construction only)")

stage("B: exact index of the retained character quotient")
quotient = group.finite_character_quotient()
index = quotient.index()
stage(f"B: [O^+(N)-retained quotient index] = {index}")

stage("C: the image obligation: group.discriminant_image().cardinality()")
image = group.discriminant_image()
order = int(image.cardinality())
stage(f"C: |rho(Gamma_h)| = {order}  (published {case['group_order']})")
assert order == case["group_order"], "the image order disagrees with the published value"

print("\n===== image obligation: case_3 ACCEPTED =====", flush=True)

stage("D: orbit obligations: isotropic_classes(N, 1)")
lines = isotropic_classes(anti_invariant, 1)
stage(f"D: {len(lines)} O(N)-orbits of lines")
stage("D: subgroup_classes(G_h, lines)")
split_lines = subgroup_classes(group, lines)
stage(f"D: lines split into {len(split_lines)}  (published {case['line_orbits']})")
assert len(split_lines) == case["line_orbits"]

stage("D: isotropic_classes(N, 2)")
planes = isotropic_classes(anti_invariant, 2)
stage(f"D: {len(planes)} O(N)-orbits of planes")
stage("D: subgroup_classes(G_h, planes)")
split_planes = subgroup_classes(group, planes)
stage(f"D: planes split into {len(split_planes)}  (published {case['plane_orbits']})")
assert len(split_planes) == case["plane_orbits"]

stage("D: flag_classes(N)")
flags = flag_classes(anti_invariant)
stage(f"D: {len(flags)} O(N)-orbits of flags")
stage("D: subgroup_classes(G_h, flags)")
split_flags = subgroup_classes(group, flags)
stage(f"D: flags split into {len(split_flags)}  (published {case['flag_orbits']})")
assert len(split_flags) == case["flag_orbits"]

print("\n===== orbit obligations: case_3 ACCEPTED =====", flush=True)
print("PROBE_OK", flush=True)
