r"""Parabolic subgroups of primitive isotropic subobjects, and their Levi data.

Let ``iota: I -> L`` be a primitive totally isotropic subobject of a lattice.
Its parabolic subgroup is the stabilizer

``P_I = Stab_{O(L)}(I) = {g in O(L) : g(iota(I)) = iota(I)}``.

Every ``g`` in ``P_I`` preserves ``I^perp`` as well, so it restricts along
``iota`` and descends to the isotropic reduction, giving two group morphisms
out of ``P_I``.  Writing ``K_I = I^perp/I``,

``1 -> U_I -> P_I -> M_I -> 1``,   ``M_I <= GL(I) x O(K_I)``,

where ``U_I`` is the common kernel: the isometries acting as the identity on
``I`` and on ``K_I``.  Membership in ``U_I`` is decided from that definition,
without constructing the quotient: ``g`` acts trivially on ``I^perp/I``
exactly when ``(g - 1)(I^perp)`` lies in ``iota(I)``.

For ``rank(I) = 1`` the ``O(L)``-orbit of ``I`` is a cusp, ``P_I`` is that
cusp's arithmetic stabilizer, and ``K_I = v^perp/v`` is the lattice whose
reflection group acts on the cusp's fundamental domain.  This is the object in
which the Sterk simple-root counts are compared: one count is taken under the
full reflection group ``W(K_I)`` of ``K_I``, the other under a reflection
subgroup of it, and the two group actions are what differ.

The Levi target ``GL(I) x O(K_I)`` is delivered here by its two components
separately.  ``levi_restriction`` lands in ``GL(I)``, the module
automorphisms of ``I``: the form ``I`` inherits is identically zero, so its
isometry group is all of ``GL(I)`` and nothing smaller is being asserted.
``levi_quotient_action`` lands in the module automorphisms of the represented
cokernel ``I^perp/I``.  Whether that automorphism is an isometry of the
induced form is the statement ``O(K_I)`` makes, and stating it needs the
projection ``I^perp ->> K_I`` that the owned ``isotropic_reduction`` does not
return; see ``isotropic_quotient_projection`` below.
"""

from sage.matrix.constructor import matrix
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import parent as element_parent

from sage_extensions.categories.modules.pure.modules import ModuleSubobjects
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)


def _integral_solution(system, target):
    r"""Return one integral solution of ``system * x = target``, or ``None`` when there is none.

    ``system`` is a matrix over `ZZ` and ``target`` a column of its height.
    Smith normal form writes ``U * system * V = S`` with ``S`` diagonal, so
    ``system * x = target`` has an integral solution exactly when
    ``U * target`` is divisible entry by entry by the diagonal of ``S`` and
    vanishes past its rank; then ``x = V * (S^-1 * U * target)``.  Both answers
    are exact: a solution is never missed and a non-solution is never returned.
    """
    diagonal, left, right = system.smith_form()
    transformed = left * target
    rows, columns = system.nrows(), system.ncols()
    coordinates = [SageZZ.zero() for _ in range(columns)]
    for position in range(rows):
        entry = transformed[position, 0]
        pivot = (
            diagonal[position, position]
            if position < min(rows, columns)
            else SageZZ.zero()
        )
        if pivot:
            if entry % pivot:
                return None
            coordinates[position] = entry // pivot
        elif entry:
            return None
    solution = right * matrix(SageZZ, [[entry] for entry in coordinates])
    values = tuple(solution[position, 0] for position in range(columns))
    assert system * matrix(SageZZ, [[entry] for entry in values]) == target, (
        f"the Smith-normal-form solution of {system} * x = {target} does not satisfy it"
    )
    return values


def _content(values):
    r"""Return the content of an integer vector: the gcd of its entries, and zero for the zero vector."""
    content = SageZZ.zero()
    for value in values:
        content = content.gcd(SageZZ(value))
    return abs(content)


def general_linear_images(vectors):
    r"""Return images of ``vectors`` under generators of ``GL_k(Z)``, for ``k = len(vectors)``.

    Adjacent transpositions, one shear and one sign change generate ``GL_k(Z)``
    (Newman, *Integral Matrices*, VII.1).
    """
    images = []
    for i in range(len(vectors) - 1):
        swapped = list(vectors)
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        images.append(tuple(swapped))
    if len(vectors) > 1:
        images.append((vectors[0] + vectors[1], *vectors[1:]))
    images.append((-vectors[0], *vectors[1:]))
    return tuple(images)


