r"""Probe: which public answers depend on the route that reached a G-set (#517)."""
from sage_extensions.all import *


def say(*parts):
    print("PROBE", *parts, flush=True)


def describe(tag, g_set, points):
    for point in points:
        orbit, section = g_set.orbit_transversal_words(point)
        say(tag, "point", point, "orbit_card", orbit.point_set().cardinality(),
            "orbit_points", tuple(orbit), "is_this_set", orbit is g_set,
            "section", tuple(section(candidate) for candidate in orbit))
        letters, transversals = g_set.orbit_schreier_factors(point)
        say(tag, "point", point, "letters", letters, "transversals", transversals)
        morphism = g_set.orbit_schreier_morphism(point)
        say(tag, "point", point, "family", tuple(morphism(g) for g in morphism.domain().group_generators()))
        say(tag, "point", point, "perms", g_set.orbit_generator_permutations(point))


group = Groups.C(3)
one = group.one()

a = FiniteGSets(group).from_finite_orbits((one,), lambda g, x: g * x)
say("A card", a.cardinality())
describe("A", a, (one,))

c_multi = lambda g, x: x if x == 5 else g * x
b = FiniteGSets(group).from_finite_orbits((one, 5), c_multi)
say("B card", b.cardinality())
describe("B one-first", b, (one, 5))

b2 = FiniteGSets(group).from_finite_orbits((one, 5), c_multi)
describe("B five-first", b2, (5, one))

c_line = FiniteGSets(group).from_finite_orbits((5, one), c_multi)
describe("C five-seed-first", c_line, (5, one))

s3 = Groups.S(3)
transpositions = (s3((1, 2)), s3((1, 3)), s3((2, 3)))
d = FiniteGSets(s3).from_finite_orbits((transpositions[0],), lambda g, x: g * x * ~g)
say("D card", d.cardinality())
describe("D", d, transpositions)

subgroup = s3.subgroup((s3((1, 2)),))
cosets = s3.left_cosets(subgroup)
full = cosets.schreier_generating_morphism()
trimmed = cosets.schreier_generating_morphism(drop_trivial=True)
say("E full", tuple(full(g) for g in full.domain().group_generators()))
say("E trimmed", tuple(trimmed(g) for g in trimmed.domain().group_generators()))
say("E again", cosets.schreier_generating_morphism().domain().group_generators().cardinality())
say("E same object", cosets.schreier_generating_morphism() is cosets.schreier_generating_morphism())

calls = []


def counted(g, x):
    calls.append((g, x))
    return g * x


e = FiniteGSets(group).from_finite_orbits((one,), counted)
say("F action calls after the sweep", calls.__len__())
describe("F", e, (one,))
say("F action calls after the orbit question", calls.__len__())
