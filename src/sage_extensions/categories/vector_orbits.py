r"""Exact vector-orbit data for owned lattices."""

from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.modules.framed.formed.torsion_form_modules import _torsion_form_isometry


def _module_matrix(morphism):
    r"""Forget a structured map to its finite-free module Mor."""
    return morphism.domain().module_category().Mor(
        morphism.domain(), morphism.codomain()
    )(morphism)


def _rank_one_coefficient(element):
    r"""Return the coefficient in a selected rank-one framing."""
    parent = element.parent()
    labels = tuple(parent.module_generating_set())
    if len(labels) != 1:
        raise ValueError(
            f"cannot read {element} as a multiple of a basis vector of {parent}: that "
            f"lattice must have rank one, but its basis has {len(labels)} vectors"
        )
    return element.to_vector()(labels[0])


class VectorPrimitiveExtension:
    r"""Nikulin's primitive extension cut out by one anisotropic primitive vector.

    For ``w in L`` this records

    ``M = Zw ⊥ w^perp -> L``

    together with its finite index, the two discriminant inclusions into
    ``A_M``, the gluing subgroup ``H=L/M <= A_M``, and representatives of
    ``A_L`` in ``H^perp``.
    """

    def __init__(self, lattice, element) -> None:
        vector = (
            element
            if element_parent(element) is lattice
            else lattice(element)
        )
        if vector.q() == 0:
            raise ValueError(
                f"cannot decompose {lattice} along {vector}: the vector must have nonzero "
                f"square so that Zv + v^perp has finite index, but q = {vector.q()}"
            )
        if not lattice.module_rank().is_finite() or not lattice.is_nondegenerate():
            raise ValueError(
                f"cannot decompose {lattice} along {vector}: the lattice must have finite rank "
                f"and a nondegenerate form, and it has rank {lattice.module_rank()} and is "
                f"not known to be nondegenerate"
            )

        line = lattice.subobject_on((vector,))
        if not line.is_primitive():
            raise ValueError(
                f"cannot decompose {lattice} along {vector}: the vector must be primitive, and "
                f"it is not"
            )
        complement = line.orthogonal_complement()
        if line.module_rank() + complement.module_rank() != lattice.module_rank():
            raise ArithmeticError(
                f"the line spanned by {vector} (rank {line.module_rank()}) and its orthogonal "
                f"complement (rank {complement.module_rank()}) do not have total rank "
                f"{lattice.module_rank()}, the rank of {lattice}"
            )
        line_lattice = line.inclusion().domain()
        complement_lattice = complement.inclusion().domain()
        sum_lattice = line_lattice + complement_lattice

        line_images = tuple(
            line.inclusion()(generator)
            for generator in line_lattice.module_generators()
        )
        complement_images = tuple(
            complement.inclusion()(generator)
            for generator in complement_lattice.module_generators()
        )
        inclusion = sum_lattice.Emb(lattice)(line_images + complement_images)
        ring = lattice.base_ring()
        index = ring(int(inclusion.index().finite_value()))
        if index <= ring.zero():
            raise ArithmeticError(
                f"Zv + v^perp for v = {vector} does not have finite positive index in {lattice}: "
                f"the computed index is {index}"
            )

        sum_generators = tuple(sum_lattice.module_generators())
        split = int(line_lattice.module_rank())
        line_in_sum = line_lattice.Emb(sum_lattice)(sum_generators[:split])
        complement_in_sum = complement_lattice.Emb(sum_lattice)(sum_generators[split:])
        line_discriminant_inclusion = line_in_sum.discriminant_inclusion()
        complement_discriminant_inclusion = complement_in_sum.discriminant_inclusion()

        sum_form = sum_lattice.discriminant_group()
        sum_dual = sum_lattice.dual_lattice()
        dual_labels = tuple(sum_dual.module_generating_set())
        gluing_classes = []
        for ambient_generator in lattice.module_generators():
            pairings = tuple(
                lattice.b(ambient_generator, inclusion(generator))
                for generator in sum_generators
            )
            dual_element = sum_dual.linear_combination(
                {
                    label: ring(coefficient)
                    for label, coefficient in zip(dual_labels, pairings, strict=True)
                    if coefficient
                }
            )
            gluing_classes.append(sum_form.projection()(dual_element))
        gluing_subgroup = sum_form.subgroup_on(tuple(gluing_classes))
        if int(gluing_subgroup.cardinality()) != int(index):
            raise ArithmeticError(
                f"the gluing subgroup L/M for L = {lattice} and M = Zv + v^perp, v = {vector}, "
                f"has order {gluing_subgroup.cardinality()}, not the index [L:M] = {index}"
            )
        gluing_images = gluing_subgroup.embedded_elements()
        if any(
            sum_form.b(left, right) != sum_form.bilinear_value_module().zero()
            for left in gluing_images
            for right in gluing_images
        ):
            raise ArithmeticError(
                f"the gluing subgroup L/M for L = {lattice} and M = Zv + v^perp, v = {vector}, "
                f"is not isotropic for the discriminant bilinear form of M"
            )
        if lattice.is_even() and any(
            sum_form.q(element) != sum_form.quadratic_value_module().zero()
            for element in gluing_images
        ):
            raise ArithmeticError(
                f"the gluing subgroup L/M for the even lattice L = {lattice} and M = Zv + v^perp, "
                f"v = {vector}, is not isotropic for the discriminant quadratic form of M"
            )

        discriminant_form = lattice.discriminant_group()
        # Restricting along i: M -> L sends the dual basis vector e^p of L^#
        # to the functional m_r |-> e^p(i m_r), the e_p-coordinate of i(m_r).
        image_coordinates = tuple(
            inclusion(generator).to_vector() for generator in sum_generators
        )
        discriminant_representatives = []
        for label in lattice.module_generating_set():
            dual_element = sum_dual.linear_combination(
                {
                    dual_label: coordinates(label)
                    for dual_label, coordinates in zip(
                        dual_labels, image_coordinates, strict=True
                    )
                    if coordinates(label)
                }
            )
            discriminant_representatives.append(sum_form.projection()(dual_element))
        discriminant_representatives = tuple(discriminant_representatives)
        if any(
            sum_form.b(representative, glued) != sum_form.bilinear_value_module().zero()
            for representative in discriminant_representatives
            for glued in gluing_images
        ):
            raise ArithmeticError(
                f"the chosen representatives of A_L for L = {lattice} do not all lie in H^perp, "
                f"where H is the gluing subgroup of M = Zv + v^perp, v = {vector}"
            )

        self.lattice = lattice
        self.vector = vector
        self.line = line
        self.complement = complement
        self.sum_lattice = sum_lattice
        self.inclusion = inclusion
        self.index = index
        self.sum_form = sum_form
        self.line_discriminant_inclusion = line_discriminant_inclusion
        self.complement_discriminant_inclusion = complement_discriminant_inclusion
        self.gluing_subgroup = gluing_subgroup
        self.gluing_images = gluing_images
        self.discriminant_form = discriminant_form
        self.discriminant_representatives = discriminant_representatives

    def representative_of(self, discriminant_class):
        r"""Return the selected representative in ``A_M`` of a class of ``A_L``."""
        discriminant_class = self.discriminant_form(discriminant_class)

        coordinates = self.discriminant_form.framing_morphism().lift(discriminant_class)
        return sum(
            (
                coordinates(label) * representative
                for label, representative in zip(
                    self.discriminant_form.module_generating_set(),
                    self.discriminant_representatives,
                    strict=True,
                )
                if label in coordinates.support()
            ),
            self.sum_form.zero(),
        )

    @cached_method
    def _representative_table(self):
        r"""Return the exact quotient lookup ``H^perp -> A_L``."""
        table = {}
        for discriminant_class in self.discriminant_form.elements():
            representative = self.representative_of(discriminant_class)
            for glued in self.gluing_images:
                element = representative + glued
                key = self.sum_form(element)
                previous = table.get(key)
                if previous is not None and previous != discriminant_class:
                    raise ArithmeticError(
                        f"the classes {previous} and {discriminant_class} of A_L for L = {self.lattice} "
                        f"give the same coset {key} of H^perp/H, so H^perp/H -> A_L is not injective"
                    )
                table[key] = discriminant_class
        expected = int(self.discriminant_form.cardinality()) * int(
            self.gluing_subgroup.cardinality()
        )
        if len(table) != expected:
            raise ArithmeticError(
                f"the representatives of A_L for L = {self.lattice} give {len(table)} elements of "
                f"H^perp, not |A_L| * |H| = {expected}"
            )
        return table

    def class_of_representative(self, element):
        r"""Return the class of ``A_L`` represented by an element of ``H^perp``."""
        key = self.sum_form(element)
        table = self._representative_table()
        if key not in table:
            raise ValueError(
                f"{element} does not lie in H^perp for L = {self.lattice}, so it represents no "
                f"class of A_L"
            )
        return table[key]

    def complement_is_definite(self) -> bool:
        r"""Return whether the orthogonal complement is definite."""
        _signature = self.complement.signature_pair()
        positive, negative = _signature.first(), _signature.second()
        return positive == 0 or negative == 0


