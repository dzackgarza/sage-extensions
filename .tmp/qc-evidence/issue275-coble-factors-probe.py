"""Issue #275 on the Coble G-set: the factors, the composites, and what they certify.

The amended acceptance runs the certificate on the actions the provider's own
tests build.  This is the Coble point stabilizer of
``tests/lattices/test_coble_point_stabilizer_generators.sage``: ``|letters| = 4``,
``|orbit| = 496``, family 1984, which the word-by-word realization does not reach
(measured: 1800 s cap).  What is measured here is whether the *factor* route does:
build the 1984 composites from 4 letters and 496 transversals, then
  (a) every composite fixes the point,
  (b) a sample of composites equals the family element at the same position,
  (c) the subgroup the composites generate has the stabilizer's order.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


base = Lattices(ZZ)([[1]]) + Lattices(ZZ)("U") + Lattices(ZZ)("E8").twist(-1)
form = base.twist(2).discriminant_quadratic_form()
group = form.orthogonal_group()
g_set = group.element_action()
stage("g-set built")
one = form.value_module()(1)
point = next(element for element in form.elements() if form.q(element) == one)
stage("point with q(c)=1 found")

letters, transversals = g_set.orbit_schreier_factors(point)
stage(f"|letters|={len(letters)} |orbit|={len(transversals)}")

orbit, words, augmentation = g_set._orbit_of(point)
points = tuple(orbit)
positions = {candidate: index for index, candidate in enumerate(points)}
stage(f"orbit order read: {len(points)} points, product {len(points) * len(letters)}")

rebuilt = []
for index, candidate in enumerate(points):
    for letter in letters:
        target = positions[g_set.act(letter, candidate)]
        rebuilt.append((~transversals[target]) * letter * transversals[index])
rebuilt = tuple(rebuilt)
stage(f"composites rebuilt: {len(rebuilt)}")

fixing = all(composite(point) == point for composite in rebuilt)
stage(f"every composite fixes the point: {fixing}")
print(f"CERT_POINT {fixing}", flush=True)

preserving = all(composite.validate_form_preservation(check=True) is None for composite in rebuilt[:64])
print(f"CERT_FORM first 64: {preserving}", flush=True)

# (b) elementwise against the family at a sample of positions
morphism = g_set.orbit_schreier_morphism(point)
stage("schreier morphism built")
generators = tuple(morphism.domain().group_generators())
stage(f"family words: {len(generators)}")
sample = tuple(range(0, min(len(generators), len(rebuilt)), max(1, len(rebuilt) // 8)))
agreements = []
for position in sample:
    began = time.monotonic()
    family_element = morphism(generators[position])
    agreements.append((position, rebuilt[position] == family_element))
    print(f"  sample {position}: equal {agreements[-1][1]} ({time.monotonic() - began:.1f}s)", flush=True)
stage(f"sample agreement: {agreements}")
print(f"CERT_SAMPLE {all(flag for _position, flag in agreements)} over {len(agreements)} positions", flush=True)

# (c) the order certificate
expected = group.order() // group.orbit_cardinality(point)
began = time.monotonic()
actual = group.subgroup_on(rebuilt).cardinality()
stage(f"subgroup order {actual} (expected {expected}) in {time.monotonic() - began:.1f}s")
print(f"CERT_ORDER {actual == expected}", flush=True)
print("PROBE_DONE", flush=True)
