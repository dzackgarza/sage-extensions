r"""Relative spectra of represented quasi-coherent algebra descent data.

On an affine cover ``U_i = Spec(A_i)`` of ``X`` an algebra sheaf is given by
finitely presented ``A_i``-algebras ``B_i`` with compatible overlap
isomorphisms over the restrictions ``B_i tensor_{A_i} A_ij``.  Its relative
spectrum is obtained by gluing ``Spec(B_i)``.  Over ``U_ij = D(f)`` the
preimage of the overlap in ``Spec(B_i)`` is the distinguished open ``D(g)``
for ``g`` the image of ``f`` under ``A_i -> B_i``, and
``B_i tensor_{A_i} (A_i)_f = (B_i)_g``: both are universal among maps out of
``B_i`` inverting ``g``.  The relative spectrum glues along those distinguished
opens, and it transports the descent datum's overlap isomorphisms through that
canonical comparison.

Each descent-data owner supplies its own cover presentation.  An affine
scheme can also have a finite affine atlas; its being affine does not choose
a distinguished-cover representation for data stated on that atlas.
"""

from itertools import combinations

from sage_extensions.categories.rings.ring_foundation import OwnedRings

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.schemes.schemes import (
    Schemes,
    _affine_morphism_from_pullback,
)


def _semilinear_scalar_extension_map(source, target, scalar_map):
    r"""Return the canonical semilinear map ``B -> B tensor_A A'`` into one represented scalar extension."""
    from sage_extensions.categories.schemes.gluing import (
        SemilinearAlgebraMorphism,
    )

    return SemilinearAlgebraMorphism(
        source,
        target,
        scalar_map,
        {
            label: target.algebra_generator(label)
            for label in source.algebra_generating_set()
        },
    )


def _cover_overlap_presentation(datum, source_index, target_index):
    r"""``(B_i tensor A_ij, A_i -> A_ij, f)`` over ``D(f_i) cap D(f_j)`` of a distinguished affine cover.

    ``f`` is ``f_j`` read in ``A_i``: on ``D(f_i)`` the element ``f_i`` is a
    unit, so ``D(f_i f_j) = D(f_j)`` there.
    """
    cover = datum.cover()
    source_base = cover.open(source_index).coordinate_algebra()
    return (
        datum.restricted_algebra(source_index, source_index, target_index),
        cover.structure_sheaf_restriction(source_index, target_index),
        source_base.localization_map()(cover.defining_element(target_index)),
    )


def _atlas_overlap_presentation(datum, source_index, target_index):
    r"""``(B_i tensor A_ij, A_i -> A_ij, f)`` over the overlap ``U_ij = D(f)`` of a glued base."""
    atlas = datum.gluing_datum()
    base_overlap = atlas.overlap(source_index, target_index)
    return (
        datum.pair_algebra(source_index, target_index),
        base_overlap.inclusion().coordinate_algebra_morphism(),
        atlas.chart(source_index).coordinate_algebra()(base_overlap.distinguished_open_element()),
    )


def _scalar_extension(datum, presentation, source_index, target_index):
    r"""``B_i -> B_i tensor_{A_i} A_ij``, the scalar extension map onto the restricted algebra."""
    restricted, base_restriction, _ = presentation(datum, source_index, target_index)
    return _semilinear_scalar_extension_map(datum.local_algebra(source_index), restricted, base_restriction)


@cached_function(key=lambda datum, presentation, source_index, target_index: (id(datum), presentation, source_index, target_index))
def _relative_overlap(datum, presentation, source_index, target_index):
    r"""``D(g) <= Spec(B_i)``, the preimage of the base overlap ``D(f) <= U_i``, with ``g`` the image of ``f``."""
    local = datum.local_algebra(source_index)
    _, _, base_element = presentation(datum, source_index, target_index)
    return local.affine_spectrum(base_ring=datum.scheme().scheme_base_ring()).distinguished_open(local.algebra_structure_morphism()(base_element))


def _overlap_comparison(datum, presentation, source_index, target_index):
    r"""``B_i tensor_{A_i} A_ij -> (B_i)_g``, the canonical isomorphism of the two restrictions.

    It is the factor of the localization map ``B_i -> (B_i)_g`` through the
    scalar extension, which exists because ``f`` maps to the unit ``g``.
    """
    overlap = _relative_overlap(datum, presentation, source_index, target_index)
    return _scalar_extension(datum, presentation, source_index, target_index).induced_morphism(
        overlap.inclusion().coordinate_algebra_morphism()
    )


def _overlap_pullback(datum, presentation, pullback_of, source_index, target_index):
    r"""``(B_j)_{g_j} -> (B_i)_{g_i}``, the descent datum's overlap isomorphism read on the distinguished opens.

    ``pullback_of(i, j)`` maps ``B_j tensor A_ji`` to ``B_i tensor A_ij``.  Its
    composite with the scalar extension out of ``B_j`` and the comparison into
    ``(B_i)_{g_i}`` inverts ``g_j``, so the universal property of
    ``(B_j)_{g_j}`` extends it uniquely.
    """
    source_algebra = _relative_overlap(datum, presentation, source_index, target_index).coordinate_algebra()
    target_local = datum.local_algebra(target_index)
    comparison = _overlap_comparison(datum, presentation, source_index, target_index)
    extension = _scalar_extension(datum, presentation, target_index, source_index)
    transition = pullback_of(source_index, target_index)
    into_source = OwnedRings().Mor(target_local, source_algebra)(
        lambda element: comparison(transition(extension(element))),
    )
    return _relative_overlap(datum, presentation, target_index, source_index).coordinate_algebra().induced_morphism(into_source)


