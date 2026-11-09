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

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.modules.pure.modules import ModuleSubobjects
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)


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
            # its "allowed action on J" (IndefiniteForms.g:1710-1723): the
            # sign change on a line, and the generating set of GL(J) on a
            # plane.  No owner supplies those images for higher rank, so above a
            # plane this raises rather than guessing an action.
            match vectors:
                case (line,):
                    radical_images = ((-line,),)
                case (first, second):
                    radical_images = (
                        (second, first),
                        (first + second, second),
                        (-first, second),
                    )
                case _:
                    raise ValueError(
                        f"the stabilizer action of {self} is realized here for a line or a "
                        f"plane, not for {vectors!r}: no owner supplies the radical images "
                        "of a higher-rank isotropic sublattice"
                    )
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


__all__ = ["PrimitiveIsotropicSubobjects"]
