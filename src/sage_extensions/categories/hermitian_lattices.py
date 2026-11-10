r"""Hermitian lattices over an order of a CM number field.

A Hermitian lattice is a free module over an order ``O`` of a CM field ``K``
with a Hermitian form ``h``. Its trace lattice is the same abelian group with
``b(x, y) = Tr_{K/QQ} h(x, y)``. Since ``Tr(alpha h) = 0`` for all ``alpha``
forces ``h = 0``, the unitary group is the centralizer of the ``O``-action in
the orthogonal group of the trace lattice.
"""

from copy import copy
from itertools import product

from sage.arith.functions import lcm
from sage.matrix.constructor import matrix
from sage.modules.free_module_element import vector
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.sage_object import SageObject

from sage_extensions.categories.lattices import Lattices


class HermitianLattice(SageObject):
    r"""The free ``O``-module ``O^n`` with Hermitian Gram matrix ``gram``.

    ``order_basis`` is a ``ZZ``-basis of the order ``O`` in a CM field.
    """

    def __init__(self, order_basis, gram) -> None:
        self._order_basis = tuple(order_basis)
        self._gram = matrix(gram)
        self._field = self._gram.base_ring()
        rank = self._gram.nrows()
        if self._gram.ncols() != rank:
            raise ValueError("a Hermitian Gram matrix must be square")
        if any(self._gram[i, j] != self._gram[j, i].conjugate() for i in range(rank) for j in range(rank)):
            raise ValueError("the Gram matrix is not Hermitian")
        if self._gram.det() == 0:
            raise ValueError("a Hermitian lattice here is nondegenerate")
        self._basis_matrix = matrix(SageQQ, [list(element.vector()) for element in self._order_basis])
        if self._basis_matrix.nrows() != self._field.degree() or self._basis_matrix.det() == 0:
            raise ValueError("the order basis must be a QQ-basis of the field")

    def __repr__(self) -> str:
        return f"Hermitian lattice of rank {self.rank()} over {self._field}"

    def field(self):
        return self._field

    def order_basis(self):
        return self._order_basis

    def rank(self):
        return self._gram.nrows()

    def gram_matrix(self):
        return self._gram

    def h(self, x, y):
        r"""Return ``h(x, y)`` for coordinate vectors over ``K``."""
        return sum(x[i] * self._gram[i, j] * y[j].conjugate() for i in range(self.rank()) for j in range(self.rank()))

    def _labels(self):
        return tuple((i, a) for i in range(self.rank()) for a in range(len(self._order_basis)))

    @cached_method
    def trace_lattice(self):
        r"""Return the ``ZZ``-lattice ``(O^n, Tr h)``."""
        from sage_extensions.all import ZZ

        labels = self._labels()
        basis = self._order_basis
        rows = [
            [(basis[a] * self._gram[i, j] * basis[b].conjugate()).trace() for j, b in labels]
            for i, a in labels
        ]
        if any(entry not in SageZZ for row in rows for entry in row):
            raise ValueError("the trace form of this Hermitian form is not integral on the order")
        return Lattices(ZZ)([[int(entry) for entry in row] for row in rows])

    def _coordinates_in_order(self, element):
        vector_ = (matrix(SageQQ, [list(element.vector())]) * ~self._basis_matrix).row(0)
        if any(entry not in SageZZ for entry in vector_):
            raise ValueError(f"{element} does not lie in the order")
        return tuple(int(entry) for entry in vector_)

    def order_action(self, element):
        r"""Return multiplication by ``element`` of ``O`` as an endomorphism of the trace lattice."""
        lattice = self.trace_lattice()
        labels = self._labels()
        names = tuple(lattice.module_generating_set())
        positions = {label: name for label, name in zip(labels, names, strict=True)}
        images = {}
        for (i, a), name in positions.items():
            coordinates = self._coordinates_in_order(element * self._order_basis[a])
            images[name] = lattice.linear_combination({
                positions[(i, b)]: lattice.base_ring()(value) for b, value in enumerate(coordinates) if value
            })
        return lattice.module_category().Mor(lattice, lattice)(images)

    def unit_isometry(self, unit):
        r"""Return multiplication by a norm-one unit as an isometry of the trace lattice."""
        if unit * unit.conjugate() != self._field.one():
            raise ValueError(f"{unit} is not a norm-one element: its multiplication is not an isometry")
        lattice = self.trace_lattice()
        action = self.order_action(unit)
        return lattice.Aut()(lambda label: action(lattice.module_generator(label)))

    def isometry_from_matrix(self, g):
        r"""Return the isometry of the trace lattice given by a unitary matrix acting on column coordinates."""
        trace = self.trace_lattice()
        positions = dict(zip(self._labels(), trace.module_generating_set(), strict=True))
        basis = self._order_basis

        def image(name):
            i, a = next(key for key, value in positions.items() if value == name)
            terms = {}
            for row in range(self.rank()):
                for b, value in enumerate(self._coordinates_in_order(g[row, i] * basis[a])):
                    if value:
                        terms[positions[(row, b)]] = trace.base_ring()(value)
            return trace.linear_combination(terms)

        return trace.Aut()(image)

    def is_order_linear(self, isometry):
        r"""Return whether an isometry of the trace lattice commutes with the order."""
        lattice = self.trace_lattice()
        actions = [self.order_action(element) for element in self._order_basis]
        return all(
            isometry(action(point)) == action(isometry(point))
            for action in actions for point in lattice.module_generators()
        )

    def unitary_group_elements(self):
        r"""Return every element of ``U(h)`` when the trace lattice is definite."""
        lattice = self.trace_lattice()
        if not lattice.is_definite():
            raise ValueError(f"{self} has an indefinite trace lattice, so U(h) is infinite in general and is not enumerated")
        return tuple(element for element in lattice.O() if self.is_order_linear(element))

    def witt_frame(self, isotropic):
        r"""Return a Witt frame whose first columns are the given isotropic vectors of ``O^n``.

        Dual vectors solve ``B(v_i, w_j) = delta_ij`` for ``B(x, y) = x^* G^T y``;
        with ``c = B(w_i, w_j)``, replacing ``w_j`` by ``w_j - (1/2) sum c_ij v_i``
        makes them isotropic. The middle block is the orthogonal complement.
        """
        V = matrix(self._field, isotropic).transpose()
        k = V.ncols()
        form = self._gram.transpose()
        if _star(V) * form * V != matrix(self._field, k, k):
            raise ValueError("the given vectors do not span a totally isotropic subspace")
        W = (_star(V) * form).solve_right(matrix.identity(self._field, k))
        W = W - V * (_star(W) * form * W) / 2
        M = (_star(V.augment(W)) * form).right_kernel().basis_matrix().transpose()
        frame = V.augment(M).augment(W)
        return HermitianWittFrame(self, frame, _star(M) * form * M, k)

    def isotropic_transporter(self, source, target, blocks=None, based=False):
        r"""Return ``g`` in ``U(O^n, h)`` carrying one primitive isotropic sublattice to another, or ``None``.

        ``source`` and ``target`` list ``O``-bases, see :meth:`HermitianWittFrame.transporter_to`.
        """
        return self.witt_frame(source).transporter_to(self.witt_frame(target), blocks, based)

    def definite_scaling(self):
        r"""Return a real ``alpha`` in the order with ``Tr(alpha h)`` positive definite.

        ``h`` must be definite at every complex place. Then ``alpha`` must
        have the sign of ``h`` at each place, and such an element exists by
        weak approximation; small coordinates are searched in growing boxes.
        """
        from itertools import count, product

        from sage.rings.qqbar import QQbar

        embeddings = self._field.embeddings(QQbar)
        signs = []
        for embedding in embeddings:
            image = self._gram.apply_map(embedding)
            minors = [image[:size, :size].det() for size in range(1, self.rank() + 1)]
            if all(minor.real() > 0 for minor in minors):
                signs.append(1)
            elif all((minor.real() > 0) == (size % 2 == 0) for size, minor in zip(range(1, self.rank() + 1), minors, strict=True)):
                signs.append(-1)
            else:
                raise ValueError(f"{self} is indefinite at the place {embedding}: U(h) is not finite")
        for radius in count(0):
            for coefficients in product(range(-radius, radius + 1), repeat=len(self._order_basis)):
                alpha = sum((int(c) * element for c, element in zip(coefficients, self._order_basis, strict=True)), self._field.zero())
                if alpha != 0 and alpha == alpha.conjugate() and all(
                    (embedding(alpha).real() > 0) == (sign > 0) for embedding, sign in zip(embeddings, signs, strict=True)
                ):
                    return alpha
        raise AssertionError("count() does not terminate")

    def definite_unitary_group_generators(self):
        r"""Return generators of the finite ``U(h)``, through ``O(Tr(alpha h))`` commuting with the order.

        Uses the ``GAP`` centralizer of the root of unity generating the
        order when the order is ``ZZ[zeta]``, and filters ``O`` otherwise.
        """
        scaled = HermitianLattice(self._order_basis, self.definite_scaling() * self._gram)
        lattice = scaled.trace_lattice()
        zeta = self._field.zeta(self._field.zeta_order())
        if scaled._generates_order(zeta):
            return tuple(lattice.O().centralizer(scaled.unit_isometry(zeta)).group_generators())
        return tuple(element for element in lattice.O() if scaled.is_order_linear(element))

    def _generates_order(self, zeta):
        powers = matrix(SageQQ, [list((zeta**k).vector()) for k in range(self._field.degree())])
        return powers.det() != 0 and all(entry in SageZZ for entry in (self._basis_matrix * ~powers).list())

    def isometry_to(self, other):
        r"""Return an order-linear isometry of definite trace lattices to ``other``, or ``None``."""
        source, target = self.trace_lattice(), other.trace_lattice()
        if not source.is_definite():
            raise ValueError(f"{self} has an indefinite trace lattice, so a search over isometries is not finite")
        if self._order_basis != other._order_basis:
            raise ValueError("the two Hermitian lattices must have the same order basis")
        isometries = source.Isom(target)
        if isometries.is_empty() is True:
            return None
        witness = isometries.an_element()
        for automorphism in source.O():
            candidate = witness * automorphism
            if all(
                candidate(self.order_action(element)(point)) == other.order_action(element)(candidate(point))
                for element in self._order_basis for point in source.module_generators()
            ):
                return candidate
        return None


