r"""Positive-cone components and their projectivized hyperbolic geometry."""

from itertools import count, product
from math import gcd

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.objects import OwnedParameterizedCategory
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.owned_category import _object_of
from sage_extensions.rings.real import RR


def _real_ambient_vector(lattice, ambient, vector):
    match element_parent(vector):
        case parent if parent is ambient:
            return vector
        case parent if parent is lattice:
            coordinates = vector.to_vector()
            return ambient.linear_combination(
                {
                    label: RR(coordinates(label))
                    for label in coordinates.support().domain()
                }
            )
        case _:
            return ambient(vector)


def _real_pairing(lattice, ambient, left, right):
    left = _real_ambient_vector(lattice, ambient, left)
    right = _real_ambient_vector(lattice, ambient, right)
    labels = tuple(lattice.module_generating_set())
    left_coordinates = left.to_vector()
    right_coordinates = right.to_vector()
    zero = RR.zero()
    return sum(
        (
            left_coordinates(left_label)
            * right_coordinates(right_label)
            * RR(
                lattice.b(
                    lattice.module_generator(left_label),
                    lattice.module_generator(right_label),
                )
            )
            for left_label in labels
            for right_label in labels
        ),
        zero,
    )


def _positive_component_contains(lattice, ambient, timelike, vector, *, closure=False) -> bool:
    vector = _real_ambient_vector(lattice, ambient, vector)
    square = _real_pairing(lattice, ambient, vector, vector)
    pairing = _real_pairing(lattice, ambient, vector, timelike)
    match closure:
        case True:
            return square >= RR.zero() and pairing >= RR.zero()
        case False:
            return square > RR.zero() and pairing > RR.zero()


def _timelike_witness(lattice):
    r"""Find an integral vector in the nonempty positive cone of a ``(1,n)`` lattice."""
    assert lattice.module_rank().is_finite(), (
        f"cannot search {lattice} for a vector of positive square: the search needs a "
        f"lattice of finite rank, and {lattice} has rank {lattice.module_rank()}"
    )
    rank = int(lattice.module_rank())
    for height in count(1):
        for coordinates in product(range(-height, height + 1), repeat=rank):
            match max((abs(value) for value in coordinates), default=0) == height:
                case False:
                    continue
                case True:
                    vector = lattice(coordinates)
                    match lattice.q(vector) > lattice.base_ring().zero():
                        case True:
                            return vector
                        case False:
                            pass


class _HyperbolicTopologyData(SageObject):
    r"""Private standard topology of one represented hyperbolic projectivization."""

    def open_subsets(self, space):
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, subset) -> bool:
        power = space.power_set()
        selected = power(subset)
        match selected:
            case _ if selected == power.bottom():
                return True
            case _ if selected == power.top():
                return True
            case _:
                assert False, (
                    f"cannot decide whether {selected} is open in the hyperbolic space "
                    f"{space}: openness is decided only for the empty set and the whole "
                    f"space"
                )