def _isometries_between_definite_lattices(source, target):
    r"""Yield the finite ``Isom(source,target)`` torsor exactly."""
    mor = source.Isom(target)
    empty = mor.is_empty()
    if empty is True:
        return
    assert empty is False, (
        f"cannot list the isometries {source} -> {target}: whether there is any isometry was "
        f"not decided (the answer was {empty})"
    )
    first = mor.an_element()
    for automorphism in target.O():
        yield mor.act(automorphism, first)


def _definite_complement_extensions(lattice, left, right):
    r"""Return all integral extensions when the two complements are definite.

    Definite complement isometries form a finite torsor. Each member extends
    through the general nonisotropic orthogonal splitting, and its integral
    restriction exists exactly when it preserves both ambient lattices.
    """
    if left.q() != right.q():
        return ()
    if (
        lattice.module_rank() == 2
        and left.q() != 0
        and left.content() == 1
        and right.content() == 1
    ):
        from sage_extensions.categories import lattice_engines

        discriminant = lattice_engines._binary_form_discriminant(lattice)
        if discriminant > 0 and discriminant.is_square():
            orthogonal = lattice.O()
            return tuple(
                isometry
                for images in lattice_engines._split_binary_orthogonal_group_generators(lattice)
                if (isometry := orthogonal(images))(left) == right
            )
    source = VectorPrimitiveExtension(lattice, left)
    target = VectorPrimitiveExtension(lattice, right)
    if not source.complement_is_definite() or not target.complement_is_definite():
        raise ValueError(
            f"cannot list isometries of {lattice} carrying {left} to {right}: "
            "both orthogonal complements must be definite"
        )
    extensions = []
    for restriction in _isometries_between_definite_lattices(
        source.complement.inclusion().domain(),
        target.complement.inclusion().domain(),
    ):
        rational = restriction.extension_across(source.vector, target.vector)
        integral = rational.integral_restriction(lattice, lattice)
        if integral is not None:
            extensions.append(integral)
    return tuple(extensions)


