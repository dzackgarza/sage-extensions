r"""Exact rational polyhedral cones retained by homogeneous half-spaces."""

from sage.arith.functions import lcm
from sage.arith.misc import gcd
from sage.geometry.cone import Cone as SageCone
from sage.geometry.polyhedron.constructor import Polyhedron
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values
from sage_extensions.categories.abstract_categories.objects import OwnedParameterizedCategory
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _own_ring,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of
from sage_extensions.validation import validator


def _primitive_integral_coordinates(coordinates):
    rationals = tuple(SageQQ(coordinate) for coordinate in coordinates)
    scale = lcm(tuple(coordinate.denominator() for coordinate in rationals))
    integers = tuple(SageZZ(scale * coordinate) for coordinate in rationals)
    content = gcd(tuple(abs(coordinate) for coordinate in integers if coordinate))
    if content == 0:
        return integers
    return tuple(coordinate // content for coordinate in integers)


def _owned_vector(module, coordinates):
    ring = module.base_ring()
    return module.linear_combination(
        {
            label: ring(int(coordinate))
            for label, coordinate in zip(module.module_generating_set(), coordinates, strict=True)
            if coordinate
        }
    )


def _integral_covector(lattice, coordinates):
    r"""The primitive integral covector of ``lattice`` on the ray of the rational ``coordinates``.

    A homogeneous half-space ``a(x) >= 0`` is unchanged by a positive
    rescaling of ``a``, so a rational covector is stated by the primitive
    integral covector on its ray.
    """
    return _owned_vector(lattice.dual_module(), _primitive_integral_coordinates(tuple(coordinates)))


def _engine_rational_coordinates(coordinates):
    r"""Lower session rational coordinates of a wall to the engine, for :func:`_integral_covector`."""
    rationals = _owned_rationals()
    return tuple(_engine_element(rationals, coordinate) for coordinate in coordinates)


def _ambient_vector(lattice, ambient, vector):
    r"""Read a lattice or rational-coordinate vector in ``lattice tensor QQ``."""
    match element_parent(vector):
        case parent if parent is ambient:
            return vector
        case parent if parent is lattice:
            coordinates = vector.to_vector()
            rationals = ambient.base_ring()
            return ambient.linear_combination(
                {
                    label: rationals(coordinates(label))
                    for label in coordinates.support().domain()
                }
            )
        case _:
            return ambient(vector)


def _evaluate_covector(lattice, ambient, covector, vector):
    dual = lattice.dual_module()
    covector = dual(covector)
    vector = _ambient_vector(lattice, ambient, vector)
    rationals = ambient.base_ring()
    covector_coordinates = covector.to_vector()
    vector_coordinates = vector.to_vector()
    return sum(
        (
            rationals(covector_coordinates(label)) * vector_coordinates(label)
            for label in covector_coordinates.support().domain()
        ),
        rationals.zero(),
    )


def _cone_contains(lattice, ambient, halfspaces, equations, vector) -> bool:
    zero = ambient.base_ring().zero()
    return all(
        _evaluate_covector(lattice, ambient, covector, vector) >= zero
        for covector in halfspaces
    ) and all(
        _evaluate_covector(lattice, ambient, covector, vector) == zero
        for covector in equations
    )


def _cone_from_engine_polyhedron(lattice, polyhedron, wall_roots=None):
    r"""The cone whose homogeneous H-representation is that of Sage's exact ``polyhedron``.

    Private engine crossing of :meth:`RationalPolyhedralCones.from_rays` and
    of the cone operations that compute a new cone in the engine.
    """
    assert all(inequality.b() == 0 for inequality in polyhedron.inequalities()), (
        f"{polyhedron} is not a cone in {lattice}: a cone is cut out by homogeneous "
        f"inequalities, but some inequality has a nonzero constant term"
    )
    assert all(equation.b() == 0 for equation in polyhedron.equations()), (
        f"{polyhedron} is not a cone in {lattice}: a cone is cut out by homogeneous "
        f"equations, but some equation has a nonzero constant term"
    )
    return _rational_polyhedral_cone(
        lattice,
        tuple(_integral_covector(lattice, inequality.A()) for inequality in polyhedron.inequalities()),
        equation_covectors=tuple(
            _integral_covector(lattice, equation.A()) for equation in polyhedron.equations()
        ),
        wall_roots=wall_roots,
    )


class RationalPolyhedralConeMorphism:
    r"""A rational linear map carrying one cone into another."""

    def __init__(self, parent, linear_map):
        self._linear_map = linear_map
        super().__init__(
            parent,
            Sets().Mor(parent.domain(), parent.codomain())(linear_map),
        )

    def linear_map(self):
        return self._linear_map

    @validator
    def validate_cone_image(self):
        target = self.codomain()
        source = self.domain()
        ambient = source.ambient_space()
        if not all(
            target.contains(self.linear_map()(_ambient_vector(source.ambient_lattice(), ambient, ray)))
            for ray in source.primitive_rays()
        ):
            raise ValueError(f"{self.linear_map()} does not carry every ray of {source} into {target}")
        if not all(
            target.contains(self.linear_map()(_ambient_vector(source.ambient_lattice(), ambient, line)))
            and target.contains(-self.linear_map()(_ambient_vector(source.ambient_lattice(), ambient, line)))
            for line in source.lineality_generators()
        ):
            raise ValueError(f"{self.linear_map()} does not carry the lineality of {source} into {target}")

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        return RationalPolyhedralCones(other.domain().ambient_lattice()).Mor(
            other.domain(), self.codomain()
        )(self.linear_map() * other.linear_map())


class RationalPolyhedralConeMor(CategoricalMor):
    r"""Linear maps that carry the source cone into the target cone."""

    ElementMethods = RationalPolyhedralConeMorphism

    def _element_constructor_(self, linear_map, *, check=False):
        if element_parent(linear_map) is self:
            return linear_map
        source = self.domain().ambient_space()
        target = self.codomain().ambient_space()
        linear = source.module_category().Mor(source, target)(linear_map)
        arrow = self.element_class(self, linear)
        arrow.validate_cone_image(check=check)
        return arrow

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError("a cone identity requires the same source and target cone")
        ambient = self.domain().ambient_space()
        return self(ambient.module_category().Mor(ambient, ambient).identity())


class RationalPolyhedralConeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RationalPolyhedralConeMor


class RationalPolyhedralCones(OwnedParameterizedCategory):
    r"""Rational polyhedral cones in a selected integral coordinate lattice.

    A cone is retained by homogeneous integral covectors ``ell`` defining
    ``ell(x) >= 0``.  Sage's exact polyhedral objects are private computation
    engines; the public object retains the ambient lattice and the covectors.
    """

    _MorCategory = RationalPolyhedralConeMorCategoryConstruction

    def parameter_category(self):
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )

        return FramedFreeModules(_owned_integers())

    def ambient_lattice(self):
        return self.base()

    @cached_method
    def ambient_space(self):
        rationals = _owned_rationals()
        return rationals.free_module(self.ambient_lattice().module_generating_set())

    @classmethod
    def _repr_object_names(cls):
        return "rational polyhedral cones"

    def super_categories(self):
        return [Sets().Subobjects(self.ambient_space())]

    def an_object(self):
        dual = self.ambient_lattice().dual_module()
        return _rational_polyhedral_cone(
            self.ambient_lattice(),
            tuple(dual.module_generators()),
        )

    def from_halfspaces(self, halfspace_covectors, *, equation_covectors=(), wall_roots=None):
        r"""Return the rational cone defined by homogeneous covector inequalities.

        Each covector imposes a nonnegative pairing with points of the cone.
        Equations impose zero pairing; both families use the ambient dual module.
        """
        return _rational_polyhedral_cone(
            self.ambient_lattice(), halfspace_covectors,
            equation_covectors=equation_covectors, wall_roots=wall_roots,
        )

    def from_rays(self, rays, *, wall_roots=None):
        r"""Return the cone generated by the rays in this category's lattice.

        The rays are nonzero vectors of ``lattice``; the half-spaces cutting
        the cone out are computed by the exact polyhedral engine.  The
        ``wall_roots``, when stated, are the roots of ``lattice`` whose
        mirrors contain the cone, so that
        :meth:`ParentMethods.reflection_group` is the subgroup of the
        reflection group fixing the cone pointwise.
        """
        lattice = self.ambient_lattice()
        labels = tuple(lattice.module_generating_set())

        def engine_row(ray):
            coordinates = lattice(ray).to_vector()
            return tuple(SageQQ(int(coordinates(label))) for label in labels)

        rows = tuple(engine_row(ray) for ray in rays)
        return _cone_from_engine_polyhedron(
            lattice,
            Polyhedron(vertices=[(0,) * len(labels)], rays=rows, base_ring=SageQQ),
            wall_roots=wall_roots,
        )

    class ParentMethods:
        def __init__(
            self,
            lattice,
            halfspace_covectors,
            equation_covectors=(),
            wall_roots=None,
            complete=None,
            **rest,
        ):
            self._lattice = lattice
            dual = lattice.dual_module()
            self._halfspace_covectors = finite_ordered_set(
                tuple(dual(covector) for covector in halfspace_covectors)
            )
            self._equation_covectors = finite_ordered_set(
                tuple(dual(covector) for covector in equation_covectors)
            )
            self._wall_roots = None if wall_roots is None else finite_ordered_set(tuple(wall_roots))
            self._complete = complete
            labels = tuple(dual.module_generating_set())

            def engine_row(covector):
                coordinates = covector.to_vector()
                return [SageQQ.zero()] + [
                    SageQQ(int(coordinates(label))) for label in labels
                ]

            rows = [engine_row(covector) for covector in self._halfspace_covectors]
            equations = [engine_row(covector) for covector in self._equation_covectors]
            self._engine = Polyhedron(ieqs=rows, eqns=equations, base_ring=SageQQ)
            super().__init__(**rest)

        def ambient_lattice(self):
            return self._lattice

        def ambient_space(self):
            return self.codomain()

        def halfspace_covectors(self):
            return self._halfspace_covectors

        def equation_covectors(self):
            return self._equation_covectors

        def wall_roots(self):
            return self._wall_roots

        def reflection_group(self):
            r"""Return the subgroup generated by reflections in the retained wall roots.

            This operation is available exactly when the cone was constructed
            from roots of its ambient lattice.  It uses those retained roots,
            not a second root enumeration.
            """
            if self._wall_roots is None:
                raise ValueError(
                    f"{self} has no reflection group: it was not constructed with the roots "
                    f"whose mirrors are its walls"
                )
            lattice = self.ambient_lattice()
            return lattice.O().subgroup(
                tuple(lattice.reflection(root) for root in self._wall_roots)
            )

        weyl_group = reflection_group

        def coxeter_diagram(self):
            r"""Return the exact Coxeter diagram determined by the retained wall roots."""
            if self._wall_roots is None:
                raise ValueError(
                    f"{self} has no Coxeter diagram: it was not constructed with the roots "
                    f"whose mirrors are its walls"
                )
            from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams

            return CoxeterDiagrams().from_roots(finite_indexed_family_from_values(None, tuple(self._wall_roots)))

        def transport(self, isometry):
            r"""Transport this cone and all retained defining covectors along an isometry."""
            source = self.ambient_lattice()
            if isometry.domain() is not source:
                raise ValueError(
                    f"cannot transport {self} along {isometry}: the cone lies in {source}, "
                    f"but the isometry has domain {isometry.domain()}"
                )
            target = isometry.codomain()
            inverse = isometry.inverse()
            labels = tuple(target.module_generating_set())
            inverse_basis = tuple(inverse(target.module_generator(label)) for label in labels)
            dual = target.dual_module()

            def transport_covector(covector):
                return dual.linear_combination({
                    label: self.evaluate_covector(covector, point)
                    for label, point in zip(labels, inverse_basis, strict=True)
                })

            roots = None
            if self._wall_roots is not None:
                roots = tuple(isometry(root) for root in self._wall_roots)
            return _rational_polyhedral_cone(
                target,
                tuple(
                    transport_covector(covector)
                    for covector in self._halfspace_covectors
                ),
                equation_covectors=tuple(
                    transport_covector(covector)
                    for covector in self._equation_covectors
                ),
                wall_roots=roots,
                complete=self.is_complete_wall_set(),
            )

        def chamber_complex(self):
            r"""Return the lazy Weyl-chamber complex generated by this root chamber."""
            if self._wall_roots is None:
                raise ValueError(
                    f"{self} generates no Weyl chamber complex: it was not constructed with "
                    f"the roots whose mirrors are its walls"
                )
            from sage_extensions.categories.chamber_complexes import (
                WeylChamberComplexes,
            )
            from sage_extensions.owned_category import _object_of

            return _object_of(
                WeylChamberComplexes(),
                fundamental_chamber=self,
            )

        def is_complete_wall_set(self):
            return self._complete

        def _engine_polyhedron(self):
            return self._engine

        def dimension(self):
            return self.ambient_lattice().base_ring()(int(self._engine.dim()))

        def is_pointed(self) -> bool:
            return len(tuple(self._engine.lines())) == 0

        def evaluate_covector(self, covector, vector):
            return _evaluate_covector(
                self.ambient_lattice(),
                self.ambient_space(),
                covector,
                vector,
            )

        def contains(self, vector) -> bool:
            return _cone_contains(
                self.ambient_lattice(),
                self.ambient_space(),
                self.halfspace_covectors(),
                self.equation_covectors(),
                vector,
            )

        def primitive_rays(self):
            lattice = self.ambient_lattice()
            return finite_ordered_set(
                tuple(_owned_vector(lattice, _primitive_integral_coordinates(ray)) for ray in self._engine.rays())
            )

        def lineality_generators(self):
            lattice = self.ambient_lattice()
            return finite_ordered_set(
                tuple(_owned_vector(lattice, _primitive_integral_coordinates(line)) for line in self._engine.lines())
            )

        def face_on_covector(self, covector):
            r"""Intersect this cone with the homogeneous wall ``covector=0``."""
            dual = self.ambient_lattice().dual_module()
            covector = dual(covector)
            return _rational_polyhedral_cone(
                self.ambient_lattice(),
                tuple(self._halfspace_covectors),
                equation_covectors=tuple(self._equation_covectors) + (covector,),
                complete=self.is_complete_wall_set(),
            )

        def _covector_from_engine_hrepresentation(self, inequality):
            r"""Cross one private homogeneous H-row back to the owned dual lattice."""
            if inequality.b() != 0:
                raise ArithmeticError(
                    f"a face of {self} was computed with the inequality {inequality}, which "
                    f"has a nonzero constant term; a face of a cone is cut out by "
                    f"homogeneous inequalities"
                )
            dual = self.ambient_lattice().dual_module()
            coordinates = _primitive_integral_coordinates(inequality.A())
            return _owned_vector(dual, coordinates)

        def _face_from_engine_face(self, face):
            r"""Cross one nonempty engine face using its ambient active inequalities."""
            active = tuple(
                self._covector_from_engine_hrepresentation(relation)
                for relation in face.ambient_Hrepresentation()
            )
            return _rational_polyhedral_cone(
                self.ambient_lattice(),
                tuple(self._halfspace_covectors),
                equation_covectors=tuple(self._equation_covectors) + active,
                complete=self.is_complete_wall_set(),
            )

        def faces(self, dimension):
            r"""Return all nonempty faces of the stated dimension as owned cones.

            Sage's exact polyhedron engine computes the face incidence and
            reports the ambient H-representations active on each face.  Those
            active rows are crossed back as owned equality covectors, so the
            public face remains an exact cone rather than an engine face.
            """
            dimension = int(dimension)
            if dimension < 0 or dimension > int(self.dimension()):
                return finite_ordered_set(())
            return finite_ordered_set(
                tuple(
                    self._face_from_engine_face(face)
                    for face in self._engine.faces(dimension)
                )
            )

        def ambient_dimension(self):
            r"""Return the rank of the ambient lattice, the dimension of ``L tensor QQ``."""
            return self.ambient_lattice().module_rank()

        def intersection(self, other):
            r"""Return the cone cut out by the half-spaces and equations of both cones."""
            assert other.ambient_lattice() is self.ambient_lattice(), (
                f"cannot intersect {self} with {other}: they are cones in different "
                f"lattices, {self.ambient_lattice()} and {other.ambient_lattice()}"
            )
            return _rational_polyhedral_cone(
                self.ambient_lattice(),
                tuple(self._halfspace_covectors) + tuple(other.halfspace_covectors()),
                equation_covectors=tuple(self._equation_covectors) + tuple(other.equation_covectors()),
            )

        def __eq__(self, other):
            if self is other:
                return True
            if other in RationalPolyhedralCones(self.ambient_lattice()):
                return self.is_equal_to(other)
            return super().__eq__(other)

        def is_equal_to(self, other) -> bool:
            r"""Return whether the two cones are the same subset of ``L tensor QQ``.

            Two presentations by different covector families can cut out one
            cone, so this compares the cones and not their presentations.
            """
            return (
                other.ambient_lattice() is self.ambient_lattice()
                and self._engine_polyhedron() == other._engine_polyhedron()
            )

        def is_face_of(self, other) -> bool:
            r"""Return whether this cone is a face of ``other``."""
            if other.ambient_lattice() is not self.ambient_lattice():
                return False
            polyhedron = self._engine_polyhedron()
            return any(
                face.as_polyhedron() == polyhedron
                for face in other._engine_polyhedron().faces(int(polyhedron.dim()))
            )

        def is_adjacent_to(self, other) -> bool:
            r"""Return whether the two cones share a common facet."""
            if other.ambient_lattice() is not self.ambient_lattice():
                return False
            common = self.intersection(other)
            return (
                common.dimension() == self.dimension() - 1
                and common.dimension() == other.dimension() - 1
                and common.is_face_of(self)
                and common.is_face_of(other)
            )

        def transporter_witness_to(self, other, group):
            r"""Return one element of the finite group ``group`` carrying this cone to ``other``, or ``None``.

            The search runs over the elements of the represented finite
            group; an infinite arithmetic group is handled by the surrounding traversal.
            """
            if other.ambient_lattice() is not self.ambient_lattice():
                return None
            lattice = self.ambient_lattice()
            assert group.domain() is lattice and group.codomain() is lattice, (
                f"cannot search {group} for an element carrying {self} to {other}: the "
                f"group must act on {lattice}, but it acts by maps {group.domain()} -> "
                f"{group.codomain()}"
            )
            assert group.cardinality().is_finite(), (
                f"cannot search {group} for an element carrying {self} to {other}: the "
                f"search runs over the elements of a finite group, and this group is "
                f"infinite; an infinite arithmetic group is handled by the reduction complex"
            )
            for isometry in group:
                if self.transport(isometry).is_equal_to(other):
                    return isometry
            return None

        def stabilizer(self, group):
            r"""Return the subgroup of ``group`` carrying this cone onto itself."""
            lattice = self.ambient_lattice()
            assert group.domain() is lattice and group.codomain() is lattice, (
                f"cannot form the stabilizer of {self} in {group}: the group must act on "
                f"{lattice}, but it acts by maps {group.domain()} -> {group.codomain()}"
            )
            return group.predicate_subgroup(
                lambda isometry: self.transport(isometry).is_equal_to(self),
                f"g preserves the rational polyhedral cone {self}",
            )

        def face_stabilizer(self, face, group):
            r"""Return the subgroup of ``group`` preserving this cone and its face ``face``.

            Membership in the cone stabilizer is required: the group may
            preserve the lower-dimensional face while moving the cone to
            another cone containing it.
            """
            assert face.is_face_of(self), (
                f"cannot form the stabilizer of {face} as a face of {self}: it is not a "
                f"face of that cone"
            )
            return self.stabilizer(group).intersection(face.stabilizer(group))

        def face_incidences(self, dimension, group):
            r"""Return the face inclusions of ``dimension`` with the subgroup stabilizing each pair."""
            from sage_extensions.categories.reduction_complexes import (
                ReductionFaceIncidence,
            )
            from sage_extensions.categories.sets.indexed_families import (
                finite_indexed_family,
            )

            return finite_indexed_family(
                self.faces(dimension),
                lambda face: ReductionFaceIncidence(
                    face,
                    self,
                    self.face_stabilizer(face, group),
                ),
                name=f"Face incidences of dimension {dimension} in {self}",
            )

        def adjacency_to(self, other, group):
            r"""Return the adjacency of this cone to ``other`` across their common facet, or ``None``.

            It exists when the cones share a facet and the finite group
            ``group`` carries this cone to ``other``; it retains the common
            facet and that transporter.
            """
            from sage_extensions.categories.reduction_complexes import (
                ReductionCellAdjacency,
            )

            if not self.is_adjacent_to(other):
                return None
            transporter = self.transporter_witness_to(other, group)
            if transporter is None:
                return None
            return ReductionCellAdjacency(self, other, self.intersection(other), transporter)

        def with_marks(self, marked_vectors):
            r"""Return this cone with the labelled finite family ``marked_vectors`` of nonzero-norm lattice vectors."""
            from sage_extensions.categories.reduction_complexes import (
                MarkedReductionCell,
            )

            return MarkedReductionCell(self, marked_vectors)

        def nonempty_faces(self):
            r"""Return every geometric face, from the zero face through this cone."""
            return finite_ordered_set(
                tuple(
                    face
                    for dimension in range(int(self.dimension()) + 1)
                    for face in self.faces(dimension)
                )
            )

        def facet_covectors(self):
            if self._engine.dim() <= 0:
                return finite_ordered_set(())
            return finite_ordered_set(
                tuple(
                    self._covector_from_engine_hrepresentation(inequality)
                    for inequality in self._engine.inequalities()
                )
            )

        def facets(self):
            from sage_extensions.categories.sets.indexed_families import (
                finite_indexed_family,
            )

            facets = self.facet_covectors()
            return finite_indexed_family(
                facets,
                self.face_on_covector,
                name="Facets of a rational polyhedral cone",
            )

        def hilbert_basis(self):
            assert self.is_pointed(), (
                f"cannot compute the Hilbert basis of {self}: it is computed only for a "
                f"pointed cone, and this cone contains the lines {self.lineality_generators()}"
            )
            lattice = self.ambient_lattice()
            rows = [
                tuple(int(ray.to_vector()(label)) for label in lattice.module_generating_set())
                for ray in self.primitive_rays()
            ]
            cone = SageCone(rows)
            return finite_ordered_set(tuple(_owned_vector(lattice, row) for row in cone.Hilbert_basis()))

        def ideal_rays(self):
            r"""Return the isotropic extremal rays when the ambient module is a lattice."""
            lattice = self.ambient_lattice()
            from sage_extensions.categories.lattices import Lattices

            if lattice not in Lattices(lattice.base_ring()):
                raise TypeError(
                    f"{self} has no isotropic rays: it lies in {lattice}, which has no "
                    f"quadratic form; it is in {lattice.category()}"
                )
            return finite_ordered_set(tuple(ray for ray in self.primitive_rays() if lattice.q(ray) == 0))

        def timelike_rays(self):
            r"""Return the positive-square extremal rays in the repository's hyperbolic convention."""
            lattice = self.ambient_lattice()
            from sage_extensions.categories.lattices import Lattices

            if lattice not in Lattices(lattice.base_ring()):
                raise TypeError(
                    f"{self} has no timelike rays: it lies in {lattice}, which has no "
                    f"quadratic form; it is in {lattice.category()}"
                )
            return finite_ordered_set(tuple(ray for ray in self.primitive_rays() if lattice.q(ray) > 0))

        def lies_in_closed_positive_cone(self, timelike) -> bool:
            r"""Whether this cone lies in one closed sheet of a signature ``(1,n)`` light cone.

            The exact criterion is ray/lineality based: the cone is pointed,
            every extremal ray has nonnegative square, and all nonzero rays
            pair with the selected timelike vector with one weak sign.  This
            distinguishes ideal isotropic rays from ordinary timelike rays and
            never inspects the cone's vertex at the origin.
            """
            lattice = self.ambient_lattice()
            from sage_extensions.categories.lattices import Lattices

            if lattice not in Lattices(lattice.base_ring()):
                raise TypeError(
                    f"cannot decide whether {self} lies in the closed positive cone of "
                    f"{timelike}: it lies in {lattice}, which has no quadratic form; it is "
                    f"in {lattice.category()}"
                )
            timelike = lattice(timelike)
            if lattice.q(timelike) <= 0 or not self.is_pointed():
                return False
            rays = tuple(self.primitive_rays())
            if any(lattice.q(ray) < 0 for ray in rays):
                return False
            pairings = tuple(lattice.b(ray, timelike) for ray in rays)
            return all(value >= 0 for value in pairings)

        @cached_method
        def triangulation(self):
            r"""Return simplicial subcones covering this pointed cone, as a family.

            The family is indexed by the simplices of a triangulation of the
            primitive rays: each simplex ``t`` is a set of linearly independent
            rays, its value is the subcone ``S_t`` they generate (built by
            ``from_rays``), and the ``S_t`` cover the cone.  Each ``S_t`` lies in
            the cone because its rays do; :meth:`simplicial_subcone_inclusion`
            is that inclusion.  Private engine (``OWN-06``): Sage's
            ``PointConfiguration`` on the rays as projective points computes the
            simplices; only their ray labels leave it.
            """
            from sage_extensions.categories.sets.indexed_families import finite_indexed_family

            assert self.is_pointed(), (
                f"cannot triangulate {self} by its rays: it contains the lines {self.lineality_generators()}"
            )
            lattice = self.ambient_lattice()
            rays = self.primitive_rays()
            simplices = _engine_ray_triangulation(lattice, rays)
            category = RationalPolyhedralCones(lattice)
            return finite_indexed_family(
                simplices,
                lambda simplex: category.from_rays(simplex),
                name=f"Simplicial subcones covering {self}",
            )

        def simplicial_subcone_inclusion(self, simplex):
            r"""Return the inclusion ``S_t -> C`` of the subcone of :meth:`triangulation` at ``simplex``.

            ``S_t`` is generated by rays of ``C``, so the ambient identity
            restricts to a cone morphism with these exact endpoints.
            """
            subcone = self.triangulation().value(simplex)
            ambient = self.ambient_space()
            linear = ambient.module_category().Mor(ambient, ambient).identity()
            return RationalPolyhedralCones(self.ambient_lattice()).Mor(subcone, self)(linear)

        def ray_span_saturation_index(self, subcone):
            r"""Return ``[sat(ZZ S) : ZZ S]`` for the rays ``S`` of ``subcone``.

            ``ZZ S`` is the sublattice the rays span, with its inclusion into
            the ambient lattice; the saturation quotient ``sat(ZZ S)/ZZ S`` is
            the torsion of its cokernel, and the index is its cardinality. A
            lattice point of a simplicial subcone has coordinates in
            ``(1/D) ZZ`` in its rays, ``D`` this index.
            """
            lattice = self.ambient_lattice()
            span = lattice.subobject_on(subcone.primitive_rays())
            return span.inclusion().cokernel().torsion_submodule().cardinality()

        def _repr_(self):
            return f"Rational polyhedral cone in {self.ambient_lattice()} cut out by {self.halfspace_covectors().cardinality()} half-spaces"


