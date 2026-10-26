r"""Native primitive embeddings by finite discriminant gluing and genera.

This is the construction of OSCAR's pinned ``primitive_embeddings``
(``QuadFormAndIsom/embeddings.jl``, ``d135b70b``, lines 1914--2239).
An embedding into a unimodular target is obtained by gluing the source to
a complement with opposite discriminant form.  For a general target L,
first glue M to T = -L, then glue the resulting V to a complement in a
unimodular lattice W, and take T^perp in W.  Every lattice and every
inclusion in these two steps is retained as an owned mathematical object.

The finite gluing families are enumerated in full.  Their duplicate
embeddings are identified using the actual images of the orthogonal
groups on the discriminant forms of the source and complement.
"""

from sage_extensions.categories._lattice import signature_pair
from sage_extensions.categories.lattice_extensions import (
    _orthogonal_sum_embeddings,
    _primitive_extensions,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set


def _embedding_glue_data(embedding):
    r"""Return the complement and ``L/(M + M^perp)`` in its two discriminant factors."""
    source = embedding.domain()
    complement = embedding.orthogonal_complement()
    total, source_inclusion, complement_inclusion = _orthogonal_sum_embeddings(
        source, complement
    )
    combined = total.from_summands(embedding, complement.inclusion())
    extension = total.Emb(embedding.codomain())(
        lambda label: combined(total.module_generator(label))
    )
    source_discriminant = source_inclusion.discriminant_inclusion()
    complement_discriminant = complement_inclusion.discriminant_inclusion()
    product = Modules(source.base_ring()).biproduct((
        source_discriminant.domain(), complement_discriminant.domain()
    ))
    split = product.from_summands(
        source_discriminant.module_morphism(),
        complement_discriminant.module_morphism(),
    ).inverse()
    first = product.left_projection() * split
    second = product.right_projection() * split
    glue = extension.gluing_subgroup().inclusion()
    return complement, tuple(
        (first(glue(element)), second(glue(element)))
        for element in glue.domain().elements()
    )


def _primitive_embeddings_equivalent(left, right, classification):
    r"""Decide equality of primitive-embedding classes by their finite glue.

    An isometry of the complements extends over the two primitive
    extensions precisely when its discriminant action, together with
    the selected source action, carries one glue subgroup to the other.
    For ``emb`` the source is fixed pointwise.  For ``sub`` its full
    arithmetic discriminant image acts.  Every finite action used here
    has an actual arithmetic lift by the definition of that image.
    """
    source = left.domain()
    if all(left(vector) == right(vector) for vector in source.module_generators()):
        return True
    left_complement, left_glue = _embedding_glue_data(left)
    right_complement, right_glue = _embedding_glue_data(right)
    if len(left_glue) != len(right_glue):
        return False
    isometries = left_complement.Isom(right_complement)
    empty = isometries.is_empty()
    if empty is True:
        return False
    assert empty is False, (
        f"whether the complements of {left} and {right} are isometric "
        "must be decided before comparing their primitive-embedding classes"
    )
    start = isometries.an_element().discriminant_isometry()
    source_actions = (
        (source.discriminant_group().orthogonal_group().one(),)
        if classification == "emb"
        else source.discriminant_image()
    )
    complement_actions = right_complement.discriminant_image()
    target_glue = set(right_glue)
    for source_action in source_actions:
        for complement_action in complement_actions:
            moved_glue = {
                (source_action(first), complement_action(start(second)))
                for first, second in left_glue
            }
            if moved_glue == target_glue:
                return True
    return False


def _primitive_embedding_class_representatives(embeddings, classification):
    r"""Compute the pinned genus/gluing construction in the specified target."""
    source = embeddings.domain()
    target = embeddings.codomain()
    source_rank = int(source.module_rank())
    target_rank = int(target.module_rank())
    source_signature = source.signature_pair()
    target_signature = target.signature_pair()
    positive = int(target_signature.first()) - int(source_signature.first())
    negative = int(target_signature.second()) - int(source_signature.second())
    if positive < 0 or negative < 0 or (target.is_even() and not source.is_even()):
        return finite_ordered_set(())
    if source_rank == 0:
        return finite_ordered_set((embeddings(lambda _label: target.zero()),))
    if source_rank == target_rank:
        isometries = source.Isom(target)
        empty = isometries.is_empty()
        if empty is True:
            return finite_ordered_set(())
        assert empty is False, f"whether {source} and {target} are isometric must be decided"
        isometry = isometries.an_element()
        return finite_ordered_set((embeddings(
            lambda label: isometry(source.module_generator(label))
        ),))

    if not target.is_even():
        # Common scaling changes neither the integral maps preserving the
        # forms nor primitivity.  It reduces the odd case to the same even
        # discriminant-gluing construction, retaining the original marking.
        even_source = source.twist(source.base_ring()(2))
        even_target = target.twist(target.base_ring()(2))
        representatives = _primitive_embedding_class_representatives(
            even_source.Emb(even_target), classification
        )
        return finite_ordered_set(tuple(
            embeddings({
                label: target(representative(even_source(source.module_generator(label))))
                for label in source.module_generating_set()
            })
            for representative in representatives
        ))

    complement_signature = signature_pair(positive, negative)
    lattices = source.lattice_category()
    representatives = []

    def accept(candidate):
        candidate_target = candidate.codomain()
        isometries = candidate_target.Isom(target)
        empty = isometries.is_empty()
        if empty is True:
            return
        assert empty is False, (
            f"whether the glued target {candidate_target} is isometric to "
            f"the prescribed target {target} must be decided"
        )
        witness = isometries.an_element()
        realized = embeddings({
            label: witness(candidate(source.module_generator(label)))
            for label in source.module_generating_set()
        })
        if not any(
            _primitive_embeddings_equivalent(realized, previous, classification)
            for previous in representatives
        ):
            representatives.append(realized)

    def complements(form):
        opposite_form = form.twist(-source.base_ring().one())
        if not opposite_form.is_discriminant_form_of_even_lattice(complement_signature):
            return ()
        return lattices.genus(complement_signature, opposite_form).representatives()

    if target.is_unimodular():
        # Pinned _primitive_embeddings_in_unimodular_safe: the complement
        # genus is fixed by its signature and -q_M.
        for complement in complements(source.discriminant_group()):
            for source_inclusion, _complement_inclusion in _primitive_extensions(
                source, complement, unimodular=True
            ):
                accept(source_inclusion)
        return finite_ordered_set(tuple(representatives))

    # Pinned _primitive_embeddings_generic_safe and _step_2_primitive_embeddings.
    # Taking T = -L, any desired embedding M -> L occurs in the canonical
    # unimodular gluing of L + (-L): the saturation of M + T is one of the
    # V's enumerated here, and its perpendicular has the stated genus.
    opposite_target = target.twist(-target.base_ring().one())
    for source_inclusion, opposite_inclusion in _primitive_extensions(source, opposite_target):
        intermediate = source_inclusion.codomain()
        for complement in complements(intermediate.discriminant_group()):
            for intermediate_inclusion, _complement_inclusion in _primitive_extensions(
                intermediate, complement, unimodular=True
            ):
                unimodular = intermediate_inclusion.codomain()
                opposite_into_unimodular = opposite_target.Emb(unimodular)(
                    lambda label: intermediate_inclusion(
                        opposite_inclusion(opposite_target.module_generator(label))
                    )
                )
                candidate_target = opposite_into_unimodular.orthogonal_complement()
                into_unimodular = candidate_target.inclusion()
                candidate = source.Emb(candidate_target)({
                    label: into_unimodular.lift(intermediate_inclusion(
                        source_inclusion(source.module_generator(label))
                    ))
                    for label in source.module_generating_set()
                })
                accept(candidate)
    return finite_ordered_set(tuple(representatives))
