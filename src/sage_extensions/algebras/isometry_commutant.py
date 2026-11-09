r"""Simultaneous commutants of integral isometries.

For a nonsingular integral Gram matrix `B` and isometries `F_1, ..., F_s` acting on
column vectors, `A` is the rational commutant, `O = A \cap M_r(Z)` its integral order
and `a^\dagger = B^{-1} a^t B` the adjoint. Each `F_i^\dagger = F_i^{-1}`, so `A` is
stable under the adjoint, and the centralizer of the `F_i` in `O(L)` is the set of units
`u` of `O` with `u^\dagger u = 1`. `O` need not be stable under the adjoint when `B`
is not unimodular.

The integer kernel of the commutation equations is saturated, so its basis is a
`Z`-basis of `O`. The trace form of a faithful module has kernel the Jacobson radical
in characteristic zero (Curtis-Reiner, *Methods of Representation Theory I*, 5.26).
"""

from sage.matrix.constructor import matrix
from sage.matrix.special import identity_matrix
from sage.modules.free_module_element import vector
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ


class IsometryCommutant:
    r"""The commutant algebra and integral order of a set of isometries."""

    def __init__(self, gram, isometries):
        self.gram = matrix(ZZ, gram)
        self.rank = self.gram.nrows()
        self.isometries = tuple(matrix(ZZ, self.rank, self.rank, F) for F in isometries)
        assert self.gram == self.gram.transpose() and self.gram.det() != 0
        assert all(F.transpose() * self.gram * F == self.gram for F in self.isometries)
        assert all(F.det() in (1, -1) for F in self.isometries)
        self._adjoint_factor = self.gram.change_ring(QQ).inverse()
        self.order_basis = self._integral_basis()
        self._coordinates = matrix(QQ, [m.list() for m in self.order_basis])

    def _integral_basis(self):
        r = self.rank
        if not self.isometries:
            equations = matrix(ZZ, 0, r**2)
        else:
            rows = []
            for F in self.isometries:
                for i in range(r):
                    for j in range(r):
                        row = [0] * r**2
                        for k in range(r):
                            row[k * r + j] += F[i, k] * -1
                            row[i * r + k] += F[k, j]
                        rows.append(row)
            equations = matrix(ZZ, rows)
        return tuple(
            matrix(ZZ, r, r, list(v)) for v in equations.right_kernel().basis()
        )

    def dimension(self):
        return len(self.order_basis)

    def coordinates(self, element):
        r"""Return rational coordinates of an element of `A` in the order basis."""
        target = vector(QQ, matrix(QQ, element).list())
        return self._coordinates.solve_left(target)

    def contains(self, element):
        r"""Decide membership in `A`."""
        element = matrix(QQ, element)
        return all(element * F == F * element for F in self.isometries)

    def in_order(self, element):
        r"""Decide membership in `O`."""
        element = matrix(QQ, element)
        return self.contains(element) and element.denominator() == 1

    def adjoint(self, element):
        return self._adjoint_factor * matrix(QQ, element).transpose() * self.gram

    def multiplication_table(self):
        r"""Return the integral structure constants of `O` in its basis."""
        return tuple(
            tuple(
                vector(ZZ, self.coordinates(left * right))
                for right in self.order_basis
            )
            for left in self.order_basis
        )

    def involution_table(self):
        r"""Return the rational coordinates of the adjoint of each basis element."""
        return tuple(self.coordinates(self.adjoint(m)) for m in self.order_basis)

    def order_is_adjoint_stable(self):
        return all(self.adjoint(m).denominator() == 1 for m in self.order_basis)

    def radical_basis(self):
        r"""Return a `Q`-basis of the Jacobson radical of `A`."""
        form = matrix(
            QQ, [[(x * y).trace() for y in self.order_basis] for x in self.order_basis]
        )
        return tuple(
            sum(c * m.change_ring(QQ) for c, m in zip(v, self.order_basis))
            for v in form.right_kernel().basis()
        )

    def is_semisimple(self):
        return not self.radical_basis()

    def is_centralizer_element(self, element):
        r"""Decide whether `element` is an isometry of `L` commuting with every `F_i`."""
        element = matrix(QQ, element)
        return (
            self.in_order(element)
            and element.det() in (1, -1)
            and self.adjoint(element) * element == identity_matrix(QQ, self.rank)
        )