def _engine_ray_triangulation(lattice, rays):
    r"""Private adapter (``OWN-06``): the simplices of a triangulation of a pointed cone's rays.

    Engine: Sage's ``PointConfiguration`` on the rays scaled onto the affine
    hyperplane ``c(x) = 1``, ``c`` the sum of the rays of the dual cone, which
    is positive on every ray of a pointed cone; the triangulations of the
    cone are those of these points (Sage's ``projective=True`` input accepts
    only points with last coordinate one, TRAPS.md).  ``triangulate()``
    returns simplices as tuples of point positions.  Each ray is lowered once,
    through its owned coordinate function ``to_vector()`` and the ring
    adapter ``_engine_element``.  Returned: the finite ordered set of
    simplices, each a finite ordered set of the rays (owned lattice elements)
    it contains.
    """
    from sage.geometry.cone import Cone
    from sage.geometry.triangulation.point_configuration import PointConfiguration
    from sage.modules.free_module_element import vector as engine_vector

    ring = lattice.base_ring()
    labels = tuple(lattice.module_generating_set())
    points = tuple(rays)
    rows = [
        [SageQQ(_engine_element(ring, ray.to_vector()(label))) for label in labels]
        for ray in points
    ]
    functional = sum((engine_vector(SageQQ, ray) for ray in Cone(rows).dual().rays()), engine_vector(SageQQ, [0] * len(labels)))
    heights = [engine_vector(SageQQ, row) * functional for row in rows]
    assert all(height > 0 for height in heights), (
        f"the rays {rows} do not span a pointed cone: the sum of the dual rays is not positive on all of them"
    )
    affine = [[entry / height for entry in row] for row, height in zip(rows, heights, strict=True)]
    return finite_ordered_set(tuple(
        finite_ordered_set(tuple(points[position] for position in simplex))
        for simplex in PointConfiguration(affine).triangulate()
    ))


def _rational_polyhedral_cone(
    lattice,
    halfspace_covectors,
    *,
    equation_covectors=(),
    wall_roots=None,
    complete=None,
):
    category = RationalPolyhedralCones(lattice)
    ambient = category.ambient_space()
    halfspaces = tuple(halfspace_covectors)
    equations = tuple(equation_covectors)
    subset = ambient.condition_set(
        lambda vector: _cone_contains(
            lattice,
            ambient,
            halfspaces,
            equations,
            vector,
        )
    )
    return Sets().Subobjects(ambient).object(
        subset.inclusion(),
        categories=(category,),
        construction_data={
            "lattice": lattice,
            "halfspace_covectors": halfspaces,
            "equation_covectors": equations,
            "wall_roots": wall_roots,
            "complete": complete,
        },
    )


__all__ = ["RationalPolyhedralCones"]
