from sage_extensions.all import *


def test_the_split_fibre_of_issue_407_is_one_orthogonal_orbit() -> None:
    r"""On $L = \langle 2\rangle \oplus \langle -2\rangle$ the fibre $q^{-1}(2)$ is the single orbit $\{\pm e_1\}$ under $O(L)$ and under $SO(L)$.

    Derivation: $q(x e_1 + y e_2) = 2x^2 - 2y^2 = 2$ gives $(x - y)(x + y) = 1$, so
    $x = \pm 1$, $y = 0$.  The same computation at $-2$ gives $\{\pm e_2\}$, so an
    isometry sends $e_1$ to $\pm e_1$ and $e_2$ to $\pm e_2$:
    $O(L) = \{\operatorname{diag}(\pm 1, \pm 1)\}$ and $SO(L) = \{\pm 1\}$.  The
    element $-1$ of $SO(L)$ carries $e_1$ to $-e_1$.  This is research issue #407.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    e1 = lattice.basis_vector(0)
    for group in (lattice.O(), lattice.SO()):
        orbits = lattice.binary_fixed_norm_representatives(2, group)
        assert orbits.cardinality() == 1
        assert orbits.projection()(e1) == orbits.projection()(-e1)
        assert all(orbits.section()(orbit).q() == 2 for orbit in orbits)


def test_the_split_fibre_orbit_relation_has_actual_witnesses() -> None:
    r"""The isometries of $\langle 2\rangle \oplus \langle -2\rangle$ carrying $e_1$ to $-e_1$ are $-1$ and $\operatorname{diag}(-1, 1)$.

    By the derivation above, $g(e_1) = -e_1$ leaves $g(e_2) = \pm e_2$, with
    determinants $1$ and $-1$; the first witnesses the $SO(L)$-orbit relation.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    e1 = lattice.basis_vector(0)
    witnesses = lattice.definite_complement_extensions(e1, -e1)
    assert all(witness(e1) == -e1 for witness in witnesses)
    assert any(witness.determinant() == 1 for witness in witnesses)
    assert any(witness.determinant() == -1 for witness in witnesses)


def test_the_hyperbolic_plane_separates_orthogonal_and_special_orbits() -> None:
    r"""On $U$ the fibre $q^{-1}(4)$ is one $O(U)$-orbit and two $SO(U)$-orbits.

    Derivation: $q(x e + y f) = 2xy = 4$ gives $\pm(e + 2f)$ and $\pm(2e + f)$.  An
    isometry sends the primitive isotropic $e, f$ to primitive isotropic vectors
    $\pm e, \pm f$ pairing to $1$, so $O(U) = \{\pm 1, \pm\sigma\}$ with $\sigma$ the swap,
    of determinants $1, 1, -1, -1$, and $SO(U) = \{\pm 1\}$.  The swap joins
    $e + 2f$ and $2e + f$; $\pm 1$ does not.
    """
    plane = Lattices(ZZ)([[0, 1], [1, 0]])
    e, f = plane.basis_vector(0), plane.basis_vector(1)
    orthogonal = plane.binary_fixed_norm_representatives(4, plane.O())
    special = plane.binary_fixed_norm_representatives(4, plane.SO())
    assert orthogonal.cardinality() == 1
    assert orthogonal.projection()(e + 2 * f) == orthogonal.projection()(2 * e + f)
    assert special.cardinality() == 2
    assert special.projection()(e + 2 * f) != special.projection()(2 * e + f)
    assert special.projection()(e + 2 * f) == special.projection()(-e - 2 * f)


def test_the_nonsplit_fibre_of_x2_minus_2y2_is_one_special_orbit() -> None:
    r"""On $\langle 1\rangle \oplus \langle -2\rangle$ the fibre $q^{-1}(1)$ is one $SO(L)$-orbit.

    Derivation: $L$ is $\mathbb Z[\sqrt 2]$ with basis $1, \sqrt 2$ and $q$ its norm
    form $N(x + y\sqrt 2) = x^2 - 2y^2$.  The fibre is the group of units of norm
    one.  Multiplication by such a unit $u$ is $\mathbb Z$-linear, preserves $N$, and
    has determinant $N(u) = 1$, so it lies in $SO(L)$ and carries $1$ to $u$.  In
    particular $3 + 2\sqrt 2$ lies in the orbit of $1$.
    """
    lattice = Lattices(ZZ)([[1, 0], [0, -2]])
    e, f = lattice.basis_vector(0), lattice.basis_vector(1)
    orbits = lattice.binary_fixed_norm_representatives(1, lattice.SO())
    assert orbits.cardinality() == 1
    assert orbits.projection()(e) == orbits.projection()(3 * e + 2 * f)
    assert all(orbits.section()(orbit).q() == 1 for orbit in orbits)
