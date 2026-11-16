r"""Marked rank-one reduction lifts as kernel-group torsors.

The defining map fixes a chosen isotropic vector and induces the specified
isometry on its perpendicular quotient. A rational Witt splitting supplies
one lift. Its left translates by the target reduction kernel are all lifts.
The additive coordinates evaluate by Eichler transvections, not by affine
combinations of matrices (V. Gritsenko, K. Hulek, G. Sankaran, *Abelianisation
of orthogonal groups and the fundamental group of modular varieties*,
arXiv:0810.1614, section 3.1: equation (4), printed p. 8, is the transvection,
equation (5), printed p. 9, composes and inverts it, and equation (10), printed
p. 9, is its integrality on an even lattice; the paper is at
``.tmp/sources/gritsenko-hulek-sankaran-arxiv-0810.1614``).
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.group.g_objects import GObjects
from sage_extensions.categories.group.g_sets import TrivializedTorsors
from sage_extensions.categories.lattices import IsotropicReductions, Lattices
from sage_extensions.categories.modules.pure.modules import Modules, ModulesOverIntegralDomains
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import NN, Sets
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

            for the section ``s`` of ``r`` selected by the cokernel.

            **What is constructed.**  ``r`` is a cokernel projection, hence
            onto, and ``phi`` is a bijection onto ``T``, so ``T_Z`` is the
            subset of ``T`` of the lifts whose parameter lies in ``P`` with its
            class in ``C``, cut out by ``lift |-> r(phi^{-1}(lift)) in C``.  A
            parameter outside ``P`` is a point of ``T`` that no class of
            ``P/mP`` names, and the predicate answers ``False`` for it.

            ``T_Z`` is empty exactly when ``C`` is, since ``r`` is onto and
            ``phi`` bijective, so emptiness is decided from ``C``.  ``C`` empty
            gives the empty subset of ``T``, the least point of ``T``'s power
            set, decided empty by that construction.

            A zero-dimensional parameter space has ``P = 0``, so ``P/mP`` is its
            one class and ``0`` is the only parameter an integral lift has: the
            locus is the base point ``phi(0)``, and it is presented as that
            one-point subset, whose count and emptiness the set owner decides
            from the point.  Otherwise the locus is cut out of ``T`` by the
            residue predicate, and the lift the residue locus built for its
            first passing representative is admitted into it: that lift's class
            lies in ``C`` by the construction that built it, which is what
            decides that the subset is not empty, and this construction lifts
            no point of its own.
            """
            target = self.target_reduction().isotropic_embedding().codomain()
            integral_kernel = self.acting_group().predicate_subgroup(
                lambda g: g.integral_restriction(target, target) is not None,
                "integral automorphisms in the marked-line reduction kernel",
            )
            residue = self.integral_parameter_quotient()
            lattice_inclusion = residue.domain().inclusion()
            classes = self.integral_parameter_classes()
            parameterization = self.parameterization()
            coordinates = parameterization.inverse()

            def parameter_of(lift):
                return lattice_inclusion.codomain().wrap(coordinates(lift))

            def in_residue(locus_lift):
                r"""Whether this lift's parameter lies in ``P`` with class one of ``C``'s.

                ``T`` is the ``phi``-image of the whole parameter space, so a
                lift whose parameter lies outside ``P`` is a point of ``T`` that
                no class of ``P/mP`` names: membership answers ``False`` for it.
                """
                parameter = parameter_of(locus_lift)
                preimage = lattice_inclusion.preimage_or_none(parameter)
                if preimage is None:
                    return False
                return residue(preimage) in classes

            if classes.is_empty() is True:
                return integral_kernel, self.power_set().bottom()
            if self.parameter_space().module_rank() == 0:
                return integral_kernel, self.power_set()((self.base_point(),))
            locus = self.power_set().from_predicate(in_residue)
            locus._retain_admitted_member(self.integral_base_point())
            return integral_kernel, locus

        @cached_method
        def integral_lift_locus(self):
            r"""The integral lift locus ``T_Z``, as a subset of the rational lift torsor ``T``.

            ``T_Z`` is the set of integral lifts of this reduction isometry,
            presented as the subset of ``T`` cut out by the parameter's residue
            class (:meth:`_integral_lift_locus` states the theorem), so it
            answers with the inclusion of a subset of ``T`` and membership is
            one class test.  It is empty exactly when the finite residue locus
            :meth:`integral_parameter_classes` is.

            EXAMPLES::

                sage: U = Lattices(ZZ)("U") + Lattices(ZZ)([[2]])
                sage: R = U.basis_vector(0).isotropic_reduction()
                sage: T = R.rational_lifts(R, R.Isom(R).identity())
                sage: T.integral_lift_locus().is_empty()
                False
                sage: T.integral_lift_locus().inclusion().codomain() == T
                True
            """
            _integral_kernel, locus = self._integral_lift_locus()
            return locus

        @cached_method
        def integral_members(self):
            r"""The integral lift locus ``T_Z = phi(r^{-1}(C))`` with its ``K_Z``-action.

            ``T_Z`` is constructed in :meth:`_integral_lift_locus` as the subset
            of the torsor ``T`` cut out by the parameter's residue class; it is
            empty exactly when the finite residue locus ``C`` is, which that
            construction decides from ``C`` alone. The integral kernel ``K_Z``
            acts by composition. Emptiness is never inferred from one chosen
            rational lift.
            """
            integral_kernel, locus = self._integral_lift_locus()
            return GObjects(integral_kernel, Sets()).on_set(
                locus, lambda g, lift: g * lift, orbit_relation=lambda left, right: True
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
            # The period is a positive integer, so every class of `P/mP` is killed by it:
            # the quotient is a torsion module, and that is this construction's claim to
            # make (`CAT-04`: the construction that states a placement makes it, and no
            # rank is read to justify it).  The claim is also what places the quotient
            # where its elements are enumerated, so a caller can walk `P/mP`.
            quotient = Modules(ring).FinitelyPresented().Torsion()(multiplication)
            # The quotient map sends each generator of `P` to the generator of the same
            # name, which is the map `cokernel_projection` states; it is built here
            # because the quotient above is constructed on this construction's own
            # placement and retains no cokernel morphism of its own.
            return Modules(ring).Mor(parameter_lattice, quotient)(
                lambda label: quotient.module_generator(label)
            )

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

        def _parameter_at(self, coordinates):
            r"""Return the parameter with the given coordinates on the parameter lattice.

            The coordinates are the coefficients on
            :meth:`integral_parameter_quotient`'s domain's selected generators, which is
            the one coordinate system the locus' cosets, its kernel and the parameters
            naming them are all read in.
            """
            parameter_lattice = self.integral_parameter_quotient().domain()
            labels = tuple(parameter_lattice.module_generating_set())
            ring = parameter_lattice.base_ring()
            return parameter_lattice.inclusion()(parameter_lattice.linear_combination({
                label: ring(coefficient)
                for label, coefficient in zip(labels, coordinates, strict=True)
            })).underlying_element()

        def _lift_at(self, coordinates):
            r"""Return the lift ``phi(a) = E_{f,s(a)} * base`` at a parameter of the locus.

            The transvection is ``Lattices.ParentMethods.eichler_transvection``'s -- the
            same operation :meth:`parameterization` composes -- so the locus evaluates no
            second statement of the formula.
            """
            return (
                self._target_witt.rational_lattice().eichler_transvection(
                    self._target_witt.isotropic_vector(),
                    self._target_section(self._parameter_at(coordinates)),
                )
                * self.base_point()
            )

        @cached_method
        def _integral_parameter_cosets(self):
            r"""The integral lift locus as cosets of the transvection kernel, and their parameters.

            Write ``f`` for the target's marked isotropic vector, ``s`` for the target
            section, ``L'`` for the target lattice, ``P`` for the parameter lattice and
            ``m`` for its period (:meth:`integral_parameter_quotient`).  The
            parameterization (:meth:`parameterization`) is ``phi(a) = E_{f,s(a)} phi(0)``,
            with the Eichler transvection of
            ``Lattices.ParentMethods.eichler_transvection``

                ``E_{f,x}(y) = y - b(x,y) f + b(f,y) x - (q(x)/2) b(f,y) f``,

            which is equation (4) of V. Gritsenko, K. Hulek and G. Sankaran,
            *Abelianisation of orthogonal groups and the fundamental group of modular
            varieties*, arXiv:0810.1614, §3.1, printed p. 8.  Equation (5) there
            (printed p. 9) is

                ``E_{f,x} E_{f,y} = E_{f,x+y}``,   ``E_{f,x}^{-1} = E_{f,-x}``,

            and equation (10) (printed p. 9) states that ``E_{f,x}`` preserves ``L'``
            when ``f`` and ``x`` both lie in it.  Hence ``phi(a + y) = E_{f,s(y)} phi(a)``.

            **The kernel is not the locus.**  ``K = {a in P/mP : s(a) in L'}`` is the
            kernel of ``a + mP |-> s(a) + L'``; on ``a`` in ``K`` the transvection
            ``E_{f,s(a)}`` is integral and integrally invertible by (10) and (5), so the
            lift at ``a + k`` is that integral isometry times the lift at ``a`` and the
            locus is a union of ``K``-cosets.  ``K`` is a *proper* subset of the locus as
            soon as the divisibility of ``f`` exceeds one, because (10) is then not a
            criterion: at divisibility two the parameter ``f/2`` has
            ``b(y, f/2) = b(y,f)/2`` and ``q(f/2) = 0``, so ``E_{f,f/2}`` is the
            identity although ``f/2`` is not a lattice vector.

            **The cosets.**  ``s(a)`` lies in ``L'`` exactly when ``A a`` is integral,
            where the columns of ``A`` are the coordinates of ``s`` on ``P``'s selected
            generators and the integer ``N`` clears their denominators.  With
            ``U (N A) V = D`` one Smith form, ``N A a = U^{-1} D (V^{-1} a)`` lies in
            ``N Z^rank`` exactly when ``(V^{-1} a)_i`` is a multiple of
            ``step_i = N / gcd(D_ii, N)``.  So the saturation ``S = {a : s(a) in L'}``
            is ``V u`` for ``u`` in the coordinate cube ``prod_i step_i Z``.  That cube is
            not ``S`` itself unless the steps are all equal: ``V`` unimodular carries the
            cube to a lattice of the same index which need not be the cube -- the swap
            ``[[0,1],[1,0]]`` carries ``Z x 2Z`` to ``2Z x Z`` -- so every reading of
            ``S`` below is taken through ``V``, which is what :meth:`coordinates_at`
            does.  Hence the kernel ``K = S/mP`` has ``prod_i m / gcd(step_i, m)``
            classes, generated by the classes of the parameters ``V(gcd(step_i, m) e_i)``,
            and the classes of ``P/S``, which are the ``K``-cosets, are numbered by
            ``prod_i gcd(step_i, m)`` representatives.  The representatives returned are
            ``a = V u`` for ``u`` ranging over ``prod_i [0, gcd(step_i, m))``: ``V`` is
            unimodular, so no two of them are congruent modulo a kernel class, and
            ``(V^{-1} a)_i = u_i`` exhibits the coordinate reading above.

            **The test is the lift.**  Each representative's lift is built by
            :meth:`_lift_at` and asked for its own
            ``...LatticeIsometryMethods.integral_restriction``; nothing decides
            integrality except that answer.  A lift that passes is therefore one
            the construction has already built, and the lifts that pass are
            retained with the coordinates: they are the points of the integral
            locus, one per passing class, and a consumer that needs one reads it
            instead of lifting and testing again.

            Returns ``(passing, kernel, parameters)``: ``passing`` the finite ordered set
            of the classes of the representatives whose lift restricts to an isometry of
            the target, ``kernel`` the finite ordered set of the classes of ``K``, and
            ``parameters`` the quadruple ``(representatives, kernel generators, period
            generators, lifts)`` -- the coordinates of the passing representatives, of the
            generators ``V(gcd(step_i, m) e_i)`` of ``K``, of the period's own generators,
            and the lift of each passing representative in the same order.
            """
            from sage.all import QQ, ZZ, gcd, lcm
            from sage.matrix.constructor import matrix

            source = self.source_reduction().isotropic_embedding().codomain()
            target = self.target_reduction().isotropic_embedding().codomain()
            assert target.is_even() is True, (
                f"the integral lift locus of {self.reduction_isometry()!r} is computed as a "
                f"union of cosets of the transvection kernel only on an even lattice: on "
                f"{target!r} the transvection of a kernel class need not be integral, so "
                f"integrality is not constant on those cosets"
            )
            ring = source.base_ring()
            assert ring is target.base_ring(), (
                f"the integral lift locus of {self.reduction_isometry()!r} is read in "
                f"the target's coordinates only when both endpoints are lattices over "
                f"one ring, but the source is over {ring} and the target over "
                f"{target.base_ring()}"
            )
            quotient = self.integral_parameter_quotient()
            parameter_lattice = quotient.domain()
            classes_module = quotient.codomain()
            period_scalar = int(NN(self.integral_parameter_period()))
            labels = tuple(parameter_lattice.module_generating_set())
            parameter_rank = int(parameter_lattice.module_rank())
            assert len(labels) == parameter_rank, (
                f"the parameter lattice {parameter_lattice} must be free on its selected "
                f"generators for the class map to be read off them, but it has rank "
                f"{parameter_rank} and {len(labels)} generators"
            )
            rational_target = self._target_witt.rational_lattice()
            target_labels = tuple(target.module_generating_set())
            assert (
                tuple(rational_target.module_generating_set()) == target_labels
                and self._target_witt.isotropic_vector().parent() is rational_target
            ), (
                f"the integral lift locus of {self.reduction_isometry()!r} is read in "
                f"the target's own coordinates only when its rationalization carries "
                f"the target's generators and the marked isotropic vector: "
                f"{rational_target!r} is indexed by "
                f"{tuple(rational_target.module_generating_set())} against the target's "
                f"{target_labels}, and the marked vector lies in "
                f"{self._target_witt.isotropic_vector().parent()!r}"
            )
            # s(a) in a basis of L', as one rational column per parameter generator.
            # The entry loop below is row-major, so the matrix's j-th column is the
            # coordinate of the image of the j-th generator: that is this reading's
            # one convention, and the Smith form of the matrix is taken in it.
            columns = tuple(
                tuple(
                    entry
                    for entry in rational_target.rational_coordinates(
                        self._target_section(
                            parameter_lattice.inclusion()(
                                parameter_lattice.module_generator(label)
                            ).underlying_element()
                        )
                    ).list()
                )
                for label in labels
            )
            ambient_rank = int(target.module_rank())
            assert all(len(column) == ambient_rank for column in columns), (
                f"the target's rational coordinates of a vector of {target!r} must have "
                f"one entry per generator, but a coordinate column has lengths "
                f"{tuple(len(column) for column in columns)} against the rank {ambient_rank}"
            )
            coordinates = matrix(QQ, ambient_rank, parameter_rank, [
                columns[column][entry]
                for entry in range(ambient_rank)
                for column in range(parameter_rank)
            ])
            denominator = ZZ(1)
            for entry in coordinates.list():
                denominator = lcm(denominator, ZZ(entry.denominator()))
            integral_coordinates = matrix(ZZ, ambient_rank, parameter_rank, [
                ZZ((entry * denominator).numerator()) for entry in coordinates.list()
            ])
            # B = U D V with U and V unimodular: B a = U D (V^-1 a), and U and V
            # preserve integrality of a vector up to unimodular change, so N B a is in
            # N Z^ambient_rank exactly when (V^-1 a)_i is in step_i Z for every i.
            smith, _left, right = integral_coordinates.smith_form()
            steps = tuple(
                int(denominator // gcd(abs(smith[index, index]), denominator))
                for index in range(parameter_rank)
            )
            # In the coordinates w = V^-1 a the kernel condition (V^-1 a)_i in step_i Z
            # is the condition w_i in gcd(step_i, m) Z modulo the period, so
            # gcd(step_i, m) numbers the classes of P/S in that coordinate and
            # m / gcd(step_i, m) counts the kernel's classes there.
            coset_steps = tuple(int(gcd(step, period_scalar)) for step in steps)
            counts = tuple(period_scalar // step for step in coset_steps)
            images = tuple(
                classes_module(quotient(parameter_lattice.module_generator(label)))
                for label in labels
            )
            zero = classes_module.zero()

            def class_of(coefficients):
                r"""The class in ``P/mP`` of the parameter with these coordinates."""
                return sum(
                    (
                        classes_module.scalar_multiple(
                            classes_module.base_ring()(coefficient), image
                        )
                        for coefficient, image in zip(coefficients, images, strict=True)
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

            def coordinates_at(indices):
                r"""The coordinates ``V u`` of the parameter whose Smith coordinate is ``u``.

                The saturation's coordinate lattice is read in ``u = V^-1 a``, so the
                parameter with ``u`` given is ``a = V u``; that is the reading the
                representatives are taken in, and ``V`` is unimodular.
                """
                column = right * matrix(
                    ZZ, parameter_rank, 1, [ZZ(index) for index in indices]
                )
                return tuple(int(entry) % period_scalar for entry in column.list())

            tested = tuple(
                coordinates_at(indices) for indices in parameters(coset_steps)
            )
            passing_coordinates = []
            passing_lifts = []
            for coordinates in tested:
                lift = self._lift_at(coordinates)
                if lift.integral_restriction(source, target) is None:
                    continue
                passing_coordinates.append(coordinates)
                passing_lifts.append(lift)
            passing_coordinates = tuple(passing_coordinates)
            passing = tuple(class_of(coordinates) for coordinates in passing_coordinates)
            kernel = tuple(
                class_of(coordinates_at(tuple(
                    int(index) * step
                    for index, step in zip(indices, coset_steps, strict=True)
                )))
                for indices in parameters(counts)
            )
            kernel_generators = tuple(
                coordinates_at(tuple(
                    step if position == unit else 0
                    for position, step in enumerate(coset_steps)
                ))
                for unit in range(parameter_rank)
            )
            period_inclusion = quotient.kernel().inclusion()
            period_generators = tuple(
                tuple(int(period_inclusion(generator).to_vector()(label)) for label in labels)
                for generator in period_inclusion.domain().module_generators()
            )
            return (
                finite_ordered_set(passing),
                finite_ordered_set(kernel),
                (
                    passing_coordinates,
                    kernel_generators,
                    period_generators,
                    tuple(passing_lifts),
                ),
            )

        @cached_method
        def integral_parameter_classes(self):
            r"""The integral residue locus, as a union of cosets of the transvection kernel.

            The classes of ``P/mP`` whose lift restricts to an integral isometry, where
            ``P`` is the parameter lattice of :meth:`integral_parameter_quotient` and
            ``m`` its period.  :meth:`_integral_parameter_cosets` states and computes
            the decomposition: the locus is a union of cosets of

                ``K = {a in P/mP : s(a) in L'}``,

            the kernel of ``a + mP |-> s(a) + L'``, which is a proper subset of the
            locus as soon as the marked isotropic vector has divisibility greater than
            one, and one representative per coset of ``P/S`` is tested by the lift's own
            integral restriction.

            The locus is presented as the image of the passing representatives and the
            kernel under the coset addition, with the inverse naming both components of
            the pair, so the union is never listed as one set.
            """
            passing, kernel, _parameters = self._integral_parameter_cosets()
            classes_module = self.integral_parameter_quotient().codomain()
            cosets = passing.product_with(kernel)
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
        def integral_kernel_group_generators(self):
            r"""A generating family of the integral kernel ``K_Z``, as quotients of integral lifts.

            ``K_Z = {g in K_v : g(L) subset L'}`` is the kernel of the Levi map's own
            integral points, and it acts simply transitively on the integral lift locus
            ``T_Z = phi(r^{-1}(C))`` (:meth:`_integral_lift_locus`,
            :meth:`integral_members`): for integral lifts ``phi(x)`` and ``phi(x_0)``
            the quotient ``phi(x) phi(x_0)^{-1} = E_{f,s(x) - s(x_0)}`` is an integral
            element of the kernel, by ``phi(x+y) = E_{f,s(y)} phi(x)`` and equation (5)
            of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §3.1, printed p. 9.  With
            ``x_0`` one passing representative, the parameters of ``K_Z`` are therefore

                ``r^{-1}(C) - x_0 = { s(c) - s(x_0) + s(k) : c in C, k in mP }``,

            the set whose differences form a subgroup of ``P``, and that subgroup is
            generated by the differences of the locus' representatives
            ``s(c) - s(x_0)`` over the classes of ``P/S``, by the generators of ``K``,
            and by the period's generators (:meth:`_integral_parameter_cosets`).  The
            family returned is those quotients, one per generator, and every one of them
            is admitted by ``K_Z``'s own predicate subgroup -- which asks the lift for
            its integral restriction -- rather than assumed integral.

            The family returned is the quotients' *integral restrictions*: a quotient
            of two integral lifts is itself integral, so each restriction is an isometry
            of the target lattice, and those are what the consumers ask
            ``\rho`` and the Levi map about.  ``K_Z`` is abelian because it is a family
            of Eichler transvections of the one vector ``f`` and they compose by adding
            their parameters (equation (5), printed p. 9).

            It requires a nonempty integral locus; the identity marking of a reduction
            always has one.
            """
            _passing, _kernel, parameters = self._integral_parameter_cosets()
            representatives, kernel_generators, period_generators, _lifts = parameters
            assert len(representatives) > 0, (
                f"the integral lifts of {self.reduction_isometry()!r} form an empty set, so they "
                f"determine no elements of the integral kernel: ask the identity marking of "
                f"{self.target_reduction()!r} for its integral kernel"
            )
            period_scalar = int(NN(self.integral_parameter_period()))
            origin = representatives[0]
            base = self.parameterization()(self._parameter_at(origin))

            def shifted(shift):
                r"""The coordinates of the parameter ``origin + shift`` modulo the period."""
                return tuple(
                    (entry + increment) % period_scalar
                    for entry, increment in zip(origin, shift, strict=True)
                )

            family = (
                *representatives[1:],
                *(shifted(shift) for shift in (*kernel_generators, *period_generators)),
            )
            target = self.target_reduction().isotropic_embedding().codomain()
            quotients = tuple(
                self.parameterization()(self._parameter_at(coordinates)) * base.inverse()
                for coordinates in family
            )
            restricted = tuple(
                quotient.integral_restriction(target, target) for quotient in quotients
            )
            assert all(restriction is not None for restriction in restricted), (
                f"a quotient of two integral lifts of {self.reduction_isometry()!r} has no "
                f"integral restriction, but both factors are isometries onto {target!r} and "
                f"so their quotient is one of its automorphisms"
            )
            return finite_ordered_set(restricted)

        @cached_method
        def integral_base_point_or_none(self):
            r"""Decide existence and retain one integral lift, or ``None``.

            An integral rational base point is a lift and answers at once, and an
            empty residue locus answers ``None``.  Otherwise the integral
            residue locus has already built the lift of each of its
            representatives and tested it (:meth:`_integral_parameter_cosets`,
            which decides the classes by exactly that test), so one of those
            lifts is a point of the locus and this answers it.  Lifting the first
            class again, and asking that second lift for its integral
            restriction, would decide a fact the residue locus has decided.
            """
            source = self.source_reduction().isotropic_embedding().codomain()
            target = self.target_reduction().isotropic_embedding().codomain()
            base = self.base_point()
            if base.integral_restriction(source, target) is not None:
                return base
            _passing, _kernel, parameters = self._integral_parameter_cosets()
            lifts = parameters[3]
            return lifts[0] if lifts else None

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
