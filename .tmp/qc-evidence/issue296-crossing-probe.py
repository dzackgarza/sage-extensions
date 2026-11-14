"""Issue #296: the enumeration and crossing costs the plane walk would rely on."""
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
stamp("specimen built")

elements = form.elements()
stamp(f"elements() is {type(elements).__name__} in {elements.category()}")
materialized = rate("tuple(elements())", 1, lambda: tuple(elements))
stamp(f"|A| = {len(materialized)}")
rate("index the materialized tuple", 512, lambda: [materialized[k % 2048] for k in range(512)])
rate("index elements() itself", 64, lambda: [elements[k % 2048] for k in range(64)])

ranking = elements.ranking_map()
stamp(f"ranking_map is {type(ranking).__name__}")
rate("ranking(element)", 512, lambda: [ranking(element) for element in materialized[:512]])
inverse = ranking.inverse()
rate("ranking inverse(rank)", 32, lambda: [inverse(k) for k in range(32)])
stamp(f"inverse(3) is {inverse(3)}")

element = materialized[5]
rate("one letter applied, same element", 32, lambda: [letters[0](element) for _ in range(32)])
image = letters[0](element)
rate("element equality, equal copies", 32, lambda: [image == letters[0](element) for _ in range(8)])

engine = group._engine_group()
engine_letters = [group._to_engine(letter) for letter in letters]
rate("_from_engine (one crossing)", 3, lambda: [group._from_engine(engine_letters[0]) for _ in range(3)])
stamp(f"engine subgroup order: {int(engine.subgroup(engine_letters).order())}")
stamp(f"|O(q)| = {int(group.cardinality())}")
stamp("DONE")
