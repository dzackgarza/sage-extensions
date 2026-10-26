r"""The universal invertible quotient on ``Proj Sym(V)`` (Stacks, Tag 01OA)."""

from sage_extensions.all import *


def test_rank_two_projectivization_has_its_tautological_invertible_sheaf():
    vector_space = QQ.free_module(("s", "t"))
    family = vector_space.projectivization()
    total = family.arrow().domain()
    line_bundle = total.tautological_line_bundle()

    assert line_bundle in QuasiCoherentSheaves(total).Invertible()
    assert all(
        line_bundle.local_module(index).module_rank() == 1
        for index in line_bundle.chart_indices()
    )
    assert line_bundle.open_sections_presheaf().domain() is PresheafObjects(total).site().opposite()
    assert total.universal_quotient().is_surjective()
