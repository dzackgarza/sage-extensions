r"""The cusp reduction of the even unimodular Lorentzian lattice $E_{10}$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_isotropic_reduction_of_e10_at_a_primitive_isotropic_vector_is_e8() -> None:
    r"""$E_{10} \cong U \oplus E_8$, and for primitive isotropic $e \in U$,
    $e^\perp/\mathbf{Z}e \cong E_8$: it is even unimodular definite of rank 8
    (Conway--Sloane, *SPLAG*, ch. 16 and ch. 26).
    """
    lattice = NamedLattices.U + NamedLattices.E8
    isotropic = next(v for v in lattice.module_generators() if v.is_isotropic())

    assert lattice.is_isometric(NamedLattices.E10)
    reduction = isotropic.isotropic_reduction()
    assert reduction.module_rank() == 8
    assert reduction.is_isometric(NamedLattices.E8)
