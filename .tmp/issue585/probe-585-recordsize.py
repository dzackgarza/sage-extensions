r"""Probe: what one record of the class route's relation costs, measured on a lattice with cusps.

The relation the class route returns is one :class:`DividedClassCuspIncidence` per
endpoint pair.  The per-plane walk retains nothing, so the relation is the one
term of the row that grows with the plane count: this prices it by holding
200000 copies of a real record -- the two cusps and the class datum are shared,
as they are in a row, where every edge of one line vertex holds that vertex --
and reading the RSS delta.
"""

import os
import sys
import time

START = time.monotonic()
COPIES = int(os.environ.get("PROBE_COPIES", "200000"))


def rss_mib():
    with open(f"/proc/{os.getpid()}/status") as handle:
        for line in handle:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024
    return float("nan")


from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordinal_set,
    finite_ordered_set,
)

lattice = (
    Lattices(ZZ)("U")
    + Lattices(ZZ)(((0, 2), (2, 0)))
    + Lattices(ZZ)(((-2,),))
)
subgroup = lattice.stable_orthogonal_group()
print(f"[probe] {lattice}; line cusps {subgroup.cusps(1).cardinality()},"
      f" plane cusps {subgroup.cusps(2).cardinality()}", flush=True)
relation = subgroup.tits_building_incidence_by_divided_classes()
print(f"[probe] the class route's relation: {relation.cardinality()} edges", flush=True)
records = tuple(relation)
certified = subgroup.tits_building_incidence()
print(f"[probe] the certificate route's relation: {certified.cardinality()} edges", flush=True)
for record in records:
    print(f"    {record}", flush=True)

template = records[0]
# one comparison of two records with different endpoints: what the literal
# ingress pays per pair of points whose hashes collide
distinct = [(first, second) for first in records for second in records if first is not second]
if distinct:
    first, second = distinct[0]
    mark = time.monotonic()
    for _ in range(100):
        assert not (first == second)
    one_comparison = (time.monotonic() - mark) / 100
    print(f"[probe] one comparison of two distinct edges: {1e6 * one_comparison:.1f} us", flush=True)

mark = time.monotonic()
literal = finite_ordered_set(tuple(records))
literal_seconds = time.monotonic() - mark
mark = time.monotonic()
positioned = FiniteOrderedSets().from_indexed(
    finite_ordinal_set(len(records)),
    lambda position: records[int(position)],
    index_of=lambda point: {id(record): index for index, record in enumerate(records)}.get(id(point)),
)
indexed_seconds = time.monotonic() - mark
print(
    f"[probe] the ingress on {len(records)} edges: literal {1e3 * literal_seconds:.3f} ms,"
    f" supplied inverse {1e3 * indexed_seconds:.3f} ms;"
    f" both cardinalities {literal.cardinality()} and {positioned.cardinality()}",
    flush=True,
)

before = rss_mib()
held = [
    DividedClassCuspIncidence(
        template.subgroup(),
        template.line_cusp(),
        template.plane_cusp(),
        template.divided_classes(),
    )
    for _ in range(COPIES)
]
after = rss_mib()
print(
    f"[probe] RESULT copies={COPIES} bytes_a_record={1024 * (after - before) / COPIES:.1f}"
    f" rss_before={before:.1f} MiB rss_after={after:.1f} MiB"
    f" wall={time.monotonic() - START:.1f} s",
    flush=True,
)
