r"""Norm-one extraction, checked by hand.

Over K = Q(sqrt 2) take GL_2(O_K) with d = 2 and C = O_K^x = <-1, e>, e = 1 + sqrt 2.
C^2 = <e^2>, so O_K^x / C^2 has order 4 and det is onto it. diag(e, 1) squared has
determinant e^2, so its extraction is diag(e, 1/e). The transvection has trivial
coset and is returned unchanged. Over Q in the order Z<1,i,j,k> of (-1,3), Nrd(1+i+j) = -1
and (1+i+j)^2 = 3+2i+2j has norm one with root 1.
"""

from sage_extensions.all import *
from sage.algebras.quatalg.quaternion_algebra import QuaternionAlgebra
from sage.matrix.constructor import matrix as sage_matrix
from sage.rings.number_field.number_field import QuadraticField
from sage.rings.rational_field import QQ as SageQQ
from sage_extensions.algebras.norm_one_units import norm_one_generators


def test_gl2_over_a_real_quadratic_order_has_the_hand_extractions():
    field = QuadraticField(int(2), "a")
    e = int(1) + field.gen()
    zero, one = field.zero(), field.one()
    units = [
        sage_matrix(field, [[e, zero], [zero, one]]),
        sage_matrix(field, [[-one, zero], [zero, one]]),
        sage_matrix(field, [[one, one], [zero, one]]),
        sage_matrix(field, [[zero, one], [one, zero]]),
    ]
    generators, kernel = norm_one_generators(units, [-one, e], int(2), lambda m: m.det(), field)
    assert all(g.det() == one for g in generators)
    assert sage_matrix(field, [[e, zero], [zero, ~e]]) in generators
    assert units[2] in generators
    assert tuple(kernel) == (-one,)


def test_a_quaternion_order_with_a_unit_of_norm_minus_one():
    algebra = QuaternionAlgebra(SageQQ, int(-1), int(3))
    i, j, k = algebra.gens()
    unit = int(1) + i + j
    other = int(2) + j
    assert unit.reduced_norm() == int(-1)
    generators, kernel = norm_one_generators([unit, other], [SageQQ(int(-1))], int(2), lambda x: x.reduced_norm(), SageQQ)
    assert all(g.reduced_norm() == int(1) for g in generators)
    assert int(3) + int(2) * i + int(2) * j in generators
    assert other in generators
    assert tuple(kernel) == (SageQQ(int(-1)),)