class PrimitiveIsotropicSubobjects(OwnedCategoryOverBaseRing):
    r"""Primitive totally isotropic subobjects of a lattice over ``R``.

    Membership states two facts about the chosen monomorphism ``iota``: the
    form of the codomain restricts to zero along it, and its cokernel is
    torsion free.  Both are checked by the ambient lattice's admission method.
    """

    def _repr_object_names(self):
        return f"primitive totally isotropic subobjects over {self.base_ring()}"

    def an_object(self):
        r"""The isotropic line spanned by the first generator of ``U``."""
        from sage_extensions.categories.lattices import Lattices

        plane = Lattices(self.base_ring())("U")
        return plane.primitive_isotropic_subobject(plane.module_generators()[0])

    def super_categories(self):
        return [ModuleSubobjects(self.base_ring())]

    class ParentMethods:
        def is_totally_isotropic(self) -> bool:
            r"""Return whether the codomain's form restricts to zero along the inclusion."""
            lattice = self.ambient_module()
            zero = lattice.base_ring().zero()
            embedded = self.embedded_module_generators()
            labels = self.module_generating_set()
            return all(
                lattice.b(embedded[left], embedded[right]) == zero
                for left in labels
                for right in labels
            )

        def ambient_lattice(self):
            r"""Return the lattice this isotropic subobject sits in."""
            return self.inclusion().codomain()

        @cached_method
        def isotropic_perpendicular(self):
            r"""Return ``I^perp`` as a subobject of the same lattice.

            The subobject is totally isotropic, so ``I <= I^perp``: this is
            the flag whose successive quotient is the isotropic reduction.
            """
            return self.inclusion().orthogonal_complement()

        @cached_method
        def into_perpendicular(self):
            r"""Return ``I -> I^perp``, the inclusion factored through its own perpendicular."""
            perpendicular = self.isotropic_perpendicular()
            lift = perpendicular.inclusion().lift
            inclusion = self.inclusion()
            return self.Mono(perpendicular)({
                    label: lift(inclusion(self.module_generator(label)))
                    for label in self.module_generating_set()
                })

        @cached_method
        def isotropic_quotient(self):
            r"""Return the represented module ``I^perp/I``.

            This is the underlying module of ``self.isotropic_reduction()``,
            which is the same quotient carrying the form ``I^perp`` induces
            on it.  The two ranks are asserted to agree.
            """
            quotient = self.into_perpendicular().cokernel()
            assert quotient.module_rank() == self.isotropic_reduction().module_rank(), (
                f"two constructions of I^perp/I for the isotropic sublattice I = {self} "
                f"disagree: the cokernel of I -> I^perp has rank {quotient.module_rank()}, "
                f"but the isotropic reduction has rank "
                f"{self.isotropic_reduction().module_rank()}"
            )
            return quotient

        def isotropic_quotient_projection(self):
            r"""Return the projection ``I^perp ->> I^perp/I``.

            The owned ``isotropic_reduction`` returns the quotient lattice
            ``K_I`` but not this map, so the descent of a parabolic element is
            expressed here on the represented cokernel.
            """
            return self.isotropic_quotient().presentation_projection()

        def stabilizes(self, automorphism) -> bool:
            r"""Return whether ``automorphism`` carries this subobject onto itself.

            Both ``g`` and ``g^{-1}`` are asked to send the selected
            generators into the image, so the answer is the set equality
            ``g(I) = I`` and not the inclusion ``g(I) <= I``.
            """
            inclusion = self.inclusion()
            inverse = ~automorphism
            embedded = self.embedded_module_generators()
            return all(
                inclusion.is_in_image(automorphism(embedded[label]))
                and inclusion.is_in_image(inverse(embedded[label]))
                for label in self.module_generating_set()
            )

        @cached_method
        def _stabilizer_action(self):
            r"""The integral-structure action whose stabilizer is ``Stab_{O(L)}(I)``.

            ``None`` for the zero isotropic sublattice, whose stabilizer is the
            whole ambient orthogonal group and so has no orbit to split.
            """
            from sage_indefinite_port.indefinite.marked_lattices import INDUCTION

            embedded = self.embedded_module_generators()
            vectors = tuple(embedded[label] for label in self.module_generating_set())
            if not vectors:
                return None
            # The radical action is what the port's stabilizer problem takes as
            # its "allowed action on J" (IndefiniteForms.g:1710-1723): generators
            # of GL(J). Adjacent transpositions, one shear and one sign change
            # generate GL_k(Z) for every k (Newman, Integral Matrices, VII.1).
            radical_images = general_linear_images(vectors)
            return INDUCTION.recursion.isotropic_stabilizer_action(
                vectors, radical_images
            )

        def _stabilizer_representation(self):
            r"""The finite lattice-orbit representation of the stabilizer action."""
            action = self._stabilizer_action()
            if action is None:
                raise ValueError(
                    f"the stabilizer of {self} has no lattice orbit to represent: it is the "
                    "zero isotropic sublattice, whose stabilizer is the ambient orthogonal group"
                )
            return action.finite_representation()

        def stabilizer_schreier_factors(self):
            r"""Return ``(letters, transversals)`` of the stabilizer's Schreier family.

            ``letters`` are the action groupoid's generators and ``transversals[i]``
            is the transporter of the ``i``-th lattice-orbit point, so the family is
            ``t_(s.p)^-1 s t_p`` over the two.
            """
            return self._stabilizer_representation().stabilizer_schreier_factors()

        def orbit_lattice_records(self):
            r"""Return one record per lattice-orbit point, with its maps (#286).

            See ``_FiniteIntegralRepresentation.orbit_lattice_records``: each record
            states the orbit lattice, the module image and its own generating
            labels, the inclusion into the rational ambient, the images of the
            ambient lattice's generators, and the transport ``t_p: L -> L_p``.
            """
            return self._stabilizer_representation().orbit_lattice_records()

        def middle_transport(self, position, letter):
            r"""Return ``letter`` as an isometry between two orbit lattices (#286).

            The domain is the orbit lattice at ``position``, whose generators are
            the image module's own canonical basis; the transported source basis is
            read once, by the transport, and not again here.
            """
            return self._stabilizer_representation().middle_transport(position, letter)

        def stabilizer_discriminant_image(self):
            r"""Return rho(P_I) as a subgroup of O(A_L) by the action-groupoid construction (#310).

            The stabilizer is presented by the action's own orbit data, and each
            Schreier factor is converted through discriminant transports between
            integral orbit lattices, so no individual rational transporter is
            applied to A_L. The radical action is the full general linear
            group of the isotropic sublattice at every positive rank.
            The zero sublattice has the full ambient orthogonal stabilizer.
            """
            action = self._stabilizer_action()
            if action is None:
                return self.ambient_lattice().O().discriminant_image()
            return action.finite_representation().stabilizer_discriminant_image()

        def rational_stabilizer_right_cosets(self):
            r"""Return a transversal of ``G/H`` for the rational stabilizer ``G`` of ``I^perp``.

            ``G`` extends the integral stabilizer of ``I^perp`` to the
            rational space, and ``H`` is its intersection with ``O(L)``.
            Elements of the transversal are isometries of ``L tensor QQ``.
            """
            from sage_extensions.categories.isotropic_orbits import _marked_isotropic_category, _marked_isotropic_object
            from sage_indefinite_port.indefinite.marked_lattices import isotropic_stabilizer_right_cosets

            return isotropic_stabilizer_right_cosets(
                _marked_isotropic_category(self.ambient_lattice(), 1), _marked_isotropic_object(self, flag=False)
            )

        def parabolic_subgroup(self):
            r"""Return ``P_I = Stab_{O(L)}(I)``, the one parabolic of the isotropic reduction of ``I``."""
            return self.isotropic_reduction().parabolic_subgroup()

        def levi_restriction(self, automorphism):
            r"""Return ``g|_I`` in ``GL(I)`` for ``g`` in the parabolic subgroup: the isotropic action of ``g``."""
            return self.isotropic_reduction().isotropic_action()(automorphism)

        def levi_quotient_action(self, automorphism):
            r"""Return the descent of ``g`` to ``I^perp/I`` for ``g`` in ``P_I``."""
            assert self.stabilizes(automorphism), (
                f"cannot descend {automorphism} to I^perp/I for the isotropic sublattice "
                f"I = {self}: descent is defined only for an isometry g with g(I) = I, "
                f"and this isometry does not map {self} onto itself"
            )
            perpendicular = self.isotropic_perpendicular()
            perpendicular_inclusion = perpendicular.inclusion()
            projection = self.isotropic_quotient_projection()
            quotient = self.isotropic_quotient()
            return quotient.module_category().Mor(quotient, quotient)(
                {
                    label: projection(
                        perpendicular_inclusion.lift(
                            automorphism(
                                perpendicular_inclusion(
                                    perpendicular.module_generator(label)
                                )
                            )
                        )
                    )
                    for label in perpendicular.module_generating_set()
                }
            )

        def acts_trivially_on_isotropic_reduction(self, automorphism) -> bool:
            r"""Return whether ``(g - 1)(I^perp)`` lies in ``iota(I)``.

            This is the definition of acting as the identity on ``I^perp/I``,
            decided on ``I^perp`` itself, so no quotient is constructed.
            """
            inclusion = self.inclusion()
            perpendicular = self.isotropic_perpendicular()
            perpendicular_inclusion = perpendicular.inclusion()
            return all(
                inclusion.is_in_image(automorphism(embedded) - embedded)
                for embedded in (
                    perpendicular_inclusion(perpendicular.module_generator(label))
                    for label in perpendicular.module_generating_set()
                )
            )

        @cached_method
        def unipotent_radical(self):
            r"""Return the generated kernel on I and on its perpendicular quotient."""
            return self.isotropic_reduction().unipotent_kernel()

        def eichler_transvection(self, orthogonal_vector):
            r"""Return the Eichler transvection ``E_{f,x}`` of this isotropic line.

            For the selected generator ``f`` of a rank-one isotropic subobject
            and ``x`` in ``f^perp``,

            ``E_{f,x}(y) = y + b(y,x) f - (q(x)/2) b(y,f) f - b(y,f) x``.

            The framing supplies ``f``: the transvection depends on the chosen
            generator and not only on the line, since ``E_{-f,x} = E_{f,-x}``.
            The coefficient ``q(x)/2`` is integral because ``x`` lies in an
            even lattice, which is asserted.

            ``E_{f,x}`` fixes ``f`` and satisfies ``(E_{f,x} - 1)(f^perp) <=
            Z f``, so it lies in ``unipotent_radical()``.  The assignment
            ``x -> E_{f,x}`` is a group morphism from ``(f^perp, +)`` killing
            ``f``, hence a morphism from ``f^perp/f``.
            """
            lattice = self.ambient_lattice()
            ring = lattice.base_ring()
            assert int(self.module_rank()) == 1, (
                f"no Eichler transvection is attached to {self}: an Eichler transvection "
                f"needs an isotropic sublattice of rank one, but {self} has rank "
                f"{self.module_rank()}"
            )
            assert lattice.is_even(), (
                f"no Eichler transvection of {self} is defined in {lattice}: the "
                f"coefficient q(x)/2 is integral only on an even lattice, and {lattice} "
                f"is not even"
            )
            isotropic_vector = self.embedded_module_generators()[
                self.module_generating_set()[0]
            ]
            assert (
                lattice.b(isotropic_vector, orthogonal_vector) == ring.zero()
            ), (
                f"no Eichler transvection E_(f,x) with f = {isotropic_vector} and "
                f"x = {orthogonal_vector}: x must be orthogonal to f, but b(f, x) = "
                f"{lattice.b(isotropic_vector, orthogonal_vector)}"
            )
            square = lattice.q(orthogonal_vector)
            half_square = square // ring(2)
            assert ring(2) * half_square == square, (
                f"no Eichler transvection E_(f,x) with x = {orthogonal_vector} preserves "
                f"{lattice}: q(x) = {square} is odd, so q(x)/2 is not in {ring}"
            )

            def image(label):
                source = lattice.module_generator(label)
                against_x = lattice.b(source, orthogonal_vector)
                against_f = lattice.b(source, isotropic_vector)
                return (
                    source
                    + lattice.scalar_multiple(
                        against_x - half_square * against_f, isotropic_vector
                    )
                    - lattice.scalar_multiple(against_f, orthogonal_vector)
                )

            return lattice.Aut()(
                {label: image(label) for label in lattice.module_generating_set()}
            )

        def unipotent_group_generators(self):
            r"""Return a finite indexed family generating the full integral unipotent radical.

            These are the integral generators of the common kernel on I and
            I-perp/I. In higher null rank this includes the full Hom parameters
            and the central pointwise-perpendicular shears.
            """
            from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values

            return finite_indexed_family_from_values(None, tuple(self.unipotent_radical().group_generators()))

        def is_equivalent_to(self, other) -> bool:
            r"""Return whether ``O(L)`` carries this isotropic subobject to ``other``.

            The decision comes from the exact indefinite computation; where its
            hypotheses do not hold, that computation states the absence rather
            than searching the group.
            """
            return self.transporter_witness_to(other) is not None

        def transporter_witness_to(self, other):
            r"""Return one ``g`` in ``O(L)`` with ``g(I) = other``, or ``None``.

            The full transporter is the coset ``g P_I``, which is infinite
            whenever ``P_I`` is; one witness together with
            ``parabolic_subgroup`` presents it.
            """
            assert other.ambient_lattice() is self.ambient_lattice(), (
                f"no isometry can carry {self} to {other}: they are sublattices of "
                f"different lattices, {self.ambient_lattice()} and {other.ambient_lattice()}"
            )
            return self.ambient_lattice().Aut().isotropic_equivalence_witness(
                self, other
            )

        def _kernel_parameter_witness(self, source, target):
            r"""Solve ``k(source) = target`` for one element ``k`` of the pointwise kernel, or ``None``.

            The kernel is ``K = ker(P_I -> O(I^perp))`` and its elements act on
            the ambient lattice by ``x |-> x + N(pi(x))`` with
            ``N: L/I^perp -> rad(I^perp)`` linear, which is the parametrization
            :meth:`IsotropicReductions._pointwise_perpendicular_kernel_data`
            retains: there ``N`` runs over the complete integral solution module
            of the homogeneous isometry equations
            ``b(N f_a, f_b) + b(f_a, N f_b) = 0``, so the assignment
            ``parameter |-> 1 + N`` is a homomorphism from an additive lattice to
            ``K`` and every element of ``K`` is one of its values.  On a vector
            ``x`` the displacement is therefore linear in the parameter, and
            ``k(source) = target`` is one integer linear system, solved exactly
            by Smith normal form.  ``None`` is the exact statement that ``K``
            carries ``source`` onto ``target``; the returned isometry is checked
            against the two endpoints before it leaves this method.
            """
            lattice = self.ambient_lattice()
            reduction = self.isotropic_reduction()
            parameters = reduction.pointwise_perpendicular_parameter_module()
            labels = tuple(parameters.module_generating_set())
            ring = parameters.base_ring()
            source_coordinates = self.coordinates(source)
            target_coordinates = self.coordinates(target)
            if not labels:
                return lattice.Aut().one() if source_coordinates == target_coordinates else None
            columns = []
            for label in labels:
                isometry = reduction.pointwise_perpendicular_isometry(
                    parameters.module_generator(label)
                )
                image = self.coordinates(isometry(source))
                columns.append(
                    [
                        reached - start
                        for reached, start in zip(image, source_coordinates, strict=True)
                    ]
                )
            rows = [
                [column[position] for column in columns]
                for position in range(len(source_coordinates))
            ]
            displacement = [
                reached - start
                for reached, start in zip(target_coordinates, source_coordinates, strict=True)
            ]
            values = _integral_solution(
                matrix(SageZZ, rows),
                matrix(SageZZ, [[entry] for entry in displacement]),
            )
            if values is None:
                return None
            parameter = parameters.zero()
            for entry, label in zip(values, labels, strict=True):
                parameter = parameter + ring(int(entry)) * parameters.module_generator(label)
            isometry = reduction.pointwise_perpendicular_isometry(parameter)
            assert isometry(source) == target, (
                f"the pointwise-kernel parameter solving {source} |-> {target} does not carry "
                f"{source} onto {target}: it carries it onto {isometry(source)}"
            )
            return isometry

        def pointwise_vector_equivalence_witness(self, left, right):
            r"""Return one element of the pointwise stabilizer of ``I`` carrying ``left`` onto ``right``, or ``None``.

            ``left`` and ``right`` are vectors of the ambient lattice, and the
            pointwise stabilizer is ``{g in O(L) : g(iota(I)) = iota(I) pointwise}``.

            When ``I`` is maximal isotropic, i.e. ``I = I^perp``, that group is
            exactly ``K = ker(P_I -> O(I^perp))``: an element fixing ``I``
            pointwise stabilizes ``I^perp`` and acts trivially on the whole of
            ``I = I^perp``, and conversely an element fixing ``I^perp``
            pointwise fixes ``I``.  That hypothesis is asserted here, and the
            kernel is the one
            :meth:`IsotropicReductions._pointwise_perpendicular_kernel_data`
            retains as a complete integral parameter module, so
            :meth:`_kernel_parameter_witness` decides ``k(left) = right`` for
            ``k`` in the whole pointwise stabilizer and not merely for some
            selected generators of it.

            The answer is therefore a decision: ``None`` says that no element of
            the pointwise stabilizer carries ``left`` onto ``right``.  No element
            of the infinite group is listed and no generating family of it is
            selected.
            """
            assert self.isotropic_perpendicular().module_rank() == self.module_rank(), (
                f"the pointwise stabilizer of {self} is not its pointwise kernel: "
                f"that identification needs I = I^perp, and {self} has rank "
                f"{int(self.module_rank())} in a perpendicular of rank "
                f"{int(self.isotropic_perpendicular().module_rank())}"
            )
            lattice = self.ambient_lattice()
            source = left if element_parent(left) is lattice else lattice(left)
            target = right if element_parent(right) is lattice else lattice(right)
            return self._kernel_parameter_witness(source, target)

        def vector_equivalence_witness(self, left, right):
            r"""Return one element of ``P_I = Stab_{O(L)}(I)`` carrying ``left`` onto ``right``, or ``None``, or refuse.

            ``left`` and ``right`` are vectors of the ambient lattice.  The
            parabolic is the semidirect-like product of its Levi factor and its
            unipotent radical, ``1 -> U_I -> P_I -> M_I -> 1`` with
            ``M_I <= GL(I) x O(I^perp/I)`` (this module's own statement at the
            top of the file), so a witness in ``P_I`` is a unipotent element
            composed with a Levi element and the decision below is exact on the
            unipotent part:

            * ``q(left) != q(right)``: ``None``, because every element of ``P_I``
              is an isometry of ``L`` and preserves the quadratic form.
            * the content of ``b(left, -)|_I`` differs from the content of
              ``b(right, -)|_I``, or the content of ``b(-, left)`` differs from
              the content of ``b(-, right)``: ``None``, because an element of
              ``P_I`` carries ``I`` onto ``I`` bijectively and hence acts on
              ``Hom(I, ZZ)`` and on ``Hom(L, ZZ)`` by unimodular changes of
              coordinates, which preserve the content, the gcd of the values on
              a basis.
            * the pointwise kernel ``K = ker(P_I -> O(I^perp))`` carries ``left``
              onto ``right``: that element is returned, solved for exactly as
              :meth:`_kernel_parameter_witness` does, and ``K`` is a subgroup of
              ``P_I``.  ``K`` lies in the unipotent radical ``U_I``, and equals it
              when ``I = I^perp``, so this decides the unipotent part of the
              parabolic on a maximal isotropic subobject.
            * otherwise the call refuses.  What remains undecided is the image of
              ``P_I`` in ``O(I^perp)``, whose orbits on the reduction are not
              computed here: the closed-form Levi lifts are
              :meth:`levi_lift_generators`, and turning those generators into an
              orbit decision on ``I^perp/I`` is the missing step.

            ``None`` is therefore a decision, and this call never answers
            ``None`` because it failed to find a witness.  No element of the
            infinite group is listed and no generating family of it is selected.
            """
            lattice = self.ambient_lattice()
            source = left if element_parent(left) is lattice else lattice(left)
            target = right if element_parent(right) is lattice else lattice(right)
            if lattice.q(source) != lattice.q(target):
                return None
            if _content(self._reduction_values(source)) != _content(
                self._reduction_values(target)
            ):
                return None
            if _content(self._dual_values(source)) != _content(self._dual_values(target)):
                return None
            witness = self._kernel_parameter_witness(source, target)
            if witness is not None:
                return witness
            raise ArithmeticError(
                f"cannot decide whether {source} and {target} are equivalent under "
                f"{self.parabolic_subgroup()}: they have the same square "
                f"{lattice.q(source)} and the same reduction contents, and no element of the "
                f"pointwise kernel ker(P_I -> O(I^perp)) carries one onto the other.  The "
                f"remainder of the parabolic is its image in O(I^perp); its orbits on the "
                f"reduction I^perp/I are not computed here, so neither answer is claimed"
            )

        def _reduction_values(self, vector):
            r"""Return the values of ``b(vector, -)`` on the generators of ``I``."""
            lattice = self.ambient_lattice()
            embedded = self.embedded_module_generators()
            return tuple(
                int(lattice.b(vector, embedded[label]))
                for label in self.module_generating_set()
            )

        def _dual_values(self, vector):
            r"""Return the values of ``b(-, vector)`` on the generators of the ambient lattice."""
            lattice = self.ambient_lattice()
            return tuple(
                int(lattice.b(generator, vector))
                for generator in lattice.module_generators()
            )


        # -- the parabolic subgroup of a primitive isotropic plane -------------

        def plane_basis(self):
            r"""Return the two generators of this subobject, as vectors of the ambient lattice.

            The parabolic construction below is stated for a rank-two totally
            isotropic ``P``: its basis ``(p_1, p_2)`` fixes the coordinates in
            which the action on ``P`` is read.
            """
            embedded = self.embedded_module_generators()
            labels = tuple(self.module_generating_set())
            if len(labels) != 2:
                raise ValueError(
                    f"the parabolic construction here is stated for a primitive isotropic plane, "
                    f"but {self} has rank {int(self.module_rank())}"
                )
            return (embedded[labels[0]], embedded[labels[1]])

        def coordinates(self, vector):
            r"""Return the coordinates of ``vector`` on the ambient lattice's generating set."""
            lattice = self.ambient_lattice()
            coordinates = vector.to_vector()
            return tuple(
                int(coordinates(label)) for label in lattice.module_generating_set()
            )

        def vector_from_coordinates(self, coordinates):
            r"""Return the ambient-lattice vector with the given coordinates."""
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            ring = lattice.base_ring()
            return lattice.linear_combination(
                {
                    label: ring(int(entry))
                    for label, entry in zip(labels, coordinates, strict=True)
                    if int(entry)
                }
            )

        def gram_matrix(self):
            r"""Return the Gram matrix of the ambient lattice on its generating set."""
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            generators = tuple(lattice.module_generator(label) for label in labels)
            return [
                [int(lattice.b(left, right)) for right in generators]
                for left in generators
            ]

        @cached_method
        def perpendicular_basis(self):
            r"""Return a `ZZ`-basis of \(P^\perp\) as vectors of the ambient lattice."""
            return self.vector_perpendicular_basis(self.plane_basis())

        def vector_perpendicular_basis(self, vectors):
            r"""Return a `ZZ`-basis of the perpendicular of a family of ambient vectors."""
            lattice = self.ambient_lattice()
            generators = tuple(
                lattice.module_generator(label)
                for label in lattice.module_generating_set()
            )
            rows = [
                [int(lattice.b(generator, vector)) for generator in generators]
                for vector in vectors
            ]
            basis = _kernel_basis_rows(matrix(SageZZ, rows))
            return tuple(self.vector_from_coordinates(row) for row in basis)

        @cached_method
        def unipotent_radical_generators(self):
            r"""Return the Eichler transvections that generate the unipotent radical of the parabolic.

            For an isotropic \\(p \\in P\\) and \\(x \\in p^\\perp\\) the Eichler
            transvection

            \\[ t(p, x)(y) = y - b(x, y)\\, p + b(p, y)\\, x - \\tfrac12 q(x)\\, b(p, y)\\, p \\]

            (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, equations
            (4)--(5), transcribed in
            :meth:`sage_extensions.categories.lattices.Lattices.ParentMethods.eichler_transvection`,
            after Dawes, section 2 equation (7)) is an integral isometry on an even
            lattice, fixes `p`, and for `x\\perp p` it acts on \\(P^\\perp/P\\) as the
            identity: for \\(k \\in P^\\perp\\) it sends `k` to
            \\(k - b(x,k)p \\in k + P\\).  So every one of them lies in the
            unipotent radical \\(U_I\\) of the parabolic at the plane, and
            Eichler's criterion takes exactly this family, one parameter per basis
            vector of \\(p^\\perp\\): Dutour Sikirić--Hulek, arXiv:2302.01679v2,
            subsection "Approximate models and the case of signature \\(p,q\\geq 2\\)"
            (Lemma `sublattice_approx_model`, which cites Eichler's criterion and
            Scattone, Ph.D. thesis, section 3.7, Proposition 3.7.3: generators of
            \\(SL_2(ZZ)^2\\) together with the transvections \\(E_{e_i, v_{i,j}}\\)
            over a `ZZ`-basis \\((v_{i,j})\\) of \\(e_i^\\perp\\)).

            On \\(L = U \\oplus U(2) \\oplus E_8(-2)\\) at \\(P_1\\) this family has
            2 x 11 members, and the radical they generate has the rank 17 that the
            root count of the parabolic gives: \\(2 \\cdot 8\\) from
            \\(\\mathrm{Hom}(K, P)\\) and one from the skew part of
            \\(\\mathrm{End}(P^*)\\).
            """
            lattice = self.ambient_lattice()
            assert lattice.is_even() is True, (
                f"the Eichler transvections of the radical at {self} need the half-integral "
                f"coefficient q(x)/2 of an even lattice, and {lattice} is odd"
            )
            generators = []
            for isotropic in self.plane_basis():
                seen = set()
                for vector in self.vector_perpendicular_basis((isotropic,)):
                    if vector.is_zero():
                        continue
                    key = self.coordinates(vector)
                    if key in seen:
                        continue
                    seen.add(key)
                    transvection = lattice.eichler_transvection(isotropic, vector)
                    if all(
                        transvection(generator) == generator
                        for generator in lattice.module_generators()
                    ):
                        continue
                    generators.append(transvection)
            return tuple(generators)

        @cached_method
        def quotient_reflection_generators(self):
            r"""Return the pointwise-plane reflections in the root shells of \(P^\perp/P\).

            The quotient \(K = P^\perp/P\) is the lattice the Levi acts on.  When
            it is definite its shells are finite; a vector `w` of `K` lifts to a
            vector `\tilde w` of \(P^\perp\) through the reduction's frame, and
            the reflection \(s_{\tilde w}\) is an integral isometry of `L`
            (asserted by the lattice's own reflection) that fixes `P` pointwise,
            since \(P \subseteq \tilde w^\perp\).  So every such reflection lies
            in the parabolic, and its image in \(O(K)\) is the reflection in
            `w`: the Levi factor.

            A shell is taken whole, and further shells are taken while the
            running count stays below 128: for \(T_{\mathrm{En}}\) at \(P_1\),
            \(K = E_8(-4)\) (the catalogue's doubling of \(E_8(-2)\)) has one
            shell of 240 vectors, whose reflections generate
            \(W(E_8) = O(E_8)/(\pm 1)\) and so the whole Levi factor; for the
            odd \(I_{0,7}(2)\) of the Coble ambient the first shell alone gives
            only the sign changes and the second is needed for the permutations.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            if quotient.is_definite() is not True:
                raise ValueError(
                    f"the Levi factor of the parabolic at {self} is not spanned by "
                    f"reflections: the quotient P^perp/P = {quotient} is not definite, "
                    f"so its shells are infinite and no shell enumeration of the "
                    f"reflection family is available here"
                )
            lattice = self.ambient_lattice()
            if int(quotient.module_rank()) == 0:
                # P^perp = P: the whole group is the parabolic, and the Levi factor
                # on K = P^perp/P = 0 is trivial.  A rank-zero cartesian lattice has
                # no shortest vector, so the shell enumeration below must not run.
                return ()
            labels = tuple(quotient.module_generating_set())
            lifts = self.quotient_frame_lifts()

            def coordinates(element):
                vector = element.to_vector()
                return tuple(int(vector(label)) for label in labels)

            def lift(element):
                entries = coordinates(element)
                return sum(
                    (
                        lattice.scalar_multiple(
                            lattice.base_ring()(entries[position]), lifts[label]
                        )
                        for position, label in enumerate(labels)
                        if entries[position]
                    ),
                    lattice.zero(),
                )

            shortest = tuple(quotient.shortest_vectors())
            if not shortest:
                raise ValueError(
                    f"the Levi factor of the parabolic at {self} has no reflection to "
                    f"lift: the definite quotient P^perp/P = {quotient} has no shortest "
                    f"vector other than zero"
                )
            square = int(quotient.b(shortest[0], shortest[0]))
            shells = [shortest]
            count = len(shortest)
            step = 1
            while count <= 128 and step <= 3:
                shells.append(tuple(quotient.vectors_of_square(square * (step + 1))))
                count = sum(len(shell) for shell in shells)
                step += 1
            lifted = []
            seen = set()
            for shell in shells:
                for element in shell:
                    key = coordinates(element)
                    if all(-entry == 0 for entry in key):
                        continue
                    negative = tuple(-entry for entry in key)
                    if negative in seen:
                        continue
                    seen.add(key)
                    lifted.append(lift(element))
            generators = []
            for vector in lifted:
                if vector.is_integral_reflection_vector():
                    generators.append(lattice.reflection(vector))
            return tuple(generators)

        @cached_method
        def quotient_frame_lifts(self):
            r"""Return the reduction's frame, lifted into the ambient lattice, by quotient label.

            ``isotropic_reduction().coordinate_frame()`` is a section of
            \(P^\perp \twoheadrightarrow P^\perp/P\) on a generating set of the
            quotient lattice; this returns the same section with values in the
            ambient lattice, so a vector of the quotient can be lifted linearly.
            """
            reduction = self.isotropic_reduction()
            quotient = reduction.quotient_lattice()
            perpendicular_inclusion = reduction.orthogonal_complement().inclusion()
            frame = reduction.coordinate_frame()
            return {
                label: perpendicular_inclusion(frame(label))
                for label in quotient.module_generating_set()
            }

        @cached_method
        def splitting_complement(self):
            r"""Return a `ZZ`-basis complement of `P^\perp` that is orthogonal to `K`, or ``None``.

            The Levi action on `P` is read in the coordinates `(P, U)` where `U`
            completes a `ZZ`-basis of \(P^\perp\) to one of `L`.  A Levi element
            acts on `P` by `M` and on `U` by the contragredient matrix; it is an
            isometry of `L` exactly when that matrix is integral, which is what
            makes the lift constructive in the *split* case of
            :meth:`levi_lift_generators`: `P \perp U` is then an orthogonal
            summand of `L` carrying the plane.  The returned pair is ``None``
            when no such complement exists, i.e. when the complement pairs
            nontrivially with \(K = P^\perp/P\).
            """
            lattice = self.ambient_lattice()
            labels = tuple(lattice.module_generating_set())
            rank = len(labels)
            current = matrix(
                SageZZ, [self.coordinates(vector) for vector in self.perpendicular_basis()]
            )
            complement = []
            for position in range(rank):
                row = tuple(1 if other == position else 0 for other in range(rank))
                augmented = matrix(SageZZ, tuple(current.rows()) + (row,))
                if augmented.rank() > current.rank():
                    current = augmented
                    complement.append(row)
                if len(complement) == 2:
                    break
            if len(complement) != 2:
                return None
            vectors = tuple(self.vector_from_coordinates(row) for row in complement)
            zero = lattice.base_ring().zero()
            for lifted in self.quotient_frame_lifts().values():
                for vector in vectors:
                    if lattice.b(vector, lifted) != zero:
                        return None
            return vectors

        @cached_method
        def levi_lift_generators(self):
            r"""Return the integral Levi lifts of the elementary matrices of \(GL(P)\).

            For a fixed plane basis `(p_1, p_2)` and a complement `(u_1, u_2)` of
            \(P^\perp\) the isometry `g` with `g|_P = M` and `g|_{K} = 1` has
            contragredient matrix

            \[
            g|_{U} = {}^{t}\left(J\,M^{-1}\,J^{-1}\right),
            \qquad J = (b(p_i, u_j)),
            \]

            the block equation `J = g|_P J g|_U^t` of Dutour Sikirić--Hulek,
            *Moduli of polarised Enriques surfaces -- computational aspects*,
            J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, §"The Tits
            building", Theorem (`theorem_isotropic_k_planes`, printed p. 22),
            which determines the `P`-block from the `U`-block uniquely (their
            `P_1` from `Q_1`); the same equations give `g|_{P^\perp}` from the
            action on `K`.  Row-vector convention there, column-vector
            convention here: `J = P_1 J Q_1^t` becomes `g|_P J g|_U^t = J`.
            So `g` is integral exactly when that matrix is, and the lifts of the
            elementary matrices of `GL_2(ZZ)` generate the image of the
            parabolic in `GL(P)`: for `J = diag(1, 2)` the condition is
            `b` even on `[[a, b], [c, d]]`, i.e. `\Gamma^0(2)`, generated by
            `[[1, 0], [1, 1]]`, `[[1, 2], [0, 1]]` and `\pm 1`.
            """
            complement = self.splitting_complement()
            if complement is None:
                return ()
            lattice = self.ambient_lattice()
            plane = self.plane_basis()
            ring = lattice.base_ring()
            pairing = matrix(
                SageZZ,
                [
                    [int(lattice.b(left, right)) for right in complement]
                    for left in plane
                ],
            )
            if int(pairing.determinant()) == 0:
                raise ValueError(
                    f"the complement of P^perp found for {self} does not pair "
                    f"nondegenerately with the plane"
                )
            # A ZZ-basis of P^perp on the plane's own generators, continued by a frame
            # of K = P^perp/P; the plane's vectors are already inside P^perp.
            rank = len(lattice.module_generating_set())
            current = matrix(SageZZ, [self.coordinates(vector) for vector in plane])
            frame = []
            for vector in self.perpendicular_basis():
                row = self.coordinates(vector)
                augmented = matrix(SageZZ, tuple(current.rows()) + (row,))
                if augmented.rank() > current.rank():
                    current = augmented
                    frame.append(row)
                if len(frame) == rank - 4:
                    break
            basis = tuple(plane) + tuple(complement) + tuple(
                self.vector_from_coordinates(row) for row in frame
            )
            change = matrix(
                SageZZ,
                [self.coordinates(vector) for vector in basis],
            )
            inverse = change.inverse()
            images = {}
            candidates = [
                ((1, 0), (1, 1)),
                ((1, 0), (-1, 1)),
                ((1, 0), (2, 1)),
                ((1, 2), (0, 1)),
                ((1, -2), (0, 1)),
                ((1, 4), (0, 1)),
                ((1, 6), (0, 1)),
                ((1, 0), (3, 1)),
                ((1, 0), (6, 1)),
                ((-1, 0), (0, -1)),
                ((-1, 0), (0, 1)),
                ((1, 0), (0, -1)),
            ]
            found = []
            for entries in candidates:
                action = matrix(SageZZ, [[entries[0][0], entries[0][1]], [entries[1][0], entries[1][1]]])
                if int(action.determinant()) not in (1, -1):
                    continue
                contragredient = (pairing * action.inverse() * pairing.inverse()).transpose()
                if any(entry not in SageZZ for entry in contragredient.list()):
                    continue
                block = matrix(SageZZ, rank, rank, 0)
                for row in range(2):
                    for column in range(2):
                        block[row, column] = action[row, column]
                        block[2 + row, 2 + column] = contragredient[row, column]
                for position in range(4, rank):
                    block[position, position] = 1
                lifted = inverse * block * change
                if any(entry not in SageZZ for entry in lifted.list()):
                    continue
                images = {}
                for column, label in enumerate(lattice.module_generating_set()):
                    images[label] = lattice.linear_combination(
                        {
                            other: ring(int(lifted[row, column]))
                            for row, other in enumerate(
                                lattice.module_generating_set()
                            )
                            if lifted[row, column]
                        }
                    )
                found.append(lattice.Aut()(images))
            return tuple(found)

        def is_parabolic_complete(self) -> bool:
            r"""Return whether the split hypothesis of :meth:`levi_lift_generators` holds."""
            return self.splitting_complement() is not None

        @cached_method
        def parabolic_stabilizer_generators(self):
            r"""Return generators of the parabolic \(P_I = \mathrm{Stab}_{O(L)}(I)\) at this plane.

            The construction is the published block decomposition of the
            parabolic, and its three factors are constructed separately:

            * the **unipotent radical**, as `1 + n` over a `ZZ`-basis of the
              nilpotent endomorphisms that kill `I` and carry \(I^\perp\) into
              `I` (:meth:`unipotent_radical_generators`);
            * the **Levi factor on \(I^\perp/I\)**, as the reflections in the
              root shells of the definite quotient lifted into \(I^\perp\)
              (:meth:`quotient_reflection_generators`);
            * the **Levi factor on \(I\)**, as the integral lifts of the
              elementary matrices of `GL_2(ZZ)` (:meth:`levi_lift_generators`).

            When `L` splits along the plane as `P \perp U \perp K` with
            `(P, U)` an orthogonal summand and `K = P^\perp/P`, this is a
            generating set of the whole parabolic: an isometry `g` preserving
            `I` induces `(g|_I, g|_K)` in `GL(I) \times O(K)`, a lift of that
            pair differs from `g` by an element of the radical, and each of the
            three factors is generated above.  Without the splitting the last
            two factors are only a subgroup, and :meth:`is_parabolic_complete`
            says so; the discriminant image is what the caller compares.

            Sources, all read in the arXiv text of the cited version: Dutour
            Sikirić--Hulek, arXiv:2302.01679v2, §"The Tits building",
            Theorem `theorem_isotropic_k_planes` (the block form of an isometry
            preserving an isotropic `k`-plane, its Levi blocks `P_1, Q_1, Q_3`
            and the unipotent blocks, with their row-vector convention), and
            the "Approximate models" subsection (Eichler's criterion: the
            transvections `E_{e,x}`, `e` isotropic and `x \perp e`, after
            Scattone, *Ph.D. thesis*, §3.7 Proposition 3.7.3).
            """
            return (
                self.unipotent_radical_generators()
                + self.quotient_reflection_generators()
                + self.levi_lift_generators()
            )


__all__ = ["PrimitiveIsotropicSubobjects"]

# ---------------------------------------------------------------------------
# The parabolic subgroup of an isotropic plane, by its published block form.
# ---------------------------------------------------------------------------


def _kernel_basis_rows(integer_matrix):
    r"""Return the integer kernel of ``integer_matrix`` as a tuple of coordinate rows.

    The kernel of an integer matrix is a saturated sublattice of ``ZZ^n``, so the
    rows returned span its integer points and not only its rational span.  Sage's
    ``kernel()`` is the left kernel, so the transpose is what carries the rows
    ``x`` with ``A x = 0``.
    """
    kernel = integer_matrix.transpose().kernel()
    return tuple(tuple(int(entry) for entry in row) for row in kernel.basis_matrix().rows())
