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

from itertools import combinations, count, product

from sage.arith.functions import lcm
from sage.arith.misc import CRT_list as crt
from sage.arith.misc import binomial, factorial
from sage.matrix.constructor import block_matrix, matrix
from sage.matrix.special import identity_matrix
from sage.modules.free_module_element import vector
from sage.libs.pari import pari
from sage.rings.number_field.number_field import NumberField
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ


def symplectic_generators(gram):
    r"""Return generators of `Sp(M, b)` for an alternating `b` of constant elementary divisor.

    In a symplectic basis `a_i, b_i`, the transvections along `a_i`, `b_i` and
    `a_i - a_{i+1}` are the homology images of Humphries' generators of the mapping class
    group, which surjects onto `Sp_{2g}(Z)`. A scalar multiple of a unimodular form has the same group.
    """
    gram = matrix(ZZ, gram)
    size = gram.nrows()
    form, change = gram.symplectic_form()
    divisors = set(form[i, size // 2 + i] for i in range(size // 2))
    assert len(divisors) == 1, f"{gram} is not a multiple of a unimodular form"
    basis = change.inverse().change_ring(QQ)
    half = size // 2
    unit = lambda i: identity_matrix(QQ, size).row(i)
    vectors = [unit(i) for i in range(size)]
    vectors += [unit(i) - unit(i + 1) for i in range(half - 1)]
    scale = next(iter(divisors))
    result = []
    for v in vectors:
        along = v * basis
        pairing = gram.change_ring(QQ) * along / scale
        result.append(matrix(ZZ, identity_matrix(QQ, size) + along.column() * pairing.row()))
    return tuple(result)


def _form_generators(gram):
    r"""Return generators of the isometry group of a symmetric or alternating integral form."""
    if gram == gram.transpose():
        from sage_extensions.categories.lattices import Lattices

        lattice = Lattices(ZZ)([[int(c) for c in row] for row in gram.rows()])
        frame = tuple(lattice.module_generators())
        return tuple(
            matrix(ZZ, [[int(c) for c in g(v)] for v in frame]).transpose()
            for g in lattice.O().group_generators()
        )
    assert gram == -gram.transpose(), f"the form {gram} is neither symmetric nor alternating"
    return symplectic_generators(gram)


_RATIONAL_COEFFICIENTS = (-2, -1, 1, 2, QQ((-1, 2)), QQ((1, 2)), QQ((-1, 3)), QQ((1, 3)), QQ((-1, 4)), QQ((1, 4)))


def _short_vectors(gram, bound):
    r"""Return every integer vector `x \ne 0` with `x^t G x \le` ``bound``, for `G` rational positive definite.

    Fincke-Pohst enumeration (Fincke, Pohst, Math. Comp. 44 (1985), 463-471), as PARI's
    ``qfminim``, which lists one vector of each pair `\pm x`.
    """
    denominator = gram.denominator()
    found = pari(matrix(ZZ, denominator * gram)).qfminim(denominator * bound)[2].sage()
    vectors = [vector(ZZ, column) for column in found.columns()]
    return vectors + [-v for v in vectors]


def _integer_solution(equations, target):
    r"""Return an integer solution of `equations x = target`, or ``None``."""
    diagonal, left, right = equations.smith_form()
    moved = left * target
    solution = []
    for i in range(diagonal.ncols()):
        entry = diagonal[i, i] if i < diagonal.nrows() else 0
        value = moved[i] if i < len(moved) else 0
        if entry == 0:
            if value != 0:
                return None
            solution.append(0)
        elif value % entry != 0:
            return None
        else:
            solution.append(value // entry)
    if any(moved[i] != 0 for i in range(diagonal.ncols(), len(moved))):
        return None
    return right * vector(ZZ, solution)


def _factor_centralizer_generators(factor):
    r"""Return the centralizer generators of a central factor through the port's dispatch.

    A factor can be a division quaternion algebra over `Q` or central simple over a field `K \ne Q`;
    their arithmetic groups are built by ``sage_indefinite_port.indefinite.commutant_groups``
    (Voronoi units, unitary models over `O_K`), which falls back to this class otherwise and
    raises :class:`NotImplementedError` naming the factor when no route exists.
    """
    from sage_indefinite_port.indefinite.commutant_groups import centralizer_generators

    return centralizer_generators(factor)


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

    def _radical_nilpotency(self):
        r"""Return the least `p` with `rad^{p+1} = 0` and `Q`-bases of `rad^1, ..., rad^p`."""
        r = self.rank
        radical = self.radical_basis()
        if not radical:
            return 0, ()
        powers = [matrix(QQ, [x.list() for x in radical])]
        while True:
            products = [(matrix(QQ, r, r, list(row)) * y).list() for row in powers[-1].rows() for y in radical]
            span = matrix(QQ, products).row_space().basis_matrix()
            if span.nrows() == 0:
                return len(powers), tuple(powers)
            powers.append(span)

    def _unipotent_frame(self):
        r"""Return a `Z`-basis of `n \cap M_r(Z)` adapted to `n_k = n \cap rad^k`, with the level of each vector.

        `n` is the skew radical `\{x \in rad A : x^\dagger = -x\}`, a nilpotent Lie algebra with
        `[n_i, n_j] \subseteq n_{i+j}`. Each `n_k \cap M_r(Z)` is saturated in the next, so a basis of
        the deeper lattice extends by the rows of a unimodular completion.
        """
        if hasattr(self, "_frame"):
            return self._frame
        r = self.rank
        nilpotency, powers = self._radical_nilpotency()
        lattices = []
        for rows in powers:
            elements = [matrix(QQ, r, r, list(row)) for row in rows.rows()]
            equations = matrix(QQ, [(x + self.adjoint(x)).list() for x in elements])
            skew = [sum(c * x for c, x in zip(v, elements)) for v in equations.left_kernel().basis()]
            if not skew:
                lattices.append(matrix(ZZ, 0, r**2))
                continue
            denominator = lcm([m.denominator() for m in skew])
            lattices.append(matrix(ZZ, [(denominator * m).list() for m in skew]).saturation())
        basis_rows, levels = [], []
        for level in range(nilpotency, 0, -1):
            lattice = lattices[level - 1]
            if lattice.nrows() == len(basis_rows):
                continue
            if not basis_rows:
                new_rows = list(lattice.rows())
            else:
                inside = matrix(ZZ, [lattice.change_ring(QQ).solve_left(vector(QQ, row)) for row in basis_rows])
                _diagonal, _left, right = inside.smith_form()
                completion = right.inverse()
                new_rows = [completion.row(i) * lattice for i in range(inside.nrows(), lattice.nrows())]
            basis_rows += new_rows
            levels += [level] * len(new_rows)
        basis = tuple(matrix(QQ, r, r, list(row)) for row in basis_rows)
        self._frame = (basis, tuple(levels), nilpotency)
        return self._frame

    def _exp(self, x):
        nilpotency = self._radical_nilpotency()[0]
        term = total = identity_matrix(QQ, self.rank)
        for k in range(1, nilpotency + 1):
            term = term * x / k
            total = total + term
        return total

    def _integral_point(self, element, level):
        r"""Return an integral element of ``element`` `\cdot N_{level}(Q)`, or ``None``.

        Here `N_k = \exp(n_k)` and ``element`` is a rational unitary element of `A`. A member
        `\gamma` of the coset is `g \exp(s) w` with `s` in the level-``level`` span of the frame
        and `w \in N_{level+1}`, since `N_k / N_{k+1}` is the vector group `n_k / n_{k+1}`. For
        `\gamma` integral, `g^{-1}\gamma \in E^{-1} M_r(Z)` with `E` the denominator of `g^{-1}`, and
        `(g^{-1}\gamma - 1)^{p+1} = 0`, so its logarithm lies in `(E^p \mathrm{lcm}(1..p))^{-1}(n \cap M_r(Z))`.
        Right multiplication by `\exp(p!\,\mu)` for `\mu` in the frame keeps `\gamma` integral and
        moves `s` by `p!\,\mu`, so `s` is decided modulo `p!` on that finite residue set
        (Mal'cev coordinates of the second kind: Segal, *Polycyclic Groups*, Ch. 6).
        """
        basis, levels, nilpotency = self._unipotent_frame()
        if level > nilpotency:
            return matrix(ZZ, element) if element.denominator() == 1 else None
        indices = [i for i, value in enumerate(levels) if value == level]
        if not indices:
            return self._integral_point(element, level + 1)
        scale = element.inverse().denominator() ** nilpotency * lcm(range(1, nilpotency + 1))
        period = scale * factorial(nilpotency)
        for residue in product(range(period), repeat=len(indices)):
            step = sum((QQ((c, scale)) * basis[i] for c, i in zip(residue, indices)), 0 * element)
            found = self._integral_point(element * self._exp(step), level + 1)
            if found is not None:
                return found
        return None

    def unipotent_kernel_generators(self):
        r"""Return generators of the kernel `N(Z)` of `C(Z) \to (A / rad A)^\times`.

        Over `Q` the kernel is `\exp(n)` for the skew radical `n` (the logarithm of a unitary
        unipotent element is skew). With `N_k = \exp(n_k)`, each `N_k(Z) / N_{k+1}(Z)` embeds in
        `n_k / n_{k+1}` by the logarithm. Its image `\Lambda_k` contains `p!` times the level-`k`
        frame lattice, since `\exp(p!\,\mu)` is integral, and lies in `\mathrm{lcm}(1..p)^{-1}` times
        it, since the logarithm of an integral unipotent has those denominators. Each residue
        between is decided by :meth:`_integral_point`, and lifts of `\Lambda_k` for every `k`
        generate `N(Z)` (Segal, *Polycyclic Groups*, Ch. 6, Thm. 2).
        """
        basis, levels, nilpotency = self._unipotent_frame()
        if not basis:
            return ()
        one = identity_matrix(QQ, self.rank)
        modulus = lcm(range(1, nilpotency + 1))
        depth = factorial(nilpotency)
        result = {}
        for level in range(nilpotency, 0, -1):
            indices = [i for i, value in enumerate(levels) if value == level]
            for i in indices:
                element = self._exp(depth * basis[i])
                result[element.str()] = matrix(ZZ, element)
            for residue in product(range(modulus * depth), repeat=len(indices)):
                if all(c % (modulus * depth) == 0 for c in residue):
                    continue
                step = sum((QQ((c, modulus)) * basis[i] for c, i in zip(residue, indices)), 0 * one)
                found = self._integral_point(self._exp(step), level + 1)
                if found is not None and found != one:
                    result[found.str()] = found
        assert all(self.is_centralizer_element(g) for g in result.values())
        return tuple(result.values())

    def _primitive_idempotent(self, degree, coefficients=(-2, -1, 1, 2)):
        r"""Return an idempotent of `A` of rank `r / degree`, a sparse combination of the order basis."""
        target = self.rank / degree
        size = len(self.order_basis)
        for support in range(1, min(size, 3) + 1):
            for positions in combinations(range(size), support):
                for values in product(coefficients, repeat=support):
                    element = sum(c * self.order_basis[i] for c, i in zip(values, positions))
                    if element * element == element and element.rank() == target:
                        return element
        raise ArithmeticError(
            f"no idempotent of rank {target} among sparse elements of the order of {self.isometries}"
        )

    def simple_centralizer_generators(self):
        r"""Return generators of the centralizer when `A \cong M_n(Q)`, for any order `O`.

        A rational idempotent `e` of rank `r/n` gives the simple module `A e`, and `X = O e`
        is an `O`-stable lattice in it. `A` acts faithfully on `A e`, so `A = End_Q(A e)`
        and `O' = End_Z(X)` is a maximal order containing `O`, with matrix units `E_{ij}`.
        For `e' = E_{11}`, the space `e'^\dagger A e'` is a line, so `x^\dagger y = b(x, y) t`
        defines a form on `O' e'`. A unit `u` of `O'` satisfies `u^\dagger u = 1` exactly when
        it preserves `b`, so the unitary units of `O'` are the isometry group of `b`:
        orthogonal when `b` is symmetric, symplectic when alternating. A unit of `O` is a
        unit of `O'`, and the unitary units of `O` are an arithmetic subgroup of finite index
        (Platonov-Rapinchuk, *Algebraic Groups and Number Theory*, Prop. 4.1), so Schreier's
        lemma on membership in `O` gives them when `O \ne O'`.
        """
        assert not self.radical_basis(), f"the commutant of {self.isometries} is not semisimple"
        degree = ZZ(self.dimension()).isqrt()
        assert degree**2 == self.dimension() and len(self._center_basis()) == 1, (
            f"the commutant of {self.isometries} is not central simple of square dimension"
        )
        r = self.rank
        e = self._primitive_idempotent(degree, _RATIONAL_COEFFICIENTS)
        images = matrix(QQ, [(m.change_ring(QQ) * e).list() for m in self.order_basis])
        denominator = images.denominator()
        span = matrix(QQ, matrix(ZZ, denominator * images).hermite_form(include_zero_rows=False)) / denominator
        assert span.nrows() == degree
        module = tuple(matrix(QQ, r, r, list(row)) for row in span.rows())

        def on_module(element):
            return matrix(
                QQ, [span.solve_left(vector(QQ, (element * m).list())) for m in module]
            ).transpose()

        action_rows = matrix(QQ, [on_module(m.change_ring(QQ)).list() for m in self.order_basis])
        assert action_rows.denominator() == 1, f"the order of {self.isometries} does not preserve O e"
        inverse = action_rows.inverse()

        def element_of(block):
            combination = vector(QQ, matrix(QQ, block).list()) * inverse
            return sum(c * m.change_ring(QQ) for c, m in zip(combination, self.order_basis))

        def unit(i, j):
            block = matrix(QQ, degree, degree)
            block[i, j] = 1
            return element_of(block)

        corner = unit(0, 0)
        column = tuple(unit(i, 0) for i in range(degree))
        adjoint_corner = self.adjoint(corner)
        line = next(
            value
            for value in (adjoint_corner * unit(i, j) * corner for i in range(degree) for j in range(degree))
            if not value.is_zero()
        )
        generator = matrix(QQ, [line.list()])
        form = matrix(
            QQ,
            [[generator.solve_left(vector(QQ, (self.adjoint(x) * y).list()))[0] for y in column] for x in column],
        )
        gram = matrix(ZZ, form.denominator() * form)
        group = tuple(element_of(isometry) for isometry in _form_generators(gram))
        if abs(action_rows.det()) == 1:
            assert all(self.is_centralizer_element(g) for g in group)
            return tuple(matrix(ZZ, g) for g in group)
        return self._order_subgroup_generators(group)

    def _order_subgroup_generators(self, moves):
        r"""Return Schreier generators of the elements of `\langle` ``moves`` `\rangle` lying in `O`.

        The moves are unitary units of an order containing `O`, and the subgroup has finite
        index. A unitary `w \in O` has `\det w = \pm 1`, so `w^{-1}` is integral and lies in
        `O`: right cosets are compared by membership of `x y^{-1}` in `O`.
        """
        one = identity_matrix(QQ, self.rank)
        moves = [matrix(QQ, m) for m in moves if m != one]
        if not moves:
            return ()
        transversal = [one]
        result = {}
        position = 0
        while position < len(transversal):
            current = transversal[position]
            position += 1
            for move in moves:
                product_element = current * move
                for known in transversal:
                    quotient = product_element * known.inverse()
                    if self.in_order(quotient):
                        if quotient != one:
                            result[quotient.str()] = matrix(ZZ, quotient)
                        break
                else:
                    transversal.append(product_element)
        assert all(self.is_centralizer_element(g) for g in result.values())
        return tuple(result.values())

    def radical_centralizer_generators(self):
        r"""Return generators of the centralizer when `rad \ne 0` (:class:`LeviQuotient`)."""
        return LeviQuotient(self).centralizer_generators()

    def inversion_transporter(self):
        r"""Return `t \in O(L)` with `t F t^{-1} = F^{-1}`, or ``None``, for `A` a real quadratic field."""
        F = self.isometries[0]
        return self.equivariant_transporter(self.gram, F.inverse())

    def find_inversion_transporter(self, height):
        r"""Return a verified `t` with `t F t^{-1} = F^{-1}` among small intertwiners, or ``None``.

        The intertwiners are a saturated integer lattice, searched to coefficient ``height``.
        A result is a proof of existence. ``None`` says only that the box holds no isometry.
        """
        assert len(self.isometries) == 1
        F = self.isometries[0]
        inverse = F.inverse()
        r = self.rank
        rows = []
        for i in range(r):
            for j in range(r):
                row = [0] * r**2
                for k in range(r):
                    row[i * r + k] += F[k, j]
                    row[k * r + j] -= inverse[i, k]
                rows.append(row)
        basis = [matrix(ZZ, r, r, list(v)) for v in matrix(ZZ, rows).right_kernel().basis()]
        for values in product(range(-height, height + 1), repeat=len(basis)):
            candidate = sum(c * m for c, m in zip(values, basis))
            if candidate.det() in (1, -1) and candidate.transpose() * self.gram * candidate == self.gram:
                assert candidate * F == inverse * candidate
                return candidate
        return None

    def equivariant_transporter(self, target_gram, target_isometry):
        r"""Return `t` in `GL_r(Z)` with `t^t B' t = B` and `t F = F' t`, or ``None``, for `A` a real quadratic field.

        Rationally, `t = t_0 a` with `t_0` an invertible solution of the linear equation and
        `a \in A`. Then `B_0 = t_0^t B' t_0` is the form `B` scaled by an element of `A`, and
        `\sigma(a) c a = 1` for a rational `c`. The solutions form cosets of the centralizer,
        generated up to sign by a norm-one unit `\eta > 1`, so each coset has a member with
        `|a_1 / a_2|` in `[1, \eta^2)`. Then `|a_1| \le \sqrt{n} \eta` and `|a_2| \le \sqrt{n}`,
        which bounds the integer coordinates of `a` on the lattice of `a` with `t_0 a` integral.
        Exhausting that box decides the question. ``None`` is returned at once when the
        linear system has no invertible solution, since the modules are then not isomorphic.
        """
        if self.is_compact():
            return self.compact_equivariant_transporter(target_gram, (target_isometry,))
        assert len(self.isometries) == 1 and self.dimension() == 2 and not self.radical_basis()
        F = self.isometries[0]
        target_gram = matrix(QQ, target_gram)
        target_isometry = matrix(QQ, target_isometry)
        r = self.rank
        rows = []
        for i in range(r):
            for j in range(r):
                row = [0] * r**2
                for k in range(r):
                    row[i * r + k] += F[k, j]
                    row[k * r + j] -= target_isometry[i, k]
                rows.append(row)
        solutions = [matrix(QQ, r, r, list(v)) for v in matrix(QQ, rows).right_kernel().basis()]
        candidates = (*solutions, *(x + y for x in solutions for y in solutions))
        start = next((m for m in candidates if m.det() != 0), None)
        if start is None:
            return None
        source_gram = self.gram.change_ring(QQ)
        square = source_gram.inverse() * start.transpose() * target_gram * start
        scalar = square[0, 0]
        if square != scalar * identity_matrix(QQ, r):
            square_coordinates = self.coordinates(square)
            raise ArithmeticError(f"t_0^dagger t_0 is not rational: {square_coordinates}")
        generator = self._primitive_element()
        field = NumberField(generator.minimal_polynomial(), "a")
        assert field.signature() == (2, 0), "the commutant is not a real quadratic field"
        powers = matrix(QQ, [identity_matrix(QQ, r).list(), generator.change_ring(QQ).list()])
        coordinates = lambda m: field(list(powers.solve_left(vector(QQ, m.list()))))
        places = field.real_embeddings(prec=200)
        norm_target = abs(1 / scalar)
        units = [coordinates(matrix(QQ, g)) for g in self.commutative_centralizer_generators()]
        eta = max(max(abs(place(u)) for place in places) for u in units)
        assert eta > 1, "the norm-one units of the order are finite"
        basis_matrix = matrix(QQ, [(start * b.change_ring(QQ)).list() for b in self.order_basis])
        scale = basis_matrix.denominator()
        lattice = matrix(ZZ, scale * basis_matrix).saturation()
        combinations_ = [basis_matrix.solve_left(vector(QQ, row)) for row in lattice.rows()]
        elements = [sum(c * b.change_ring(QQ) for c, b in zip(v, self.order_basis)) for v in combinations_]
        values = [[place(coordinates(m)) for place in places] for m in elements]
        radius = norm_target.sqrt(prec=200)
        determinant = abs(values[0][0] * values[1][1] - values[1][0] * values[0][1])
        first_radius, second_radius = radius * eta, radius
        x_bound = int(((first_radius * abs(values[1][1]) + second_radius * abs(values[1][0])) / determinant).ceil()) + 1
        y_bound = int(((first_radius * abs(values[0][1]) + second_radius * abs(values[0][0])) / determinant).ceil()) + 1
        for x in range(-x_bound, x_bound + 1):
            for y in range(-y_bound, y_bound + 1):
                candidate = start * (x * elements[0] + y * elements[1])
                if candidate.denominator() != 1 or candidate.det() not in (1, -1):
                    continue
                if candidate.transpose() * target_gram * candidate == source_gram and candidate * F == target_isometry * candidate:
                    return matrix(ZZ, candidate)
        return None

    def _center_basis(self):
        r"""Return a `Q`-basis of the center of `A`."""
        size = self.dimension()
        rows = []
        for x in self.order_basis:
            rows.append(matrix(QQ, [(m * x - x * m).list() for m in self.order_basis]).transpose())
        equations = block_matrix(QQ, [[r] for r in rows], subdivide=False)
        return tuple(
            sum(c * m.change_ring(QQ) for c, m in zip(v, self.order_basis))
            for v in equations.right_kernel().basis()
        )

    @staticmethod
    def _integral_idempotent_atoms(idempotents):
        r"""Return the finest partition of the family whose block sums are integral."""
        size = len(idempotents)
        masks = [mask for mask in range(1, 2**size) if sum(idempotents[i] for i in range(size) if mask >> i & 1).denominator() == 1]
        atoms = []
        for i in range(size):
            atom = (2**size - 1)
            for mask in masks:
                if mask >> i & 1:
                    atom &= mask
            if atom not in atoms:
                atoms.append(atom)
        return [sum(idempotents[i] for i in range(size) if atom >> i & 1) for atom in atoms]

    def _product_centralizer_generators(self):
        r"""Return centralizer generators through a splitting by central idempotents, or ``None``.

        The sums `e_j` of adjoint orbits of primitive central idempotents of `A` are orthogonal
        under the form, so an integral family splits `L` orthogonally. Every element of `A`
        preserves each `e_j L`, so the centralizer is the product of the centralizers of the
        factors. A family with no integral partition goes to
        :meth:`_glued_centralizer_generators`.
        """
        if self.radical_basis():
            return None
        center = self._center_basis()
        if len(center) < 2 or len(center) == self.dimension():
            return None
        generic = None
        for values in product(range(-3, 4), repeat=len(center)):
            element = sum(c * m for c, m in zip(values, center))
            if element.minimal_polynomial().degree() == len(center):
                generic = element
                break
        assert generic is not None, "no generator of the center in the height box"
        minimal = generic.minimal_polynomial()
        factors = [factor for factor, _ in minimal.factor()]
        idempotents = []
        for factor in factors:
            cofactor = minimal // factor
            _d, inverse, _other = cofactor.xgcd(factor)
            idempotents.append((inverse * cofactor)(generic))
        family = []
        for idempotent in idempotents:
            adjoint = self.adjoint(idempotent)
            merged = idempotent if adjoint == idempotent else idempotent + adjoint
            if merged not in family:
                family.append(merged)
        if len(family) < 2:
            return None
        idempotents = self._integral_idempotent_atoms(family)
        if len(idempotents) < 2:
            return self._glued_centralizer_generators(family)
        results = []
        for index, idempotent in enumerate(idempotents):
            image = matrix(ZZ, idempotent).transpose().row_module().basis_matrix()
            coordinates = image.change_ring(QQ)
            gram_block = matrix(ZZ, image * self.gram * image.transpose())
            pieces = [
                coordinates.solve_left(vector(QQ, (F * row).list()))
                for F in self.isometries
                for row in image.rows()
            ]
            size = image.nrows()
            restricted = [
                matrix(ZZ, [pieces[k * size + i] for i in range(size)]).transpose()
                for k in range(len(self.isometries))
            ]
            for generator in _factor_centralizer_generators(IsometryCommutant(gram_block, restricted)):
                basis = image.stack(matrix(ZZ, sum((matrix(ZZ, e).transpose().row_module().basis_matrix().rows() for j, e in enumerate(idempotents) if j != index), [])))
                block = identity_matrix(ZZ, self.rank)
                block[:size, :size] = generator.transpose()
                results.append(matrix(ZZ, basis.transpose().change_ring(QQ) * block.transpose().change_ring(QQ) * basis.transpose().change_ring(QQ).inverse()))
        return tuple(results)

    def _glued_centralizer_generators(self, idempotents):
        r"""Return centralizer generators through adjoint-fixed central idempotents that are not integral.

        A centralizer element lies in `A`, so it commutes with each `e_j` and preserves
        `e_j L`. Hence `M = \bigoplus_j e_j L` contains `L` with finite index, and the centralizer
        is the stabilizer of `L` in `\prod_j C(e_j L)`, each factor carrying the restricted
        form scaled to be integral. The orbit of `L` lies in the finite set of lattices between
        `M` and `d M`, for `d` the exponent of `M / L`. Schreier's lemma gives the generators.
        """
        blocks = []
        for idempotent in idempotents:
            denominator = idempotent.denominator()
            span = matrix(ZZ, denominator * idempotent).transpose().hermite_form(include_zero_rows=False)
            blocks.append(matrix(QQ, span).transpose() / denominator)
        frame = block_matrix(QQ, [blocks], subdivide=False)
        assert frame.is_square() and frame.det() != 0, f"the projections {blocks} do not span the ambient space"
        to_frame = frame.inverse()
        lattice = matrix(ZZ, to_frame)
        one = identity_matrix(ZZ, self.rank)
        generators = []
        offset = 0
        for basis in blocks:
            form = basis.transpose() * self.gram * basis
            scaled = matrix(ZZ, form.denominator() * form)
            restricted = [matrix(ZZ, basis.solve_right(F * basis)) for F in self.isometries]
            size = basis.ncols()
            for generator in _factor_centralizer_generators(IsometryCommutant(scaled, restricted)):
                move = identity_matrix(ZZ, self.rank)
                move[offset : offset + size, offset : offset + size] = generator
                generators.append(move)
            offset += size

        def key(element):
            return (element * lattice).transpose().hermite_form(include_zero_rows=False).str()

        transversal = {key(one): one}
        frontier = [one]
        schreier = {}
        while frontier:
            current = frontier.pop()
            for generator in generators:
                image = generator * current
                label = key(image)
                if label not in transversal:
                    transversal[label] = image
                    frontier.append(image)
                    continue
                element = transversal[label].inverse().change_ring(ZZ) * image
                if element != one:
                    schreier[element.str()] = element
        result = tuple(frame * element * to_frame for element in schreier.values())
        assert all(self.is_centralizer_element(g) for g in result)
        return tuple(matrix(ZZ, g) for g in result)

    def trace_form(self):
        r"""Return the Gram matrix of `(x, y) \mapsto \mathrm{Tr}(x^\dagger y)` on the order basis."""
        return matrix(QQ, [[(self.adjoint(x) * y).trace() for y in self.order_basis] for x in self.order_basis])

    def is_compact(self):
        r"""Decide whether the real unitary group `\{u \in A_R : u^\dagger u = 1\}` is compact.

        It is compact exactly when the trace form is positive definite: then
        `\mathrm{Tr}(u^\dagger u) = r` bounds the group, and otherwise an `x` with
        `\mathrm{Tr}(x^\dagger x) \le 0` gives a noncompact one-parameter subgroup
        (Weil, *Algebras with involutions and the classical groups*, J. Indian Math. Soc. 24 (1960), \S 2).
        """
        return self.trace_form().is_positive_definite()

    def compact_centralizer_elements(self):
        r"""Return every element of the centralizer when it is finite.

        A centralizer element `u` lies in `O` with `\mathrm{Tr}(u^\dagger u) = \mathrm{Tr}(1) = r`,
        so it is among the vectors of the positive definite trace form of norm at most `r`.
        This covers every compact commutant: nonsplit (for example definite quaternion), nonmaximal and glued.
        """
        assert self.is_compact(), f"the unitary group of the commutant of {self.isometries} is not compact"
        result = []
        for coordinates in _short_vectors(self.trace_form(), self.rank):
            element = sum(c * m for c, m in zip(coordinates, self.order_basis))
            if self.is_centralizer_element(element):
                result.append(matrix(ZZ, element))
        return tuple(result)

    def compact_equivariant_transporter(self, target_gram, target_isometries):
        r"""Return `t \in GL_r(Z)` with `t^t B' t = B` and every `t F_i = F'_i t`, or ``None``, for compact `A`.

        On the integral intertwiners `I`, `Q(x) = \mathrm{Tr}(B^{-1} x^t B' x)`. For a solution
        `t_1`, `x = t_1 a` identifies `I_Q` with `A` and `Q(t_1 a) = \mathrm{Tr}(a^\dagger a)`, so `Q`
        is positive definite and every solution has `Q(t) = r`. ``None`` is therefore a proof
        when `Q` is not positive definite or no vector of norm at most `r` is a solution.
        """
        assert self.is_compact()
        target_gram = matrix(ZZ, target_gram)
        targets = tuple(matrix(ZZ, self.rank, self.rank, T) for T in target_isometries)
        assert len(targets) == len(self.isometries)
        r = self.rank
        rows = []
        for F, T in zip(self.isometries, targets):
            for i in range(r):
                for j in range(r):
                    row = [0] * r**2
                    for k in range(r):
                        row[i * r + k] += F[k, j]
                        row[k * r + j] -= T[i, k]
                    rows.append(row)
        basis = [matrix(ZZ, r, r, list(v)) for v in matrix(ZZ, rows).right_kernel().basis()]
        if len(basis) != self.dimension():
            return None
        inverse = self.gram.change_ring(QQ).inverse()
        form = matrix(QQ, [[(inverse * x.transpose() * target_gram * y).trace() for y in basis] for x in basis])
        if not form.is_positive_definite():
            return None
        for coordinates in _short_vectors(form, r):
            candidate = sum(c * m for c, m in zip(coordinates, basis))
            if candidate.det() in (1, -1) and candidate.transpose() * target_gram * candidate == self.gram:
                assert all(candidate * F == T * candidate for F, T in zip(self.isometries, targets))
                return candidate
        return None

    def centralizer_generators(self):
        r"""Return generators of the simultaneous centralizer, by the structure of `A`."""
        if self.is_compact():
            return self.compact_centralizer_elements()
        split = self._product_centralizer_generators()
        if split is not None:
            return split
        radical = self.radical_basis()
        if radical and self.dimension() - len(radical) == 1:
            # A / rad = Q: a unit is +-(1 + x) with x in the radical, and -1 is central.
            return (-identity_matrix(ZZ, self.rank), *self.unipotent_kernel_generators())
        if radical:
            return self.radical_centralizer_generators()
        if all(x * y == y * x for x in self.order_basis for y in self.order_basis):
            return self.commutative_centralizer_generators()
        return self.simple_centralizer_generators()

    def _primitive_element(self):
        r"""Return an integral generator of a commutative semisimple `A`, by increasing height.

        Over `Q` the elements failing to generate lie in finitely many proper subspaces, so
        the search ends.
        """
        size = self.dimension()
        for height in count(1):
            for values in product(range(-height, height + 1), repeat=size):
                element = sum(c * m for c, m in zip(values, self.order_basis))
                polynomial = element.minimal_polynomial()
                if polynomial.degree() == size and polynomial.is_squarefree():
                    return element

    def commutative_centralizer_generators(self):
        r"""Return generators of the centralizer when the commutant `A` is a product of fields.

        Let `a` generate `A`, with squarefree minimal polynomial `\prod p_j` and
        `K_j = Q[x]/p_j`. The adjoint permutes the factors. On a fixed factor the unitary
        equation is `u \sigma(u) = 1`, solved on the Dirichlet unit group. On a swapped
        pair, `u` is any unit of one factor and determines the other. These generate the
        norm-one units of the maximal order, and `O` has finite index in it, so Schreier's
        lemma on membership in `O` gives the subgroup.
        """
        size = self.dimension()
        assert not self.radical_basis() and all(
            x * y == y * x for x in self.order_basis for y in self.order_basis
        ), f"the commutant of {self.isometries} is not commutative semisimple"
        generator = self._primitive_element()
        minimal = generator.minimal_polynomial().change_ring(QQ)
        factors = tuple(factor for factor, _multiplicity in minimal.factor())
        fields = tuple(NumberField(factor, "a") if factor.degree() > 1 else QQ for factor in factors)
        element_of = lambda j, polynomial: fields[j](polynomial) if factors[j].degree() > 1 else polynomial(-factors[j][0] / factors[j][1])
        powers = matrix(QQ, [(generator.change_ring(QQ) ** k).list() for k in range(size)])
        ring = minimal.parent()
        adjoint_polynomial = ring(list(powers.solve_left(vector(QQ, self.adjoint(generator).list()))))
        thetas = tuple(element_of(j, adjoint_polynomial) for j in range(len(factors)))
        partner = tuple(
            next(i for i, factor in enumerate(factors) if factor(thetas[j]) == 0) for j in range(len(factors))
        )

        def to_matrix(values):
            residues = [ring(v.polynomial()) if factors[j].degree() > 1 else ring(v) for j, v in enumerate(values)]
            combined = crt(residues, list(factors)) if len(factors) > 1 else residues[0]
            return sum(
                c * generator.change_ring(QQ) ** k for k, c in enumerate(combined.padded_list(size))
            )

        def unit_generators(j):
            if factors[j].degree() == 1:
                return (QQ(-1),)
            return tuple(fields[j](u) for u in fields[j].unit_group().gens())

        moves = []
        done = set()
        for j, field in enumerate(fields):
            if j in done:
                continue
            ones = [fields[i](1) for i in range(len(fields))]
            if partner[j] == j:
                done.add(j)
                for u in self._norm_one_generators(field, thetas[j], factors[j]):
                    entry = list(ones)
                    entry[j] = u
                    moves.append(to_matrix(entry))
            else:
                other = partner[j]
                done |= set((j, other))
                for u in unit_generators(j):
                    entry = list(ones)
                    entry[j] = u
                    inverse = ~u
                    if factors[j].degree() > 1:
                        entry[other] = field.hom([thetas[other]])(inverse)
                    else:
                        entry[other] = inverse
                    moves.append(to_matrix(entry))
        return self._order_subgroup_generators(moves)

    @staticmethod
    def _norm_one_generators(field, theta, factor):
        r"""Return generators of the units `u` of `field` with `u \sigma(u) = 1`, `\sigma(a) = \theta`."""
        if factor.degree() == 1:
            return (QQ(-1),)
        conjugate = field.hom([theta])
        units = field.unit_group()
        values = tuple(field(u) for u in units.gens())
        relation = matrix(ZZ, [list(units.log(v * conjugate(v))) for v in values])
        torsion = units.torsion_generator().order()
        columns = relation.ncols()
        extended = relation.stack(matrix(ZZ, [[torsion if j == 0 else 0 for j in range(columns)]]))
        generators = []
        for row in extended.left_kernel().basis():
            element = field.one()
            for value, exponent in zip(values, row[: len(values)]):
                element = element * value ** int(exponent)
            generators.append(element)
        return tuple(u for u in generators if u != 1)

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


def _lift_idempotent(element):
    r"""Return the idempotent lifting ``element``, idempotent modulo a nilpotent ideal containing `e^2 - e`.

    The iteration `e \mapsto 3e^2 - 2e^3` moves `e^2 - e` from `I^k` into `I^{2k}` (Lam, *A First Course in
    Noncommutative Rings*, Thm. 21.28), so it stops at an exact idempotent.
    """
    while True:
        square = element * element
        if square == element:
            return element
        element = 3 * square - 2 * square * element


def _splitting_idempotents(element, minimal):
    r"""Return `\iota_i(x)` for the coprime factorization `\mu = \prod_i P_i` into prime powers, `\iota_i \equiv \delta_{ij} \bmod P_j`."""
    result = []
    for factor, multiplicity in minimal.factor():
        power = factor**multiplicity
        cofactor = minimal // power
        _d, inverse, _other = cofactor.xgcd(power)
        result.append((inverse * cofactor)(element))
    return result


def _general_linear_generators(size):
    r"""Return generators of `GL_n(Z)`: the elementary matrices and `\mathrm{diag}(-1, 1, \ldots)`.

    Elementary matrices generate `SL_n(Z)` since `Z` is Euclidean (Hahn-O'Meara, *The Classical Groups and
    K-Theory*, 1.2.10), and `\mathrm{diag}(-1, 1, \ldots)` has determinant `-1`.
    """
    sign = identity_matrix(ZZ, size)
    sign[0, 0] = -1
    result = [sign]
    for i in range(size):
        for j in range(size):
            if i != j:
                move = identity_matrix(ZZ, size)
                move[i, j] = 1
                result.append(move)
    return result


class LeviQuotient:
    r"""The Levi modules and forms of a commutant `A` with radical, for `A / rad = \prod_k M_{n_k}(Q)`.

    Let `S = A / rad` with central primitive idempotents `\bar c_k` and `S_k = \bar c_k S \cong M_{n_k}(Q)`. For a
    primitive idempotent `e_k` of `A` over `S_k` (lifted modulo the nilpotent radical), `\bar M_k = O e_k / rad\, e_k`
    is a lattice on which `S_k` acts as `M_{n_k}(Q)` and the other factors act as zero; `S` acts faithfully on
    `\bar M = \bigoplus_k \bar M_k`, and the image `\bar O` of `O` is an order of finite index in `\prod_k End(\bar M_k)`.
    The adjoint permutes the factors, `\bar c_k^\dagger = \bar c_{\pi(k)}`. Since `e_j^\dagger` lies over `S_{\pi(j)}`, the
    space `e_j^\dagger A e_{\pi(j)}` is a line modulo the radical, and `x^\dagger h y = b^h_j(x, y)\, t_j` defines pairings
    `\bar M_j \times \bar M_{\pi(j)} \to Q` for self-adjoint `h`. A rational `\bar a = (g_k)` is the image of a solution of
    `a^\dagger h a = 1` exactly when `g_j^t G^h_j g_{\pi(j)} = G_j` for every `j`: the orthogonal or symplectic group
    of `G_j` when `\pi(j) = j`, and `GL(\bar M_j)` with `g_{\pi(j)} = G_j^{-1} g_j^{-t} G_j` for a swapped pair.

    The integral image `\bar\Gamma` of `C(Z)` is an arithmetic subgroup of finite index in the group `H` generated by
    these factor groups (Platonov-Rapinchuk, *Algebraic Groups and Number Theory*, Thm. 4.1). A preimage `p` of
    `\bar a` has `d = p^\dagger h p - 1` self-adjoint in the radical, so `p (1 + d)^{-1/2}` is a rational solution,
    and all solutions over `\bar a` are `p (1 + d)^{-1/2} N(Q)`, decided by :meth:`IsometryCommutant._integral_point`.
    A factor whose centre is a field `\ne Q` or that is not split raises :class:`NotImplementedError`.
    """

    def __init__(self, commutant):
        self.commutant = commutant
        radical = commutant.radical_basis()
        assert radical, f"the commutant of {commutant.isometries} is semisimple"
        size = commutant.dimension()
        radical_rows = matrix(QQ, [commutant.coordinates(x) for x in radical])
        radical_lattice = matrix(ZZ, radical_rows.denominator() * radical_rows).saturation()
        _diagonal, _left, change = radical_lattice.smith_form()
        kernel_rank = radical_lattice.nrows()
        self._project = lambda element: (commutant.coordinates(element) * change.change_ring(QQ))[kernel_rank:]
        inverse_change = change.inverse().change_ring(QQ)
        order = [m.change_ring(QQ) for m in commutant.order_basis]
        self._order = order
        self._section = tuple(
            sum(c * m for c, m in zip(inverse_change.row(kernel_rank + i), order)) for i in range(size - kernel_rank)
        )
        project, section = self._project, self._section
        equations = block_matrix(
            QQ, [[matrix(QQ, [project(x * m - m * x) for x in section]).transpose()] for m in order], subdivide=False
        )
        center = [sum(c * x for c, x in zip(v, section)) for v in equations.right_kernel().basis()]
        left = lambda element: matrix(QQ, [project(element * x) for x in section])
        generic = next(
            (
                z
                for values in product(range(-3, 4), repeat=len(center))
                for z in (sum(c * m for c, m in zip(values, center)),)
                if left(z).minimal_polynomial().degree() == len(center)
            ),
            None,
        )
        if generic is None:
            raise ArithmeticError(f"no generator of the centre of the Levi quotient of {commutant.isometries} in the box")
        minimal = left(generic).minimal_polynomial()
        if any(factor.degree() != 1 for factor, _m in minimal.factor()):
            raise NotImplementedError(
                f"the Levi quotient of the commutant of {commutant.isometries} has a central factor field of degree > 1 "
                f"(centre minimal polynomial {minimal}); its unitary group has no Levi-module route (#54)"
            )
        self._central = _splitting_idempotents(generic, minimal)
        self.degrees = []
        self._idempotents = []
        for c in self._central:
            dimension = matrix(QQ, [project(c * x) for x in section]).rank()
            n = ZZ(dimension).isqrt()
            if n**2 != dimension:
                raise NotImplementedError(
                    f"a factor of dimension {dimension} of the Levi quotient of the commutant of {commutant.isometries} "
                    f"is not M_n(Q); a division Levi factor has no Levi-module route (#54)"
                )
            self.degrees.append(n)
            self._idempotents.append(self._primitive(c, n))
        self._bases, self._lifts = [], []
        for e, n in zip(self._idempotents, self.degrees):
            images = matrix(QQ, [project(m * e) for m in order])
            hermite = matrix(ZZ, images.denominator() * images).hermite_form(include_zero_rows=False)
            assert hermite.nrows() == n
            basis = matrix(QQ, hermite) / images.denominator()
            self._bases.append(basis)
            self._lifts.append([sum(c * m for c, m in zip(images.solve_left(row), order)) * e for row in basis.rows()])
        self.offsets = [sum(self.degrees[:k]) for k in range(len(self.degrees))]
        self.size = sum(self.degrees)
        action_rows = matrix(QQ, [self._flatten(self.on_module(x)) for x in section])
        assert action_rows.is_square() and action_rows.denominator() == 1 and action_rows.det() != 0
        self._action_inverse = action_rows.inverse()
        self.partner = [
            next(j for j, other in enumerate(self._central) if all(v == 0 for v in project(commutant.adjoint(c) - other)))
            for c in self._central
        ]
        self._lines = []
        for j, e in enumerate(self._idempotents):
            other = self._idempotents[self.partner[j]]
            line = matrix(QQ, [project(commutant.adjoint(e) * m * other) for m in order])
            generator = matrix(QQ, matrix(ZZ, line.denominator() * line).hermite_form(include_zero_rows=False))
            assert generator.nrows() == 1
            self._lines.append(generator / line.denominator())
        one = identity_matrix(QQ, commutant.rank)
        self.grams = [self.form(one, j) for j in range(len(self.degrees))]

    def _primitive(self, central, degree):
        r"""Return a primitive idempotent of `A` over the factor of ``central``: `\dim \bar e S \bar e = 1`.

        Candidates are the idempotents `\iota_i(y)` of the primary decomposition of `y = c\, m` for order elements
        `m` and their products, lifted by :func:`_lift_idempotent`.
        """
        project, order = self._project, self._order
        corner = lambda a: matrix(QQ, [project(a * m * a) for m in order]).rank()
        if degree == 1:
            return _lift_idempotent(central)
        left = lambda element: matrix(QQ, [project(element * x) for x in self._section])
        found = []
        for m in order:
            y = central * m * central
            for a in _splitting_idempotents(y, left(y).minimal_polynomial()):
                a = central * a * central
                if all(v == 0 for v in project(a * a - a)) and any(v != 0 for v in project(a)):
                    found.append(a)
        for a in found:
            if corner(a) == 1:
                return _lift_idempotent(a)
        for a, b in product(found, repeat=2):
            for c in (a * b * a, a * b, b * a * b):
                if all(v == 0 for v in project(c * c - c)) and any(v != 0 for v in project(c)) and corner(c) == 1:
                    return _lift_idempotent(c)
        raise ArithmeticError(
            f"no primitive idempotent of the factor M_{degree}(Q) of the Levi quotient of {self.commutant.isometries} "
            f"among the primary idempotents of order elements"
        )

    def _block(self, matrix_, k):
        o, n = self.offsets[k], self.degrees[k]
        return matrix_[o : o + n, o : o + n]

    def _flatten(self, blocks):
        return [c for k in range(len(self.degrees)) for c in self._block(blocks, k).list()]

    def block_diagonal(self, blocks):
        result = matrix(QQ, self.size, self.size)
        for k, block in enumerate(blocks):
            o, n = self.offsets[k], self.degrees[k]
            result[o : o + n, o : o + n] = block
        return result

    def on_module(self, element):
        r"""Return the block-diagonal action of ``element`` on `\bar M = \bigoplus_k \bar M_k`."""
        return self.block_diagonal(
            [
                matrix(QQ, [basis.solve_left(self._project(element * m)) for m in lifts]).transpose()
                for basis, lifts in zip(self._bases, self._lifts)
            ]
        )

    def form(self, middle, j):
        r"""Return `G^h_j`, the Gram of `b^h_j` on `\bar M_j \times \bar M_{\pi(j)}`, `h =` ``middle``."""
        adjoint = self.commutant.adjoint
        return matrix(
            QQ,
            [
                [self._lines[j].solve_left(self._project(adjoint(x) * middle * y))[0] for y in self._lifts[self.partner[j]]]
                for x in self._lifts[j]
            ],
        )

    def group_generators(self):
        r"""Return block-diagonal generators of `H`: `O(G_j)` for `\pi(j) = j`, `GL(\bar M_j)` for a swapped pair."""
        result = []
        identity_blocks = [identity_matrix(QQ, n) for n in self.degrees]
        for j, k in enumerate(self.partner):
            if k < j:
                continue
            gram = self.grams[j]
            if k == j:
                moves = [(g,) for g in _form_generators(matrix(ZZ, gram.denominator() * gram))]
            else:
                moves = [(g, gram.inverse() * g.transpose().inverse() * gram) for g in _general_linear_generators(self.degrees[j])]
            for move in moves:
                blocks = list(identity_blocks)
                blocks[j] = matrix(QQ, move[0])
                if k != j:
                    blocks[k] = move[1]
                result.append(self.block_diagonal(blocks))
        return result

    def lift(self, start, middle, isometry):
        r"""Return an integral `t_0 a` with `\bar a =` ``isometry`` and `a^\dagger h a = 1`, or ``None``."""
        commutant = self.commutant
        combination = vector(QQ, self._flatten(isometry)) * self._action_inverse
        preimage = sum(c * m for c, m in zip(combination, self._section))
        defect = commutant.adjoint(preimage) * middle * preimage - identity_matrix(QQ, commutant.rank)
        nilpotency = commutant._radical_nilpotency()[0]
        assert (defect ** (nilpotency + 1)).is_zero() and commutant.adjoint(defect) == defect
        root = sum(binomial(QQ((-1, 2)), k) * defect**k for k in range(nilpotency + 1))
        return commutant._integral_point(start * preimage * root, 1)

    def coset_representatives(self):
        r"""Return representatives `g` of the left cosets `g \bar\Gamma` in `H`; `x \bar\Gamma = y \bar\Gamma` when `y^{-1} x` lifts."""
        if not hasattr(self, "_cosets"):
            one = identity_matrix(QQ, self.commutant.rank)
            representatives = [identity_matrix(QQ, self.size)]
            position = 0
            while position < len(representatives):
                current = representatives[position]
                position += 1
                for generator in self.group_generators():
                    moved = generator * current
                    if not any(self.lift(one, one, known.inverse() * moved) is not None for known in representatives):
                        representatives.append(moved)
            self._cosets = tuple(representatives)
        return self._cosets

    def centralizer_generators(self):
        r"""Return the unipotent kernel and lifts of generators of `\bar\Gamma` (Schreier's lemma on liftability)."""
        from sage_extensions.categories.lattice_centralizers import finite_preimage_generators

        commutant = self.commutant
        one = identity_matrix(QQ, commutant.rank)
        generators = self.group_generators()
        lifts = [self.lift(one, one, g) for g in generators]
        if any(value is None for value in lifts):
            image, _index = finite_preimage_generators(
                generators, lambda element: element, lambda element: self.lift(one, one, element) is not None
            )
            lifts = [self.lift(one, one, g) for g in image]
        assert all(commutant.is_centralizer_element(g) for g in lifts)
        return (*commutant.unipotent_kernel_generators(), *lifts)
