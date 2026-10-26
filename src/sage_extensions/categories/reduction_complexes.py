r"""The reduction complex of an indefinite lattice, and what it would need.

A reduction complex is a ``G``-CW structure on the symmetric space of
``O(L)(R)``: for an indefinite form the cells are the perfect domains of
Opgenorth's reduction theory, each a rational polyhedral cone spanned by the
minimal vectors of an auxiliary positive form, and two cells are adjacent when
they share a facet.  Traversing the complex from one cell, taking the
stabilizer of each cell and the transporters along its facets, yields
generators of ``O(L)`` and decides isometry of two lattices in the same genus.
The *marked* variant carries with each cell a finite family of nonzero-norm
vectors, which is how a general Lorentzian vector orbit is computed: the
traversal then answers about the pair (cell, marked family) rather than about
the cell alone.

A cell is an object of ``RationalPolyhedralCones``: the cone in
``L tensor QQ`` cut out by homogeneous half-spaces, with its faces,
intersections, transport along isometries and stabilizers.  The records below
join cells into the complex: an oriented adjacency, a face incidence, a marked
cell, and the finite explorations and completed traversals built from them.

None of this is computed here.  ``sage-indefinite-port`` computes the
traversal, in ``sage_indefinite_port.indefinite.lorentzian_cells``.

What *is* owned, so that a caller does not reach here for it:

- generators of ``O(L)`` for an indefinite lattice, through
  ``L.O().group_generators()``, whose selection of generators goes to the indefinite
  automorphism group of ``sage-indefinite-port`` and so does not need the cell traversal;
- the ``O(L)``-orbits of vectors of a given square, their stabilizers and
  their equivalence witnesses, through the exact indefinite backend;
- the Lorentzian component character in signature ``(1, n)``, through
  ``L.positive_cone_subgroup()``, whose product with ``<-1>`` is ``O(L)``
  because ``-1`` exchanges the two components of the positive cone.
"""

from sage.structure.sage_object import SageObject

from sage_extensions.categories.polyhedral_cones import (
    RationalPolyhedralCones,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)


class ReductionCellAdjacency(SageObject):
    r"""An oriented adjacency of two rational reduction cells.

    It consists of the source cell, target cell, their actual common facet,
    and one lattice isometry carrying source to target.  Reversing the
    adjacency inverts that same transporter and preserves the shared face.
    """

    def __init__(self, source, target, common_face, transporter) -> None:
        if source.ambient_lattice() is not target.ambient_lattice():
            raise ValueError(
                f"the reduction cells {source} and {target} cannot be adjacent: they lie in different lattices, {source.ambient_lattice()} and {target.ambient_lattice()}"
            )
        if common_face.ambient_lattice() is not source.ambient_lattice():
            raise ValueError(
                f"{common_face} cannot be the common face of {source} and {target}: it lies in {common_face.ambient_lattice()}, not in the lattice {source.ambient_lattice()} of the cells"
            )
        if not source.is_adjacent_to(target):
            raise ValueError(f"the reduction cells {source} and {target} are not adjacent: they do not share a facet")
        if not common_face.is_equal_to(source.intersection(target)):
            raise ValueError(f"{common_face} is not the common face of {source} and {target}: it is not their intersection")
        if not source.transport(transporter).is_equal_to(target):
            raise ValueError(f"the isometry {transporter} does not carry the reduction cell {source} onto {target}")
        self._source = source
        self._target = target
        self._common_face = common_face
        self._transporter = transporter

    def source(self):
        return self._source

    def target(self):
        return self._target

    def lattice(self):
        return self.source().ambient_lattice()

    def common_face(self):
        return self._common_face

    def transporter(self):
        return self._transporter

    def reversed(self):
        return ReductionCellAdjacency(
            self.target(),
            self.source(),
            self.common_face(),
            ~self.transporter(),
        )

    def _repr_(self):
        return f"Reduction-cell adjacency {self.source()} -> {self.target()}"


