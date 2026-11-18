r"""Smooth real vector bundles on a smooth manifold, and their modules of sections.

A smooth real vector bundle of rank ``r`` over a smooth manifold ``M`` is a
smooth manifold ``E`` with a smooth surjection ``E -> M`` whose fibres are
``r``-dimensional real vector spaces and which is locally a product: every point
of ``M`` has a neighbourhood over which the projection is the projection of
``U x R^r`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  A
section is a smooth map ``s: M -> E`` whose composite with the projection is the
identity, and the sections of one bundle form a module over the algebra
``C^oo(M)`` of smooth functions under the pointwise operations (Lee, Ch. 10).

The bundle this module owns first is the tangent bundle ``TM``, whose fibre at
``p`` is the tangent space ``T_pM`` (Lee, Ch. 3).  A vector field is a section of
``TM``, and it acts on a smooth function as a derivation,
``(V f)(p) = d_p f (V_p)``; conversely every derivation of ``C^oo(M)`` is the
derivative along a unique vector field, because a tangent vector at ``p`` is a
derivation of the algebra of germs of smooth functions there (Lee, Ch. 3).  The
two readings of a vector field are therefore one object, and this module states
both: a section is written by its components in the charts of an atlas, and it
is applied to a smooth function.

SageManifolds is the private realization.  Its tangent bundle, its scalar
fields and its vector fields carry the chart expressions and perform the
differentiation; none of them is a parent of an owned object, and the engine's
own answer to whether a bundle is trivial is never read.  A bundle is trivial
here exactly when a frame is stated for it -- a datum, not a flag about which
frames an engine happens to know.
"""

from sage.misc.cachefunc import cached_method
from sage.rings.rational_field import QQ
from sage.structure.element import Element
from sage.structure.element import parent as element_parent
from sage.structure.sage_object import SageObject
from sage.symbolic.ring import SR

