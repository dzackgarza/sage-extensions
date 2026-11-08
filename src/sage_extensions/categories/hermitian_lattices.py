r"""Hermitian lattices over an order of a CM number field.

A Hermitian lattice is a free module over an order ``O`` of a CM field ``K``
with a Hermitian form ``h``. Its trace lattice is the same abelian group with
``b(x, y) = Tr_{K/QQ} h(x, y)``. Since ``Tr(alpha h) = 0`` for all ``alpha``
forces ``h = 0``, the unitary group is the centralizer of the ``O``-action in
the orthogonal group of the trace lattice.
"""

from sage.matrix.constructor import matrix
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


__all__ = ["HermitianLattice"]
