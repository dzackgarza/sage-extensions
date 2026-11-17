r"""Probe: what a record keyed on a subobject's carried name would answer.

The candidate repair "re-key the registries on something the object carries"
replaces an address with a datum.  A datum is not an object: two subobjects of
one span are two objects naming one sublattice, so a record keyed on the span
answers a question about the second with the Mor of the first -- and a Mor's
identity is its endpoints, which is what its consumers read.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.isotropic_orbits import _span_key
from sage_extensions.categories.lattices import (
    _lattice_subobject_spanning,
    _primitive_isotropic_subobject,
)

lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
e1, _f1, _e2, f2 = lattice.module_generators()
first = lattice.primitive_isotropic_subobject(e1, f2)
span = _span_key(first)
for construction in (_lattice_subobject_spanning, _primitive_isotropic_subobject):
    construction.cache.clear()
second = lattice.primitive_isotropic_subobject(e1, f2)
print(
    f"[probe] two objects, one span: {_span_key(second) == span}"
    f", the same object: {second is first}",
    flush=True,
)

family = first.module_category().Mor(first, first).mor_family()
mor_of_first = family.Of(first, first)
mor_of_second = family.Of(second, second)
print(
    f"[probe] each object's Mor names its own endpoint:"
    f" {mor_of_first.domain_object() is first}, {mor_of_second.domain_object() is second}",
    flush=True,
)
print(f"[probe] and the two Mors are distinct: {mor_of_first is not mor_of_second}", flush=True)
record = {span: mor_of_first}
answered = record[_span_key(second)]
print(
    f"[probe] a span-keyed record answers the second question with a Mor of the first:"
    f" {answered.domain_object() is first}, of the second: {answered.domain_object() is second}",
    flush=True,
)