from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.manifolds import (
    SmoothManifolds,
    _admit_manifold_expression,
    _chartwise_family_agrees,
    _chartwise_formulas,
    _engine_manifold,
    _engine_manifold_chart,
    _engine_manifold_expression,
    _raise_manifold_expression,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


def _engine_tangent_bundle(manifold):
    r"""The engine's tangent bundle of ``manifold`` (private adapter)."""
    return _engine_manifold(manifold).tangent_bundle()


def _engine_vector_field(manifold, components):
    r"""The engine's vector field with the given owned components, one tuple per chart.

    A vector field is stated on a chart by the components of its value in that
    chart's coordinate frame, and the engine's own object for it is assembled
    from exactly those: on each chart's domain the engine is told the
    components, and its transition maps are what make the result one object on
    the manifold.  Private computation adapter (``OWN-06``): the engine's
    vector field is the computation, and the owned section is built on it.
    """
    engine = _engine_manifold(manifold)
    field = engine.vector_field(name=f"a section of T{manifold.manifold_name()}")
    for label, component in components.items():
        chart = _engine_manifold_chart(manifold.atlas()[label])
        field.restrict(chart.domain())[chart.frame(), :] = [
            _engine_manifold_expression(entry) for entry in component
        ]
    return field


def _rational_polynomial(expression):
    r"""``expression``, a polynomial in one variable over the rationals, as that polynomial.

    A real polynomial with no real root is never zero, and the roots are found
    in the real algebraic numbers: the coefficients are the chart formulas'
    rational numbers, and an expression whose coefficients are not rational has
    no polynomial reading here and is refused by the caller.
    """
    return SR(expression).polynomial(QQ)


def _decided_nowhere_vanishing(expression, variables):
    r"""Whether the real function ``expression`` of ``variables`` is decided to take no zero.

    A component of a frame is a real-valued function on a chart's domain, and the
    charts of a manifold take values in the real coordinates, so the component
    vanishes nowhere when its numerator -- it is read as a fraction of
    polynomials, as every chart expression of this tree is -- takes no real zero
    at any point: a real polynomial with no real root is never zero, and a
    constant is decided by the exact reals.  ``True`` and ``False`` are
    decisions, and ``None`` is the statement that this owner does not decide the
    question for the expression it was given.

    A denominator is not decided here: a chart expression that divides is stated
    where its denominator does not vanish (``ManifoldAtlasChart.section_ratio``),
    and that nonvanishing is the overlap the chart's own transition states.
    """
    from sage.rings.qqbar import AA

    from sage_extensions.categories.functions.real_functions import _decided_nonzero

    formula = SR(expression)
    numerator = SR(formula.numerator())
    free = tuple(numerator.variables())
    if not free:
        return _decided_nonzero(numerator)
    match len(tuple(variables)):
        case 1 if numerator.is_polynomial(tuple(variables)[0]):
            return not tuple(_rational_polynomial(numerator).roots(AA))
        case _:
            return None


class SmoothVectorBundles(OwnedParameterizedCategory):
    r"""Smooth real vector bundles on one smooth manifold.

    An object is a bundle of a stated finite rank over the parameter manifold,
    and its sections are the objects of :class:`SmoothSectionModules`.  The
    tangent bundle is the one every smooth manifold carries, and it is a bundle
    before it is a trivialization: a frame is a datum a caller states, never a
    fact this owner infers from the frames an engine happens to know.
    """

    def parameter_category(self):
        return SmoothManifolds()

    def super_categories(self):
        r"""A bundle is, in particular, a set: the points of its total space.

        No finer owned supercategory is stated here.  A vector bundle over a
        manifold is not a manifold of this tree's own, and naming one would make
        this family a subcategory of a construction that does not exist rather
        than the one datum it does state -- a rank over a base.
        """
        return [Sets()]

    def base_manifold(self):
        r"""The manifold every bundle of this family is over."""
        return self._owned_parameter

    def _repr_object_names(self):
        return f"smooth real vector bundles on {self.base_manifold()}"

    def tangent_bundle(self):
        r"""``TM``, the bundle whose fibre at ``p`` is the tangent space ``T_pM``.

        The tangent space ``T_pM`` is the vector space of derivations of the
        algebra of germs of smooth functions at ``p`` (Lee, *Introduction to
        Smooth Manifolds*, 2nd ed., Ch. 3), so the fibres are real vector spaces
        of dimension ``dim(M)`` and their disjoint union over the charts is a
        smooth vector bundle of that rank (Lee, Ch. 3 and Ch. 10).  No
        trivialization comes with it: a frame is retained only when a caller
        states one (:meth:`SmoothSectionModules.ParentMethods.trivialized_by`).
        """
        manifold = self.base_manifold()
        return _object_of(
            self,
            bundle_base_manifold=manifold,
            bundle_rank=manifold.dimension(),
            engine_bundle=_engine_tangent_bundle(manifold),
        )

    class ParentMethods:
        def __init__(
            self,
            bundle_base_manifold,
            bundle_rank,
            engine_bundle,
            **rest,
        ) -> None:
            self._bundle_base_manifold = bundle_base_manifold
            self._bundle_rank = bundle_rank
            self._engine_bundle = engine_bundle
            super().__init__(**rest)

        def base_manifold(self):
            r"""The manifold this bundle is over."""
            return self._bundle_base_manifold

        def rank(self):
            r"""The rank of this bundle: the dimension of each of its fibres."""
            return self._bundle_rank

        @cached_method
        def sections(self):
            r"""The ``C^oo(M)``-module of smooth sections of this bundle.

            A section assigns to each point of the base a point of the fibre
            over it, smoothly (Lee, *Introduction to Smooth Manifolds*, 2nd
            ed., Ch. 10).  The sections are the objects of
            :class:`SmoothSectionModules`, and the module is this bundle's: two
            bundles that differ only in a frame read the same sections.
            """
            return _object_of(
                SmoothSectionModules(self),
                vector_bundle=self,
                base_ring=self.base_manifold().smooth_functions(),
                retained_frame=None,
            )

        def _repr_(self):
            return (
                f"rank-{self.rank()} smooth real vector bundle on {self.base_manifold()}"
            )


class SmoothSectionModules(OwnedParameterizedCategory):
    r"""The ``C^oo(M)``-module of smooth sections of one smooth vector bundle.

    Sections are added and scaled pointwise in the fibres, so they form a module
    over the functions on the base (Lee, *Introduction to Smooth Manifolds*,
    2nd ed., Ch. 10).  For the tangent bundle the same module is the module of
    derivations of ``C^oo(M)``: a section applies to a smooth function by the
    derivation law the tangent space is defined by (Lee, Ch. 3), and the result
    is the element of ``C^oo(M)`` the derivation takes.

    The module is free exactly when a frame is retained
    (:meth:`SmoothSectionModules.ParentMethods.trivialized_by`); the rank of a
    module of sections is not read off how many charts happen to exist.
    """

    def parameter_category(self):
        return SmoothVectorBundles(self._owned_parameter.base_manifold())

    def vector_bundle(self):
        r"""The bundle whose sections these are."""
        return self._owned_parameter

    def base_ring(self):
        r"""``C^oo(M)``, the algebra the sections are a module over."""
        return self.vector_bundle().base_manifold().smooth_functions()

    def super_categories(self):
        return [Modules(self.base_ring())]

    def _repr_object_names(self):
        return f"smooth sections of {self.vector_bundle()}"

    class ElementMethods(Element):
        r"""A smooth section: one tuple of components per chart, agreeing under the transitions.

        The section is the datum of its components in the charts of the atlas;
        :meth:`SmoothSectionModules.ParentMethods.section` is the one
        constructor, and it decides that the components state one object on the
        manifold rather than one object per chart.
        """

        def __init__(self, parent, components, engine_field) -> None:
            Element.__init__(self, parent)
            self._components = components
            self._engine_field = engine_field

        def components(self):
            r"""The components of the section in each chart's coordinate frame."""
            return self._components

        def __call__(self, function):
            r"""The derivative ``V f`` of a smooth function along this section.

            A vector field is a derivation of the smooth functions (Lee,
            *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3), so applying it
            to ``f`` gives the smooth function whose value at ``p`` is
            ``d_p f (V_p)``.  The engine differentiates the chart expressions
            of ``f`` along the components of ``V``, and the result is raised to
            a smooth function chart by chart.
            """
            manifold = self.parent().base_manifold()
            assert element_parent(function) is manifold.smooth_functions(), (
                f"{function} is not a smooth function on {manifold}: a section of "
                f"{self.parent().vector_bundle()} is a derivation of "
                f"{manifold.smooth_functions()}, and its parent is "
                f"{element_parent(function)}"
            )
            formulas = _chartwise_formulas(function, manifold)
            assert formulas is not None, (
                f"cannot differentiate {function} along {self}: the function is not written by "
                f"chart expressions, and a derivation is computed on the expressions both are "
                f"written by"
            )
            engine = _engine_manifold(manifold)
            scalar_field = engine.scalar_field(
                {
                    _engine_manifold_chart(manifold.atlas()[label]): formula
                    for label, formula in formulas.items()
                }
            )
            derivative = self._engine_field(scalar_field)
            return manifold.smooth_function(
                {
                    label: _raise_manifold_expression(
                        derivative.expr(_engine_manifold_chart(manifold.atlas()[label])),
                        manifold.atlas()[label],
                    )
                    for label in manifold.chart_labels()
                }
            )

        def _add_(self, other):
            r"""``V + W``: the section whose value at ``p`` is ``V(p) + W(p)``."""
            components = self.components()
            other_components = other.components()
            return self.parent().section(
                {
                    label: tuple(
                        left + right
                        for left, right in zip(
                            component, other_components[label], strict=True
                        )
                    )
                    for label, component in components.items()
                }
            )

        def _neg_(self):
            r"""``-V``: the section whose value at ``p`` is ``-V(p)``."""
            return self.parent().section(
                {
                    label: tuple(-entry for entry in component)
                    for label, component in self.components().items()
                }
            )

        def _lmul_(self, scalar):
            r"""``f V``: the pointwise action of the functions on the base."""
            return self.parent().scalar_multiple(scalar, self)

        def __eq__(self, other) -> bool:
            r"""Two sections of one bundle are equal when their components agree in every chart.

            The components of a section in a chart are its values in that
            chart's coordinate frame, and the frames of the charts of an atlas
            are related by the transitions, so the components agree in one
            chart exactly when they agree in every chart.
            """
            if element_parent(other) is not self.parent():
                return False
            for label, component in self._components.items():
                other_component = other.components()[label]
                for left, right in zip(component, other_component, strict=True):
                    residual = SR(
                        _engine_manifold_expression(left) - _engine_manifold_expression(right)
                    ).simplify_full()
                    if residual != 0:
                        return False
            return True

        def __ne__(self, other) -> bool:
            return not self == other

        def __hash__(self) -> int:
            return hash((id(self.parent()), id(self)))

        def _repr_(self):
            return f"a section of {self.parent().vector_bundle()}"

    class ParentMethods:
        def __init__(self, vector_bundle, base_ring, retained_frame=None, **rest) -> None:
            self._vector_bundle = vector_bundle
            self._base_ring = base_ring
            self._retained_frame = retained_frame
            super().__init__(base_ring=base_ring, **rest)

        def vector_bundle(self):
            r"""The bundle whose sections these are."""
            return self._vector_bundle

        def base_manifold(self):
            r"""The manifold the sections are defined on."""
            return self._vector_bundle.base_manifold()

        def base_ring(self):
            r"""``C^oo(M)``, the algebra the sections are a module over."""
            return self._base_ring

        def zero(self):
            r"""The zero section: the component zero in every chart's coordinate frame."""
            manifold = self.base_manifold()
            return self.section(
                {
                    label: tuple(
                        manifold.atlas()[label].function_ring().zero()
                        for _index in range(int(self._vector_bundle.rank()))
                    )
                    for label in manifold.chart_labels()
                }
            )

        def scalar_multiple(self, scalar, element):
            r"""``f V``: the section whose value at ``p`` is ``f(p) V(p)``.

            A section is a map into the fibres and the functions on the base act
            on it pointwise, which is what makes the sections a module over
            ``C^oo(M)`` (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 10).  The product is read from the function's own chart
            expressions and the section's components there.
            """
            manifold = self.base_manifold()
            assert element_parent(scalar) is self.base_ring(), (
                f"{scalar} is not a function on {manifold}: the sections of "
                f"{self._vector_bundle} are a module over {self.base_ring()}, and the scalar's "
                f"parent is {element_parent(scalar)}"
            )
            assert element_parent(element) is self, (
                f"{element} is not a section of {self._vector_bundle}: its parent is "
                f"{element_parent(element)}"
            )
            formulas = _chartwise_formulas(scalar, manifold)
            assert formulas is not None, (
                f"cannot multiply the section {element} by {scalar}: the function is not "
                f"written by chart expressions, and the product is read from the expressions "
                f"both are written by"
            )
            components = element.components()
            return self.section(
                {
                    label: tuple(
                        _raise_manifold_expression(
                            formulas[label] * _engine_manifold_expression(entry),
                            manifold.atlas()[label],
                        )
                        for entry in components[label]
                    )
                    for label in manifold.chart_labels()
                }
            )

        def section(self, components):
            r"""The section whose component in each chart is ``components[label]``.

            A section is stated on a chart by the components of its value in
            that chart's coordinate frame, and the components of one section are
            related by the derivative of the atlas transitions: writing ``y``
            for the coordinates of the target chart as functions of the
            coordinates ``x`` of the source chart, a vector field's components
            satisfy ``a_t^j(y(x)) = sum_i a_s^i(x) dy_j/dx_i`` (Lee,
            *Introduction to Smooth Manifolds*, 2nd ed., Ch. 3).  A family that
            does not satisfy that is a different vector field on each chart, and
            is refused here rather than becoming a section of anything.
            """
            manifold = self.base_manifold()
            atlas = manifold.atlas()
            labels = tuple(manifold.chart_labels())
            missing = tuple(label for label in labels if label not in components)
            extra = tuple(label for label in components if label not in labels)
            assert not missing, (
                f"a section of {self._vector_bundle} is stated on every chart of {manifold}, "
                f"and no component is given for the charts {missing}"
            )
            assert not extra, (
                f"a section of {self._vector_bundle} is stated on the charts of {manifold}, "
                f"and the components given for {extra} are on charts it does not have"
            )
            admitted = {}
            for label in labels:
                chart = atlas[label]
                component = tuple(components[label])
                assert len(component) == int(self._vector_bundle.rank()), (
                    f"a section of the rank-{self._vector_bundle.rank()} bundle "
                    f"{self._vector_bundle} has {self._vector_bundle.rank()} components in every "
                    f"chart, and the component given on the chart {label} has {len(component)}"
                )
                admitted[label] = tuple(
                    _admit_manifold_expression(entry, chart) for entry in component
                )
            _chartwise_family_agrees(manifold, admitted, 1)
            return self.element_class(
                self, admitted, _engine_vector_field(manifold, admitted)
            )

        def module_rank(self):
            r"""The rank of this module as a free ``C^oo(M)``-module.

            A module of sections is free exactly when a global frame is known,
            and a frame is a datum the module retains rather than a fact about
            which charts an engine has coordinates on: without one this refuses,
            because the sections of a nontrivial bundle are not free.
            """
            assert self._retained_frame is not None, (
                f"the module of sections of {self._vector_bundle} has no known rank: it is free "
                f"exactly when a global frame is retained, and no frame is retained here"
            )
            return self._vector_bundle.rank()

        def basis(self):
            r"""The frame that trivializes the bundle, as the basis of this module."""
            assert self._retained_frame is not None, (
                f"the module of sections of {self._vector_bundle} has no known basis: a basis is "
                f"a global frame, and no frame is retained here"
            )
            return tuple(self._retained_frame)

        def trivialized_by(self, frame):
            r"""These sections read through the stated global frame.

            A frame is a family of as many sections as the rank, a basis of
            every fibre (Lee, *Introduction to Smooth Manifolds*, 2nd ed.,
            Ch. 10); one section states the rank-one case.  The frame is
            decided to be one: in every chart the determinant of its components
            is decided to take no zero, which is what makes the family a basis
            of each fibre (:func:`_decided_nowhere_vanishing`), and a family
            whose determinant vanishes somewhere, or whose vanishing is not
            decided, is refused.  The result is a module for the same bundle
            that retains the frame and answers its rank and basis; this one is
            unchanged.
            """
            from sage.matrix.constructor import matrix as _engine_matrix

            assert self._retained_frame is None, (
                f"the module of sections of {self._vector_bundle} already retains the frame "
                f"{self._retained_frame}; a second frame states another trivialization, and "
                f"these sections are not re-read through one"
            )
            rank = int(self._vector_bundle.rank())
            family = (
                (frame,) if element_parent(frame) is self else tuple(frame)
            )
            assert len(family) == rank, (
                f"a frame of the rank-{rank} bundle {self._vector_bundle} is a family of "
                f"{rank} sections, and {(len(family))} were given"
            )
            for section in family:
                assert element_parent(section) is self, (
                    f"{section} is not a section of {self._vector_bundle}: its parent is "
                    f"{element_parent(section)}"
                )
            manifold = self.base_manifold()
            for label in manifold.chart_labels():
                chart = manifold.atlas()[label]
                entries = tuple(
                    SR(_engine_manifold_expression(entry))
                    for section in family
                    for entry in section.components()[label]
                )
                determinant = _engine_matrix(SR, rank, rank, entries).det()
                verdict = _decided_nowhere_vanishing(
                    determinant, tuple(_engine_manifold_chart(chart)[:])
                )
                assert verdict is True, (
                    f"the family {family} does not trivialize {self._vector_bundle}: its "
                    f"components on the chart {label} have determinant {determinant}, and "
                    + (
                        "that determinant takes the value zero at a point of the chart"
                        if verdict is False
                        else "this owner does not decide that it vanishes nowhere there"
                    )
                )
            return _object_of(
                self.category(),
                vector_bundle=self._vector_bundle,
                base_ring=self.base_ring(),
                retained_frame=family,
            )

        def trivialization(self):
            r"""The isomorphism ``M x R -> E`` that the retained frame states.

            Its forward map sends a smooth function ``a`` to the section
            ``a frame``, and its inverse sends a section to the function that
            reads it in the frame; the two are inverse because the frame is a
            basis of every fibre (Lee, *Introduction to Smooth Manifolds*, 2nd
            ed., Ch. 10).
            """
            assert self._retained_frame is not None, (
                f"the module of sections of {self._vector_bundle} retains no frame, and a "
                f"trivialization of a bundle is read in a frame"
            )
            assert int(self._vector_bundle.rank()) == 1, (
                f"the trivialization of the rank-{self._vector_bundle.rank()} bundle "
                f"{self._vector_bundle} is a matrix of functions per chart; this owner reads the "
                f"rank-one case, whose trivialization is the frame's own section"
            )
            return SmoothVectorBundleTrivialization(
                self._vector_bundle, self._retained_frame[0]
            )

        def _repr_(self):
            return f"smooth sections of {self._vector_bundle}"


class SmoothVectorBundleTrivialization(SageObject):
    r"""The trivialization ``M x R -> E`` of a rank-one bundle that a global frame states.

    The frame is a section that is a basis of every fibre, so a smooth function
    ``a`` determines the section ``p |-> a(p) frame(p)`` and a section ``V``
    determines the function ``p |-> a(p)`` with ``V(p) = a(p) frame(p)`` (Lee,
    *Introduction to Smooth Manifolds*, 2nd ed., Ch. 10).  The two maps are
    computed on the owned chart expressions: the product is the pointwise
    product of functions, and the coordinate reads a section's component against
    the frame's own, on the open subset where that component does not vanish
    (:meth:`ManifoldAtlasChart.section_ratio`).
    """

    def __init__(self, bundle, frame) -> None:
        self._bundle = bundle
        self._frame = frame

    def bundle(self):
        r"""The bundle this trivialization is of."""
        return self._bundle

    def base_manifold(self):
        r"""The manifold the trivialized bundle is over."""
        return self._bundle.base_manifold()

    def frame(self):
        r"""The global frame the trivialization is read in."""
        return self._frame

    def forward(self, function):
        r"""``a |-> a frame``: the section the smooth function ``a`` states.

        The product of a function and a section is the pointwise product of
        their components in a chart, which is how the ``C^oo(M)``-module
        structure on sections is written (Lee, *Introduction to Smooth
        Manifolds*, 2nd ed., Ch. 10).
        """
        manifold = self.base_manifold()
        assert element_parent(function) is manifold.smooth_functions(), (
            f"{function} is not a smooth function on {manifold}: its parent is "
            f"{element_parent(function)}, and a trivialization is a map from "
            f"{manifold.smooth_functions()}"
        )
        function_formulas = _chartwise_formulas(function, manifold)
        assert function_formulas is not None, (
            f"cannot multiply the frame of {self._bundle} by {function}: the function is not "
            f"written by chart expressions, and the product of a function and a section is read "
            f"from the expressions of both"
        )
        frame_components = self._frame.components()
        return self._bundle.sections().section(
            {
                label: tuple(
                    _raise_manifold_expression(
                        function_formulas[label] * _engine_manifold_expression(entry),
                        manifold.atlas()[label],
                    )
                    for entry in frame_components[label]
                )
                for label in manifold.chart_labels()
            }
        )

    def inverse(self, section):
        r"""``V |-> a``: the smooth function with ``V = a frame``.

        In a chart the section has components ``V_i`` and the frame has
        components ``e_i``, and the function read there is ``V_i / e_i``.  The
        quotient is stated where the frame's component does not vanish
        (:meth:`ManifoldAtlasChart.section_ratio`), which for a frame is every
        point of the chart by hypothesis.
        """
        manifold = self.base_manifold()
        assert element_parent(section) is self._bundle.sections(), (
            f"{section} is not a section of {self._bundle}: its parent is "
            f"{element_parent(section)}"
        )
        assert int(self._bundle.rank()) == 1, (
            f"the coordinates of a section in a frame of rank {self._bundle.rank()} are one "
            f"function per basis section; this owner reads the rank-one case"
        )
        frame_components = self._frame.components()
        section_components = section.components()
        return manifold.smooth_function(
            {
                label: manifold.atlas()[label].section_ratio(
                    section_components[label][0], frame_components[label][0]
                )
                for label in manifold.chart_labels()
            }
        )

    def _repr_(self):
        return f"the trivialization of {self._bundle} by the frame {self._frame}"