def _star(entries):
    return entries.apply_map(lambda value: value.conjugate()).transpose()


class HermitianWittFrame(SageObject):
    r"""A rational Witt frame ``V = I + V_0 + I^vee`` of a Hermitian lattice.

    The columns of ``frame`` express the Witt basis in the coordinates of
    ``O^n``, and ``frame^* G^T frame`` is the block matrix ``J`` with middle
    block ``middle``. The unipotent elements are the matrices

    .. MATH::

        n(Z,T)=\begin{pmatrix}I&-Z^*H&T-\tfrac12Z^*HZ\\0&I&Z\\0&0&I\end{pmatrix},
        \qquad T^*=-T,

    with ``n(Z,T)n(W,S)=n(Z+W,T+S+\tfrac12(W^*HZ-Z^*HW))``. The integral
    kernel is computed in the original module: a parameter is admitted only
    when ``frame n(Z,T) frame^{-1}`` has entries in the order.
    """

    def __init__(self, lattice, frame, middle, isotropic_rank) -> None:
        self._lattice = lattice
        self._field = lattice.field()
        self._frame = matrix(self._field, frame)
        self._middle = matrix(self._field, middle)
        self._k = int(isotropic_rank)
        self._m = self._middle.nrows()
        self._n = 2 * self._k + self._m
        if self._frame.nrows() != lattice.rank() or self._frame.ncols() != self._n:
            raise ValueError("the frame must be a square matrix of the rank of the lattice")
        if _star(self._frame) * lattice.gram_matrix().transpose() * self._frame != self.j():
            raise ValueError("the columns of the frame are not a Witt basis with the given middle block")

    def _blocks(self, *entries):
        result = matrix(self._field, self._n, self._n)
        sizes = (self._k, self._m, self._k)
        starts = (0, self._k, self._k + self._m)
        for (row, column), block in entries:
            for i in range(sizes[row]):
                for j in range(sizes[column]):
                    result[starts[row] + i, starts[column] + j] = block[i, j]
        return result

    def _identity(self, size):
        return matrix.identity(self._field, size)

    def j(self):
        r"""Return the Gram matrix ``J`` in the Witt frame."""
        one = self._identity(self._k)
        return self._blocks(((0, 2), one), ((1, 1), self._middle), ((2, 0), one))

    def _unipotent_part(self, parameters):
        Z, T = parameters
        return self._blocks(((0, 1), -_star(Z) * self._middle), ((0, 2), T), ((1, 2), Z))

    def _quadratic_part(self, Z):
        return self._blocks(((0, 2), -_star(Z) * self._middle * Z / 2))

    def unipotent(self, Z, T):
        r"""Return ``n(Z, T)`` in the Witt frame."""
        if _star(T) != -T:
            raise ValueError("T must be skew-Hermitian")
        return matrix.identity(self._field, self._n) + self._unipotent_part((Z, T)) + self._quadratic_part(Z)

    def compose(self, first, second):
        r"""Return the parameters of ``n(first) n(second)``."""
        Z, T = first
        W, S = second
        return (Z + W, T + S + (_star(W) * self._middle * Z - _star(Z) * self._middle * W) / 2)

    def levi(self, A, U):
        r"""Return ``diag(A, U, A^{-*})`` in the Witt frame."""
        if _star(U) * self._middle * U != self._middle:
            raise ValueError("U does not preserve the middle form")
        return self._blocks(((0, 0), A), ((1, 1), U), ((2, 2), ~_star(A)))

    def conjugate(self, A, U, parameters):
        r"""Return the parameters of ``l(A,U) n(Z,T) l(A,U)^{-1}``."""
        Z, T = parameters
        return (U * Z * _star(A), A * T * _star(A))

    def in_lattice(self, witt_matrix):
        r"""Return the matrix of a Witt-frame operator on ``O^n``."""
        return self._frame * witt_matrix * ~self._frame

    def preserves_lattice(self, witt_matrix):
        r"""Return whether the operator and its inverse have entries in the order."""
        return self._integral(self.in_lattice(witt_matrix)) and self._integral(self.in_lattice(~witt_matrix))

    def _order_coordinates(self, entries):
        inverse = ~self._lattice._basis_matrix
        return [value for entry in entries.list() for value in (matrix(SageQQ, [list(entry.vector())]) * inverse).row(0)]

    def _integral(self, entries):
        return all(value in SageZZ for value in self._order_coordinates(entries))

    def _parameter_basis(self):
        field_basis = [self._field.gen() ** power for power in range(self._field.degree())]
        images = matrix(SageQQ, [list((a + a.conjugate()).vector()) for a in field_basis])
        imaginary = [
            sum((coefficient * a for coefficient, a in zip(row, field_basis, strict=True)), self._field.zero())
            for row in images.left_kernel().basis()
        ]
        zero_Z = matrix(self._field, self._m, self._k)
        zero_T = matrix(self._field, self._k, self._k)
        basis = []
        for row in range(self._m):
            for column in range(self._k):
                for a in field_basis:
                    Z = copy(zero_Z)
                    Z[row, column] = a
                    basis.append((Z, zero_T))
        z_rank = len(basis)
        for i in range(self._k):
            for a in imaginary:
                T = copy(zero_T)
                T[i, i] = a
                basis.append((zero_Z, T))
            for j in range(i + 1, self._k):
                for a in field_basis:
                    T = copy(zero_T)
                    T[i, j] = a
                    T[j, i] = -a.conjugate()
                    basis.append((zero_Z, T))
        return tuple(basis), z_rank

    def _combine(self, basis, coordinates):
        Z = sum((c * b[0] for c, b in zip(coordinates, basis, strict=True)), matrix(self._field, self._m, self._k))
        T = sum((c * b[1] for c, b in zip(coordinates, basis, strict=True)), matrix(self._field, self._k, self._k))
        return (Z, T)

    @staticmethod
    def _preimage_of_integers(images):
        r"""Return a basis of ``{x : x images in ZZ^N}`` for an injective rational map."""
        denominator = images.denominator()
        scaled = (denominator * images).change_ring(SageZZ)
        return images.solve_left(scaled.saturation().change_ring(SageQQ))

    def _solutions(self, left):
        r"""Return the parameters modulo the centre with ``left n(Z,T)`` integral, and the lattices used.

        ``N = n-1`` satisfies ``L = N - N^2/2`` for the part ``L`` linear in
        the parameters, so ``delta N`` integral bounds the parameters by
        ``2 delta^2 L`` integral, where ``delta`` clears ``left^{-1}``.
        Integrality is constant on classes modulo ``c`` times this lattice.
        """
        basis, z_rank = self._parameter_basis()
        delta = lcm([SageZZ(1), *(value.denominator() for value in self._order_coordinates(~left))])
        frame_inverse = ~self._frame
        linear = lambda parameters: self._frame * self._unipotent_part(parameters) * frame_inverse
        images = matrix(SageQQ, [self._order_coordinates(linear(b)) for b in basis])
        bounding = self._preimage_of_integers(2 * delta * delta * images)
        common = bounding.denominator()
        echelon = (common * bounding).change_ring(SageZZ).echelon_form().change_ring(SageQQ) / common
        section = [row for row in echelon.rows() if row[: z_rank] != 0]
        fibre = [row for row in echelon.rows() if row[: z_rank] == 0]
        centre_images = matrix(SageQQ, [self._order_coordinates(linear(b)) for b in basis[z_rank:]]) if len(basis) > z_rank else None
        centre = self._preimage_of_integers(centre_images) if centre_images is not None else matrix(SageQQ, 0, 0)
        return basis, z_rank, section, fibre, centre, delta

    def _modulus(self, left, basis, rows):
        frame_inverse = ~self._frame
        parameters = [self._combine(basis, list(row)) for row in rows]
        pieces = [left * self._frame * self._unipotent_part(p) * frame_inverse for p in parameters]
        for p in parameters:
            for q in parameters:
                sum_Z = p[0] + q[0]
                pieces.append(left * self._frame * (self._quadratic_part(sum_Z) - self._quadratic_part(p[0]) - self._quadratic_part(q[0])) * frame_inverse)
        denominators = [value.denominator() for piece in pieces for value in self._order_coordinates(piece)]
        return 2 * lcm([SageZZ(1), *denominators])

    def _admissible(self, left):
        r"""Yield integer section coordinates and parameters with ``left n`` integral, one per class."""
        basis, z_rank, section, fibre, centre, delta = self._solutions(left)
        modulus = int(self._modulus(left, basis, section + fibre))
        fibre_lattice = matrix(SageQQ, [list(row)[z_rank:] for row in fibre]) if fibre else None
        fibre_representatives = [vector(SageQQ, len(basis) - z_rank)]
        if fibre_lattice is not None:
            inside = centre * ~fibre_lattice
            quotient = matrix(SageZZ, inside)
            smith, _, transform = quotient.smith_form()
            sizes = [int(smith[i, i]) for i in range(smith.nrows())]
            inverse = ~transform.change_ring(SageQQ)
            fibre_representatives = [
                vector(SageQQ, residue) * inverse * fibre_lattice
                for residue in product(*(range(size) for size in sizes))
            ]
        size = len(basis)
        unit = lambda *indices: [sum(1 for index in indices if index == position) for position in range(size)]
        negative = lambda index: [-entry for entry in unit(index)]
        def value(point):
            parameters = self._combine(basis, point)
            return vector(SageQQ, self._order_coordinates(left * self.in_lattice(matrix.identity(self._field, self._n) + self._unipotent_part(parameters) + self._quadratic_part(parameters[0]))))
        # The entries have degree two in the coordinates, so these samples determine them exactly.
        constant = value([0] * size)
        plus = [value(unit(i)) for i in range(size)]
        minus = [value(negative(i)) for i in range(size)]
        linear = [(p - m) / 2 for p, m in zip(plus, minus, strict=True)]
        square = [(p + m) / 2 - constant for p, m in zip(plus, minus, strict=True)]
        cross = {(i, j): value(unit(i, j)) - plus[i] - plus[j] + constant for i in range(size) for j in range(i + 1, size)}
        rows = [constant, *linear, *square, *cross.values()]
        scale = int(lcm([SageZZ(1), *(entry.denominator() for row in rows for entry in row)]))
        as_integers = lambda row: [int(entry * scale) for entry in row]
        constant_integers, linear_integers, square_integers = as_integers(constant), [as_integers(r) for r in linear], [as_integers(r) for r in square]
        cross_integers = [(i, j, as_integers(r)) for (i, j), r in cross.items()]
        points_denominator = int(lcm([SageZZ(1), *(entry.denominator() for row in section for entry in row), *(entry.denominator() for extra in fibre_representatives for entry in extra)]))
        section_integers = [[int(entry * points_denominator) for entry in row] for row in section]
        extra_integers = [[0] * z_rank + [int(entry * points_denominator) for entry in extra] for extra in fibre_representatives]
        target = scale * points_denominator * points_denominator
        for coordinates in product(range(modulus), repeat=len(section)):
            base = [sum(c * row[position] for c, row in zip(coordinates, section_integers, strict=True)) for position in range(size)]
            for extra, extra_point in zip(fibre_representatives, extra_integers, strict=True):
                t = [b + e for b, e in zip(base, extra_point, strict=True)]
                integral = True
                for k, c0 in enumerate(constant_integers):
                    total = c0 * points_denominator * points_denominator
                    for i in range(size):
                        total += t[i] * linear_integers[i][k] * points_denominator + t[i] * t[i] * square_integers[i][k]
                    for i, j, row in cross_integers:
                        total += t[i] * t[j] * row[k]
                    if total % target:
                        integral = False
                        break
                if integral:
                    point = vector(SageQQ, t) / points_denominator
                    yield coordinates, self._combine(basis, list(point))
                    break

    def integral_unipotent_kernel(self):
        r"""Return ``(generators, centre)`` of the integral unipotent subgroup as parameter pairs.

        ``centre`` is a basis of the central ``T`` lattice; the generators,
        with it, generate the group for the two-step law.
        """
        one = matrix.identity(self._field, self._n)
        basis, z_rank, section, fibre, centre, _ = self._solutions(one)
        centre_generators = tuple(self._combine(basis[z_rank:], list(row)) for row in centre.rows()) if centre.nrows() else ()
        centre_generators = tuple((matrix(self._field, self._m, self._k), pair[1]) for pair in centre_generators)
        modulus = int(self._modulus(one, basis, section + fibre))
        found = {tuple(coordinates): parameters for coordinates, parameters in self._admissible(one)}
        rows = matrix(SageZZ, [[modulus if i == j else 0 for j in range(len(section))] for i in range(len(section))]) if section else matrix(SageZZ, 0, 0)
        generators = []
        spanned = rows
        for coordinates, parameters in sorted(found.items()):
            if not any(coordinates):
                continue
            enlarged = spanned.stack(vector(SageZZ, coordinates)).echelon_form()
            enlarged = enlarged[: enlarged.rank()]
            if abs(enlarged.det()) != abs(spanned.det()):
                spanned = enlarged
                generators.append(parameters)
        for row in section:
            multiple = self._combine(basis, list(modulus * row))
            generators.append(multiple)
        return tuple(generators), centre_generators

    def quotient_lattice_basis(self):
        r"""Return a ``ZZ``-basis of ``I^perp / I`` in the middle Witt coordinates."""
        degree = self._field.degree()
        inverse = ~self._frame
        images = []
        for position in range(self._n):
            for scalar in self._lattice.order_basis():
                point = vector(self._field, self._n)
                point[position] = scalar
                images.append(inverse * point)
        flatten = lambda entries: [value for entry in entries for value in entry.vector()]
        last = matrix(SageQQ, [flatten(image[self._k + self._m :]) for image in images])
        kernel = (last.denominator() * last).change_ring(SageZZ).left_kernel().basis_matrix()
        projected = kernel.change_ring(SageQQ) * matrix(SageQQ, [flatten(image[self._k : self._k + self._m]) for image in images])
        common = projected.denominator()
        echelon = (common * projected).change_ring(SageZZ).echelon_form()
        return tuple(
            vector(self._field, [self._field(list(row[degree * j : degree * (j + 1)])) / common for j in range(self._m)])
            for row in echelon[: echelon.rank()].rows()
        )

    def _quotient_trace_gram(self):
        basis = self.quotient_lattice_basis()
        gram = matrix(SageQQ, [[(left.conjugate() * self._middle * right).trace() for right in basis] for left in basis])
        return matrix(self._field, basis).transpose(), gram

    def quotient_unitary_elements(self):
        r"""Return every element of ``U(I^perp / I)`` for a definite trace form on the quotient."""
        return self.quotient_isometries_to(self)

    def quotient_isometries_to(self, other):
        r"""Return every ``O``-linear isometry ``I^perp / I -> I'^perp / I'`` in middle coordinates.

        The trace forms must be definite. Trace isometries are a coset of the finite orthogonal
        group of the source; ``O``-linear ones preserve ``h`` because ``Tr(alpha h) = 0`` for
        all ``alpha`` forces ``h = 0``.
        """
        from sage.quadratic_forms.quadratic_form import QuadraticForm

        if self._m == 0:
            return (matrix(self._field, 0, 0),)
        columns, gram = self._quotient_trace_gram()
        target_columns, target_gram = other._quotient_trace_gram()
        if gram[0, 0] * target_gram[0, 0] < 0:
            return ()
        if gram[0, 0] < 0:
            gram, target_gram = -gram, -target_gram
        if not gram.is_positive_definite() or not target_gram.is_positive_definite():
            raise ValueError("the trace form of the quotient is indefinite, so its unitary group is infinite in general")
        scale = 2 * lcm([gram.denominator(), target_gram.denominator()])
        form = QuadraticForm((scale * gram).change_ring(SageZZ))
        target_form = QuadraticForm((scale * target_gram).change_ring(SageZZ))
        witness = target_form.is_globally_equivalent_to(form, return_matrix=True)
        if witness is False:
            return ()
        if witness.transpose() * target_gram * witness != gram:
            raise ArithmeticError("the equivalence of quadratic forms does not carry the target form to the source form")
        pivots = list(columns.pivots())
        chart_inverse = ~columns[:, pivots]
        elements = []
        for automorphism in form.automorphisms():
            image = target_columns * (witness * automorphism).change_ring(self._field)
            candidate = image[:, pivots] * chart_inverse
            if candidate * columns == image:
                elements.append(candidate)
        return tuple(elements)

    def levi_candidates(self):
        r"""Return all ``(A, U)`` with ``A`` a root of unity of the order, for an isotropic line."""
        if self._k != 1:
            raise ValueError("levi_candidates requires an isotropic line: GL_k of the order is infinite for k > 1")
        if self._field.unit_group().rank() != 0:
            raise ValueError("levi_candidates requires a finite unit group of the order")
        return tuple((matrix(self._field, 1, 1, [unit]), element) for unit in self._order_units() for element in self.quotient_unitary_elements())

    def levi_image(self):
        r"""Return the pairs of :meth:`levi_candidates` that lift to integral isometries."""
        return self.liftable_levi_image(self.levi_candidates())

    def pointwise_levi_image(self):
        r"""Return the liftable pairs with ``A`` the identity, which fix ``I`` pointwise."""
        identity = matrix.identity(self._field, self._k)
        return tuple((identity, U) for U in self.quotient_unitary_elements() if self.levi_lift(identity, U) is not None)

    def _require_isotropic_basis(self):
        r"""Require the first ``k`` columns to be an ``O``-basis of a primitive sublattice.

        Only then is the group induced on ``I`` equal to ``GL_k(O)`` in the frame coordinates.
        """
        rows = [
            [value for entry in scalar * self._frame.column(column) for value in self._order_coordinates(matrix(self._field, [[entry]]))]
            for column in range(self._k) for scalar in self._lattice.order_basis()
        ]
        if any(value not in SageZZ for row in rows for value in row):
            raise ValueError("the isotropic columns of the frame do not lie in the lattice")
        if any(divisor != 1 for divisor in matrix(SageZZ, rows).elementary_divisors()):
            raise ValueError("the isotropic columns of the frame are not a basis of a primitive sublattice")

    def stabilizer_generators(self, pointwise, blocks=None):
        r"""Return matrices on ``O^n`` generating the stabilizer of ``I`` or of a flag ending in ``I``.

        Every ``n(Z,T)`` is the identity on ``I``, so the integral unipotent kernel lies in the
        stabilizer of each flag in ``I``. The stabilizer is therefore generated by this kernel
        and exact lifts of generators of its Levi image.

        With ``pointwise``, the frame columns of ``I`` are fixed and ``A`` is the identity.
        Otherwise the flag is preserved setwise: ``A`` lies in the block upper triangular
        subgroup of ``GL_k(O)`` for ``blocks``, which is all of ``GL_k(O)`` when ``blocks`` is ``None``.
        """
        self._require_isotropic_basis()
        generators, centre = self.integral_unipotent_kernel()
        kernel = [self.in_lattice(self.unipotent(*parameters)) for parameters in (*generators, *centre)]
        pairs = self.pointwise_levi_image() if pointwise else self.levi_image_schreier(blocks)[1]
        lifts = [self.in_lattice(self.levi(A, U) * self.unipotent(*self.levi_lift(A, U))) for A, U in pairs]
        return (*kernel, *lifts)

    def preimage_stabilizer_generators(self, image, in_subgroup, pointwise, blocks=None):
        r"""Return ``(generators, index)`` for ``P cap rho^{-1}(S)``, ``P`` the stabilizer of :meth:`stabilizer_generators`.

        ``image`` is a homomorphism ``rho`` from ``U(O^n, h)``, on matrices acting on ``O^n``,
        to a finite group, for instance the joint residue and determinant map of several
        characters, and ``in_subgroup`` decides membership in a subgroup ``S`` of its image.
        Right cosets of ``P cap rho^{-1}(S)`` in ``P`` are decided by ``rho(g h^{-1}) in S``;
        their Schreier generators generate the intersection (Schreier's lemma), and ``index``
        is ``[P : P cap rho^{-1}(S)]``.
        """
        from sage_extensions.categories.lattice_centralizers import finite_preimage_generators

        return finite_preimage_generators(self.stabilizer_generators(pointwise, blocks), image, in_subgroup)

    def residue_coordinates(self, g, modulus):
        r"""Return the ``ZZ``-coordinates of the entries of an integral matrix in the order basis, modulo ``modulus``."""
        return tuple(int(SageZZ(value) % modulus) for value in self._order_coordinates(g))

    def congruence_stabilizer_generators(self, modulus, pointwise, blocks=None):
        r"""Return ``(generators, index)`` for the stabilizer of :meth:`stabilizer_generators` meet ``Gamma(m)``.

        ``Gamma(m)`` is the kernel of ``U(O^n, h) -> GL_n(O/mO)``, the preimage of the trivial
        subgroup under the residue map (:meth:`preimage_stabilizer_generators`).
        """
        identity = self.residue_coordinates(matrix.identity(self._field, self._lattice.rank()), modulus)
        return self.preimage_stabilizer_generators(lambda g: self.residue_coordinates(g, modulus), lambda r: r == identity, pointwise, blocks)

    def induced_action(self, g):
        r"""Return ``(A, U)``, the action of ``g`` on ``I`` and on ``I^perp / I``, in frame coordinates.

        ``g`` is a matrix on ``O^n`` acting on column coordinates; it must be integral, unitary and stabilize ``I``.
        """
        form = self._lattice.gram_matrix().transpose()
        if not self._integral(g) or not self._integral(~g) or _star(g) * form * g != form:
            raise ValueError("the matrix is not an integral unitary automorphism of the lattice")
        witt = ~self._frame * g * self._frame
        if witt[self._k :, : self._k] != 0:
            raise ValueError("the matrix does not stabilize the isotropic sublattice of the frame")
        return witt[: self._k, : self._k], witt[self._k : self._k + self._m, self._k : self._k + self._m]

    def _order_units(self):
        r"""Return the roots of unity of the field that lie in the order: its whole unit group."""
        return tuple(unit for unit in self._field.roots_of_unity() if self._integral(matrix(self._field, 1, 1, [unit])))

    def general_linear_generators(self, blocks=None):
        r"""Return generators of ``GL_k(O)``, or of its block upper triangular subgroup.

        The block-parabolic subgroup is the product of its block-diagonal ``GL``
        factors and its upper unitriangular part, and the latter is generated by
        the elementary matrices ``1 + r E_ij`` with ``r`` in a ``ZZ``-basis of ``O``.
        A ``1 x 1`` block contributes the units of ``O``, so a complete flag
        (every block of size one, the Borel subgroup) needs no hypothesis on ``O``.
        A block of size at least two needs generators of ``GL_b(O)``: elementary
        matrices and diagonal units generate ``GL_b`` of a Euclidean ring, so ``O``
        must then be a norm-Euclidean imaginary quadratic maximal order.
        ``blocks`` lists the block sizes of a flag, summing to ``k``.
        """
        identity = matrix.identity(self._field, self._k)
        blocks = (self._k,) if blocks is None else tuple(blocks)
        assert sum(blocks) == self._k and all(b > 0 for b in blocks), f"{blocks} is not a composition of {self._k}"
        if any(size > 1 for size in blocks):
            if self._field.degree() != 2 or self._field.discriminant() not in (-3, -4, -7, -8, -11):
                raise ValueError("generators of GL_b(O) for b > 1 require a norm-Euclidean imaginary quadratic field")
            maximal = matrix(SageQQ, [list(element.vector()) for element in self._field.maximal_order().basis()])
            if self._lattice._basis_matrix.det().abs() != maximal.det().abs():
                raise ValueError("generators of GL_b(O) for b > 1 require the maximal order")
        generators = []
        index = [position for position, size in enumerate(blocks) for _ in range(size)]
        for row in range(self._k):
            for column in range(self._k):
                if row != column and index[row] <= index[column]:
                    for scalar in self._lattice.order_basis():
                        elementary = copy(identity)
                        elementary[row, column] = scalar
                        generators.append(elementary)
        starts = [sum(blocks[:position]) for position in range(len(blocks))]
        for start in starts:
            for unit in self._order_units():
                diagonal = copy(identity)
                diagonal[start, start] = unit
                generators.append(diagonal)
        return tuple(generators)

    def _levi_cosets(self, blocks):
        r"""Return right coset representatives of the liftable subgroup, and its Schreier generators.

        The liftable pairs form a subgroup of finite index, since a congruence subgroup lifts.
        Right cosets are enumerated by the lifting decision and generators are Schreier elements.
        """
        identity_a, identity_u = matrix.identity(self._field, self._k), matrix.identity(self._field, self._m)
        moves = [(a, identity_u) for a in self.general_linear_generators(blocks)]
        moves += [(identity_a, u) for u in self.quotient_unitary_elements()]
        representatives = [(identity_a, identity_u)]
        generators = []
        position = 0
        while position < len(representatives):
            a, u = representatives[position]
            position += 1
            for move_a, move_u in moves:
                product_a, product_u = a * move_a, u * move_u
                for known_a, known_u in representatives:
                    quotient = (product_a * ~known_a, product_u * ~known_u)
                    if self.levi_lift(*quotient) is not None:
                        generators.append(quotient)
                        break
                else:
                    representatives.append((product_a, product_u))
        return tuple(representatives), tuple(generators)

    def levi_image_schreier(self, blocks=None):
        r"""Return ``(index, generators)`` of the liftable subgroup of ``GL_k(O) x U(K)``.

        With ``blocks``, the source group is the block upper triangular subgroup of a flag.
        """
        representatives, generators = self._levi_cosets(blocks)
        return len(representatives), generators

    def levi_lift(self, A, U):
        r"""Return parameters ``(Z,T)`` with ``l(A,U) n(Z,T)`` integral on ``O^n``, or ``None``."""
        return self._lift_to(self, A, U)

    def _lift_to(self, other, A, U):
        r"""Return ``(Z,T)`` with ``F' diag(A, U, A^{-*}) n(Z,T) F^{-1}`` integral, or ``None``."""
        left = other._frame * self._blocks(((0, 0), A), ((1, 1), U), ((2, 2), ~_star(A))) * ~self._frame
        for _, parameters in self._admissible(left):
            return parameters
        return None

    def transporter_to(self, other, blocks=None, based=False):
        r"""Return ``g`` in ``U(O^n, h)`` carrying this frame's sublattice ``I`` to that of ``other``, or ``None``.

        Both frames lie on one lattice and their first ``k`` columns are ``O``-bases of
        primitive sublattices. Each isometry has the form ``F' l(A,U) n(Z,T) F^{-1}`` with
        ``A`` in ``GL_k(O)``, or block upper triangular for a flag, and ``U`` an isometry of the quotients.
        With ``based``, ``A`` is the identity, so ``g`` matches the two bases.

        ``None`` is a proof: pairs that lift form one coset of the liftable subgroup ``S``.
        Each candidate is ``(1, U_0) r^{-1}`` for a representative ``r`` of the right cosets
        of ``S``, and these meet every coset of ``S``, so an empty result means no pair lifts.
        Unequal ranks admit no isometry.
        """
        lattice = self._lattice
        if lattice.gram_matrix() != other._lattice.gram_matrix() or lattice.order_basis() != other._lattice.order_basis():
            raise ValueError("the frames must lie on one Hermitian lattice")
        if self._k != other._k:
            return None
        self._require_isotropic_basis()
        other._require_isotropic_basis()
        isometries = self.quotient_isometries_to(other)
        if not isometries:
            return None
        if based:
            identity = matrix.identity(self._field, self._k)
            candidates = [(identity, U) for U in isometries]
        else:
            representatives, _ = self._levi_cosets(blocks)
            candidates = [(~a, isometries[0] * ~u) for a, u in representatives]
        for A, U in candidates:
            parameters = self._lift_to(other, A, U)
            if parameters is not None:
                return self._verified_transporter(other, A, U, parameters)
        return None

    def _verified_transporter(self, other, A, U, parameters):
        witt = self._blocks(((0, 0), A), ((1, 1), U), ((2, 2), ~_star(A))) * self.unipotent(*parameters)
        g = other._frame * witt * ~self._frame
        form = self._lattice.gram_matrix().transpose()
        if not self._integral(g) or not self._integral(~g) or _star(g) * form * g != form:
            raise ArithmeticError("the transporter is not an integral unitary automorphism")
        if (~other._frame * g * self._frame)[self._k :, : self._k] != 0:
            raise ArithmeticError("the transporter does not carry the isotropic sublattice to its target")
        return g

    def liftable_levi_image(self, pairs):
        r"""Return those ``(A, U)`` in ``pairs`` with an integral lift."""
        return tuple(pair for pair in pairs if self.levi_lift(*pair) is not None)


__all__ = ["HermitianLattice", "HermitianWittFrame"]
