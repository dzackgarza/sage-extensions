r"""Probe: what containment of a fixed Mor category answers, on this tree.

The Mor family's record is a record of pairs; a fixed Mor is in a family when it
is the object that family selected for its endpoints.  These are the readings of
one category of sets, written as comparisons so they print on either tree.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

points = finite_ordered_set(("a", "b"))
Mor = FiniteSets().category_packet().Mors().Of(points, points)
end = FiniteSets().category_packet().Ends().Of(points)
monos = Sets().category_packet().Monos().Of(points, points)
epis = Sets().category_packet().Epis().Of(points, points)

print(f"[probe] Of twice is one object: {Mor is FiniteSets().category_packet().Mors().Of(points, points)}", flush=True)
print(f"[probe] the end of a point is that Mor: {end is Mor}", flush=True)
print(f"[probe] the arrows of the monos are that Mor: {monos.arrow_set() is Mor}", flush=True)
print(f"[probe] Mor in MorCategories(): {Mor in MorCategories()}", flush=True)
print(f"[probe] the family contains its own Mor: {Mor in FiniteSets().category_packet().Mors()}", flush=True)
constant = Mor(lambda point: "a")
print(f"[probe] a constant is in Mor, monos, epis: {(constant in Mor, constant in monos, constant in epis)}", flush=True)
swap = Mor(lambda point: "b" if point == "a" else "a")
print(f"[probe] a swap is in monos and epis: {(swap in monos, swap in epis)}", flush=True)
print(f"[probe] the end of the swap is that Mor: {Mor.identity_2(swap) * Mor.identity_2(swap) == Mor.identity_2(swap)}", flush=True)
