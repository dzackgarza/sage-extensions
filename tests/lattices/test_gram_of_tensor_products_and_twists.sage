r"""The Gram of a tensor product is the Kronecker product; a twist scales the Gram.

For lattices \(L, M\) with Gram matrices \(A, B\) in bases \((x_i)\), \((y_j)\), the tensor
product has basis \(x_i\otimes y_j\) and \(b(x_i\otimes y_j, x_k\otimes y_l) = A_{ik}B_{jl}\).
Summing over the basis,
\(\sum_{g} q(g) = \operatorname{tr}A\cdot\operatorname{tr}B\) and
\(\sum_{g,h} b(g,h) = (\sum A_{ik})(\sum B_{jl})\).  For \(A_2\otimes U\):
\(\operatorname{tr} = -4\cdot 0 = 0\) and \((-2)\cdot 2 = -4\); for \(A_2\otimes A_2\):
\((-4)^2 = 16\) and \((-2)^2 = 4\).

The twist \(L(n)\) has Gram \(nA\); for \(n=-1\) the signature \((p,q)\) becomes \((q,p)\).
"""

from sage_extensions.all import *


def test_the_gram_of_a2_tensor_u_is_the_kronecker_product() -> None:
    product = Lattices(ZZ)("A2") @ Lattices(ZZ)("U")
    basis = product.module_generators()

    assert sum(vector * vector for vector in basis) == 0
    assert sum(left * right for left in basis for right in basis) == -4


def test_the_gram_of_a2_tensor_a2_is_the_kronecker_product() -> None:
    product = Lattices(ZZ)("A2") @ Lattices(ZZ)("A2")
    basis = product.module_generators()

    assert sum(vector * vector for vector in basis) == 16
    assert sum(left * right for left in basis for right in basis) == 4
    assert product.is_even()


def test_the_negative_twist_swaps_the_signature() -> None:
    root_lattice = Lattices(ZZ)("A2")
    plane = Lattices(ZZ)("U")
    mixed = root_lattice + plane

    assert root_lattice.twist(-1).signature_pair() == signature_pair(2, 0)
    assert root_lattice.twist(-1).is_positive_definite()
    assert plane.twist(-1).signature_pair() == signature_pair(1, 1)
    assert mixed.twist(-1).signature_pair() == signature_pair(3, 1)
    assert mixed.twist(-1).determinant() == mixed.determinant()
    assert mixed.twist(3).determinant() == 3 ** 4 * mixed.determinant()