def _line_isometry(source, target):
    source_line = source.line.inclusion().domain()
    target_line = target.line.inclusion().domain()
    source_vector = source.line.inclusion().lift(source.vector)
    target_vector = target.line.inclusion().lift(target.vector)
    source_coefficient = _rank_one_coefficient(source_vector)
    target_coefficient = _rank_one_coefficient(target_vector)
    target_generator = target_line.module_generators()[0]
    if source_coefficient not in (1, -1) or target_coefficient not in (1, -1):
        raise ArithmeticError(
            f"the primitive vectors {source.vector} and {target.vector} are not plus or minus "
            f"the basis vector of the lines they span: their coefficients are "
            f"{source_coefficient} and {target_coefficient}"
        )
    isometry = source_line.Isom(target_line)(
        (source_coefficient * target_coefficient * target_generator,)
    )
    if isometry(source_vector) != target_vector:
        raise ArithmeticError(
            f"the isometry {isometry} of lines does not send {source.vector} to "
            f"{target.vector}"
        )
    return isometry


def _finite_form_isometries(start):
    r"""Yield the complete finite-form isometry torsor generated from ``start``."""
    from sage_extensions.categories.modules.framed.formed.form_modules import (
        QuadraticFormModules,
    )

    source = start.domain()
    target = start.codomain()
    quadratic = (
        source in QuadraticFormModules(source.base_ring())
        and target in QuadraticFormModules(target.base_ring())
    )
    for automorphism in target.O():
        forward = automorphism.forward() * start.forward().module_morphism()
        inverse = start.inverse().forward().module_morphism() * automorphism.inverse_morphism()

        yield _torsion_form_isometry(
            forward,
            inverse,
            quadratic=quadratic,
        )


