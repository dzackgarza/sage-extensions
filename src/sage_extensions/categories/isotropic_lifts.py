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
    # The source model is the rank-one *lattice*, not the bare regular module:
    # ``denominator_ideal`` requires the rational map to join
    # ``source.base_change(field_map)`` and ``target.base_change(field_map)``, and
    # the regular module's base change is a restriction of scalars rather than a
    # lattice over the fraction field, so a map out of it is semilinear over the
    # wrong ring.  A rank-one lattice with the unit form is the same free module
    # with the same single generator, and its base change is of the right shape.
    line = Lattices(ring)([[1]])
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
            period = self.integral_parameter_period()
            multiplication = Modules(ring).Mor(parameter_lattice, parameter_lattice)(
                lambda label: parameter_lattice.scalar_multiple(period, parameter_lattice.module_generator(label))
            )
            return multiplication.cokernel_projection()

        @cached_method
        def integral_parameter_period(self):
            r"""Return ``m``, the period of the integral parameter quotient.

            Write ``x = base^-1(f_target)`` and choose ``D`` with ``Dx`` integral.  Every
            integral lift has its parameter in ``P = projection(E)/D``.  If ``e`` has
            denominator ``A`` and the section of ``P`` has denominator ``B``, then
            ``m = 2AB`` makes the section of ``mP`` lie in ``2A*E``, and the Eichler
            formula and its inverse are integral for those parameters
            (:meth:`integral_parameter_quotient`).
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
            return ring(2) * isotropic_denominator * section_denominator

        @cached_method
        def integral_parameter_classes(self):
            r"""The integral residue locus, as a union of cosets of the transvection kernel.

            Write ``f`` for the target's marked isotropic vector, ``phi: P -> T`` for the
            parameterization (:meth:`parameterization`), ``s`` for the target section and
            ``L'`` for the target lattice.  Eichler's transvection formula
            (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, (4)--(5), cited in
            this module's docstring; the owner of the formula here is
            ``Lattices.ParentMethods.eichler_transvection``)

                ``E_{f,x}(y) = y + b(y,x) f - (q(x)/2) b(y,f) f - b(y,f) x``

            is integral for ``x`` in ``L'``: each term is then integral, ``q(x)/2`` because
            ``L'`` is even.  A primitive isotropic ``f`` does **not** make that an exact
            criterion, because the converse needs a ``y`` with ``b(y,f) = 1`` and a primitive
            isotropic vector only gives ``b(f, L') = d Z`` for the divisibility ``d = div(f)``,
            which may exceed one.  On a lattice of divisibility ``d = 2`` the parameter
            ``x = f/2`` has ``b(y,x) = b(y,f)/2`` and ``q(x) = 0``, so ``E_{f,f/2}`` is the
            identity: an integral isometry whose parameter is not a lattice vector.  The
            integral parameters are therefore not the parameters that lie in ``L'``, and a
            locus computed as ``{a : s(a) in L'}`` loses exactly those lifts.

            What holds for every base point and every divisibility is that the locus is a
            union of cosets of

                ``K = {a in P/mP : s(a) in L'}``,

            the kernel of ``a + mP |-> s(a) + L'`` in ``L'^vee/L' = A_{L'}``.  The
            section lands in the perpendicular of the marked isotropic vector, so the
            transvections ``E_{f,s(a)}`` and ``E_{f,s(k)}`` commute and compose to the
            transvection of the sum, and ``phi(a) = E_{f,s(a)} phi(0)`` is how
            :meth:`parameterization` defines these coordinates.  Hence

                ``phi(a + k) = E_{f,s(k)} phi(a)``

            for every ``k`` in ``K``.  Both ``E_{f,s(k)}`` and its inverse
            ``E_{f,-s(k)}`` are integral, because ``s(k)`` and ``-s(k)`` lie in ``L'`` and
            ``L'`` is even.  Multiplying by an integral isometry whose inverse is integral
            preserves integrality, so ``phi(a + k)`` is integral exactly when ``phi(a)`` is:
            the locus is a union of ``K``-cosets, integral base point or not.

            The locus is computed here from the parameter module's structure, never by
            listing its elements: ``K`` from one integer Smith form of the coordinates of
            ``s`` on a basis of ``P`` (:meth:`integral_parameter_quotient`,
            ``Modules.ParentMethods.rational_coordinates``); one representative of each
            coset of ``P/mP`` modulo ``K``, which is ``|P/mP| / |K| = prod_i step_i`` of
            them; the lift ``phi`` of that parameter, asked for its integral restriction --
            the lift test itself, not a criterion for it; and the union of the cosets that
            pass, presented as the image of the passing representatives and the kernel
            under the coset addition, with the inverse naming both components of the pair,
            so the union itself is never listed as one set.  A coset whose representative
            fails contributes nothing, and its representative's lift is the only lift
            built for it.
            """
            from sage.all import QQ, ZZ, gcd, lcm
            from sage.matrix.constructor import matrix

            from sage_extensions.categories.rings.ring_foundation import _engine_element

            source = self.source_reduction().isotropic_embedding().codomain()
            target = self.target_reduction().isotropic_embedding().codomain()
            assert target.is_even() is True, (
                f"the integral lift locus of {self.reduction_isometry()!r} is computed as a "
                f"union of cosets of the transvection kernel only on an even lattice: on "
                f"{target!r} the transvection of a kernel class need not be integral, so "
                f"integrality is not constant on those cosets"
            )
            quotient = self.integral_parameter_quotient()
            parameter_lattice = quotient.domain()
            classes_module = quotient.codomain()
            period = self.integral_parameter_period()
            period_scalar = ZZ(_engine_element(period.parent(), period))
            labels = tuple(parameter_lattice.module_generating_set())
            parameter_rank = int(parameter_lattice.module_rank())
            assert len(labels) == parameter_rank, (
                f"the parameter lattice {parameter_lattice} must be free on its selected "
                f"generators for the class map to be read off them, but it has rank "
                f"{parameter_rank} and {len(labels)} generators"
            )
            rational_target = self._target_witt.rational_lattice()
            inclusion = parameter_lattice.inclusion()
            # s(a_i) in a basis of L', as one rational column per parameter generator.
            columns = [
                rational_target.rational_coordinates(
                    self._target_section(
                        inclusion(parameter_lattice.module_generator(label)).underlying_element()
                    )
                )
                for label in labels
            ]
            ambient_rank = int(target.module_rank())
            coordinates = matrix(QQ, ambient_rank, parameter_rank, [
                entry for column in columns for entry in column.list()
            ])
            denominator = ZZ(1)
            for entry in coordinates.list():
                denominator = lcm(denominator, ZZ(entry.denominator()))
            integral_coordinates = matrix(ZZ, ambient_rank, parameter_rank, [
                ZZ((entry * denominator).numerator()) for entry in coordinates.list()
            ])
            # B = U D V with U, V unimodular: B a = U D V a, and U and V preserve the
            # integrality of a vector up to unimodular change, so B a is in
            # denominator * Z^ambient_rank exactly when (D V a)_i is in denominator * Z
            # for every i, that is when (V a)_i is a multiple of
            # denominator / gcd(D_ii, denominator).
            smith, _left, right = integral_coordinates.smith_form()
            steps = tuple(
                denominator // gcd(abs(smith[index, index]), denominator)
                for index in range(parameter_rank)
            )
            # In the coordinates w = V a of P/mP = (Z/m)^r the kernel condition
            # (V a)_i in step_i Z is the condition w_i in gcd(step_i, m) Z, so
            # gcd(step_i, m) indexes the cosets in that coordinate and
            # m / gcd(step_i, m) counts the kernel's classes there.
            coset_steps = tuple(gcd(step, period_scalar) for step in steps)
            counts = tuple(period_scalar // step for step in coset_steps)
            images = tuple(
                classes_module(quotient(parameter_lattice.module_generator(label)))
                for label in labels
            )
            zero = classes_module.zero()

            def class_of(coefficients):
                return sum(
                    (
                        classes_module.scalar_multiple(
                            classes_module.base_ring()(coefficient), image
                        )
                        for coefficient, image in zip(coefficients, images)
                        if coefficient % period_scalar != 0
                    ),
                    zero,
                )

            def parameters(moduli):
                r"""The index vectors ``indices`` with ``0 <= indices[i] < moduli[i]``."""
                indices = [0] * parameter_rank
                while True:
                    yield tuple(indices)
                    position = 0
                    while position < parameter_rank:
                        indices[position] += 1
                        if ZZ(indices[position]) < ZZ(moduli[position]):
                            break
                        indices[position] = 0
                        position += 1
                    if position == parameter_rank:
                        return

            inverse_right = right.inverse()

            def coefficients_at(indices):
                r"""The coordinates ``V^-1 indices`` of one class of ``P/mP``."""
                column = inverse_right * matrix(
                    ZZ, parameter_rank, 1, [ZZ(index) for index in indices]
                )
                return tuple(int(entry) % int(period_scalar) for entry in column.list())

            def parameter_class(indices):
                r"""The class of the parameter ``V^-1 indices`` in ``P/mP``."""
                return class_of(coefficients_at(indices))

            def parameter_at(indices):
                r"""The parameter of the class :func:`parameter_class` gives for ``indices``.

                The class's coordinates name a parameter of it, namely the linear
                combination of ``P``'s generators with those coefficients, so the
                parameter is read off rather than solved for.  Solving instead -- the
                quotient's ``preimage`` -- was 64% of one locus's time on `T_Co`: it
                rebuilds an element of the quotient and inverts the projection per class
                (#361).
                """
                coefficients = coefficients_at(indices)
                parameter_ring = parameter_lattice.base_ring()
                return inclusion(
                    parameter_lattice.linear_combination(
                        {
                            label: parameter_ring(coefficient)
                            for label, coefficient in zip(labels, coefficients)
                        }
                    )
                ).underlying_element()

            # K itself, as the classes of P/mP with w = V a a multiple of the steps.
            transvection_kernel = tuple(
                parameter_class(
                    tuple(ZZ(index) * step for index, step in zip(indices, coset_steps))
                )
                for indices in parameters(counts)
            )
            # The lift at a parameter is ``phi(a) = t(f, s(a)) * base``
            # (:meth:`parameterization`): the Eichler transvection of the section
            # composed with the base point.  Its images of the source basis are
            # therefore the transvection's matrix times the base point's coordinate
            # matrix, and the lift is integral exactly when those images are integral
            # combinations of the target's generators with a unimodular coordinate
            # matrix -- the reading
            # :meth:`...LatticeIsometryMethods.integral_restriction` makes on its
            # integral branch.  The one product is formed per class: composing the two
            # isometries and asking the composed object answers the same question
            # through three constructions per class -- the transvection, the
            # composition, and the torsor's membership check of the composition --
            # which were 581 of the `T_Co` line row's 637 seconds (#361).
            ring = source.base_ring()
            assert ring is target.base_ring(), (
                f"the integral lift locus of {self.reduction_isometry()!r} is read in "
                f"the target's coordinates only when both endpoints are lattices over "
                f"one ring, but the source is over {ring} and the target over "
                f"{target.base_ring()}"
            )
            base = self.base_point()
            rational_source = base.domain()
            rational_target = base.codomain()
            isotropic_vector = self._target_witt.isotropic_vector()
            source_labels = tuple(source.module_generating_set())
            target_labels = tuple(target.module_generating_set())
            assert (
                tuple(rational_target.module_generating_set()) == target_labels
                and isotropic_vector.parent() is rational_target
            ), (
                f"the integral lift locus of {self.reduction_isometry()!r} is read in "
                f"the target's own coordinates only when its rationalization carries "
                f"the target's generators and the marked isotropic vector: "
                f"{rational_target!r} is indexed by "
                f"{tuple(rational_target.module_generating_set())} against the target's "
                f"{target_labels}, and the marked vector lies in "
                f"{isotropic_vector.parent()!r}"
            )
            # The base point's images of the source generators, one rational column
            # each, so a class's lift is one matrix product away.
            base_images = matrix(
                QQ,
                len(target_labels),
                len(source_labels),
                [
                    entry
                    for label in source_labels
                    for entry in rational_target.rational_coordinates(
                        base(rational_source.module_generator(label))
                    ).list()
                ],
            )

            def lifts_integrally(parameter):
                r"""Whether the lift at ``parameter`` restricts to an isometry of ``L'``.

                The lift is ``phi(a) = t(f, s(a)) * base``, so its images of the source
                generators are the transvection's matrix times the base point's, and it
                restricts to an isometry of ``L'`` exactly when every coordinate of
                every image in the target's basis lies in the common base ring and the
                coordinate matrix has determinant ``+-1``.
                """
                section = self._target_section(parameter)
                images = (
                    rational_target.eichler_transvection_matrix(
                        isotropic_vector, section
                    )
                    * base_images
                )
                for entry in images.list():
                    if entry.denominator() != 1:
                        return False
                return int(matrix(ZZ, [[int(entry) for entry in row] for row in images.rows()]).determinant()) in (1, -1)

            passing = tuple(
                residue
                for residue, parameter in (
                    (parameter_class(indices), parameter_at(indices))
                    for indices in parameters(coset_steps)
                )
                if lifts_integrally(parameter)
            )
            # The locus is the union of the cosets that pass, each translated
            # from its own tested representative by the transvection kernel.
            # That union is presented as the image of the passing
            # representatives and the kernel under the coset addition, with the
            # inverse naming both components of the pair, so the union itself
            # is never listed as one set: on ``T_Co`` it has 131072 classes
            # and it is built once per candidate the port tests, so its
            # listing was the row's own cost.
            passing_residues = finite_ordered_set(passing)
            kernel = finite_ordered_set(transvection_kernel)
            cosets = passing_residues.product_with(kernel)
            residue_projection, kernel_projection = (
                cosets.projection(index) for index in cosets.index_set()
            )

            def sum_of(pair):
                return residue_projection(pair) + kernel_projection(pair)

            def pair_of(value):
                r"""The unique representative and kernel class summing to this class, or ``None``."""
                for residue in passing:
                    shift = value - residue
                    if shift in kernel:
                        return cosets((residue, shift))
                return None

            return Sets().image_set(
                Sets().Mor(cosets, classes_module)(sum_of), cosets, inverse=pair_of
            )

        @cached_method
        def integral_base_point_or_none(self):
            r"""Decide existence and retain one integral lift, or ``None``.

            An integral rational base point proves nonemptiness immediately.
            Otherwise the integral residue locus decides it: its classes are the
            cosets of the transvection kernel whose representative lifts
            integrally (:meth:`integral_parameter_classes`), so the first of
            them supplies a lift and an empty locus proves emptiness without
            listing ``P/mP``.  The lift is asked for its integral restriction
            once more, on that class alone, rather than assumed.
            """
            source = self.source_reduction().isotropic_embedding().codomain()
            target = self.target_reduction().isotropic_embedding().codomain()
            base = self.base_point()
            if base.integral_restriction(source, target) is not None:
                return base
            quotient = self.integral_parameter_quotient()
            inclusion = quotient.domain().inclusion()
            for residue in self.integral_parameter_classes():
                parameter = inclusion(quotient.preimage(residue)).underlying_element()
                lift = self.parameterization()(parameter)
                if lift.integral_restriction(source, target) is not None:
                    return lift
            return None

        @cached_method
        def integral_base_point(self):
            r"""Select an integral lift, or raise when the integral lift locus is empty."""
            point = self.integral_base_point_or_none()
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
