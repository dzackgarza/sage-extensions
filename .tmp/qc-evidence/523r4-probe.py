import time

from sage_extensions.all import *
from sage_extensions.categories.modules.pure.modules import MatrixSpaces


def show(label, thunk):
    start = time.perf_counter()
    try:
        value = thunk()
        print(f"{label} -> {value!r}   [{time.perf_counter() - start:.3f} s]", flush=True)
    except Exception as error:
        print(f"{label} !! {type(error).__name__}: {error}   [{time.perf_counter() - start:.3f} s]", flush=True)


zz = ZZ.matrix_space(2)
print("dispatch of inverse:", type(zz.one()).inverse.__qualname__, flush=True)
print("dispatch of __invert__:", type(zz.one()).__invert__.__qualname__, flush=True)
show("ZZ one/2", lambda: zz.one() / 2)
show("ZZ ~2I", lambda: ~zz(2))
show("ZZ inverse_of_unit(2I)", lambda: zz(2).inverse_of_unit())
show("ZZ 2I inverse()", lambda: zz(2).inverse())
show("ZZ one/[[2,1],[1,1]]", lambda: zz.one() / zz.from_rows([[2, 1], [1, 1]]))
qq = QQ.matrix_space(2)
show("QQ one/[[1,1],[1,1]]", lambda: qq.one() / qq.from_rows([[1, 1], [1, 1]]))

ring4 = ZZ.quotient_ring(ZZ.ideal(4))
m4 = ring4.matrix_space(2)
unit4 = m4.from_rows([[3, 0], [0, 1]])
nonunit4 = m4.from_rows([[2, 0], [0, 1]])
show("Z4 unit ~", lambda: ~unit4)
show("Z4 unit inverse()", lambda: unit4.inverse())
show("Z4 unit inverse_of_unit()", lambda: unit4.inverse_of_unit())
show("Z4 unit one/A", lambda: m4.one() / unit4)
show("Z4 nonunit is_unit", lambda: nonunit4.is_unit())
show("Z4 nonunit ~", lambda: ~nonunit4)
show("Z4 nonunit inverse()", lambda: nonunit4.inverse())

v = ring4 ** 2
w = ring4.free_module(("a", "b"))
f = v.Mor(w).from_rows([[3, 0], [0, 1]])
show("Z4 distinct f.inverse()", lambda: f.inverse())
show("Z4 distinct g @ f == id_V", lambda: f.inverse() @ f == v.End().one())
show("Z4 distinct f @ g == id_W", lambda: f @ f.inverse() == w.End().one())

zx = ZZ.polynomial_ring("x")
x = zx.algebra_generator("x")
mzx = zx.matrix_space(2)
u = mzx.from_rows([[1, x], [0, 1]])
show("Z[x] ~u", lambda: ~u)
show("Z[x] u.inverse()", lambda: u.inverse())
show("Z[x] u.inverse_of_unit()", lambda: u.inverse_of_unit())
show("Z[x] xI.is_unit", lambda: mzx.from_rows([[x, 0], [0, 1]]).is_unit())
show("Z[x] ~xI", lambda: ~mzx.from_rows([[x, 0], [0, 1]]))

empty = ZZ ** 0
show("ZZ 0x0 ~", lambda: ~empty.End().from_rows(()))
rect = ZZ ** 1
show("ZZ rectangular (2,1) ~", lambda: ~rect.Mor(ZZ ** 2).from_rows([[1], [0]]))

from sage_extensions.rings.real import RR

plane = RR ** 2
real = plane.End().from_rows(((RR.pi(), 1), (0, 1)))
show("RR f.inverse()", lambda: real.inverse())
show("RR ~f", lambda: ~real)

a = zz.from_rows([[2, 1], [1, 1]])
show("ZZ det is one datum", lambda: a.determinant() is a.determinant())
show("ZZ inverse is one datum", lambda: a.inverse() is a.inverse())
show("ZZ inverse_of_unit is the inverse", lambda: a.inverse_of_unit() is a.inverse())

for n in (2, 4, 6):
    matrices = QQ.matrix_space(n)
    element = matrices.from_rows([[2 if row == column else 0 for column in range(n)] for row in range(n)])
    show(f"QQ {n}x{n} ~", lambda element=element: element @ ~element == element.parent().one())
    integers = ZZ.matrix_space(n)
    integer_element = integers.from_rows([[1 if row == column else (1 if column == row + 1 else 0) for column in range(n)] for row in range(n)])
    show(f"ZZ {n}x{n} ~", lambda integer_element=integer_element: integer_element @ ~integer_element == integer_element.parent().one())

R = MatrixAlgebras(ZZ).an_object()
print("noncommutative R commutative:", R.is_commutative(), flush=True)
show("MatrixSpaces(R).an_object()", lambda: MatrixSpaces(R).an_object())
try:
    mor = MatrixSpaces(R).an_object()
    show("noncommutative ~one", lambda: ~mor.one())
    show("noncommutative one.inverse()", lambda: mor.one().inverse())
    show("noncommutative one.inverse_of_unit()", lambda: mor.one().inverse_of_unit())
except Exception as error:
    print("noncommutative matrix space !!", type(error).__name__, error, flush=True)
