r"""Marked rank-one reduction lifts as kernel-group torsors.

The defining map fixes a chosen isotropic vector and induces the specified
isometry on its perpendicular quotient. A rational Witt splitting supplies
one lift. Its left translates by the target reduction kernel are all lifts.
The additive coordinates evaluate by Eichler transvections, not by affine
combinations of matrices (Gritsenko--Hulek--Sankaran, section 3.1, (4)--(5)).
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.group.g_objects import GObjects
from sage_extensions.categories.group.g_sets import TrivializedTorsors
from sage_extensions.categories.lattices import IsotropicReductions, Lattices
from sage_extensions.categories.modules.pure.modules import Modules, ModulesOverIntegralDomains
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of, owned_category_join


def _vector_denominator(vector, integral_module):
    r"""The denominator ideal of the map taking 1 to this vector."""
    ring = integral_module.base_ring()
    field_map = ring.fraction_field_map()
    line = ring.regular_module()
    arrow = Modules(field_map.codomain()).Mor(line.base_change(field_map), vector.parent())(
        lambda label: vector
    )
    (denominator,) = tuple(arrow.denominator_ideal(line, integral_module).ideal_generators())
    return denominator


def _rational_splitting(reduction, plane):
    r"""Present the reduction's retained quotient as the orthogonal summand."""
    witt = reduction.rational_witt_decomposition()
    ambient = witt.rational_lattice()
    rational_reduction = reduction.vector_space()
    e, f = witt.isotropic_vector(), witt.dual_isotropic_vector()
    integral_ambient = reduction.isotropic_embedding().codomain()
    rationalize = ModulesOverIntegralDomains(integral_ambient.base_ring())(integral_ambient).generic_fibre_map()
    perpendicular = reduction.orthogonal_complement().inclusion()

    def section_image(label):
        lift = rationalize(perpendicular(reduction.coordinate_frame()[label])).underlying_element()
        return lift - ambient.scalar_multiple(lift.b(f), e)

    section = rational_reduction.Mor(ambient)(section_image)
    plane_embedding = plane.Mor(ambient)((e, f))
    splitting = ambient.orthogonal_decomposition((plane_embedding, section))
    return witt, section, splitting


