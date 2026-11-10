r"""The line-stabilizer image is returned only where Eichler's criterion applies to the lattice.

Eichler's criterion (Gritsenko--Hulek--Sankaran, *Moduli of K3 Surfaces and
Irreducible Symplectic Manifolds*, Lemma 7.8, p. 503) classifies the
$\widetilde{SO}(L)$-orbits of primitive vectors of a lattice that splits two
orthogonal hyperbolic planes.  The hypothesis is a property of $L$: applied to an
enlargement the criterion classifies orbits on that enlargement, and the element it
produces need not preserve $L$.

The specimen is $L = U \oplus E_8(-1)^2 = \mathrm{II}_{1,17}$: unimodular, with one
hyperbolic plane.  Its enlargement $L \oplus U = \mathrm{II}_{2,18}$ does split two
hyperbolic planes and is still unimodular, so nothing about it constrains
$O(L)$ -- a primitive isotropic $v$ of $L$ is classified by the isometry class of
$v^\perp/\mathbb{Z} v$ (Conway--Sloane, *Sphere Packings, Lattices and Groups*,
ch. 16), which the discriminant group of a unimodular lattice cannot see at all.
The call below therefore makes no claim on $L$, and the caller keeps its exact
integral route.  What the orbit count of $L$ is belongs to a lattice-database row;
this file states no number.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""$L = U \oplus E_8(-1)^2$, and the primitive isotropic line spanned by $e_0$."""
    lattice = NamedLattices.U + NamedLattices.E8 ** 2
    labels = tuple(lattice.module_generating_set())
    line = lattice.primitive_isotropic_subobject(lattice.module_generator(labels[0]))
    return lattice, line


def test_the_line_stabilizer_image_refuses_where_the_criterion_does_not_apply() -> None:
    r"""One hyperbolic plane in $L$: the quotient returns no class set for the line."""
    lattice, line = _specimen()
    assert lattice.hyperbolic_plane_summand_count() == 1
    assert not lattice.eichler_criterion_applies()

    quotient = lattice.O_plus().finite_character_quotient()
    assert quotient.isotropic_line_stabilizer_image(line) is None


def test_the_hyperbolic_plane_the_enlargement_adds_is_where_the_criterion_applies() -> None:
    r"""$L \oplus U$ splits two hyperbolic planes, and $L$ itself does not."""
    lattice, _line = _specimen()
    assert not lattice.eichler_criterion_applies()
    assert (lattice + NamedLattices.U).eichler_criterion_applies()
