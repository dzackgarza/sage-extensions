r"""Positive-cone components and their projectivized hyperbolic geometry."""

from itertools import count, product
from math import gcd

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method
from sage.rings.infinity import Infinity
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.mor_categories import (
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import OwnedParameterizedCategory
from sage_extensions.categories.manifolds import (
    RiemannianManifoldMor,
    RiemannianManifolds,
    SmoothManifolds,
)
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import OwnedSetMorphism, Sets
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.owned_category import _object_of
from sage_extensions.rings.real import RR

HYPERBOLOID_CHART = "hyperboloid"


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
        assert lattice.has_two_component_positive_cone() is True, (
            f"{lattice} has no category of positive-cone components: it must have "
            f"signature (1, n) with n >= 1, but its signature is {lattice.signature_pair()}"
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
            if lattice.has_two_component_positive_cone() is not True:
                raise ValueError(
                    f"cannot select a component of the positive cone of {lattice}: the "
                    f"lattice must have signature (1, n) with n >= 1, but its signature "
                    f"is {lattice.signature_pair()}"
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


def _isometry_image_of_point(domain, codomain, isometry, point):
    r"""Return the point of ``codomain`` that the lattice isometry ``isometry`` carries ``point`` to.

    ``point`` is a point of the hyperboloid model ``domain``, given in the
    chart ``hyperboloid``: ``x = s t + y`` with ``t`` the timelike vector of the
    domain's component and ``y`` the coordinates in a basis of ``t^perp``.  The
    isometry is read there, in the lattice coordinates of its own images of the
    domain's generators, and the image is written in the codomain's frame,
    ``s' t' + y'``, whose timelike vector ``t'`` may be another one.  Since the
    hyperboloid is cut out by ``q = 1`` and ``-b`` is the metric, an isometry of
    the lattice whose two endpoints are one lattice carries the hyperboloid of
    the domain's component into that of one of the codomain's two, and the sign
    that puts the image in the codomain's own component is the one pairing
    positively with ``t'``: a hyperbolic point is a ray, so the sign is no part
    of it.
    """
    lattice = domain.lattice()
    assert isometry.domain() is lattice and isometry.codomain() is lattice, (
        f"{isometry} does not act on {domain}: an isometry of the hyperboloid of {lattice} "
        f"comes from an isometry of {lattice}, and {isometry} is a map "
        f"{isometry.domain()} -> {isometry.codomain()}"
    )
    match element_parent(point) is domain.point_set():
        case True:
            # A point of the model is the ray of a positive rational vector, and
            # the lattice isometry acts on that vector; the sign restoring the
            # image to the codomain's own component is the one pairing positively
            # with its timelike vector, since a point here is a ray.
            vector = isometry(point.representative())
            match codomain.positive_cone_component().contains(vector):
                case True:
                    return codomain.rational_point(vector)
                case False:
                    return codomain.rational_point(-vector)
        case False:
            pass
    match point.chart().label():
        case label if label == HYPERBOLOID_CHART:
            pass
        case label:
            raise ValueError(
                f"cannot move {point} by {isometry}: the image is read in the chart "
                f"{HYPERBOLOID_CHART}, where a point is the hyperboloid vector itself, and {point} "
                f"is given in the chart {label}"
            )
    source = domain._hyperboloid_frame()
    target = codomain._hyperboloid_frame()
    vector = source.vector(tuple(point.coordinates()))
    images = tuple(
        source.coordinates(isometry(generator)) for generator in source.generators
    )
    image = tuple(
        sum(
            (
                vector[position] * images[position][coordinate]
                for position in range(source.rank)
            ),
            RR.zero(),
        )
        for coordinate in range(source.rank)
    )
    match target.pairing(image, target.timelike) > RR.zero():
        case True:
            return codomain.point(target.chart(image), HYPERBOLOID_CHART)
        case False:
            return codomain.point(
                target.chart(tuple(-entry for entry in image)), HYPERBOLOID_CHART
            )


class HyperbolicManifoldMor(RiemannianManifoldMor):
    r"""Isometries of hyperbolic spaces induced by integral isometries of their lattice.

    An arrow ``HH(C^+) -> HH(D^+)`` of ``HyperbolicSpaces(n)`` is the smooth map
    ``[x] |-> [g x]`` induced by an isometry ``g`` of the lattice the two spaces
    are hyperboloid models of.  Such a ``g`` preserves the pairing, so it
    preserves ``q``, hence the positive cone and its two components, and it
    commutes with the projection to rays; the map it induces preserves ``-b`` on
    every tangent space, so it is a local isometry, and a local isometry of a
    complete connected hyperbolic space is its global isometry.

    The isometry group of ``HH^n`` is the projective orthogonal group
    ``PO(L_RR) = O(L_RR)/{+-1}`` of the ambient real space, which is much larger
    than the image of the integral ``O(L)``.  A real isometry given only by its
    values is not decided here, so this constructor states the arrows it does
    decide -- those induced by an integral isometry of the endpoints' own
    lattice -- and refuses anything else rather than admitting it by assumption.
    """

    class ElementMethods(RiemannianManifoldMor.ElementMethods):
        def __init__(self, parent, isometry):
            r"""Record the isometry, and the smooth map of the two hyperboloid models it induces.

            The arrow's action is a map of the two smooth manifolds, and it is
            built at the smooth owner from its coordinate representation: the
            two hyperboloid models have the one chart ``hyperboloid``, and on
            that pair of charts the isometry is the tuple of sections
            ``y |-> (eps g x(y))_i``, one per chart coordinate of the codomain,
            where ``x(y)`` is the hyperboloid vector the chart names and ``eps``
            the sign that puts its image in the codomain's component.  So this
            arrow's values are a represented smooth morphism's values, and its
            coordinate sections are stated, rather than the values being computed
            on the side of the smooth owner.
            """
            self._isometry = isometry
            domain = parent.domain()
            codomain = parent.codomain()
            labels = (HYPERBOLOID_CHART, HYPERBOLOID_CHART)
            assert (
                tuple(domain.chart_labels()) == (HYPERBOLOID_CHART,)
                and tuple(codomain.chart_labels()) == (HYPERBOLOID_CHART,)
            ), (
                f"there is no arrow {domain} -> {codomain} stated by this constructor: its "
                f"coordinate representation is written on the chart {HYPERBOLOID_CHART}, and "
                f"the endpoints' charts are {tuple(domain.chart_labels())} and "
                f"{tuple(codomain.chart_labels())}"
            )
            ring = domain.atlas()[HYPERBOLOID_CHART].function_ring()
            self._smooth_morphism = SmoothManifolds().Mor(domain, codomain)(
                {
                    labels: tuple(
                        ring(
                            lambda point, index=index: _isometry_image_of_point(
                                domain, codomain, isometry, point
                            ).coordinates()[index]
                        )
                        for index in range(int(codomain.dimension()))
                    )
                }
            )
            OwnedSetMorphism.__init__(self, parent, self._smooth_morphism)

        def lattice_isometry(self):
            r"""Return the integral isometry of the endpoints' lattice that induces this arrow."""
            return self._isometry

        def __call__(self, point):
            r"""Return the image of ``point``, each presentation of a point read by its own datum.

            This owner states two presentations of the points of a hyperboloid
            model: the chart points of the chart ``hyperboloid``, and the rational
            points, which are the rays of the component's positive rational
            vectors.  A chart point is evaluated by the represented smooth morphism
            the constructor states, section by section; a ray is carried to the ray
            of its representative's image at :func:`_isometry_image_of_point`,
            which needs no chart because a ray has none and the lattice isometry
            acts on the vector itself.
            """
            match element_parent(point) is self.domain().point_set():
                case True:
                    return _isometry_image_of_point(
                        self.domain(), self.codomain(), self._isometry, point
                    )
                case False:
                    return self._smooth_morphism(point)

        def underlying_smooth_morphism(self):
            r"""Return the smooth morphism of the two hyperboloid models this arrow is.

            Its domain and codomain are this arrow's, its values on points are
            this arrow's values, and its coordinate sections on the pair of
            charts ``hyperboloid`` are the ones the constructor stated.
            """
            return self._smooth_morphism

        def underlying_topological_morphism(self):
            r"""Return the same map as a map of the underlying topological spaces."""
            return self._smooth_morphism

        def chart_maps(self):
            r"""Return the coordinate sections of this arrow, on the chart pair ``hyperboloid``.

            One section per chart coordinate of the codomain, in the ring of
            functions on the chart of the domain: the value of the ``i``-th at a
            point is the ``i``-th coordinate of the image point.
            """
            return self._smooth_morphism.chart_maps()

        def degree(self):
            r"""Return ``Infinity``: an isometry of smooth manifolds is ``C^infinity``."""
            return Infinity

        def __mul__(self, other):
            r"""Return the composite of two composable hyperbolic arrows.

            The composite of the isometries induces the composite of the maps,
            so the product is written from the lattice isometries' own product
            and belongs to the Mor of the composite's endpoints.
            """
            match other:
                case _ if not isinstance(other, HyperbolicManifoldMor.ElementMethods):
                    return NotImplemented
                case _ if other.codomain() is not self.domain():
                    return NotImplemented
                case _:
                    return self.parent().mor_family().Of(
                        other.domain(), self.codomain()
                    )(self._isometry * other._isometry)

    def _element_constructor_(self, isometry):
        r"""Return the arrow induced by the isometry ``isometry`` of the endpoints' lattice.

        ``isometry`` is a map of the endpoints' lattice to itself, and it is
        admitted exactly when it preserves the pairing: checked on the
        lattice's chosen generating set, which decides it for the whole lattice
        because the pairing is bilinear.  A form-preserving endomorphism of a
        nondegenerate finite-rank lattice is an automorphism, so nothing weaker
        than an isometry is admitted as one.
        """
        domain = self.domain()
        codomain = self.codomain()
        lattice = domain.lattice()
        assert codomain.lattice() is lattice, (
            f"there is no arrow {domain} -> {codomain} induced by an isometry of one lattice: "
            f"{domain} is a model of {lattice} and {codomain} of {codomain.lattice()}, and an "
            f"isometry of the first induces no map of the second's points"
        )
        labels = tuple(lattice.module_generating_set())
        generators = tuple(lattice.module_generator(label) for label in labels)
        images = tuple(isometry(generator) for generator in generators)
        for position, (generator, image) in enumerate(zip(generators, images)):
            for other_position, (other_generator, other_image) in enumerate(
                zip(generators, images)
            ):
                pairing = lattice.b(generator, other_generator)
                moved = lattice.b(image, other_image)
                assert moved == pairing, (
                    f"{isometry} induces no isometry of {domain}: it does not preserve the "
                    f"pairing of {lattice}, since b(e_{position}, e_{other_position}) = {pairing} "
                    f"while the pairing of their images is {moved}"
                )
        return self.element_class(self, isometry)

    @object_level
    @cached_method
    def identity(self):
        r"""Return the identity arrow, induced by the identity isometry of the lattice."""
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity arrow from {self.domain()} to {self.codomain()}: an "
                f"identity needs its domain and codomain to be the same hyperbolic space"
            )
        return self(self.domain().lattice().Aut().one())


class HyperbolicManifoldMorCategoryConstruction(MorCategoryConstruction):
    r"""The isometries of the hyperbolic spaces, at the hyperbolic owner."""

    FixedCategoryClass = HyperbolicManifoldMor


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
        return [RiemannianManifolds().GloballySymmetric()]

    _MorCategory = HyperbolicManifoldMorCategoryConstruction

    @cached_method
    def an_object(self):
        r"""Return the standard ``H^n``, the hyperboloid of ``I_{1,n}`` in its reference positive-cone component."""
        from sage_extensions.categories.lattices import Lattices

        lattice = Lattices.IPQ(1, self.dimension())
        return PositiveConeComponents(lattice).an_object().projectivization()

    def _call_(self, component):
        r"""Return the hyperboloid model ``HH(C^+)`` of a positive-cone component of rank ``n + 1``."""
        rank = int(component.lattice().module_rank())
        dimension = int(self.dimension())
        if rank != dimension + 1:
            raise ValueError(
                f"cannot place {component} in {self}: the component spans a hyperbolic space of "
                f"dimension {rank - 1}, not {dimension}"
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

        def _chart_domain_structure(self, label, engine_chart) -> dict:
            r"""An open subset of the hyperboloid lies in the same positive-cone component.

            A chart on a proper open subset is a chart of the same space on
            fewer points, so its domain is placed by the component the space is
            placed by; what the Riemannian level adds to an open submanifold —
            the restricted metric and its own smooth domain — comes with it.
            """
            return {
                **super()._chart_domain_structure(label, engine_chart),
                "component": self._component,
            }

        def riemannian_metric(self):
            r"""Return the metric ``-b`` of the hyperboloid, in the charts of its atlas.

            ``b`` is negative definite on ``t^perp`` for ``t`` the timelike
            vector of the component, so ``-b`` is positive definite on each
            tangent space ``x^perp`` of the hyperboloid, and the differential of
            the chart ``hyperboloid`` carries ``t^perp`` onto ``T_x``.  What is
            returned is that section as it is stated in coordinates: the family
            ``chart label |-> (g(d/dy_i, d/dy_j))`` of
            :meth:`RiemannianManifolds.riemannian_metric`, whose entries are
            functions on the chart's domain
            (:meth:`_HyperboloidFrame.metric_matrix` is their value).  An open
            submanifold of the hyperboloid carries no formula of its own and is
            given the family of the space it is open in, whose charts restrict
            to it, so that datum is returned when it is there.
            """
            if self._preamble_metric is not None:
                return self._preamble_metric
            return indexed_family(
                self.chart_labels(),
                self._metric_matrix_in_chart,
                name=f"Gram matrix of the metric of {self} in each chart",
            )

        def _metric_matrix_in_chart(self, label):
            r"""The Gram matrix of ``-b`` in the chart ``label``, as functions on its domain.

            The formula is read in the coordinates of the chart
            ``hyperboloid``, which is the one chart the hyperboloid model comes
            with; a chart that does not carry it is refused rather than given a
            matrix the chart's coordinates do not state.
            """
            if label != HYPERBOLOID_CHART:
                raise ValueError(
                    f"cannot state the metric of {self} in the chart {label!r}: the metric "
                    f"``-b`` of the hyperboloid is stated in the coordinates of "
                    f"{HYPERBOLOID_CHART!r}, and no other chart of {self} carries that formula"
                )
            chart = self.atlas()[label]
            ring = chart.function_ring()
            frame = self._hyperboloid_frame()
            dimension = int(self.dimension())

            def entry(row, column):
                def value(point):
                    return frame.metric_matrix(tuple(chart(point)))[row][column]

                return value

            return tuple(
                tuple(ring(entry(row, column)) for column in range(dimension))
                for row in range(dimension)
            )

        @cached_method
        def rational_points(self):
            r"""Return the topological space of rays of positive rational vectors of the component."""
            return _object_of(
                HyperbolicRationalPoints(self._component),
                topology_data=_HyperbolicTopologyData(),
                component=self._component,
            )

        def point_set(self):
            r"""Return the points of the hyperboloid: its rational points.

            A point of a hyperboloid model is the ray of a positive vector of the
            component, and the rays of its positive rational vectors are the points
            this owner states -- the same set a hyperbolic polyhedron is cut out of
            (:meth:`projectivize_cone`), and the set a placement into this space
            lands in.
            """
            return self.rational_points()

        def _element_constructor_(self, datum, chart_label=None):
            r"""Return the point: a point of this space's own point set is a point of this space.

            An element of a hyperboloid model is the ray of a positive rational
            vector of its component, so a point of :meth:`point_set` is one of this
            space's points already, and it is returned as it is.  Coordinates
            arrive with a chart and stay with the manifold levels that build a
            point from them: a ray is not a tuple of coordinates, and reading one as
            coordinates is what those levels would otherwise do with it.
            """
            match datum:
                case _ if (
                    chart_label is None and element_parent(datum) is self.point_set()
                ):
                    return datum
                case _:
                    return super()._element_constructor_(datum, chart_label)

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
            if vector == lattice.zero():
                raise ValueError(
                    f"the zero vector of {lattice} defines no ideal point of {self}: an ideal "
                    f"point is the ray of a nonzero vector"
                )
            if lattice.q(vector) != lattice.base_ring().zero():
                raise ValueError(
                    f"{vector} does not define an ideal point of {self}: an ideal point is the "
                    f"ray of an isotropic vector, and {vector} has square {lattice.q(vector)}"
                )
            if not self._component.closure_contains(vector):
                raise ValueError(
                    f"{vector} does not define an ideal point of {self}: it is isotropic, but "
                    f"its ray is not in the closure of {self._component}, whose pairing with "
                    f"the timelike vector {self._component.timelike_vector()} is "
                    f"{lattice.b(vector, self._component.timelike_vector())}"
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

        def is_an_isometry(self, ambient_map) -> bool:
            r"""Decide whether a map of this hyperbolic space is an isometry of it.

            An arrow of a hyperbolic space is the map of the hyperboloid induced
            by an isometry of its lattice (:class:`HyperbolicManifoldMor`), so the
            decision reads that datum and not the map's values on points: the
            lattice map must preserve the pairing on the lattice's chosen
            generating set, which decides it for the whole lattice because the
            pairing is bilinear, and the sign that puts an image back in the
            selected component is the one pairing positively with its timelike
            vector -- the convention :func:`_isometry_image_of_point` writes, and
            one a hyperbolic point, being a ray, does not distinguish.

            A map of this space that carries no isometry of this space's lattice --
            a map of the point set, say -- is refused here: this space states no
            decision about such a map, and none is guessed.
            """
            if ambient_map.domain() is not self or ambient_map.codomain() is not self:
                raise ValueError(
                    f"the isometry decision of {self} is a decision about its own maps, but "
                    f"{ambient_map} carries {ambient_map.domain()} into {ambient_map.codomain()}"
                )
            if not ambient_map.parent().base_category().is_subcategory(self.category()):
                raise ValueError(
                    f"the isometry decision of {self} reads the isometry of the lattice "
                    f"{self.lattice()} that an arrow of this space carries, and {ambient_map} is "
                    f"an arrow of {ambient_map.parent().base_category()}, which carries none"
                )
            lattice = self.lattice()
            labels = tuple(lattice.module_generating_set())
            generators = tuple(lattice.module_generator(label) for label in labels)
            isometry = ambient_map.lattice_isometry()
            images = tuple(isometry(generator) for generator in generators)
            return all(
                lattice.b(image, other_image) == lattice.b(generator, other_generator)
                for generator, image in zip(generators, images, strict=True)
                for other_generator, other_image in zip(generators, images, strict=True)
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
            r"""The point ``eps g x`` for ``g`` an isometry of the lattice and ``x`` a point of the hyperboloid.

            The space is its own domain and codomain here, so this is the arrow
            the isometry induces on it (:meth:`HyperbolicManifoldMor.ElementMethods._call_`)
            with the same point map, read in this space's own frame twice.
            """
            return _isometry_image_of_point(self, self, element, point)

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

    def tangent_basis(self):
        r"""The basis ``u_1, ..., u_n`` of ``t^perp`` the chart's coordinates are read in.

        It is the coefficient of the chart coordinate ``y_j`` in
        ``x = s t + sum_j y_j u_j``, so ``u_j = w_k e_j - w_j e_k`` for the
        pivot ``k`` and ``w = (b(t, e_0), ..., b(t, e_{n}))``.
        """
        pivot = self.pivot
        basis = []
        for index in self.others:
            vector = [RR.zero()] * self.rank
            vector[index] = self.timelike_pairings[pivot]
            vector[pivot] = -self.timelike_pairings[index]
            basis.append(tuple(vector))
        return tuple(basis)

    def metric_matrix(self, chart_coordinates):
        r"""The Gram matrix ``(g(d/dy_i, d/dy_j))`` of ``-b`` in the chart ``hyperboloid``.

        The chart sends ``y`` to ``x = s t + sum_p y_p u_p`` with
        ``s = sqrt((1 - q(y))/q(t))``, so the chart's coordinate vector fields
        are ``dx(u) = ds(u) t + u`` and ``s ds(u) = -b(y, u)/q(t)``, read off
        ``2 s ds = -dq/q(t)``.  Since ``x` lies on the hyperboloid the metric is
        ``-b``, and ``b(t, u) = 0``, so

        .. math::

            g_{ij}(y) = -b(u_i, u_j)
                        - \frac{b(y, u_i)\, b(y, u_j)}{1 - q(y)},

        where ``q(y) = sum_{p r} y_p y_r b(u_p, u_r)``.  The denominator is
        ``q(t) s^2``, which is positive on the chart's domain, so the chart's
        differential carries ``t^perp`` onto each tangent space and the entries
        are functions there.
        """
        basis = self.tangent_basis()
        coordinates = tuple(RR(value) for value in chart_coordinates)
        pairings = tuple(tuple(self.pairing(left, right) for right in basis) for left in basis)
        heights = tuple(
            sum(
                (coordinates[position] * pairings[position][column] for position in range(len(basis))),
                RR.zero(),
            )
            for column in range(len(basis))
        )
        square = sum(
            (
                coordinates[left] * coordinates[right] * pairings[left][right]
                for left in range(len(basis))
                for right in range(len(basis))
            ),
            RR.zero(),
        )
        denominator = RR.one() - square
        return tuple(
            tuple(
                -pairings[row][column] - heights[row] * heights[column] / denominator
                for column in range(len(basis))
            )
            for row in range(len(basis))
        )


def _hyperbolic_space(component):
    from sage_extensions.categories.manifolds import RiemannianManifolds

    return RiemannianManifolds().GloballySymmetric().hyperbolic_space(component)


__all__ = [
    "HYPERBOLOID_CHART",
    "HyperbolicManifoldMor",
    "HyperbolicPolyhedra",
    "HyperbolicRationalPoints",
    "HyperbolicSpaces",
    "PositiveConeComponents",
]
