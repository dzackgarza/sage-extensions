"""#542 round 2: ring element hashes, the completion's kernel, picard and the chain."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        v = f()
        print(f"{label}: {v!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


print("=== ring elements")
plane = QQ.polynomial_ring(("x", "y"))
x = plane.algebra_generator("x")
y = plane.algebra_generator("y")
for label, elt in (("one", plane.one()), ("zero", plane.zero()), ("2", plane(2)), ("x", x), ("x^2", x**2)):
    show(f"type {label}", lambda e=elt: type(e).__mro__[:4])
    show(f"hash {label}", lambda e=elt: hash(e))

print("=== completion kernel")
completion = plane.adic_completion(plane.ideal(x), precision=3)
image = completion.completion_map()
im1 = image(1)
show("image(1) == plane.one()", lambda: im1 == plane.one())
show("hash(plane.one())", lambda: hash(plane.one()))
show("card of (im1, plane.one())", lambda: FiniteOrderedSets()((im1, plane.one())).cardinality())
cube = image(x**3)
show("image(x^3)", lambda: cube)
show("image(x^3) == completion.zero()", lambda: cube == completion.zero())
show("image(x^3) source", lambda: cube.exact_source_expression())
show("image(x^3) backend", lambda: cube._backend())
show("image(x) source", lambda: image(x).exact_source_expression())
show("source type", lambda: type(image(x).exact_source_expression()))
show("hash image(x)", lambda: hash(image(x)))
show("hash plane(x)", lambda: hash(x))
show("completion precision", lambda: completion.computation_precision())
show("projection type", lambda: type(completion.adic_projection(3)(image(x))))

print("=== picard on P^1")
line = ProjectiveSpaces(QQ)(1)
pic = line.picard_group()
classes = pic.underlying_set()
show("structure sheaf", lambda: line.structure_sheaf())
structural = classes(line.structure_sheaf())
show("class of O", lambda: structural)
show("hash class of O", lambda: hash(structural))
show("O(1)?", lambda: line.O(1))
o1 = line.O(1)
c1 = classes(o1)
show("class of O(1)", lambda: c1)
show("hash class of O(1)", lambda: hash(c1))
squared = pic.add(c1, c1)
show("c1 + c1", lambda: squared)
show("representative of c1+c1", lambda: squared.representative())
show("c1+c1 is c1's sheaf?", lambda: squared.representative() is c1.representative())
show("equal(c1+c1, class(O(2)))", lambda: pic.equal(squared, classes(line.O(2))) if hasattr(line, 'O') else None)
show("ask equal", lambda: ask(pic.equal(squared, classes(line.O(2)))))
show("hash c1+c1", lambda: hash(squared))
show("hash class O(2)", lambda: hash(classes(line.O(2))))

print("=== the chain")
points = Sets.Δ[2]
chain = PartiallyOrderedSets()(points, lambda left, right: int(left) <= int(right))
poset_identity = PartiallyOrderedSets().Mor(chain, chain).identity()
sets_identity = Sets().Mor(chain, chain).identity()
show("poset id == sets id", lambda: poset_identity == sets_identity)
show("sets id == poset id", lambda: sets_identity == poset_identity)
show("hash poset id", lambda: hash(poset_identity))
show("hash sets id", lambda: hash(sets_identity))
show("poset underlying", lambda: poset_identity.underlying_set_morphism())
show("hash poset underlying", lambda: hash(poset_identity.underlying_set_morphism()))
show("poset underlying == sets id", lambda: poset_identity.underlying_set_morphism() == sets_identity)
show("hash poset underlying == hash sets id", lambda: hash(poset_identity.underlying_set_morphism()) == hash(sets_identity))