class ReductionFaceIncidence(SageObject):
    r"""One exact face inclusion inside a rational reduction cell.

    The incidence retains both mathematical cells and, when requested through
    ``face_incidences`` of the cell, the subgroup preserving the pair.  It is
    therefore stronger than a dimension pair or an engine face index and can
    be transported through the lattice action without losing the actual
    embedded face.
    """

    def __init__(self, face, cell, stabilizer) -> None:
        if face.ambient_lattice() is not cell.ambient_lattice() or not face.is_face_of(cell):
            raise ValueError(f"{face} is not a face of the reduction cell {cell}")
        self._face = face
        self._cell = cell
        self._stabilizer = stabilizer

    def face(self):
        return self._face

    def cell(self):
        return self._cell

    def lattice(self):
        return self.cell().ambient_lattice()

    def stabilizer(self):
        return self._stabilizer

    def codimension(self):
        return self.cell().dimension() - self.face().dimension()

    def transported_by(self, isometry):
        transported_cell = self.cell().transport(isometry)
        transported_face = self.face().transport(isometry)
        return ReductionFaceIncidence(
            transported_face,
            transported_cell,
            transported_cell.face_stabilizer(transported_face, self.stabilizer().supergroup()),
        )

    def _repr_(self):
        return f"Reduction-face incidence {self.face()} <= {self.cell()}"


class MarkedReductionCell(SageObject):
    r"""A rational reduction cell with a labelled finite family of marked vectors.

    The marks are part of the object, not a set of vectors: labels and repeated
    values are retained.  Every mark is a nonzero-norm vector of the ambient
    lattice, which is the marked reduction problem used for nonisotropic vector
    orbit traversal.
    """

    def __init__(self, cell, marked_vectors) -> None:
        assert cell in RationalPolyhedralCones(cell.ambient_lattice()), (
            f"{cell} cannot be marked as a reduction cell: a reduction cell must be a rational polyhedral cone, but {cell} is in {cell.category()}"
        )
        assert marked_vectors.cardinality().is_finite(), f"cannot mark the reduction cell {cell} with {marked_vectors}: the family of marked vectors must be finite"
        lattice = cell.ambient_lattice()
        for vector in marked_vectors:
            if vector.parent() is not lattice:
                raise ValueError(f"cannot mark the reduction cell {cell} with {vector}: the vector lies in {vector.parent()}, not in the lattice {lattice} of the cell")
            if lattice.q(vector) == lattice.base_ring().zero():
                raise ValueError(f"cannot mark the reduction cell {cell} with {vector}: a marked vector must have nonzero square, but q({vector}) = 0")
        self._cell = cell
        self._marked_vectors = marked_vectors

    def lattice(self):
        return self.cell().ambient_lattice()

    def cell(self):
        return self._cell

    def marked_vectors(self):
        return self._marked_vectors

    def transported_by(self, isometry):
        r"""Transport the cell and every labelled mark by the same isometry."""
        marks = self.marked_vectors()
        transported_marks = finite_indexed_family(
            marks.index_set(),
            lambda label: isometry(marks[label]),
            name=f"Transported marks of {self}",
        )
        return MarkedReductionCell(
            self.cell().transport(isometry),
            transported_marks,
        )

    def is_equal_to(self, other) -> bool:
        r"""Return whether ``other``, a marked cell of the same lattice, has the same cell and the same labelled marks."""
        if not self.cell().is_equal_to(other.cell()):
            return False
        same_marks = self.marked_vectors() == other.marked_vectors()
        return same_marks is True

    def transporter_witness_to(self, other, group):
        r"""Return a finite-group element transporting both cell and labelled marks."""
        if other.lattice() is not self.lattice():
            return None
        group_cardinality = group.cardinality()
        assert group_cardinality.is_finite(), (
            f"cannot search {group} for an isometry carrying {self} to {other}: the search runs only over a finite group, and {group} has cardinality {group_cardinality}"
        )
        for isometry in group:
            if self.transported_by(isometry).is_equal_to(other):
                return isometry
        return None

    def stabilizer(self, group):
        r"""Return the subgroup preserving both the cell and every labelled mark."""
        if group.domain() is not self.lattice() or group.codomain() is not self.lattice():
            raise ValueError(
                f"{group} cannot stabilize the marked cell {self}: it must be a group of isometries of {self.lattice()}, but it acts from {group.domain()} to {group.codomain()}"
            )

        def preserves_marked_cell(isometry):
            return self.transported_by(isometry).is_equal_to(self)

        return group.predicate_subgroup(preserves_marked_cell, f"g preserves the marked reduction cell {self}")

    def adjacency_to(self, other, group):
        r"""Return the marked adjacency when one isometry transports all retained data."""
        underlying = self.cell().adjacency_to(other.cell(), group)
        if underlying is None:
            return None
        transporter = self.transporter_witness_to(other, group)
        if transporter is None:
            return None
        return MarkedReductionCellAdjacency(self, other, underlying, transporter)

    def _repr_(self):
        return f"Marked {self.cell()} with {self.marked_vectors().cardinality()} labelled vectors"


