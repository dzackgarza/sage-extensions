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
from sage.arith.misc import factorial
from sage.matrix.constructor import matrix
from sage.matrix.special import identity_matrix
from sage.modules.free_module_element import vector
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

    def _primitive_idempotent(self, degree):
        r"""Return an idempotent of `O` of rank `r / degree`, found among sparse elements."""
        target = self.rank / degree
        size = len(self.order_basis)
        for support in range(1, min(size, 3) + 1):
            for positions in combinations(range(size), support):
                for values in product((-2, -1, 1, 2), repeat=support):
                    element = sum(c * self.order_basis[i] for c, i in zip(values, positions))
                    if element * element == element and element.rank() == target:
                        return element
        raise ArithmeticError(
            f"no idempotent of rank {target} among sparse elements of the order of {self.isometries}"
        )

    def simple_centralizer_generators(self):
        r"""Return generators of the centralizer when `O` is a maximal order `M_n(Z)`.

        For a rank-`r/n` idempotent `e`, `M = O e` is free of rank `n` and `O = End(M)`.
        The space `e^\dagger O e` has rank one, so `x^\dagger y = b(x, y) t` defines an
        integral form on `M`. A unit `u` satisfies `u^\dagger u = 1` exactly when it
        preserves `b`, so the centralizer is the isometry group of `(M, b)`: orthogonal
        when `b` is symmetric, symplectic when alternating.
        """
        assert not self.radical_basis(), f"the commutant of {self.isometries} is not semisimple"
        degree = ZZ(self.dimension()).isqrt()
        assert degree**2 == self.dimension(), f"the commutant of {self.isometries} is not M_n(Q)"
        e = self._primitive_idempotent(degree)
        span = matrix(ZZ, [(m * e).list() for m in self.order_basis]).hermite_form(include_zero_rows=False)
        assert span.nrows() == degree
        module = tuple(matrix(ZZ, self.rank, self.rank, list(row)) for row in span.rows())
        coordinates = matrix(QQ, span)

        def on_module(element):
            return matrix(
                QQ, [coordinates.solve_left(vector(QQ, (element * m).list())) for m in module]
            ).transpose()

        action_rows = matrix(QQ, [on_module(m).list() for m in self.order_basis])
        assert action_rows.denominator() == 1 and abs(action_rows.det()) == 1, (
            f"the order of the commutant of {self.isometries} is not End(O e)"
        )
        adjoint_e = self.adjoint(e)
        line = matrix(QQ, [(adjoint_e * m * e).list() for m in self.order_basis])
        scale = line.denominator()
        generator = matrix(ZZ, scale * line).hermite_form(include_zero_rows=False)
        assert generator.nrows() == 1
        generator = matrix(QQ, generator) / scale
        gram = matrix(
            ZZ,
            [
                [
                    generator.solve_left(vector(QQ, (self.adjoint(x) * y).list()))[0]
                    for y in module
                ]
                for x in module
            ],
        )
        isometries = _form_generators(gram)
        inverse = action_rows.inverse()
        result = []
        for isometry in isometries:
            combination = vector(QQ, isometry.list()) * inverse
            element = sum(c * m.change_ring(QQ) for c, m in zip(combination, self.order_basis))
            assert self.is_centralizer_element(element)
            result.append(matrix(ZZ, element))
        return tuple(result)

    def square_zero_centralizer_generators(self):
        r"""Return generators of the centralizer when `rad^2 = 0` and `O / rad` is `M_n(Z)`.

        `O / (O \cap rad)` acts on `\bar M = O e / (rad e)`, carrying the form defined by
        `x^\dagger y = b(x, y) t` modulo the radical. For an isometry of `\bar M` with a
        preimage `\bar u` in `O`, a lift is `\bar u + x` with `x` integral in the radical,
        and since `rad^2 = 0` the unitary equation
        `\bar u^\dagger x + x^\dagger \bar u = 1 - \bar u^\dagger \bar u` is linear.
        Lifting a generating set proves the image is the whole isometry group; the
        kernel is :meth:`unipotent_kernel_generators`.
        """
        radical = self.radical_basis()
        assert radical and all((x * y).is_zero() for x in radical for y in radical), (
            f"the commutant of {self.isometries} does not have a nonzero radical of square zero"
        )
        size = self.dimension()
        radical_rows = matrix(QQ, [self.coordinates(x) for x in radical])
        scale = radical_rows.denominator()
        radical_lattice = matrix(ZZ, scale * radical_rows).saturation()
        _diagonal, _left, change = radical_lattice.smith_form()
        kernel_rank = radical_lattice.nrows()
        project = lambda element: (self.coordinates(element) * change.change_ring(QQ))[kernel_rank:]
        inverse_change = change.inverse().change_ring(QQ)
        section = tuple(
            sum(c * m.change_ring(QQ) for c, m in zip(inverse_change.row(kernel_rank + i), self.order_basis))
            for i in range(size - kernel_rank)
        )
        quotient_dimension = size - kernel_rank
        degree = ZZ(quotient_dimension).isqrt()
        assert degree**2 == quotient_dimension, f"the semisimple quotient of the commutant is not M_n(Q)"
        e = self._primitive_idempotent(degree)
        images = matrix(QQ, [project(m * e) for m in self.order_basis])
        denominator = images.denominator()
        hermite = matrix(ZZ, denominator * images).hermite_form(include_zero_rows=False)
        assert hermite.nrows() == degree
        basis = matrix(QQ, hermite) / denominator
        lifts = [
            sum(c * m for c, m in zip(combination, self.order_basis)) * e
            for combination in (images.solve_left(row) for row in basis.rows())
        ]

        def on_module(element):
            return matrix(QQ, [basis.solve_left(project(element * m)) for m in lifts]).transpose()

        action_rows = matrix(QQ, [on_module(m).list() for m in section])
        assert action_rows.denominator() == 1 and abs(action_rows.det()) == 1, (
            f"the semisimple quotient of the order of the commutant of {self.isometries} is not End(M)"
        )
        adjoint_e = self.adjoint(e)
        line = matrix(QQ, [project(adjoint_e * m.change_ring(QQ) * e) for m in self.order_basis])
        line_scale = line.denominator()
        generator = matrix(QQ, matrix(ZZ, line_scale * line).hermite_form(include_zero_rows=False)) / line_scale
        assert generator.nrows() == 1
        gram = matrix(
            ZZ,
            [[generator.solve_left(project(self.adjoint(x) * y))[0] for y in lifts] for x in lifts],
        )
        identity = identity_matrix(QQ, self.rank)
        radical_integral = tuple(
            sum(c * m.change_ring(QQ) for c, m in zip(row, self.order_basis)) for row in radical_lattice.rows()
        )
        action_inverse = action_rows.inverse()
        generators = list(self.unipotent_kernel_generators())
        for isometry in _form_generators(gram):
            combination = vector(QQ, isometry.list()) * action_inverse
            preimage = sum(c * m for c, m in zip(combination, section))
            preimage_adjoint = self.adjoint(preimage)
            columns = [(preimage_adjoint * x + self.adjoint(x) * preimage).list() for x in radical_integral]
            equations = matrix(QQ, columns).transpose()
            target = vector(QQ, (identity - preimage_adjoint * preimage).list())
            common = lcm([equations.denominator(), target.denominator()])
            solution = _integer_solution(matrix(ZZ, common * equations), vector(ZZ, common * target))
            assert solution is not None, (
                f"the isometry {isometry} of the semisimple quotient has no integral unitary lift"
            )
            element = preimage + sum(c * x for c, x in zip(solution, radical_integral))
            assert self.is_centralizer_element(element)
            generators.append(matrix(ZZ, element))
        return tuple(generators)

    def inversion_transporter(self):
        r"""Return `t \in O(L)` with `t F t^{-1} = F^{-1}`, or ``None``, for `A` a real quadratic field."""
        F = self.isometries[0]
        return self.equivariant_transporter(self.gram, F.inverse())

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

    def centralizer_generators(self):
        r"""Return generators of the simultaneous centralizer, by the structure of `A`."""
        radical = self.radical_basis()
        if radical and self.dimension() - len(radical) == 1:
            # A / rad = Q: a unit is +-(1 + x) with x in the radical, and -1 is central.
            return (-identity_matrix(ZZ, self.rank), *self.unipotent_kernel_generators())
        if radical:
            return self.square_zero_centralizer_generators()
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
        one = identity_matrix(QQ, self.rank)
        moves = [m for m in moves if m != one]
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
