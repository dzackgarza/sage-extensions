"""Issue #275 on a plain finite group: S(3)'s natural G-set, factors and composites."""
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


group = Groups.S(3)
g_set = group.natural_g_set()
points = tuple(g_set)
stage(f"g-set points: {points}")
point = points[0]
letters, transversals = g_set.orbit_schreier_factors(point)
stage(f"|letters|={len(letters)} |orbit|={len(transversals)}")
print("letters:", [str(letter) for letter in letters], flush=True)
print("transversals:", [str(t) for t in transversals], flush=True)

positions = {candidate: index for index, candidate in enumerate(points)}
rebuilt = tuple(
    (~transversals[positions[g_set.act(letter, candidate)]]) * letter * transversals[index]
    for index, candidate in enumerate(points)
    for letter in letters
)
stage(f"composites rebuilt: {len(rebuilt)}")

stabilizer = g_set.stabilizer(point)
stage(f"stabilizer built: {stabilizer}")
family = tuple(stabilizer.group_generators())
stage(f"|family| = {len(family)}")
print("family:", [str(element) for element in family], flush=True)
print(f"KNOWS THE LAW {rebuilt == family}", flush=True)

morphism = g_set.orbit_schreier_morphism(point)
generators = tuple(morphism.domain().group_generators())
stage(f"family words: {len(generators)}")
realized = tuple(morphism(word) for word in generators)
print(f"morphism images equal group_generators: {realized == family}", flush=True)
print(f"composites equal morphism images: {rebuilt == realized}", flush=True)
print("PROBE_DONE", flush=True)
