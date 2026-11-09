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
        for coordinates in product(range(modulus), repeat=len(section)):
            base = sum((int(c) * row for c, row in zip(coordinates, section, strict=True)), vector(SageQQ, len(basis)))
            for extra in fibre_representatives:
                total = base + vector(SageQQ, [0] * z_rank + list(extra))
                parameters = self._combine(basis, list(total))
                if self._integral(left * self.in_lattice(matrix.identity(self._field, self._n) + self._unipotent_part(parameters) + self._quadratic_part(parameters[0]))):
                    yield coordinates, parameters
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

    def levi_lift(self, A, U):
        r"""Return parameters ``(Z,T)`` with ``l(A,U) n(Z,T)`` integral on ``O^n``, or ``None``."""
        left = self.in_lattice(self.levi(A, U))
        for _, parameters in self._admissible(left):
            return parameters
        return None

    def liftable_levi_image(self, pairs):
        r"""Return those ``(A, U)`` in ``pairs`` with an integral lift."""
        return tuple(pair for pair in pairs if self.levi_lift(*pair) is not None)


__all__ = ["HermitianLattice", "HermitianWittFrame"]