class MarkedReductionCellAdjacency(SageObject):
    r"""An oriented adjacency of marked cells with one common transporter."""

    def __init__(self, source, target, cell_adjacency, transporter) -> None:
        if cell_adjacency.source() is not source.cell() or cell_adjacency.target() is not target.cell():
            raise ValueError(
                f"{cell_adjacency} cannot underlie an adjacency of the marked cells {source} and {target}: it joins {cell_adjacency.source()} to {cell_adjacency.target()}, not {source.cell()} to {target.cell()}"
            )
        if not source.transported_by(transporter).is_equal_to(target):
            raise ValueError(f"the isometry {transporter} does not carry the marked cell {source} onto {target}")
        self._source = source
        self._target = target
        self._cell_adjacency = cell_adjacency
        self._transporter = transporter

    def source(self):
        return self._source

    def target(self):
        return self._target

    def lattice(self):
        return self.source().lattice()

    def underlying_adjacency(self):
        return self._cell_adjacency

    def common_face(self):
        return self.underlying_adjacency().common_face()

    def transporter(self):
        return self._transporter

    def reversed(self):
        return MarkedReductionCellAdjacency(
            self.target(),
            self.source(),
            self.underlying_adjacency().reversed(),
            ~self.transporter(),
        )

    def _repr_(self):
        return f"Marked reduction-cell adjacency {self.source()} -> {self.target()}"


def _unpaired_facets(cells, incident_faces_of):
    r"""The facets of the stated cells that no adjacency face accounts for."""
    unpaired = []
    for cell in cells:
        incident_faces = incident_faces_of(cell)
        for facet in cell.facets():
            if not any(facet.is_equal_to(face) for face in incident_faces):
                unpaired.append(facet)
    return finite_ordered_set(tuple(unpaired))


class RationalReductionComplexExploration(SageObject):
    r"""A finite exact exploration of a rational reduction complex.

    The object retains actual cells and oriented adjacency records.  It is a
    *complete* exploration only when every irredundant facet of every retained
    cell occurs as the common face of one retained adjacency.  Merely stopping
    a traversal therefore never turns a finite prefix into a complete domain.
    """

    def __init__(self, lattice, cells, adjacencies, *, complete=False) -> None:
        cells = finite_ordered_set(tuple(cells))
        if cells.cardinality() == 0:
            raise ValueError(f"cannot form a reduction complex of {lattice} with no cells: it needs at least one cell")
        if any(cell.ambient_lattice() is not lattice for cell in cells):
            raise ValueError(f"cannot form a reduction complex of {lattice} from {cells}: some cell lies in a different lattice")
        adjacencies = finite_ordered_set(tuple(adjacencies))
        for adjacency in adjacencies:
            if adjacency.lattice() is not lattice:
                raise ValueError(f"the adjacency {adjacency} cannot be part of a reduction complex of {lattice}: it lies in {adjacency.lattice()}")
            if adjacency.source() not in cells or adjacency.target() not in cells:
                raise ValueError(
                    f"the adjacency {adjacency} cannot be part of this reduction complex of {lattice}: it joins {adjacency.source()} to {adjacency.target()}, and not both are cells of the complex"
                )
        self._lattice = lattice
        self._cells = cells
        self._adjacencies = adjacencies
        self._complete = bool(complete)
        if self._complete and self.unpaired_facets().cardinality() != 0:
            raise ValueError(f"the reduction complex of {lattice} is declared complete, but {self.unpaired_facets().cardinality()} facets of its cells have no adjacent cell")

    def lattice(self):
        return self._lattice

    def cells(self):
        return self._cells

    def adjacencies(self):
        return self._adjacencies

    def is_complete(self) -> bool:
        return self._complete

    def unpaired_facets(self):
        r"""Return the retained cell facets not represented by an adjacency."""
        return _unpaired_facets(
            self.cells(),
            lambda cell: tuple(adjacency.common_face() for adjacency in self.adjacencies() if adjacency.source() is cell or adjacency.target() is cell),
        )

    def adjacency_transporters(self):
        r"""Return the retained oriented cell transporters, preserving edge labels."""
        adjacencies = self.adjacencies()
        return finite_indexed_family(
            adjacencies,
            lambda adjacency: adjacency.transporter(),
            name=f"Adjacency transporters of {self}",
        )

    def generation_subgroup(self, group):
        r"""Return the subgroup generated by cell stabilizers and edge transporters.

        This is exposed only for a complete exploration and a finite represented
        acting group, where every cell stabilizer can be listed exactly.  An
        incomplete prefix is not a group-generation certificate.
        """
        if not self.is_complete():
            raise ValueError(f"cannot conclude that the cell stabilizers and adjacencies generate {group}: the reduction complex of {self.lattice()} is not complete")
        if group.domain() is not self.lattice() or group.codomain() is not self.lattice():
            raise ValueError(
                f"{group} cannot act on the reduction complex of {self.lattice()}: it must be a group of isometries of {self.lattice()}, but it acts from {group.domain()} to {group.codomain()}"
            )
        assert group.cardinality().is_finite(), (
            f"cannot compute generators of {group} from the reduction complex of {self.lattice()}: this is done only for a finite group, and {group} has cardinality {group.cardinality()}"
        )
        generators = []
        for cell in self.cells():
            stabilizer = cell.stabilizer(group)
            generators.extend(element for element in group if element in stabilizer)
        generators.extend(self.adjacency_transporters())
        return group.subgroup(generators)

    def generation_is_full(self, group) -> bool:
        r"""Whether the complete finite exploration generates the supplied finite group."""
        generated = self.generation_subgroup(group)
        return generated.cardinality() == group.cardinality()

    def _repr_(self):
        status = "complete" if self.is_complete() else "finite-prefix"
        return f"{status} rational reduction-complex exploration with {self.cells().cardinality()} cells in {self.lattice()}"


