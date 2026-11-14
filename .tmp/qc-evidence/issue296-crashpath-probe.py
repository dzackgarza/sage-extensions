"""Issue #296: the crash path, isolated -- multiplying owned automorphisms of A_{T_Co}.

The recorded failure (.tmp/issue296_tco_test5.log) died with SIGSEGV inside
``generator * transversals[position]`` for the plane orbit of ``A_{T_Co}``:

  torsion_form_modules.__mul__ -> _from_engine -> _transported_map -> _normalized_map
  -> sage.groups.fqf_orthogonal._act_ -> abelian_aut.matrix -> abelian_group_gap.exponents

This probe multiplies owned automorphisms of the same form directly, one product per
step, and prints the rate, so the cost of the paths the walk took is measured even
when the crash itself does not recur.
"""
import time

from sage_extensions.all import *  # noqa: F401,F403

START = time.monotonic()


def stamp(message):
    print(f"[{time.monotonic() - START:8.1f}s] {message}", flush=True)


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

engine = group._engine_group()
engine_letters = [group._to_engine(letter) for letter in letters]
began = time.monotonic()
for _ in range(20):
    engine_letters[0] * engine_letters[1]
stamp(f"20 engine products: {time.monotonic() - began:.3f} s")

began = time.monotonic()
product = letters[0] * letters[1]
stamp(f"first owned product (gen * gen): {time.monotonic() - began:.2f} s")
began = time.monotonic()
product = letters[0] * letters[1]
stamp(f"second owned product: {time.monotonic() - began:.2f} s")

# The walk of the recorded failure: one owned product per (orbit point, letter).
count = 0
began = time.monotonic()
seed = frozenset(subobject.inclusion()(element) for element in subobject.elements())
frontier = [seed]
seen = {seed}
steps = 0
while frontier and steps < 200:
    current = frontier.pop()
    for letter in letters:
        image = frozenset(letter(element) for element in current)
        steps += 1
        if image not in seen:
            seen.add(image)
            frontier.append(image)
        count += 1
        if count % 50 == 0:
            stamp(f"{count} image applications, |orbit| >= {len(seen)}, {time.monotonic() - began:.1f} s")
stamp(f"360-degree check: {count} images, |orbit| >= {len(seen)} in {time.monotonic() - began:.1f} s")
stamp("DONE without a crash")