def _relative_transition(datum, presentation, pullback_of, left_index, right_index):
    r"""The overlap isomorphism ``D(g_ij) -> D(g_ji)`` in the core of ``Sch/R``."""
    schemes = Schemes(datum.scheme().scheme_base_ring())

    def morphism(source_index, target_index):
        return schemes.Mor(
            _relative_overlap(datum, presentation, source_index, target_index),
            _relative_overlap(datum, presentation, target_index, source_index),
        )(_overlap_pullback(datum, presentation, pullback_of, source_index, target_index))

    forward = morphism(left_index, right_index)
    inverse = morphism(right_index, left_index)
    return schemes.Core().Mor(forward.domain(), forward.codomain())(forward, inverse)


def _glued_relative_spectrum(
    datum,
    indices,
    pair_indices,
    base_chart,
    base_chart_embedding,
    presentation,
    pullback_of,
    *,
    _engine=None,
    construction_data=None,
):
    r"""Glue ``Spec(B_i)`` and return ``Spec_X(B) -> X`` in the slice over ``X``."""
    base_scheme = datum.scheme()
    base_ring = base_scheme.scheme_base_ring()
    charts = {index: datum.local_algebra(index).affine_spectrum(base_ring=base_ring) for index in indices}
    transitions = {
        (left, right): _relative_transition(datum, presentation, pullback_of, left, right)
        for left, right in pair_indices
    }
    glued = Schemes(base_ring).glue_affine_atlas(
        charts,
        transitions,
        _object_engine=_engine,
        **dict(construction_data or {}),
    )
    local_maps = {
        index: base_chart_embedding(index)
        * _affine_morphism_from_pullback(
            charts[index],
            base_chart(index),
            datum.local_algebra(index).algebra_structure_morphism(),
        )
        for index in indices
    }
    structure = glued.Mor(base_scheme)(local_maps)
    atlas = glued.gluing_datum()
    assert all(structure * atlas.chart_embedding(index) == local_maps[index] for index in indices), (
        f"the structure morphism {structure} of the relative spectrum over {base_scheme} does "
        "not restrict on each affine chart to Spec of that chart's algebra structure map"
    )
    return glued.scheme_category().SliceOver(base_scheme)(structure)


@cached_function(key=lambda datum: id(datum))
def _relative_spectrum(datum, *, _engine=None, construction_data=None):
    r"""``Spec_X(A)`` for algebra data on a distinguished affine cover."""
    cover = datum.cover()
    indices = tuple(cover.atlas())
    return _glued_relative_spectrum(
        datum, indices, tuple(combinations(indices, 2)),
        cover.open, lambda index: cover.open(index).inclusion(),
        _cover_overlap_presentation,
        lambda source, target: datum.transition(source, target).inverse(),
        _engine=_engine,
        construction_data=construction_data,
    )


@cached_function(key=lambda datum: id(datum))
def _finite_atlas_relative_spectrum(datum, *, _engine=None, construction_data=None):
    r"""``Spec_X(A)`` for algebra data on a finite affine atlas of any scheme."""
    atlas = datum.gluing_datum()
    return _glued_relative_spectrum(
        datum, tuple(atlas.chart_indices()), tuple(atlas.transition_index_set()),
        atlas.chart, atlas.chart_embedding, _atlas_overlap_presentation,
        lambda source, target: datum.transition(source, target).pullback(),
        _engine=_engine,
        construction_data=construction_data,
    )


def _relative_spectrum_morphism(morphism):
    r"""Return ``Spec(target) -> Spec(source)`` for an algebra-descent morphism."""
    source_relative = morphism.domain().relative_spectrum()
    target_relative = morphism.codomain().relative_spectrum()
    source_scheme = source_relative.arrow().domain()
    target_scheme = target_relative.arrow().domain()
    source_atlas = source_scheme.gluing_datum()
    target_atlas = target_scheme.gluing_datum()
    local_maps = {
        index: source_atlas.chart_embedding(index)
        * _affine_morphism_from_pullback(
            target_atlas.chart(index),
            source_atlas.chart(index),
            morphism.local_map(index),
        )
        for index in morphism.cover().atlas()
    }
    induced = target_scheme.Mor(source_scheme)(local_maps)
    assert source_relative.arrow() * induced == target_relative.arrow(), (
        f"the morphism {induced} of relative spectra induced by {morphism} is not a morphism "
        f"over the base scheme: it does not commute with the structure morphisms to "
        f"{source_relative.arrow().codomain()}"
    )
    return induced


__all__ = []