class PerfectDomainOrbitAdjacency(SageObject):
    r"""One quotient adjacency in a complete Lorentzian perfect-domain traversal.

    The source is a selected orbit representative.  Flipping its retained
    facet produces ``neighbor``.  The exact arithmetic computation then identifies that actual
    neighbor with the selected representative ``target`` of its orbit.  The
    source and target representatives need not themselves be adjacent or lie
    in the same orbit, so this is deliberately not a ``ReductionCellAdjacency``.
    """

    def __init__(
        self,
        source,
        target,
        neighbor,
        common_face,
        target_to_neighbor,
    ) -> None:
        lattice = source.ambient_lattice()
        if any(cell.ambient_lattice() is not lattice for cell in (target, neighbor, common_face)):
            raise ValueError(
                f"the perfect domains {source}, {target}, {neighbor} and the face {common_face} cannot form an adjacency: they do not all lie in the lattice {lattice}"
            )
        if not common_face.is_face_of(source) or not common_face.is_face_of(neighbor):
            raise ValueError(f"{common_face} is not a common face of the perfect domains {source} and {neighbor}")
        if not target.transport(target_to_neighbor).is_equal_to(neighbor):
            raise ValueError(f"the isometry {target_to_neighbor} does not carry the perfect domain {target} onto its neighbor {neighbor}")
        self._source = source
        self._target = target
        self._neighbor = neighbor
        self._common_face = common_face
        self._target_to_neighbor = target_to_neighbor

    def source(self):
        return self._source

    def target_representative(self):
        return self._target

    def neighbor(self):
        return self._neighbor

    def common_face(self):
        return self._common_face

    def target_to_neighbor(self):
        return self._target_to_neighbor

    def neighbor_to_target(self):
        return ~self.target_to_neighbor()


