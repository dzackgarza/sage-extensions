from sage_extensions.all import *
from sage_extensions.categories.algebras.algebras import Algebras

group = Groups.S(3)
algebra = QQ[group]
center = algebra.center()
inclusion = algebra.center_inclusion()
unital = Algebras(QQ).Associative().Unital()
print("center rank:", center.dimension())
print("inclusion parent is center.Mor(algebra):", inclusion.parent() is center.Mor(algebra))
print("inclusion in associative-unital Mor:", inclusion in unital.Mor(center, algebra))
print("preserves_unit:", inclusion.preserves_unit())

module = Modules(QQ).free_module(3)
e, x, y = (module.module_generator(label) for label in range(3))
zero = module.zero()
mult = BilinearMap(module, module, module, {
    (0, 0): e, (0, 1): x, (0, 2): y,
    (1, 0): x, (1, 1): y, (1, 2): x,
    (2, 0): y, (2, 1): zero, (2, 2): zero,
})
A = Algebras(QQ).Unital()(module, mult, e)
Ac = A.center()
Ainc = A.center_inclusion()
print("A in Unital:", A in Algebras(QQ).Unital(), "| in Associative:", A in Algebras(QQ).Associative())
print("A centre rank:", Ac.dimension())
print("Ainc parent is Ac.Mor(A):", Ainc.parent() is Ac.Mor(A))
print("Ainc in Unital().Mor:", Ainc in Algebras(QQ).Unital().Mor(Ac, A))
print("Ainc preserves_unit:", Ainc.preserves_unit())
print("Ainc(Ac.one()) == A.one():", Ainc(Ac.one()) == A.one())

root_module = Modules(QQ).free_module(2)
p, q = root_module.module_generator(0), root_module.module_generator(1)
root_mult = BilinearMap(root_module, root_module, root_module, {
    (0, 0): root_module.zero(), (0, 1): q, (1, 0): root_module.zero(), (1, 1): root_module.zero(),
})
B = Algebras(QQ)(root_module, root_mult)
Bc = B.center()
Binc = B.center_inclusion()
print("B centre rank:", Bc.dimension())
print("Binc parent is Bc.Mor(B):", Binc.parent() is Bc.Mor(B))
print("Binc parent is root Mor:", Binc.parent() is Algebras(QQ).Mor(Bc, B))
