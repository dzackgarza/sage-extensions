import time
t0 = time.monotonic()
def mark(label):
    print(f"[{time.monotonic()-t0:8.1f}s] {label}", flush=True)
from sage_extensions.all import *
mark("import sage_extensions.all")
lattice = NamedLattices.TEn
mark("NamedLattices.TEn")
group = lattice.O()
mark(f"lattice.O() -> {group!r}")
e = lattice.module_generator(next(iter(lattice.module_generating_set())))
mark("generator e")
line = lattice.primitive_isotropic_subobject(e)
mark(f"primitive_isotropic_subobject -> {line!r}")
stabilizer = group.stabilizer(line, action="setwise")
mark(f"stabilizer -> {stabilizer!r}")
generators = tuple(stabilizer.group_generators())
mark(f"group_generators -> {len(generators)} generators")
generated = group.subgroup(generators)
mark(f"subgroup -> {generated!r}")
print("PROBE OK", flush=True)
