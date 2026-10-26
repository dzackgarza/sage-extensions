r"""The three verification milestones of the indefinite orbit program.

Each milestone fixes a lattice and asks for the orbit data of one Witt index.

Milestone 1, ``h = 1``: ``E10 = U + E8``, the even unimodular Lorentzian
lattice ``II_{1,9}`` (Conway--Sloane, *Sphere Packings, Lattices and Groups*,
ch. 26).  Its single cusp, the reduction ``e^perp/e = E8`` and the Eichler
transvections of the unipotent radical are asserted in
``test_cusp_lattices.py`` and ``test_parabolic_induction.py``; what is added
here is the Levi half of ``1 -> U_I -> P_I -> M_I -> 1``, namely that the
cusp stabilizer acts nontrivially on the reduction.  That action is onto
``O(E8)``, which is a theorem and not something a method body establishes.

Milestone 2, ``h = 2``: ``N = U + U(2) + E8(-2)``, the anti-invariant lattice
of the Enriques involution, whose isotropic lines and planes are the zero- and
one-dimensional boundary components of the Enriques period space
(Dutour Sikiric--Hulek, arXiv:2302.01679, classify the arithmetic subgroups
acting on it).  The incidence between the two ranks is the Tits building.

Milestone 3, equivariant: the K3 lattice ``Lambda = 3U + 2E8(-1)`` with the
Enriques involution.  The invariant and anti-invariant decomposition, the
gluing subgroup and the index ``2^10`` are asserted in
``test_centralizer_gluing.py``; what is added here is the intersection of the
centralizer ``O(Lambda, iota)`` with the stabilizer of a polarization, which
is the group acting on the polarized period domain.
"""

from sage_extensions.all import *


def test_milestone_one_the_E10_cusp_acts_on_its_reduction_lattice() -> None:
    lattice = NamedLattices.E10
    cusp = lattice.cusps()[0]
    line = cusp.representative()
    quotient = line.isotropic_quotient()
    assert quotient.module_rank() == 8

    descents = tuple(
        line.levi_quotient_action(generator)
        for generator in cusp.stabilizer_generators()
    )
    assert descents
    assert all(
        descent.domain() is quotient and descent.codomain() is quotient
        for descent in descents
    )

    # P_I -> O(E8) is onto, so the stabilizer generators cannot all descend to
    # the identity: a group acting trivially on the reduction could not cover
    # a group of order 696729600.
    assert any(
        any(
            descent(generator) != generator
            for generator in quotient.module_generators()
        )
        for descent in descents
    )


def test_the_enriques_lattice_has_two_line_cusps_and_nine_plane_cusps() -> None:
    r"""For \(N=U\oplus U(2)\oplus E_8(-2)\), \(O(N)\) has 2 orbits of primitive
    isotropic lines and 9 of primitive isotropic planes (Sterk, *Compactifications of
    the period space of Enriques surfaces I*, Math. Z. 207 (1991), 1--36).  The
    reductions \(I^\perp/I\) have rank \(12-2\cdot 1=10\) and \(12-2\cdot 2=8\).
    """
    lattice = NamedLattices.TEn
    line_cusps = lattice.cusps(1)
    plane_cusps = lattice.cusps(2)

    assert line_cusps.cardinality() == 2
    assert plane_cusps.cardinality() == 9
    assert all(cusp.reduction_lattice().module_rank() == 10 for cusp in line_cusps)
    assert all(cusp.reduction_lattice().module_rank() == 8 for cusp in plane_cusps)
