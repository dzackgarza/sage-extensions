"""Exact inertia of rooted and unrooted Coxeter diagrams."""

from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams


def test_coxeter_inertia_congruence():
    for cartan, expected in ((["A", 2], (2, 0, 0)), (["A", 3], (3, 0, 0)), (["A", 4], (4, 0, 0)), (["D", 4], (4, 0, 0))):
        for rooted in (False, True):
            diagram = CoxeterDiagrams().from_cartan_type(cartan, rooted=rooted)
            assert tuple(int(x) for x in diagram._inertia_counts()) == expected