class LorentzianPerfectDomainTraversal(SageObject):
    r"""A completed orbit traversal of Lorentzian perfect domains.

    The exact traversal computation returns only after every adjacency has been processed.  The
    stored generator family is exactly the family used upstream to reconstruct
    ``O(L)``: stabilizer generators of every orbit representative together
    with one equivalence matrix for every quotient adjacency.
    """

    def __init__(self, lattice, cells, adjacencies, stabilizer_generators) -> None:
        self._lattice = lattice
        self._cells = finite_ordered_set(tuple(cells))
        self._adjacencies = finite_ordered_set(tuple(adjacencies))
        self._stabilizer_generators = stabilizer_generators
        if self._cells.cardinality() == 0:
            raise ValueError(f"the perfect-domain decomposition of {lattice} has no orbit representatives: it needs at least one")
        if any(cell.ambient_lattice() is not lattice for cell in self._cells):
            raise ValueError(f"cannot decompose {lattice} into the perfect domains {self._cells}: some domain lies in a different lattice")
        if any(adjacency.source() not in self._cells for adjacency in self._adjacencies):
            raise ValueError(f"the perfect-domain decomposition of {lattice} has an adjacency starting at a domain that is not one of its orbit representatives {self._cells}")
        if any(adjacency.target_representative() not in self._cells for adjacency in self._adjacencies):
            raise ValueError(f"the perfect-domain decomposition of {lattice} has an adjacency ending at an orbit whose representative is not one of {self._cells}")
        if self.unpaired_facets().cardinality() != 0:
            raise ValueError(
                f"the perfect-domain decomposition of {lattice} is incomplete: {self.unpaired_facets().cardinality()} facets of its orbit representatives have no adjacent domain"
            )

    def lattice(self):
        return self._lattice

    def cells(self):
        return self._cells

    def adjacencies(self):
        return self._adjacencies

    def is_complete(self) -> bool:
        return True

    def unpaired_facets(self):
        r"""Return interior facets missing from the quotient adjacency list.

        A Lorentzian perfect cell lies in one closed component of the
        nonspacelike cone.  A face on the *exterior* boundary has no adjacent
        cell across it.  This happens exactly when its linear span is totally
        isotropic: all its generating rays have square zero and pairwise
        pairing zero.  For a Lorentzian form such a face is a null ray (or
        the origin).  All other facets require a quotient adjacency.
        """
        unpaired = _unpaired_facets(
            self.cells(),
            lambda cell: tuple(adjacency.common_face() for adjacency in self.adjacencies() if adjacency.source() is cell),
        )
        lattice = self.lattice()
        zero = lattice.base_ring().zero()
        missing_interior = []
        for facet in unpaired:
            if facet.is_pointed():
                rays = tuple(facet.primitive_rays())
                if all(lattice.q(ray) == zero for ray in rays) and all(
                    lattice.b(left, right) == zero
                    for index, left in enumerate(rays)
                    for right in rays[index + 1 :]
                ):
                    continue
            missing_interior.append(facet)
        return finite_ordered_set(tuple(missing_interior))

    def cell_stabilizer_generators(self, cell):
        if cell not in self.cells():
            raise ValueError(f"{cell} is not one of the orbit representatives {self.cells()} of this perfect-domain decomposition")
        return self._stabilizer_generators[cell]

    def group_generators(self):
        # The connected perfect complex lies in one cone component. Central
        # inversion exchanges the components and supplies the other coset.
        lattice = self.lattice()
        generators = [lattice.O()(tuple(-vector for vector in lattice.module_generators()))]
        for cell in self.cells():
            generators.extend(self.cell_stabilizer_generators(cell))
        generators.extend(adjacency.target_to_neighbor() for adjacency in self.adjacencies())
        return finite_ordered_set(tuple(generators))

    def generation_subgroup(self):
        r"""Return the subgroup generated by cell stabilizers and edge pairings.

        For a complete connected reduction-domain traversal this is the
        standard generation theorem: vertex stabilizers and side-pairings
        generate the component-preserving group, and central inversion gives
        the full orthogonal group. The subgroup is retained explicitly so
        downstream consumers use the actual live generators rather than a
        boolean completeness flag.
        """
        return self.lattice().O().subgroup(self.group_generators())

    def generates_orthogonal_group(self) -> bool:
        r"""Return ``True`` for this completed perfect-domain traversal.

        Construction of this object has already verified that every facet of
        every orbit representative is paired.  Together with the traversal's
        completed orbit traversal, the reduction-complex generation theorem
        identifies :meth:`generation_subgroup` with ``O(L)``.  Finite-prefix
        objects are represented by :class:`RationalReductionComplexExploration`
        and deliberately do not have this unconditional conclusion.
        """
        return self.unpaired_facets().cardinality() == 0


def _lorentzian_reduction_complex(lattice, marked_vectors=None):
    r"""Return the completed Lorentzian perfect-domain traversal of ``lattice``.

    The port receives this lattice and handles either Lorentzian sign
    convention. Its cells and isometries retain this same ambient object.
    A marked perfect-domain traversal is a different arithmetic operation: the
    local marked-cell objects above do not turn an unmarked traversal into the
    orbit decomposition of marked cells.
    """
    assert marked_vectors is None, (
        f"cannot compute the reduction complex of {lattice} marked by {marked_vectors}: only the unmarked perfect-domain decomposition of a Lorentzian lattice is available"
    )
    from sage_indefinite_port.indefinite.lorentzian_cells import (
        perfect_domain_traversal,
    )

    return perfect_domain_traversal(lattice, "total")


__all__ = [
    "LorentzianPerfectDomainTraversal",
    "MarkedReductionCell",
    "MarkedReductionCellAdjacency",
    "PerfectDomainOrbitAdjacency",
    "RationalReductionComplexExploration",
    "ReductionFaceIncidence",
    "ReductionCellAdjacency",
]
