r"""A distinguished affine cover exposes its chart metadata, Čech cover, restrictions, and gluing."""

from sage_extensions.all import *  # noqa: F401,F403


def _line_cover():
    ring = QQ["x"]
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    return ring, x, line, line.distinguished_open_cover(x, ring.one() - x)


def test_cover_chart_metadata_overlap_and_cech_family() -> None:
    ring, x, line, cover = _line_cover()
    atlas = cover.atlas()
    overlap = cover.overlap(0, 1)
    indices = cover.intersection_indices(1, 0, 1)
    site = cover.cech_site()
    family = cover.cech_covering_family()
    coverage = cover.cech_coverage()
    restriction = cover.structure_sheaf_restriction(0, 1)

    assert atlas.cardinality() == cardinal(2)
    assert cover.chart_position(cover.chart_label(0)) == 0
    assert cover.chart_position(cover.chart_label(1)) == 1
    assert cover.defining_element(0) == x
    assert cover.defining_element(1) == ring.one() - x
    assert cover.opens().cardinality() == cardinal(2)
    assert indices.cardinality() == cardinal(2)
    assert overlap is cover.intersection(0, 1)
    assert family.site_category() is site
    assert family.covered_object() == site(())
    assert family.members().cardinality() == cardinal(2)
    assert family.overlaps().cardinality() == cardinal(1)
    assert coverage.site_category() is site
    assert restriction.domain() is cover.open(0).coordinate_algebra()
    assert restriction.codomain() is overlap.coordinate_algebra()


def test_cover_restricts_and_glues_modules() -> None:
    _ring, x, line, cover = _line_cover()
    left, right = cover.opens()
    left_module = left.coordinate_ring().free_module(("e",))
    right_module = right.coordinate_ring().free_module(("e",))
    left_overlap = cover.restrict_module(left_module, 0, 1)
    right_overlap = cover.restrict_module(right_module, 1, 0)
    x_on_overlap = line.structure_sheaf().restriction_map(
        line,
        cover.overlap(0, 1),
    )(x)
    transition = left_overlap.Mor(right_overlap)(
        {"e": x_on_overlap * right_overlap.module_generator("e")}
    )
    sheaf = cover.glue_modules(
        (left_module, right_module),
        {(0, 1): transition},
    )

    assert left_overlap.base_ring() is cover.overlap(0, 1).coordinate_algebra()
    assert right_overlap.base_ring() is cover.overlap(0, 1).coordinate_algebra()
    assert sheaf in ModuleSheaves(line)


def test_cover_restricts_and_glues_polynomial_algebras() -> None:
    _ring, _x, line, cover = _line_cover()
    local_algebras = tuple(
        open_.coordinate_ring().polynomial_ring("z")
        for open_ in cover.opens()
    )
    left = cover.restrict_algebra(local_algebras[0], 0, 1)
    right = cover.restrict_algebra(local_algebras[1], 1, 0)
    transition = left.Mor(right)(
        {"z": right.algebra_generator("z")}
    )
    sheaf = cover.glue_algebras(
        local_algebras,
        {(0, 1): transition},
    )

    assert left.base_ring() is cover.overlap(0, 1).coordinate_algebra()
    assert right.base_ring() is cover.overlap(0, 1).coordinate_algebra()
    assert sheaf in AlgebraSheaves(line)
