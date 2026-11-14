r"""A formed submodule over restricted scalars: its Gram matrix and its form preservation.

$\operatorname{Res}_\iota \mathbb Q$ is $\mathbb Q$ read as a $\mathbb Z$-module, so a
$\mathbb Z$-bilinear pairing whose values lie in it states a rational form over
$\mathbb Z$; the lattice-database Höhn--Mason intake states each of its lattices that
way, with $\mathrm{leech}[1]$'s basis and the rank-19 subobject $A \subset
\mathrm{leech}[1]$ of record 02AQ among them (lattice-database#29, sage-extensions#320).

Here $V = \mathbb Z^8$ carries the $E_8$ Gram matrix in that reading, and $S \subset V$
is the submodule on the stated rows $B$, so the form of $S$ is the form of $V$ pulled
back along $B$ and its Gram matrix is $B G B^{\mathsf t}$.  Those entries are rationals,
and $\operatorname{Res}_\iota \mathbb Q$ is not a ring and has no matrix space, so the
matrix is over $\mathbb Q$ -- the ring the values are read as scalars of.  An
endomorphism of $S$ is an isometry exactly when its Gram matrix $f^{\mathsf t} G_S f$ is
$G_S$ again: the identity and $-1$ are, and doubling one basis vector is not.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _rational_view():
    r"""$\operatorname{Res}_{\iota} \mathbb Q$, the value object of each form here."""
    return Modules(QQ).restriction_of_scalars(ZZ.Mor(QQ)(lambda n: QQ(n)))(
        QQ.regular_module()
    )


def _space():
    r"""$V = \mathbb Z^8$ with the Gram matrix of $E_8$ over the restricted scalars."""
    gram = Lattices(ZZ)("E8").gram_matrix()
    rows = tuple(
        tuple(int(gram[row, column]) for column in range(8)) for row in range(8)
    )
    return FormModules(ZZ)(
        ZZ.free_module(8).bilinear_hom_space(_rational_view())(rows)
    )


def _basis_rows():
    r"""$B$: four rows of $V$, each a combination of simple roots of $E_8$."""
    return (
        (1, 0, 0, 0, 0, 0, 0, 0),
        (0, 1, 0, 0, 0, 0, 0, 0),
        (1, 1, 1, 0, 0, 0, 0, 0),
        (1, 1, 1, 1, 1, 0, 0, 0),
    )


def _submodule():
    r"""$S \subset V$: the submodule on the rows $B$, with $V$'s form pulled back."""
    space = _space()
    carrier = space.unformed_module()
    rows = _basis_rows()
    basis = ZZ.free_module(4).module_category().Mor(
        ZZ.free_module(4), carrier
    )(tuple(carrier(row) for row in rows))
    return FormModules(ZZ)(space.form().pullback(basis)), space, rows


def _endomorphism(submodule, images):
    r"""The endomorphism of the submodule sending its generators to ``images``."""
    return submodule.module_category().Mor(submodule, submodule)(images)


def test_the_gram_matrix_of_the_submodule_is_the_pulled_back_ambient_gram() -> None:
    r"""$G_S = B G_V B^{\mathsf t}$, entry by entry, over $\mathbb Q$."""
    submodule, space, rows = _submodule()
    ambient = space.gram_tensor()
    gram = submodule.gram_matrix()
    size = int(submodule.module_rank())

    for row in range(size):
        for column in range(size):
            expected = QQ(0)
            for left in range(8):
                for right in range(8):
                    expected += (
                        QQ(rows[row][left])
                        * ambient[left, right]
                        * QQ(rows[column][right])
                    )
            assert gram[row, column] == expected


def test_the_submodule_gram_is_symmetric_with_the_norm_of_each_basis_vector_on_its_diagonal() -> None:
    r"""$G_S$ is symmetric, and $G_S[i, i]$ is $b(e_i, e_i)$ read as a rational."""
    submodule, _space, _rows = _submodule()
    gram = submodule.gram_matrix()
    basis_vectors = tuple(submodule.module_generators())
    values = _rational_view()
    scalars = values.regular_module_identification()

    for index, vector in enumerate(basis_vectors):
        assert gram[index, index] == scalars(submodule.b(vector, vector))
        for other in range(int(submodule.module_rank())):
            assert gram[index, other] == gram[other, index]


def test_preserves_forms_decides_the_isometries_and_the_non_isometry_of_the_submodule() -> None:
    r"""The identity and $-1$ preserve the form of $S$; doubling $e_0$ does not."""
    submodule, _space, _rows = _submodule()
    morphisms = FormModules(ZZ).Mor(submodule, submodule)
    basis_vectors = tuple(submodule.module_generators())

    assert morphisms.preserves_forms(_endomorphism(submodule, basis_vectors)) is True
    assert (
        morphisms.preserves_forms(
            _endomorphism(submodule, tuple(-vector for vector in basis_vectors))
        )
        is True
    )
    assert (
        morphisms.preserves_forms(
            _endomorphism(
                submodule,
                (basis_vectors[0] + basis_vectors[0],) + basis_vectors[1:],
            )
        )
        is False
    )
