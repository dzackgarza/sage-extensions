r"""#603: where one pointwise membership test spends its time, on the rank-five specimen.

The walk over `O(K_I)/M_I` costs one membership test per (coset, generator)
pair.  This measures the three parts of one test -- the rational Witt lift, the
kernel's parameter lattice, and the correction search over the box -- and prints
how many box representatives a test consumes before it answers.
"""

import cProfile
import io
import pstats
import time

import sage_extensions.categories.lattices as lattices_module
from sage_extensions.all import Lattices, ZZ

LATTICE = [
    [0, 2, 0, 0, 0],
    [2, 0, 1, 0, 0],
    [0, 1, 0, 2, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, -2],
]

START = time.perf_counter()


def stamp(label, value=None):
    print(f"[{time.perf_counter() - START:9.3f}s] {label}")
    return value


def clock(label, function):
    start = time.perf_counter()
    value = function()
    print(f"[{time.perf_counter() - start:9.3f}s] {label}")
    return value


lattice = Lattices(ZZ)(LATTICE)
labels = tuple(lattice.module_generating_set())
vector = lattice.module_generator(labels[0])
subobject = lattice.primitive_isotropic_subobject(vector)
reduction = subobject.isotropic_reduction()
quotient = reduction.quotient_lattice()
generators = tuple(quotient.O().group_generators())
print("rank:", lattice.module_rank(), "div:", vector.div(), "generators:", len(generators))
stamp("specimen and generators")

parameters = clock("kernel parameter vectors (first call)", reduction._pointwise_kernel_parameter_vectors)
print("   parameters:", len(parameters))

rational = {}
for index, generator in enumerate(generators):
    extension = clock(f"rational lift [{index}]", lambda: reduction._rational_pointwise_levi_lift(generator))
    print("   denominator:", extension[1])

original = lattices_module._representatives_of_the_box
tries = {"count": 0}


def reporting(counts):
    order = 1
    for count in counts:
        order *= int(count)
    print("   box order:", order, "counts:", [int(count) for count in counts])
    for representative in original(counts):
        tries["count"] += 1
        yield representative


lattices_module._representatives_of_the_box = reporting

for index, generator in enumerate(generators):
    tries["count"] = 0
    lift = clock(f"corrected lift [{index}]", lambda: reduction._corrected_pointwise_levi_lift(generator))
    print("   representatives tried:", tries["count"], "lift is None:", lift is None)

liftable = [index for index, generator in enumerate(generators) if reduction.pointwise_levi_lift(generator) is not None]
print("liftable generators:", liftable)

tries["count"] = 0
clock("one full public membership test [0]", lambda: reduction.pointwise_levi_lift(generators[0]))

print("---- profile of the non-liftable correction ----")
profile = cProfile.Profile()
profile.enable()
reduction._corrected_pointwise_levi_lift(generators[0])
profile.disable()
stream = io.StringIO()
pstats.Stats(profile, stream=stream).sort_stats("cumulative").print_stats(24)
print(stream.getvalue())

stamp("done")
