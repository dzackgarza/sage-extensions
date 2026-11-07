"""Issue #296: micro-costs of the T_Co plane action, warm.

hash(element), element application, point hash, engine product and engine
membership, each measured on a warm loop so no figure carries startup cost.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stamp(message):
    print(f"[{time.monotonic() - START:8.1f}s] {message}", flush=True)


def rate(name, count, call):
    began = time.monotonic()
    value = call()
    elapsed = time.monotonic() - began
    stamp(f"{name}: {count} calls in {elapsed:.3f} s = {elapsed / count * 1e6:.1f} us each")
    return value


base = Lattices(ZZ)("U") + Lattices(ZZ)("U") + (Lattices(ZZ)([[-1]]) ** 7)
lattice = base.twist(2)
labels = tuple(lattice.module_generating_set())
plane = lattice.subobject_on(
    [lattice.module_generator(labels[0]), lattice.module_generator(labels[2])]
)
discriminant_images = tuple(
    lattice.divided_discriminant_class(vector) for vector in plane.embedded_module_generators()
)
form = lattice.discriminant_quadratic_form()
subobject = form.isotropic_subobject(discriminant_images)
group = form.orthogonal_group()
letters = tuple(group.group_generators())
stamp(f"specimen built: |A| = {int(form.cardinality())}, letters = {len(letters)}")

elements = tuple(form.elements())
stamp(f"{len(elements)} elements of A")

rate("hash(element)", len(elements), lambda: [hash(element) for element in elements])
rate("element equality", len(elements), lambda: [element == elements[0] for element in elements])
rate(
    "frozenset of 4 elements",
    len(elements) // 4,
    lambda: [
        frozenset(elements[4 * k : 4 * k + 4]) for k in range(len(elements) // 4)
    ],
)
rate(
    "one letter applied (first 256 elements)",
    256,
    lambda: [letters[0](element) for element in elements[:256]],
)

# A second pass over the same 256 elements: does a memo of the action help?
table = {}


def memoized(letter, element):
    key = (id(letter), element)
    image = table.get(key)
    if image is None:
        image = letter(element)
        table[key] = image
    return image


rate(
    "one letter applied again, memoized by (id, element)",
    256,
    lambda: [memoized(letters[0], element) for element in elements[:256]],
)

# Engine costs, warm.
engine = group._engine_group()
engine_letters = [group._to_engine(letter) for letter in letters]
rate("engine product", 50, lambda: [engine_letters[0] * engine_letters[1] for _ in range(50)])
identity = engine.one()
trivial = engine.subgroup([identity])
rate("engine membership test", 50, lambda: [engine_letters[0] in trivial for _ in range(50)])
rate("engine element order", 20, lambda: [int(engine_letters[0].order()) for _ in range(20)])
rate("engine inverse", 50, lambda: [engine_letters[0].inverse() for _ in range(50)])
rate("engine equality", 50, lambda: [engine_letters[0] == engine_letters[1] for _ in range(50)])
stamp("DONE")
