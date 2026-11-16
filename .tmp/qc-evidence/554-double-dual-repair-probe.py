from sage_extensions.all import *
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.schemes.polytopes import _primal_lattice_of_a_dual

lattice = ZZ.free_module(2)
dual = lattice.dual_module()
square = ConvexPolytopes(lattice)(((-1, -1), (-1, 1), (1, 1), (1, -1)))
diamond = square.polar_dual()
doubled = diamond.polar_dual()
thrice = doubled.polar_dual()

print("predicate on the primal:", _primal_lattice_of_a_dual(lattice))
print("predicate on the dual is the primal?", _primal_lattice_of_a_dual(dual) is lattice)
print("predicate on the double dual is the dual?", _primal_lattice_of_a_dual(dual.dual_module()) is dual)
print("predicate on an endomorphism Mor module:",
      _primal_lattice_of_a_dual(Modules(ZZ).Mor(lattice, lattice)))

print("diamond frame is the dual?", diamond.ambient_lattice() is dual)
print("doubled frame is the primal?", doubled.ambient_lattice() is lattice)
print("thrice frame is the dual?", thrice.ambient_lattice() is dual)
print("doubled == square?", doubled == square)
print("doubled is in ConvexPolytopes(lattice)?", doubled in ConvexPolytopes(lattice))
print("diamond is in ConvexPolytopes(lattice)?", diamond in ConvexPolytopes(lattice))
print("square in doubled?", square.is_contained_in(doubled))
print("doubled in square?", doubled.is_contained_in(square))
print("hash equal?", hash(square) == hash(doubled))
print("existing contract polar.polar_dual() == square?", diamond.polar_dual() == square)
print("thrice == diamond?", thrice == diamond)
print("diamond in square?" , diamond.is_contained_in(square))
print("square in diamond?", square.is_contained_in(diamond))
print("square == 1?", square == 1)
print("square == None?", square == None)
print("square == ()?", square == ())

# the relations still decide inside one lattice, whichever one frames it
moved = ConvexPolytopes(dual)(((1, 0), (0, 1), (-1, 0), (0, -1)))
print("diamond == moved?", diamond == moved, "| hash equal?", hash(diamond) == hash(moved))
print("moved in diamond?", moved.is_contained_in(diamond))
