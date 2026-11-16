from sage_extensions.all import *
from sage_extensions.categories.modules.pure.modules import (
    Modules, LinearMorModules, InternalMorModules,
)

ring = ZZ
lattice = ring.free_module(2)
N = lattice.dual_module()
NN = N.dual_module()

print("regular module:", ring.regular_module(), "| is ring?", ring.regular_module() is ring)
print("N target module is regular?", N.target_module() is ring.regular_module())
print("N source module is lattice?", N.source_module() is lattice)
print("N in LinearMorModules?", N in LinearMorModules(ring))
print("N in InternalMorModules?", N in InternalMorModules(ring))
print("lattice in LinearMorModules?", lattice in LinearMorModules(ring))
print("lattice in InternalMorModules?", lattice in InternalMorModules(ring))
print("NN in LinearMorModules?", NN in LinearMorModules(ring))

# a morphism module with another codomain must not be mistaken for a dual
endomorphisms = Modules(ring).Mor(lattice, lattice)
print("End(M) target is regular?", endomorphisms.target_module() is ring.regular_module())
print("End(M) source is lattice?", endomorphisms.source_module() is lattice)
print("End(M) in LinearMorModules?", endomorphisms in LinearMorModules(ring))

# evaluation identification, checked on the bases
biduality = Modules(ring).dualization().double_dual_morphism(lattice)
double_dual = lattice.dual_module().dual_module()
print("biduality codomain is lattice.dual_module().dual_module()?", biduality.codomain() is double_dual)
print("labels lattice / N / NN:", tuple(lattice.module_generating_set()), tuple(N.module_generating_set()), tuple(NN.module_generating_set()))
for label in lattice.module_generating_set():
    print("  label", label,
          "| biduality(e) is double dual generator?", biduality(lattice.module_generator(label)) is double_dual.module_generator(label),
          "| equal?", biduality(lattice.module_generator(label)) == double_dual.module_generator(label))

# current behaviour of the relations on main
square = ConvexPolytopes(lattice)(((-1, -1), (-1, 1), (1, 1), (1, -1)))
diamond = square.polar_dual()
doubled = diamond.polar_dual()
print("doubled lattice is M?", doubled.ambient_lattice() is lattice)
for name, value in (
    ("square in doubled", lambda: square.is_contained_in(doubled)),
    ("doubled in square", lambda: doubled.is_contained_in(square)),
    ("diamond in square", lambda: diamond.is_contained_in(square)),
    ("square == doubled", lambda: square == doubled),
    ("square == diamond", lambda: square == diamond),
    ("square == 1", lambda: square == 1),
    ("square == None", lambda: square == None),
):
    try:
        print(" ", name, "->", repr(value()))
    except Exception as error:
        print(" ", name, "raised", type(error).__name__, str(error)[:100])
print("polar vertices:", tuple(diamond._engine_polyhedron().vertices()))
print("double polar engine vertices:", tuple(doubled._engine_polyhedron().vertices()))
