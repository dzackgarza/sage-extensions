"""#542 round 2: the classes that still refuse a hash, and the completion's one."""
from sage_extensions.all import *  # noqa


def show(label, f):
    try:
        v = f()
        print(f"{label}: {v!r}")
    except Exception as e:
        print(f"{label}: RAISED {type(e).__name__}: {e}")


print("=== completion")
plane = QQ.polynomial_ring(("x", "y"))
x = plane.algebra_generator("x")
completion = plane.adic_completion(plane.ideal(x), precision=3)
image = completion.completion_map()
one = completion.one()
im1 = image(1)
show("type(completion.one())", lambda: type(one).__mro__[:4])
show("hash(completion.one())", lambda: hash(one))
show("type(image(1))", lambda: type(im1).__mro__[:4])
show("hash(image(1))", lambda: hash(im1))
show("image(1) == completion.one()", lambda: im1 == one)
show("one == im1", lambda: one == im1)
show("one._backend()", lambda: one._backend())
show("im1._backend()", lambda: im1._backend())
show("hash(backend one)", lambda: hash(one._backend()))
show("hash(backend im1)", lambda: hash(im1._backend()))
show("one.exact_source_expression()", lambda: one.exact_source_expression())
show("im1.exact_source_expression()", lambda: im1.exact_source_expression())
show("completion.zero() type/hash", lambda: (type(completion.zero()).__name__, hash(completion.zero())))
show("completion.element_class", lambda: completion.element_class)
show("one in FiniteOrderedSets", lambda: FiniteOrderedSets()((one, im1)).cardinality())
show("projection 3 of one", lambda: completion.adic_projection(3)(one))
show("hash(projection3 one)", lambda: hash(completion.adic_projection(3)(one)))
show("hash(projection3 im1)", lambda: hash(completion.adic_projection(3)(im1)))

print("=== CDiv(X) module elements")
line = ProjectiveSpaces(QQ)(1)
divs = CartierDivisorGroups().of_scheme(line)
show("type(divs)", lambda: type(divs).__name__)
show("divs.zero()", lambda: divs.zero())
show("type(divs.zero())", lambda: type(divs.zero()).__mro__[:6])
show("hash(divs.zero())", lambda: hash(divs.zero()))
show("divs.one()", lambda: divs.one())
show("hash(divs.one())", lambda: hash(divs.one()))
show("divs.zero() == divs.zero()", lambda: divs.zero() == divs.zero())

print("=== tensor quotient module elements")
rationals = Modules(ZZ)(QQ)
product = Modules(ZZ).tensor_product((rationals, rationals))
show("type(product)", lambda: type(product).__name__)
show("product.zero()", lambda: product.zero())
show("type(product.zero())", lambda: type(product.zero()).__mro__[:6])
show("hash(product.zero())", lambda: hash(product.zero()))

print("=== a.e. quotient module elements")
ae = Lp(1, RR, RR).quotient_by_null_functions()
show("type(ae)", lambda: type(ae).__name__)
show("ae.zero()", lambda: ae.zero())
show("type(ae.zero())", lambda: type(ae.zero()).__mro__[:6])
show("hash(ae.zero())", lambda: hash(ae.zero()))

print("=== scheme morphisms")
ring = QQ["x"]
xx = ring("x")
spec = ring.affine_spectrum()
show("spec type", lambda: type(spec).__name__)
show("structure morphism", lambda: spec.structure_morphism())
sm = None
try:
    sm = spec.structure_morphism()
except Exception as e:
    print("no structure morphism:", e)
if sm is not None:
    show("hash(structure morphism)", lambda: hash(sm))
show("identity of spec", lambda: spec.identity_morphism())
try:
    ident = spec.identity_morphism()
    show("hash(spec identity)", lambda: hash(ident))
    show("spec identity == rebuilt", lambda: ident == spec.identity_morphism())
except Exception as e:
    print("no identity morphism:", e)
