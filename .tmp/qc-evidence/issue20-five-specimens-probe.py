"""Issue #20's acceptance, measured at the current tree: five specimens.

Acceptance: a Sage-pickle round trip of a genuine stabilizer-family element
returns an equal element whose parent is the same owned parent, with a
regression over the owned parent graph (ring parents, native module bases,
order bases).  The five specimens below are that graph, one element each.
"""
import pickle
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stage(label):
    print(f"[{time.monotonic() - START:8.1f}s] {label}", flush=True)


def round_trip(name, element):
    try:
        payload = pickle.dumps(element)
    except Exception as error:
        print(f"-- {name}: PICKLE RAISED {type(error).__name__}: {error}", flush=True)
        return
    try:
        restored = pickle.loads(payload)
    except Exception as error:
        print(f"-- {name}: UNPICKLE RAISED {type(error).__name__}: {error}", flush=True)
        return
    try:
        equal = restored == element
    except Exception as error:
        equal = f"comparison raised {type(error).__name__}"
    try:
        same_parent = restored.parent() is element.parent()
    except Exception as error:
        same_parent = f"parent read raised {type(error).__name__}"
    print(f"-- {name}: equal {equal} | same parent {same_parent} | bytes {len(payload)}", flush=True)


def specimen(name, build):
    try:
        round_trip(name, build())
    except Exception as error:
        print(f"-- {name}: construction raised {type(error).__name__}: {error}", flush=True)


specimen("ZZ element", lambda: ZZ(7))
specimen("QQ element", lambda: QQ(3) / QQ(4))

field = QuadraticField(2, "a")
order = field.maximal_order()
stage(f"number field {field} and its maximal order {order}")
labels = tuple(field.module_generating_set())
print("field module labels:", labels, flush=True)
generator_label = next(label for label in labels if field.module_generator(label) != field.one())
field_generator = field.module_generator(generator_label)
print("field primitive element from the module basis:", field_generator, flush=True)
specimen("number field order element", lambda: order(field_generator))

specimen("lattice element", lambda: Lattices(ZZ)([[2, 1], [1, 2]]).module_generator(
    next(iter(Lattices(ZZ)([[2, 1], [1, 2]]).module_generating_set()))
))

plane = Lattices(QQ)("U")
plane_labels = tuple(plane.module_generating_set())
plane_basis = [plane.module_generator(label) for label in plane_labels]
orthogonal = plane.Aut()
swap = orthogonal(lambda label: plane_basis[1 - int(label)])
stage("isometry built")
specimen("isometry element", lambda: swap)

rational_space = Modules(QQ).restriction_of_scalars(ZZ.Mor(QQ)(lambda n: QQ(n)))(plane)
lattice = rational_space.subobject_on([rational_space(vector) for vector in plane_basis])
action = IntegralStructureAction(orthogonal.subgroup((swap,)), lattice.inclusion())
family = tuple(action.stabilizer().group_generators())
stage(f"stabilizer family: {len(family)} elements")
specimen("stabilizer-family element", lambda: family[0])
print("DONE", flush=True)
