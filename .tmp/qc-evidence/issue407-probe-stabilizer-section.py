import time
t0 = time.monotonic()
def mark(label):
    print(f"[{time.monotonic()-t0:8.1f}s] {label}", flush=True)
from sage_extensions.all import *
import sage_extensions.categories.orthogonal_quotients as oq
Section = oq._GapWordSection
orig_init, orig_perm, orig_gap = Section.__init__, Section.permutation_group, Section.gap_group
def init(self, gap_generators, parent=None):
    mark(f"_GapWordSection(gens={len(gap_generators)}, parent={'given' if parent is not None else 'NONE'})")
    return orig_init(self, gap_generators, parent=parent)
def perm(self):
    mark("permutation_group -> entering")
    value = orig_perm(self)
    mark("permutation_group <- returned")
    return value
def gg(self):
    mark(f"gap_group -> entering (parent {'given' if self._parent is not None else 'NONE'})")
    value = orig_gap(self)
    mark("gap_group <- returned")
    return value
Section.__init__, Section.permutation_group, Section.gap_group = init, perm, gg
lattice = NamedLattices.TEn
group = lattice.O()
e = lattice.module_generator(next(iter(lattice.module_generating_set())))
line = lattice.primitive_isotropic_subobject(e)
stabilizer = group.stabilizer(line, action="setwise")
mark("stabilizer built; calling group_generators()")
generators = tuple(stabilizer.group_generators())
mark(f"group_generators -> {len(generators)}")
print("PROBE OK", flush=True)