def _primitive_on_selected_ray(lattice, vector, timelike):
    vector = lattice(vector)
    vector_coordinates = vector.to_vector()
    coordinates = tuple(
        int(vector_coordinates(label))
        for label in lattice.module_generating_set()
    )
    nonzero_coordinates = tuple(abs(entry) for entry in coordinates if entry)
    if not nonzero_coordinates:
        raise ValueError(
            f"the zero vector of {lattice} spans no ray: a point of a projective space is "
            f"the ray of a nonzero vector"
        )
    content = gcd(*nonzero_coordinates)
    primitive = lattice(tuple(entry // content for entry in coordinates))
    if lattice.b(primitive, timelike) < 0:
        primitive = -primitive
    return primitive


class PositiveConeComponents(OwnedParameterizedCategory):
    r"""Chosen components of ``{x : q(x)>0}`` for lattices of signature ``(1,n)``."""

    def __init__(self, lattice) -> None:
        signature = lattice.signature_pair()
        assert int(signature.first()) == 1 and int(signature.second()) >= 1, (
            f"{lattice} has no category of positive-cone components: it must have "
            f"signature (1, n) with n >= 1, but its signature is {signature}"
        )
        super().__init__(lattice)

    def parameter_category(self):
        from sage_extensions.categories.lattices import Lattices

        return Lattices(_owned_integers())

    def lattice(self):
        return self.base()

    @cached_method
    def ambient_space(self):
        return RR.free_module(self.lattice().module_generating_set())

    @classmethod
    def _repr_object_names(cls):
        return "positive-cone components"

    def super_categories(self):
        return [Sets().Subobjects(self.ambient_space())]

    def an_object(self):
        return self.component_through(self.reference_vector())

    @cached_method
    def reference_vector(self):
        r"""Return the integral vector of positive square that labels the components.

        The positive cone ``{x : q(x) > 0}`` of a lattice of signature
        ``(1, n)`` has exactly two components, exchanged by ``-1``, and a
        timelike ``t`` lies in the component of ``w`` exactly when
        ``b(t, w) > 0``.  So ``w`` and ``-w`` label the two components.
        """
        return _timelike_witness(self.lattice())

    def component_through(self, timelike):
        r"""Return the component of ``{x : q(x) > 0}`` that contains ``timelike``.

        A component is a subset of ``L ⊗ RR``, determined by the sign of
        ``b(timelike, w)`` for the reference vector ``w``, so equal components
        are the same object.
        """
        lattice = self.lattice()
        timelike = lattice(timelike)
        assert lattice.q(timelike) > lattice.base_ring().zero(), (
            f"{timelike} lies in no component of the positive cone of {lattice}: "
            f"it must have positive square, but q = {lattice.q(timelike)}"
        )
        reference = self.reference_vector()
        match lattice.b(timelike, reference) > lattice.base_ring().zero():
            case True:
                return self._component_labelled_by(reference)
            case False:
                return self._component_labelled_by(-reference)

    @cached_method
    def _component_labelled_by(self, label):
        return _labelled_positive_cone_component(self, label)

    class ParentMethods:
        def __init__(self, lattice, timelike, **rest) -> None:
            signature = lattice.signature_pair()
            if int(signature.first()) != 1 or int(signature.second()) < 1:
                raise ValueError(
                    f"cannot select a component of the positive cone of {lattice}: the "
                    f"lattice must have signature (1, n) with n >= 1, but its signature "
                    f"is {signature}"
                )
            timelike = lattice(timelike)
            if lattice.q(timelike) <= 0:
                raise ValueError(
                    f"{timelike} cannot select a component of the positive cone of "
                    f"{lattice}: it must have positive square, but q = {lattice.q(timelike)}"
                )
            self._lattice = lattice
            self._timelike = timelike
            super().__init__(**rest)

        def lattice(self):
            return self._lattice

        def ambient_space(self):
            return self.codomain()

        def timelike_vector(self):
            return self._timelike

        def contains(self, vector) -> bool:
            return _positive_component_contains(
                self.lattice(),
                self.ambient_space(),
                self.timelike_vector(),
                vector,
            )

        def closure_contains(self, vector) -> bool:
            return _positive_component_contains(
                self.lattice(),
                self.ambient_space(),
                self.timelike_vector(),
                vector,
                closure=True,
            )

        def opposite(self):
            return _positive_cone_component(self.lattice(), -self.timelike_vector())

        def __eq__(self, other):
            r"""Two components of the positive cone of ``L`` are equal when they meet.

            The components of ``{x : q(x) > 0}`` are disjoint, and timelike
            ``s``, ``t`` lie in one component exactly when ``b(s, t) > 0``.  Any
            other subset of ``L ⊗ RR`` is compared through its inclusion.
            """
            if self is other:
                return True
            match other in PositiveConeComponents(self.lattice()):
                case True:
                    lattice = self.lattice()
                    pairing = lattice.b(self.timelike_vector(), other.timelike_vector())
                    return pairing > lattice.base_ring().zero()
                case False:
                    return super().__eq__(other)

        def __ne__(self, other):
            from sage_extensions.logic import negation

            return negation(self == other)

        def __hash__(self) -> int:
            # Equal subsets of ``L ⊗ RR`` have the same inclusion codomain.
            return hash(self.codomain())

        @cached_method
        def projectivization(self):
            return _hyperbolic_space(self)

        def _repr_(self):
            return f"Positive-cone component of {self.lattice()} ⊗ RR containing {self.timelike_vector()}"


class HyperbolicSpaces(OwnedParameterizedCategory):
    r"""Hyperbolic spaces of dimension ``n``.

    An object is a complete simply connected Riemannian ``n``-manifold of
    constant sectional curvature ``-1``.  Any two are isometric (the
    Killing--Hopf theorem), so the family is parameterized by the dimension
    ``n >= 1`` alone.  Each hyperboloid model ``HH(C^+)`` is an object: for a
    lattice ``L`` of signature ``(1, n)`` and a chosen component ``C^+`` of
    ``{x in L_RR : q(x) > 0}``, ``HH(C^+)`` is ``{x in C^+ : q(x) = 1}`` with
    the metric ``-b`` on each tangent space ``x^perp``.  It is
    ``SO_0(1, n)/SO(n)``, a Riemannian globally symmetric space of the
    noncompact type (Helgason, Ch. X, §6, Table V, type BDI with ``q = 1``),
    and ``RiemannianManifolds().GloballySymmetric()`` is the immediate
    supercategory.  The rays of positive rational vectors are its rational
    points, the separate object ``rational_points()``.
    """

    @staticmethod
    def __classcall__(cls, dimension):
        dimension = _owned_integers()(dimension)
        assert dimension >= 1, (
            f"a hyperbolic space has dimension at least 1, and {dimension} is not"
        )
        return Category.__classcall__(cls, dimension)

    def dimension(self):
        return self.parameter()

    def _repr_object_names(self):
        return f"hyperbolic spaces of dimension {self.dimension()}"

    def super_categories(self):
        from sage_extensions.categories.manifolds import RiemannianManifolds

        return [RiemannianManifolds().GloballySymmetric()]

    @cached_method
    def an_object(self):
        r"""Return the standard ``H^n``, the hyperboloid of ``I_{1,n}`` in its reference positive-cone component."""
        from sage_extensions.categories.lattices import Lattices

        lattice = Lattices.IPQ(1, self.dimension())
        return PositiveConeComponents(lattice).an_object().projectivization()

    def _call_(self, component):
        r"""Return the hyperboloid model ``HH(C^+)`` of a positive-cone component of rank ``n + 1``."""
        assert component.lattice().module_rank() == self.dimension() + 1, (
            f"{component} spans a hyperbolic space of dimension "
            f"{component.lattice().module_rank() - 1}, not {self.dimension()}"
        )
        return component.projectivization()

    class ParentMethods:
        def __init__(self, component, **rest) -> None:
            self._component = component
            super().__init__(**rest)

        def positive_cone_component(self):
            return self._component

        def lattice(self):
            return self._component.lattice()

        def riemannian_metric(self):
            r"""Return the metric ``-b`` restricted to each tangent space ``x^perp`` of the hyperboloid."""
            pass

        @cached_method
        def rational_points(self):
            r"""Return the topological space of rays of positive rational vectors of the component."""
            return _object_of(
                HyperbolicRationalPoints(self._component),
                topology_data=_HyperbolicTopologyData(),
                component=self._component,
            )

        def rational_point(self, vector):
            r"""Return the rational point on the ray of ``vector``, a positive vector of the component."""
            return self.rational_points()(vector)

        def ideal_point(self, vector):
            r"""Return the point at infinity on the ray of the isotropic ``vector``.

            An ideal point of the projectivized component is an isotropic ray
            of its closure, which is the one-dimensional rational polyhedral
            cone it spans.
            """
            from sage_extensions.categories.polyhedral_cones import (
                RationalPolyhedralCones,
            )

            lattice = self.lattice()
            vector = lattice(vector)
            assert lattice.q(vector) == 0 and self._component.closure_contains(vector) and vector != lattice.zero(), (
                f"{vector} does not define an ideal point of {self}: an ideal point is the "
                f"ray of a nonzero isotropic vector in the closure of {self._component}, "
                f"and {vector} has square {lattice.q(vector)}"
            )
            primitive = _primitive_on_selected_ray(
                lattice, vector, self._component.timelike_vector()
            )
            return RationalPolyhedralCones(lattice).from_rays((primitive,))

        def projectivize_cone(self, cone):
            r"""Return the hyperbolic polyhedron of rational points on the rays of ``cone``."""
            if cone.ambient_lattice() is not self.lattice():
                raise ValueError(
                    f"cannot projectivize {cone} into {self}: the cone lies in "
                    f"{cone.ambient_lattice()}, not in {self.lattice()}"
                )
            if not cone.lies_in_closed_positive_cone(self._component.timelike_vector()):
                raise ValueError(
                    f"cannot projectivize {cone} into {self}: a hyperbolic polyhedron comes "
                    f"from a cone in the closure of {self._component}, and {cone} is not "
                    f"contained in it"
                )
            points = self.rational_points()
            subset = points.condition_set(
                lambda point: cone.contains(point.representative())
            )
            return Sets().Subobjects(points).object(
                subset.inclusion(),
                categories=(HyperbolicPolyhedra(self),),
                construction_data={"space": self, "cone": cone},
            )

        def isometric_action(self, group):
            r"""Return the ``Gamma``-space ``(HH(C^+), rho)`` of a group ``Gamma`` of isometries of ``L``.

            ``group`` is a subgroup ``Gamma`` of ``O(L)``, for instance the
            reflection group ``W(L)``.  An isometry ``g`` of ``L`` maps the
            cone ``{q > 0}`` to itself and permutes its two components, so
            ``rho(g)`` is the isometry ``x |-> eps g x`` of the hyperboloid,
            with ``eps = +-1`` the sign that keeps ``g x`` in ``C^+``: this is
            the action of ``O(L)`` on ``HH(C^+)``, the set of positive lines,
            through ``O(L) -> PO(L)`` (Ratcliffe, Foundations of Hyperbolic
            Manifolds, Ch. 3).  It is a left action, and ``-1`` acts
            trivially.  ``O(L)`` is discrete in ``O(L tensor RR)`` and the
            stabilizer of a point of ``HH^n`` is compact, so ``Gamma`` acts
            properly discontinuously.  The result is an object of
            ``GObjects(Gamma, RiemannianManifolds()).ProperlyDiscontinuous()``;
            its ``orbit_space()`` is the Riemannian orbifold ``Gamma\HH^n``.
            """
            from sage_extensions.categories.group.g_objects import GObjects
            from sage_extensions.categories.manifolds import RiemannianManifolds

            return GObjects(group, RiemannianManifolds()).ProperlyDiscontinuous().on_space(
                self, lambda element, point: self._isometry_image(element, point)
            )

        def _isometry_image(self, element, point):
            r"""The point ``eps g x`` for ``g`` an isometry of the lattice and ``x`` a point of the hyperboloid."""
            frame = self._hyperboloid_frame()
            lattice = self.lattice()
            assert element.domain() is lattice and element.codomain() is lattice, (
                f"{element} does not act on {self}: an isometry of the hyperboloid of {lattice} "
                f"comes from an isometry of {lattice}, and {element} is a map "
                f"{element.domain()} -> {element.codomain()}"
            )
            vector = frame.vector(tuple(point.coordinates()))
            images = tuple(
                frame.coordinates(element(generator)) for generator in frame.generators
            )
            image = tuple(
                sum((vector[source] * images[source][target] for source in range(frame.rank)), RR.zero())
                for target in range(frame.rank)
            )
            match frame.pairing(image, frame.timelike) > RR.zero():
                case True:
                    return self.point(frame.chart(image), "hyperboloid")
                case False:
                    return self.point(frame.chart(tuple(-entry for entry in image)), "hyperboloid")

        @cached_method
        def _hyperboloid_frame(self):
            return _HyperboloidFrame(self.lattice(), self._component.timelike_vector())

        def _repr_(self):
            component = self.positive_cone_component()
            return (
                f"Hyperbolic space HH^{self.dimension()}: the hyperboloid q = 1 in the "
                f"positive-cone component of {component.lattice()} ⊗ RR containing "
                f"{component.timelike_vector()}"
            )


class HyperbolicRationalPoints(OwnedParameterizedCategory):
    r"""The rays of positive rational vectors of a chosen positive-cone component.

    A point is the ray ``RR_{>0} v`` of a vector ``v`` of ``L`` with
    ``q(v) > 0`` in ``C^+``, represented by its primitive lattice vector; it
    meets the hyperboloid of ``HH(C^+)`` in ``v / sqrt(q(v))``.
    """

    def parameter_category(self):
        component = self.parameter()
        return PositiveConeComponents(component.lattice())

    def positive_cone_component(self):
        return self.base()

    @classmethod
    def _repr_object_names(cls):
        return "spaces of rational hyperbolic points"

    def super_categories(self):
        return [TopologicalSpaces()]

    def an_object(self):
        return _hyperbolic_space(self.positive_cone_component()).rational_points()

    class ElementMethods(Element):
        r"""A rational point of a hyperbolic space: the ray of a positive vector of the component."""

        def __init__(self, parent: Parent, representative) -> None:
            Element.__init__(self, parent)
            self._representative = representative

        def representative(self):
            r"""Return the primitive lattice vector on the ray, pairing positively with the timelike vector."""
            return self._representative

        def __eq__(self, other) -> bool:
            return (
                element_parent(other) is self.parent()
                and other.representative() == self.representative()
            )

        def __ne__(self, other) -> bool:
            return not self == other

        def __hash__(self) -> int:
            return hash((id(self.parent()), self.representative()))

        def _repr_(self) -> str:
            return f"hyperbolic point [{self.representative()}]"

    class ParentMethods:
        def __init__(self, component, **rest) -> None:
            self._component = component
            super().__init__(**rest)

        def positive_cone_component(self):
            return self._component

        def lattice(self):
            return self._component.lattice()

        def __contains__(self, datum) -> bool:
            match element_parent(datum):
                case parent if parent is self:
                    return True
                case parent if parent is self.lattice():
                    return self._component.contains(datum)
                case _:
                    return False

        is_parent_of = __contains__

        def __call__(self, *args, **kwargs):
            r"""Construct a point through the owned element construction directly."""
            return self._element_constructor_(*args, **kwargs)

        def _element_constructor_(self, datum):
            r"""Return the point on the ray of ``datum``, a positive vector of the component or a point of this space."""
            match datum:
                case _ if element_parent(datum) is self:
                    return datum
                case _:
                    assert self._component.contains(datum), (
                        f"{datum} does not define a point of {self}: a rational point is "
                        f"the ray of a vector of positive square in {self._component}, "
                        f"and {datum} is not in that component"
                    )
                    return self.element_class(
                        self,
                        _primitive_on_selected_ray(
                            self.lattice(), datum, self._component.timelike_vector()
                        ),
                    )

        def rational_point(self, vector):
            return self(vector)

        def hyperbolic_space(self):
            r"""Return ``HH(C^+)``, the hyperbolic space whose rational points these are."""
            return self._component.projectivization()

        def _repr_(self):
            return f"Rational points of the hyperbolic space of {self._component}"


class HyperbolicPolyhedra(OwnedParameterizedCategory):
    r"""Projectivized rational polyhedral cones in a chosen hyperbolic space.

    An object is the subset of the rational points of ``HH(C^+)`` lying on
    the rays of a rational polyhedral cone in the closure of ``C^+``, with
    its inclusion.
    """

    def parameter_category(self):
        return HyperbolicSpaces(self.parameter().dimension())

    def hyperbolic_space(self):
        return self.base()

    @classmethod
    def _repr_object_names(cls):
        return "hyperbolic polyhedra"

    def super_categories(self):
        return [Sets().Subobjects(self.hyperbolic_space().rational_points())]

    def an_object(self):
        from sage_extensions.categories.polyhedral_cones import (
            RationalPolyhedralCones,
        )

        space = self.hyperbolic_space()
        ray = RationalPolyhedralCones(space.lattice()).from_rays(
            (space.positive_cone_component().timelike_vector(),)
        )
        return space.projectivize_cone(ray)

    class ParentMethods:
        def __init__(self, space, cone, **rest) -> None:
            self._space = space
            self._cone = cone
            super().__init__(**rest)

        def hyperbolic_space(self):
            return self._space

        def cone(self):
            return self._cone

        def ordinary_vertices(self):
            space = self.hyperbolic_space()
            lattice = space.lattice()
            return finite_ordered_set(
                tuple(space.rational_point(ray) for ray in self.cone().primitive_rays() if lattice.q(ray) > 0)
            )

        def ideal_vertices(self):
            space = self.hyperbolic_space()
            lattice = space.lattice()
            return finite_ordered_set(
                tuple(space.ideal_point(ray) for ray in self.cone().primitive_rays() if lattice.q(ray) == 0)
            )

        def wall_roots(self):
            return self.cone().wall_roots()

        def weyl_group(self):
            return self.cone().weyl_group()

        def coxeter_diagram(self):
            return self.cone().coxeter_diagram()

        def is_compact(self) -> bool:
            if self.cone().is_complete_wall_set() is not True:
                raise ValueError(
                    f"cannot decide whether {self} is compact: compactness is read from the "
                    f"ideal vertices, which requires every wall of {self.cone()} to be known, "
                    f"and its wall set is not known to be complete"
                )
            return self.ideal_vertices().cardinality() == 0

        def _repr_(self):
            return f"Hyperbolic polyhedron from {self.cone()}"


def _positive_cone_component(lattice, timelike):
    return PositiveConeComponents(lattice).component_through(timelike)


def _labelled_positive_cone_component(category, timelike):
    lattice = category.lattice()
    ambient = category.ambient_space()
    subset = ambient.condition_set(
        lambda vector: _positive_component_contains(
            lattice,
            ambient,
            timelike,
            vector,
        )
    )
    return Sets().Subobjects(ambient).object(
        subset.inclusion(),
        categories=(category,),
        construction_data={"lattice": lattice, "timelike": timelike},
    )


class _HyperboloidFrame(SageObject):
    r"""The coordinates of the chart ``hyperboloid`` of ``HH(C^+)``; a private realization.

    For ``t`` the timelike vector of ``C^+`` and ``w_j = b(t, e_j)``, choose
    ``k`` with ``w_k != 0``; the vectors ``u_j = w_k e_j - w_j e_k``, ``j != k``,
    are a basis of ``t^perp``.  A point ``x`` has chart coordinates ``y`` with
    ``x - (b(x, t)/b(t, t)) t = sum_j y_j u_j``, and conversely
    ``x = s t + sum_j y_j u_j`` with ``s = sqrt((1 - q(y))/q(t))``.
    """

    def __init__(self, lattice, timelike) -> None:
        self.labels = tuple(lattice.module_generating_set())
        self.generators = tuple(lattice.module_generator(label) for label in self.labels)
        self.rank = len(self.labels)
        self.gram = tuple(
            tuple(RR(lattice.b(left, right)) for right in self.generators) for left in self.generators
        )
        self.timelike = self.coordinates(timelike)
        self.timelike_pairings = tuple(
            sum((self.timelike[row] * self.gram[row][column] for row in range(self.rank)), RR.zero())
            for column in range(self.rank)
        )
        self.pivot = next(
            index for index, value in enumerate(self.timelike_pairings) if value != RR.zero()
        )
        self.others = tuple(index for index in range(self.rank) if index != self.pivot)

    def coordinates(self, vector):
        coordinates = vector.to_vector()
        support = {label: RR(coordinates(label)) for label in coordinates.support().domain()}
        return tuple(support.get(label, RR.zero()) for label in self.labels)

    def pairing(self, left, right):
        return sum(
            (
                left[row] * self.gram[row][column] * right[column]
                for row in range(self.rank)
                for column in range(self.rank)
            ),
            RR.zero(),
        )

    def vector(self, chart_coordinates):
        w = self.timelike_pairings
        projection = [RR.zero()] * self.rank
        for position, index in enumerate(self.others):
            projection[index] = chart_coordinates[position] * w[self.pivot]
            projection[self.pivot] -= chart_coordinates[position] * w[index]
        projection = tuple(projection)
        height = (
            (RR.one() - self.pairing(projection, projection)) / self.pairing(self.timelike, self.timelike)
        ).sqrt()
        return tuple(height * self.timelike[index] + projection[index] for index in range(self.rank))

    def chart(self, vector):
        ratio = self.pairing(vector, self.timelike) / self.pairing(self.timelike, self.timelike)
        projection = tuple(vector[index] - ratio * self.timelike[index] for index in range(self.rank))
        return tuple(projection[index] / self.timelike_pairings[self.pivot] for index in self.others)


def _hyperbolic_space(component):
    from sage_extensions.categories.manifolds import RiemannianManifolds

    return RiemannianManifolds().GloballySymmetric().hyperbolic_space(component)


__all__ = [
    "HyperbolicPolyhedra",
    "HyperbolicRationalPoints",
    "HyperbolicSpaces",
    "PositiveConeComponents",
]