def _gluing_route_discriminant_classes(lattice, left, right):
    r"""Return the finite discriminant classes compatible with ``left -> right``.

    For the primitive extensions ``M_i=Zw_i perp w_i^perp`` this enumerates
    the full finite-form isometry torsors of the line and complement factors,
    retains exactly the assembled maps ``A_{M_1}->A_{M_2}`` carrying
    ``H_1=L/M_1`` onto ``H_2=L/M_2``, and descends them to
    ``H_1^perp/H_1 -> H_2^perp/H_2 = A_L``.

    These are the admissible classes in ``O(A_L)``.  Lifting such a class to
    an actual element of ``O(L)`` is deliberately separate: it is governed by
    the image of the discriminant representation and is not assumed here.
    """
    if not lattice.is_even():
        raise ValueError(
            f"cannot compare {left} and {right} by gluing in {lattice}: this method uses "
            f"the discriminant quadratic form, so the lattice must be even, and it is not"
        )
    source = VectorPrimitiveExtension(lattice, left)
    target = VectorPrimitiveExtension(lattice, right)
    if source.vector.q() != target.vector.q():
        return ()
    if source.complement_is_definite() or target.complement_is_definite():
        raise ValueError(
            f"cannot compare {left} and {right} by gluing in {lattice}: this method needs both "
            f"orthogonal complements to be indefinite, and at least one is definite; list the "
            f"isometries of the definite complements instead"
        )

    source_complement = source.complement.inclusion().domain()
    target_complement = target.complement.inclusion().domain()
    complement_mor = source_complement.Isom(target_complement)
    complement_empty = complement_mor.is_empty()
    if complement_empty is True:
        return ()
    assert complement_empty is False, (
        f"cannot compare {left} and {right} by gluing in {lattice}: whether their orthogonal "
        f"complements {source_complement} and {target_complement} are isometric was not "
        f"decided (the answer was {complement_empty})"
    )
    complement_start = complement_mor.an_element().discriminant_isometry()
    line_start = _line_isometry(source, target).discriminant_isometry()

    source_line_form = source.line_discriminant_inclusion.domain()
    target_line_form = target.line_discriminant_inclusion.domain()
    source_complement_form = source.complement_discriminant_inclusion.domain()
    target_complement_form = target.complement_discriminant_inclusion.domain()
    if line_start.domain() is not source_line_form or line_start.codomain() is not target_line_form:
        raise ArithmeticError(
            f"the induced isometry {line_start} of discriminant forms goes "
            f"{line_start.domain()} -> {line_start.codomain()}, not from the discriminant form "
            f"{source_line_form} of the line of {left} to that {target_line_form} of {right}"
        )
    if (
        complement_start.domain() is not source_complement_form
        or complement_start.codomain() is not target_complement_form
    ):
        raise ArithmeticError(
            f"the induced isometry {complement_start} of discriminant forms goes "
            f"{complement_start.domain()} -> {complement_start.codomain()}, not "
            f"{source_complement_form} -> {target_complement_form} between the discriminant "
            f"forms of the orthogonal complements"
        )


    source_sum_labels = tuple(source.sum_form.module_generating_set())
    target_glue = {
        target.sum_form(element)
        for element in target.gluing_images
    }
    discriminant = lattice.discriminant_group()
    classes = {}
    for line_isometry in _finite_form_isometries(line_start):
        line_images = tuple(
            target.line_discriminant_inclusion(line_isometry(generator))
            for generator in source_line_form.module_generators()
        )
        for complement_isometry in _finite_form_isometries(complement_start):
            complement_images = tuple(
                target.complement_discriminant_inclusion(
                    complement_isometry(generator)
                )
                for generator in source_complement_form.module_generators()
            )
            images = {
                label: image
                for label, image in zip(
                    source_sum_labels,
                    line_images + complement_images,
                    strict=True,
                )
            }
            assembled = source.sum_form.Mono(target.sum_form)(
                images,
                quadratic=True,
            )
            assembled_glue = {
                target.sum_form(assembled(glued))
                for glued in source.gluing_images
            }
            if assembled_glue != target_glue:
                continue
            descended_images = {
                label: target.class_of_representative(
                    assembled(
                        source.representative_of(
                            discriminant.module_generator(label)
                        )
                    )
                )
                for label in discriminant.module_generating_set()
            }
            descended = discriminant.module_category().Mor(discriminant, discriminant)(descended_images)
            descended_isometry = _torsion_form_isometry(descended, descended.inverse(), quadratic=True)
            automorphism = discriminant.O().from_morphism(descended_isometry)
            classes[automorphism] = automorphism
    return tuple(classes.values())


def _stable_complement_root_reflections(lattice, element):
    r"""Return root reflections of ``element^perp`` that lie in ``ker(rho_L)``.

    For an indefinite complement, one representative of each ``O(element^perp)``
    orbit of roots of square ``+2`` and ``-2`` is obtained through the exact
    vector-orbit backend.  Each representative is embedded back into ``L`` and
    reflected there; only reflections acting trivially on ``A_L`` are retained.
    The result is a finite family inside the stable stabilizer of ``element``,
    not a claim to generate that stabilizer.
    """
    extension = VectorPrimitiveExtension(lattice, element)
    if extension.complement_is_definite():
        raise ValueError(
            f"cannot list root reflections of the orthogonal complement of {element} in "
            f"{lattice}: the complement must be indefinite, and it is definite"
        )
    complement = extension.complement.inclusion().domain()
    inclusion = extension.complement.inclusion()
    stable = lattice.stable_orthogonal_group()
    reflections = []
    for square in (lattice.base_ring()(2), lattice.base_ring()(-2)):
        for root in complement.O().vector_orbit_representatives(square):
            embedded_root = inclusion(root)
            reflection = lattice.reflection(embedded_root)
            if reflection(extension.vector) != extension.vector:
                raise ArithmeticError(
                    f"the reflection in {embedded_root}, a root of the orthogonal complement of "
                    f"{extension.vector}, does not fix {extension.vector}"
                )
            if reflection in stable:
                reflections.append(reflection)
    return tuple(reflections)


__all__ = [
    "VectorPrimitiveExtension",
]
