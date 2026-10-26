r"""Refining the standard atlas of ``P^1`` by the redundant chart ``U_0 ∩ U_1``.

``P^1_QQ = U_0 ∪ U_1`` with ``U_0 = Spec QQ[t]``, ``U_1 = Spec QQ[1/t]``.  Adding
``U_{01} = U_0 ∩ U_1`` as a third chart gives an affine cover refining the
standard one (send ``U_{01}`` to ``U_0``).  On a separated scheme Čech cohomology
of a quasi-coherent sheaf on any affine cover is sheaf cohomology (Hartshorne
III.4.5), so both atlases give ``H^0(O) = QQ`` and ``H^1(O) = 0``
(Hartshorne III.5.1).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _standard_and_redundant_atlases():
    P1 = Schemes(QQ).projective_space(1)
    U0, U1 = P1.standard_affine_charts()
    U01 = P1.standard_chart_overlap(0, 1)
    coarse = P1.affine_cover((U0, U1))
    fine = P1.affine_cover((U0, U1, U01))
    return P1, coarse, fine


def test_the_redundant_atlas_refines_the_standard_atlas_and_computes_the_same_cech_cohomology_of_o() -> None:
    r"""``Ȟ^0(O) = QQ`` and ``Ȟ^1(O) = 0`` on both the standard and the refined atlas of ``P^1``."""
    P1, coarse, fine = _standard_and_redundant_atlases()
    O = P1.structure_sheaf()

    assert fine.refines(coarse)
    assert coarse.refines(fine)
    for cover in (coarse, fine):
        assert O.cech_cohomology(cover, 0).dimension() == 1
        assert O.cech_cohomology(cover, 1).dimension() == 0


def test_a_line_bundle_pulled_back_to_the_refined_atlas_keeps_its_cohomology() -> None:
    r"""The bundle with transition ``e_0 = t e_1`` is ``O(-1)``: ``h^0 = h^1 = 0`` on either atlas.

    Its refined transition functions are the pullbacks along the refinement:
    ``g_{01} = t``, ``g_{02} = 1`` (``U_{01}`` is sent to ``U_0``), and
    ``g_{12} = g_{10} = t^{-1}``.  Hartshorne III.5.1 gives ``H^i(P^1, O(-1)) = 0``.
    """
    P1, coarse, fine = _standard_and_redundant_atlases()
    t = P1.standard_chart_overlap(0, 1).coordinate_ring().gen()
    L = P1.line_bundle({(0, 1): t}, cover=coarse)
    refined = L.transition_functions(fine)

    assert refined[(0, 1)] == t
    assert refined[(0, 2)] == 1
    assert refined[(1, 2)] == t**-1
    for cover in (coarse, fine):
        assert L.cech_cohomology(cover, 0).dimension() == 0
        assert L.cech_cohomology(cover, 1).dimension() == 0
