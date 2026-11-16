"""Probe: the finite-image key of a line row on the lattices the gate can afford.

For each kernel subgroup of a small lattice the probe prints the line row's
size and how many distinct finite-image keys it carries -- the two numbers that
decide whether a keyed lookup is exact on that row -- and, for a line that is
no cusp representative, the cusps the key names against the cusps the witness
search finds.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.orthogonal_quotients import (
    _isotropic_line_class_points,
)

START = time.monotonic()


def key_of(quotient, lattice, term):
    return frozenset(
        quotient.isotropic_class_orbit(_isotropic_line_class_points(lattice, term))
    )


def inspect(label, lattice):
    print(f"== {label}", flush=True)
    stable = lattice.stable_orthogonal_group()
    rows = (("Otilde", stable), ("Otilde+", stable.intersection(lattice.O_plus())))
    for name, subgroup in rows:
        began = time.monotonic()
        quotient = subgroup.finite_character_quotient()
        line_cusps = tuple(subgroup.cusps(1))
        plane_cusps = tuple(subgroup.cusps(2))
        print(
            f" {name}: index {quotient.index()} discriminant {quotient._has_discriminant} "
            f"lines {len(line_cusps)} planes {len(plane_cusps)} "
            f"({time.monotonic() - began:.1f} s)",
            flush=True,
        )
        if quotient._has_discriminant and line_cusps:
            keys = [key_of(quotient, lattice, cusp.representative()) for cusp in line_cusps]
            print(f"  distinct keys over the line row: {len(set(keys))} of {len(keys)}", flush=True)
            for plane_cusp in plane_cusps[:1]:
                plane = plane_cusp.representative()
                labels = tuple(plane.inclusion().domain().module_generating_set())
                domain = plane.inclusion().domain()
                first = plane.inclusion()(domain.module_generator(labels[0]))
                second = plane.inclusion()(domain.module_generator(labels[1]))
                for description, vector in (("generator", first), ("sum", first + second)):
                    line = lattice.primitive_isotropic_subobject(vector)
                    key = key_of(quotient, lattice, line)
                    bucket = [c for c, ck in zip(line_cusps, keys, strict=True) if ck == key]
                    witnessed = [
                        c for c in line_cusps if c.transporter_witness(line) is not None
                    ]
                    print(
                        f"  a plane's {description}: key names {len(bucket)} cusp(s), "
                        f"the witness search finds {len(witnessed)}, "
                        f"the same one {len(bucket) == 1 and len(witnessed) == 1 and bucket[0] is witnessed[0]}",
                        flush=True,
                    )
                    print(
                        f"    separated from every other cusp: "
                        f"{all(quotient.invariant_separates_isotropic_orbits(line, c.representative()) for c in line_cusps if c is not (bucket[0] if bucket else None))}",
                        flush=True,
                    )


inspect("U + U(2) + <-2>", Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]]))
inspect("U + U + <-4>", Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-4]]))
print(f"elapsed {time.monotonic() - START:.1f} s", flush=True)
