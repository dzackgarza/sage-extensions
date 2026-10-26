r"""Scheme-facing ingress for finite covering families of locally ringed spaces.

The mathematical object is owned by :class:`CoveringFamilies`.  This module
only translates the convenient chart/embedding/overlap input used by locally
ringed spaces into arrows of the slice over the covered space.  It deliberately
defines no second covering-family, overlap, or refinement record.
"""

from collections.abc import Mapping
from itertools import combinations

from sage.categories.morphism import Morphism

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.abstract_categories.presheaves import (
    CoveringFamilies,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    finite_indexed_family,
)


def _family(values, *, index_set=None, name):
    r"""Read finite chart data without changing its supplied labels."""

    match values:
        case IndexedFamily():
            if values.cardinality().is_finite() is not True:
                raise TypeError(
                    f"{name} must be a finite family, but {values} has cardinality {values.cardinality()}"
                )
            match index_set:
                case None:
                    return values
                case _:
                    entries = {index: values[index] for index in index_set}
        case Mapping():
            match index_set:
                case None:
                    index_set = finite_ordered_set(tuple(values))
                case _:
                    pass
            if set(values) != set(index_set):
                raise ValueError(
                    f"{name} must be indexed by the charts {sorted(map(str, index_set))}, but its "
                    f"keys are {sorted(map(str, values))}"
                )
            entries = dict(values)
        case _:
            sequence = tuple(values)
            match index_set:
                case None:
                    index_set = finite_ordered_set(range(len(sequence)))
                case _:
                    pass
            if len(sequence) != int(index_set.cardinality().finite_value()):
                raise ValueError(
                    f"{name} must have one entry for each of the {index_set.cardinality()} charts, "
                    f"but it has {len(sequence)}"
                )
            entries = {
                index: sequence[position]
                for position, index in enumerate(index_set)
            }
    return finite_indexed_family(index_set, entries.__getitem__, name=name)


def _ringed_covering_family(
    ambient_space,
    site_category,
    charts,
    embeddings,
    overlaps,
    *,
    ambient_chart_index,
):
    r"""Build a certified cover as a covering family in ``LRS/X``.

    The presently represented certificate is the deliberately small exact one
    already used by the public ingress: one selected chart is literally ``X``
    and its embedding is ``id_X``.  Every chart and overlap is then placed in
    the slice before the family is built by :class:`CoveringFamilies`.
    """

    if site_category.base_object() is not ambient_space:
        raise ValueError(
            f"a covering family of {ambient_space} must be built in the slice category over "
            f"{ambient_space}, but {site_category} is the slice over {site_category.base_object()}"
        )
    chart_family = _family(charts, name="Charts of a ringed covering family")
    embedding_family = _family(
        embeddings,
        index_set=chart_family.index_set(),
        name="Chart embeddings of a ringed covering family",
    )
    ambient_index = chart_family.index_set()(ambient_chart_index)
    for index in chart_family.index_set():
        embedding = embedding_family[index]
        if not isinstance(embedding, (Morphism, CategoricalArrow)):
            raise TypeError(
                f"the embedding of chart {index} into {ambient_space} must be a morphism of ringed "
                f"spaces, but it is {embedding}"
            )
        if embedding.domain() is not chart_family[index] or embedding.codomain() is not ambient_space:
            raise ValueError(
                f"the embedding of chart {index} must be a morphism {chart_family[index]} -> "
                f"{ambient_space}, but it is {embedding.domain()} -> {embedding.codomain()}"
            )
    if chart_family[ambient_index] is not ambient_space:
        raise ValueError(
            f"a cover is recognized as covering only when one chart is the whole space "
            f"{ambient_space}, but chart {ambient_index} is {chart_family[ambient_index]}"
        )
    if embedding_family[ambient_index] != ambient_space.categorical_identity_morphism():
        raise ValueError(
            f"chart {ambient_index} is the whole space {ambient_space}, so its embedding must be "
            f"the identity, but it is {embedding_family[ambient_index]}"
        )

    target = site_category.an_object()
    chart_objects = finite_indexed_family(
        chart_family.index_set(),
        lambda index: site_category.object(embedding_family[index]),
        name="Covering charts in the ambient slice",
    )
    members = finite_indexed_family(
        chart_family.index_set(),
        lambda index: site_category.Mor(chart_objects[index], target)(embedding_family[index]),
        name="Cover arrows in the ambient slice",
    )

    ranking = chart_family.index_set().ranking_map()
    expected_pairs = tuple(combinations(tuple(chart_family.index_set()), 2))
    normalized = {}
    for raw_pair, datum in dict(overlaps).items():
        left, right = raw_pair
        left = chart_family.index_set()(left)
        right = chart_family.index_set()(right)
        match ranking(left) < ranking(right):
            case True:
                normalized[left, right] = datum
            case False:
                normalized[right, left] = (datum[0], datum[2], datum[1])
    if set(normalized) != set(expected_pairs):
        raise ValueError(
            f"a covering family of {ambient_space} needs one overlap for each pair of charts "
            f"{[tuple(map(str, pair)) for pair in expected_pairs]}, but overlaps were given for "
            f"{[tuple(map(str, pair)) for pair in normalized]}"
        )

    overlap_data = {}
    for left, right in expected_pairs:
        overlap_space, left_map, right_map = normalized[left, right]
        if not isinstance(left_map, (Morphism, CategoricalArrow)) or not isinstance(right_map, (Morphism, CategoricalArrow)):
            raise TypeError(
                f"the overlap of charts {left} and {right} must be given by morphisms of ringed "
                f"spaces into each chart, but it is given by {left_map} and {right_map}"
            )
        if left_map.domain() is not overlap_space or right_map.domain() is not overlap_space:
            raise ValueError(
                f"both maps from the overlap {overlap_space} of charts {left} and {right} must "
                f"start at it, but they start at {left_map.domain()} and {right_map.domain()}"
            )
        if left_map.codomain() is not chart_family[left] or right_map.codomain() is not chart_family[right]:
            raise ValueError(
                f"the overlap of charts {left} and {right} must map into {chart_family[left]} and "
                f"{chart_family[right]}, but its maps land in {left_map.codomain()} and "
                f"{right_map.codomain()}"
            )
        left_to_ambient = embedding_family[left] * left_map
        right_to_ambient = embedding_family[right] * right_map
        if left_to_ambient != right_to_ambient:
            raise ValueError(
                f"the overlap {overlap_space} of charts {left} and {right} maps to {ambient_space} "
                f"in two different ways through the two charts: {left_to_ambient} and {right_to_ambient}"
            )
        overlap_object = site_category.object(left_to_ambient)
        overlap_data[left, right] = site_category.span(
            site_category.Mor(overlap_object, chart_objects[left])(left_map),
            site_category.Mor(overlap_object, chart_objects[right])(right_map),
        )

    return CoveringFamilies(site_category).family(target, members, overlap_data)


__all__ = []
