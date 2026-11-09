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

from itertools import product

from sage.arith.functions import lcm
from sage.arith.misc import factorial
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

    def _skew_radical(self):
        r"""Return a `Z`-basis of `\{x \in rad A : x^\dagger = -x\} \cap M_r(Z)`."""
        radical = self.radical_basis()
        if not radical:
            return ()
        equations = matrix(QQ, [(x + self.adjoint(x)).list() for x in radical])
        relations = equations.left_kernel().basis()
        if not relations:
            return ()
        skew = [sum(c * x for c, x in zip(v, radical)) for v in relations]
        denominator = lcm([m.denominator() for m in skew])
        scaled = matrix(ZZ, [(denominator * m).list() for m in skew]).saturation()
        return tuple(matrix(ZZ, self.rank, self.rank, list(row)) for row in scaled.rows())

    def unipotent_kernel_generators(self):
        r"""Return generators of the kernel of `C(Z) \to (A / rad A)^\times` for abelian skew radical.

        The logarithm is a bijection from the kernel over `Q` onto the skew radical
        `n`. On abelian `n` it is a homomorphism, so the kernel is a lattice in `n`.
        With `x^{c+1} = 0`, a logarithm of an integral element lies in
        `\Lambda = M^{-1}(n \cap M_r(Z))` for `M = lcm(1, ..., c)`, and `\exp` is
        integral on `c! (n \cap M_r(Z)) = D \Lambda` for `D = M c!`. Testing each
        residue of `\Lambda / D \Lambda` therefore determines the lattice.
        """
        basis = self._skew_radical()
        if not basis:
            return ()
        assert all(x * y == y * x for x in basis for y in basis), (
            f"the skew radical of the commutant of {self.isometries} is not abelian"
        )
        identity = identity_matrix(QQ, self.rank)
        nilpotency = 1
        probes = list(basis)
        power = list(basis)
        while True:
            power = [x * y for x in power for y in probes if not (x * y).is_zero()]
            if not power:
                break
            nilpotency += 1
        modulus = lcm(range(1, nilpotency + 1))
        depth = modulus * factorial(nilpotency)

        def exponential(coordinates):
            x = sum((c * m.change_ring(QQ) for c, m in zip(coordinates, basis)), 0 * identity) / modulus
            term = identity
            total = identity
            for k in range(1, nilpotency + 1):
                term = term * x / k
                total = total + term
            return total

        rows = [[depth if i == j else 0 for j in range(len(basis))] for i in range(len(basis))]
        for residue in product(range(depth), repeat=len(basis)):
            if any(residue) and exponential(residue).denominator() == 1:
                rows.append(list(residue))
        lattice = matrix(ZZ, rows).hermite_form(include_zero_rows=False)
        return tuple(matrix(ZZ, exponential(list(row))) for row in lattice.rows())

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