class IsotropicReductionLiftTorsors(OwnedCategoryOverBaseRing):
    r"""Rational isometry lifts preserving the marked generators of isotropic lines.

    The reduction of a hyperbolic plane along a primitive null line has rank
    zero; its marked-line lift torsor therefore has a rank-zero parameter
    space, and its selected point already descends to the integral lattice.

    EXAMPLES::

        sage: U = Lattices(ZZ)("U")
        sage: R = U.basis_vector(0).isotropic_reduction()
        sage: lifts = R.rational_lifts(R, R.Isom(R).identity())
        sage: lifts.parameter_space().module_rank() == 0
        True
        sage: lifts.integral_base_point().integral_restriction(U, U) is not None
        True
        sage: integral = lifts.integral_torsor()
        sage: origin = integral.base_point()
        sage: integral.difference(origin, origin) == integral.acting_group().one()
        True
    """

    def super_categories(self):
        return [Sets()]

    def _call_(self, source, target, reduction_isometry):
        ring = self.base_ring()
        for reduction in (source, target):
            if reduction not in IsotropicReductions(ring):
                raise ValueError("both endpoints must be isotropic reductions over the same ring")
            if reduction.isotropic_sublattice().module_rank() != 1:
                raise ValueError("this lift torsor requires marked isotropic lines")
            if not reduction.isotropic_embedding().codomain().is_nondegenerate():
                raise ValueError("the marked-line transvection torsor requires nondegenerate ambient forms")
        field_map = ring.fraction_field_map()
        if reduction_isometry.domain() is source and reduction_isometry.codomain() is target:
            reduction_isometry = reduction_isometry.base_change(field_map)
        if reduction_isometry.domain() is not source.vector_space() or reduction_isometry.codomain() is not target.vector_space():
            raise ValueError("the reduction isometry must have the given rational reduction endpoints")
        plane = Lattices(field_map.codomain())("U")
        source_witt, source_section, source_split = _rational_splitting(source, plane)
        target_witt, target_section, target_split = _rational_splitting(target, plane)
        source_sum, target_sum = source_split.codomain(), target_split.codomain()
        direct_sum = Lattices(field_map.codomain()).orthogonal_direct_sum_bifunctor()
        product = direct_sum.domain()
        source_pair = product(plane, reduction_isometry.domain())
        target_pair = product(plane, reduction_isometry.codomain())
        plane_identity = plane.O().one()
        forward = product.Mor(source_pair, target_pair)(plane_identity, reduction_isometry)
        inverse = product.Mor(target_pair, source_pair)(plane_identity, ~reduction_isometry)
        diagonal = direct_sum.map_isomorphism(product.Core().Mor(source_pair, target_pair)(forward, inverse))
        assert diagonal.domain() is source_sum and diagonal.codomain() is target_sum, (
            "the orthogonal direct-sum functor must retain the Witt splitting's summands"
        )
        base = target_split.inverse() * diagonal * source_split
        source_ambient, target_ambient = base.domain(), base.codomain()
        source_e = source_witt.isotropic_vector()
        target_e = target_witt.isotropic_vector()
        target_line = target_ambient.subobject_on((target_e,)).inclusion()
        source_labels = tuple(source.vector_space().module_generating_set())
        target_vectors = tuple(target_section(v) for v in target.vector_space().module_generators())

        kernel = target_ambient.Aut().predicate_subgroup(
            lambda g: g(target_e) == target_e and all(
                target_line.is_in_image(g(v) - v) for v in target_vectors
            ),
            "the kernel of the marked-line reduction action",
        )
        points = source_ambient.Isom(target_ambient).condition_set(
            lambda g: g(source_e) == target_e and all(
                target_line.is_in_image(
                    g(source_section(source.vector_space().module_generator(label)))
                    - target_section(reduction_isometry(source.vector_space().module_generator(label)))
                ) for label in source_labels
            )
        )
        forward = Sets().Mor(kernel, points)(lambda g: points(g * base))
        backward = Sets().Mor(points, kernel)(lambda g: kernel(g * base.inverse()))
        # Multiplication by base and by its inverse give the two inverse
        # maps of the fibre of the reduction action.
        trivialization = Sets().Core().Mor(kernel, points)._from_known_inverse_pair(forward, backward)
        return _object_of(
            owned_category_join((self, TrivializedTorsors(kernel))),
            trivialization=trivialization,
            source_reduction=source, target_reduction=target,
            reduction_isometry=reduction_isometry,
            source_splitting=source_split, target_splitting=target_split,
            target_section=target_section, target_witt=target_witt,
        )

    class ParentMethods:
        def __init__(self, source_reduction, target_reduction, reduction_isometry,
                     source_splitting, target_splitting, target_section, target_witt, **rest):
            self._source_reduction = source_reduction
            self._target_reduction = target_reduction
            self._reduction_isometry = reduction_isometry
            self._source_splitting = source_splitting
            self._target_splitting = target_splitting
            self._target_section = target_section
            self._target_witt = target_witt
            super().__init__(**rest)

        def source_reduction(self):
            return self._source_reduction

        def target_reduction(self):
            return self._target_reduction

        def reduction_isometry(self):
            return self._reduction_isometry

        def source_splitting(self):
            return self._source_splitting

        def target_splitting(self):
            return self._target_splitting

        def parameter_space(self):
            return self.target_reduction().vector_space()

        @cached_method
        def parameterization(self):
            r"""The chosen additive coordinates, evaluated by transvections.

            On U + <2>, t*a sends f to f+t*a-t^2*e. The parameter
            dimension is the rank of the reduction, hence ambient rank - 2.
            """
            parameters = self.parameter_space()
            witt = self._target_witt
            ambient = witt.rational_lattice()
            base = self.base_point()
            forward = Sets().Mor(parameters, self)(
                lambda a: self(ambient.eichler_transvection(witt.isotropic_vector(), self._target_section(a)) * base)
            )
            projection = self.target_splitting().codomain().projection(1) * self.target_splitting()
            backward = Sets().Mor(self, parameters)(
                lambda lift: projection((lift * base.inverse())(witt.dual_isotropic_vector()) - witt.dual_isotropic_vector())
            )
            return Sets().Core().Mor(parameters, self)._from_known_inverse_pair(forward, backward)

        @cached_method
        def _integral_lift_locus(self):
            r"""The integral kernel ``K_Z`` and the integral lift locus ``T_Z`` as a subset of ``T``.

            Write ``r: P -> P/mP`` for the residue map of
            :meth:`integral_parameter_quotient`, ``C`` for the finite residue
            locus :meth:`integral_parameter_classes`, and ``phi`` for the
            parameterization ``V -> T``.  Theorem used (established in
            :meth:`integral_parameter_quotient`, from the Eichler transvection
            formula of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
            (4)--(5), cited in this module's docstring): every integral lift has
            its parameter in ``P``; for ``m = 2AB`` (``A`` the denominator of the
            isotropic vector, ``B`` that of the section of ``P``) the
            transvection of a parameter in ``mP`` and its inverse are integral,
            and ``phi(x + y) = E(y) phi(x)``, so integrality of ``phi(x)`` depends
            only on the class of ``x`` in ``P/mP``.  Hence

                ``T_Z = phi(r^{-1}(C))``,  ``r^{-1}(C) = { s(c) + k : c in C, k in mP }``

            for the section ``s`` of ``r`` selected by the cokernel. ``T_Z`` is
            constructed as the image of ``C x ker(r)`` under
            ``(c, k) |-> phi(s(c) + k)``, a bijection onto ``T_Z`` with its inverse
            ``lift |-> (r(x), x - s(r(x)))``, ``x = phi^{-1}(lift)`` read in ``P``.
            """
            target = self.target_reduction().isotropic_embedding().codomain()
            integral_kernel = self.acting_group().predicate_subgroup(
                lambda g: g.integral_restriction(target, target) is not None,
                "integral automorphisms in the marked-line reduction kernel",
            )
            residue = self.integral_parameter_quotient()
            lattice_inclusion = residue.domain().inclusion()
            period = residue.kernel()
            period_inclusion = period.inclusion()
            classes = self.integral_parameter_classes()
            # C x ker(r), the decomposition r^{-1}(C) = { s(c) + k }; its
            # components are read by the product's own projections and its
            # points built by its universal map from the component maps.
            period_set = period.inclusion().domain()
            pairs = classes.product_with(period_set)
            class_projection, period_projection = (pairs.projection(index) for index in pairs.index_set())
            parameterization = self.parameterization()
            coordinates = parameterization.inverse()

            def lift_of(pair):
                parameter_point = (
                    residue.preimage(class_projection(pair))
                    + period_inclusion(period_projection(pair))
                )
                return parameterization(lattice_inclusion(parameter_point).underlying_element())

            def parameter_of(lift):
                return lattice_inclusion.lift(lattice_inclusion.codomain().wrap(coordinates(lift)))

            to_class = Sets().Mor(self, classes)(lambda lift: residue(parameter_of(lift)))
            to_period = Sets().Mor(self, period_set)(
                lambda lift: period_inclusion.lift(
                    parameter_of(lift) - residue.preimage(residue(parameter_of(lift)))
                )
            )
            ranking = pairs.index_set().ranking_map()
            components = (to_class, to_period)
            pair_of = pairs.from_maps(self, lambda index: components[int(ranking(index))])

            locus = Sets().image_set(Sets().Mor(pairs, self)(lift_of), pairs, inverse=pair_of)
            return integral_kernel, locus

        @cached_method
        def integral_members(self):
            r"""The integral lift locus ``T_Z = phi(r^{-1}(C))`` with its ``K_Z``-action.

            ``T_Z`` is constructed in :meth:`_integral_lift_locus` from the finite
            residue locus ``C``; it is empty exactly when ``C`` is, which the
            image and product constructions decide from ``C`` (finite, decided)
            and ``ker r`` (a module, nonempty). The integral kernel ``K_Z`` acts
            by composition. Emptiness is never inferred from one chosen
            rational lift.
            """
            integral_kernel, locus = self._integral_lift_locus()
            return GObjects(integral_kernel, Sets()).on_set(
                locus, lambda g, lift: g * lift, orbit_relation=lambda left, right: True
            )

        @cached_method
        def integral_kernel_group_generators(self):
            r"""A generating family of the integral kernel ``K_Z``, as quotients of integral lifts.

            ``phi(x + y) = E(y) phi(x)`` (Gritsenko--Hulek--Sankaran,
            arXiv:0810.1614, section 3.1, (4)--(5)), so for integral lifts
            ``phi(x)`` and ``phi(x_0)`` the quotient ``phi(x) phi(x_0)^{-1} =
            E(x - x_0)`` is an integral element of the kernel, and ``K_Z``
            acts simply transitively on ``T_Z = phi(r^{-1}(C))``
            (:meth:`_integral_lift_locus`).  With ``x_0 = s(c_0)`` for one
            residue ``c_0`` in ``C``, the parameters of ``K_Z`` are
            ``r^{-1}(C) - x_0``, generated by ``s(c) - s(c_0)`` for ``c`` in the
            finite locus ``C`` and by the period lattice ``ker r``.  The
            family is those quotients.  It requires a nonempty integral
            locus; the identity marking of a reduction always has one.
            """
            integral_kernel, _locus = self._integral_lift_locus()
            residue = self.integral_parameter_quotient()
            lattice_inclusion = residue.domain().inclusion()
            period_inclusion = residue.kernel().inclusion()
            classes = self.integral_parameter_classes()
            assert classes.is_empty() is False, (
                f"the integral lifts of {self.reduction_isometry()!r} form an empty set, so they "
                f"determine no elements of the integral kernel: ask the identity marking of "
                f"{self.target_reduction()!r} for its integral kernel"
            )
            parameterization = self.parameterization()

            def lift(parameter):
                return parameterization(lattice_inclusion(parameter).underlying_element())

            origin = residue.preimage(next(iter(classes)))
            base = lift(origin)
            parameters = (
                *(residue.preimage(residue_class) for residue_class in classes),
                *(
                    origin + period_inclusion(period)
                    for period in period_inclusion.domain().module_generators()
                ),
            )
            return finite_ordered_set(
                tuple(integral_kernel(lift(parameter) * base.inverse()) for parameter in parameters)
            )

        @cached_method
        def integral_parameter_quotient(self):
            r"""Retain a finite quotient containing every integral lift parameter class.

            Write ``x=base^-1(f_target)`` and choose D with Dx integral.
            Every integral lift has parameter in ``P=projection(E)/D``.
            If e has denominator A and the section of P has denominator B,
            then ``m=2AB`` makes the section of mP lie in ``2A*E``.
            The Eichler formula and its inverse are integral for these
            parameters. Thus integrality is constant on cosets of mP in P.
            This quotient is a finite search presentation, not an assertion
            that mP is the entire integral kernel.
            """
            source = self.source_reduction().isotropic_embedding().codomain()
            target = self.target_reduction().isotropic_embedding().codomain()
            ring = source.base_ring()
            field_map = ring.fraction_field_map()
            field = field_map.codomain()
            parameters = self.parameter_space()
            restricted_parameters = parameters.restrict_scalars(field_map)
            witt = self._target_witt
            rational_target = witt.rational_lattice()
            source_vector = self.base_point().inverse()(witt.dual_isotropic_vector())
            denominator = _vector_denominator(source_vector, source)
            projection = self.target_splitting().codomain().projection(1) * self.target_splitting()
            rationalize = ModulesOverIntegralDomains(target.base_ring())(target).generic_fibre_map()
            parameter_lattice = restricted_parameters.subobject_on(tuple(
                restricted_parameters(parameters.scalar_multiple(
                    field.one() / field_map(denominator),
                    projection(rationalize(vector).underlying_element()),
                )) for vector in target.module_generators()
            ))
            section = Modules(field).Mor(parameter_lattice.base_change(field_map), rational_target)(
                lambda label: self._target_section(
                    parameter_lattice.inclusion()(parameter_lattice.module_generator(label)).underlying_element()
                )
            )
            (section_denominator,) = tuple(section.denominator_ideal(parameter_lattice, target).ideal_generators())
            isotropic_denominator = _vector_denominator(witt.isotropic_vector(), target)
            period = ring(2) * isotropic_denominator * section_denominator
            multiplication = Modules(ring).Mor(parameter_lattice, parameter_lattice)(
                lambda label: parameter_lattice.scalar_multiple(period, parameter_lattice.module_generator(label))
            )
            return multiplication.cokernel_projection()

        @cached_method
        def integral_parameter_classes(self):
            r"""The complete finite residue locus for integral isometry lifts."""
            quotient = self.integral_parameter_quotient()
            lattice = quotient.domain()
            source = self.source_reduction().isotropic_embedding().codomain()
            target = self.target_reduction().isotropic_embedding().codomain()

            def integral(residue):
                parameter = lattice.inclusion()(quotient.preimage(residue)).underlying_element()
                lift = self.parameterization()(parameter)
                return lift.integral_restriction(source, target) is not None

            return quotient.codomain().elements().condition_set(integral)

        @cached_method
        def _integral_base_point_or_none(self):
            r"""Decide existence and retain one integral lift, or ``None``.

            Private witness contract used by the selected Levi section and
            its image predicate. An integral rational base point proves
            nonemptiness immediately. A nonintegral base point proves
            nothing; only exhaustion of the complete residue locus proves
            emptiness.
            """
            source = self.source_reduction().isotropic_embedding().codomain()
            target = self.target_reduction().isotropic_embedding().codomain()
            base = self.base_point()
            if base.integral_restriction(source, target) is not None:
                return base
            quotient = self.integral_parameter_quotient()
            for residue in self.integral_parameter_classes():
                parameter = quotient.domain().inclusion()(quotient.preimage(residue)).underlying_element()
                return self.parameterization()(parameter)
            return None

        @cached_method
        def integral_base_point(self):
            r"""Select an integral lift, or raise when the integral lift locus is empty."""
            point = self._integral_base_point_or_none()
            if point is not None:
                return point
            raise ValueError("the integral reduction-lift locus is empty")

        @cached_method
        def integral_torsor(self):
            r"""Trivialize the integral lift locus under its full integral kernel.

            EXAMPLES::

                sage: L = Lattices(ZZ)("U") + Lattices(ZZ)([[2]])
                sage: R = L.basis_vector(0).isotropic_reduction()
                sage: T = R.rational_lifts(R, R.Isom(R).identity())
                sage: a = T.parameter_space().module_generators()[0]
                sage: lift = T.parameterization()(a)
                sage: torsor = T.integral_torsor()
                sage: coordinate = torsor.trivialization().inverse()(lift)
                sage: coordinate != torsor.acting_group().one()
                True
                sage: torsor.trivialization()(coordinate) == lift
                True
                sage: torsor.base_point() == T.integral_base_point()
                True
                sage: torsor.difference(lift, torsor.base_point()) == coordinate
                True
            """
            from sage_extensions.categories.group.g_sets import Torsors

            group, points = self._integral_lift_locus()
            chosen = self.integral_base_point()
            forward = Sets().Mor(group, points)(lambda g: points(g * chosen))
            backward = Sets().Mor(points, group)(lambda lift: group(lift * chosen.inverse()))
            trivialization = Sets().Core().Mor(group, points)._from_known_inverse_pair(forward, backward)
            return Torsors(group).from_trivialization(trivialization, base_point=points(chosen))
