r"""Relative Spec of a sheaf of algebras glued on a Zariski cover of the affine line."""

from sage_extensions.all import *


def _glued_polynomial_algebra(cover, variable):
    local_algebras = tuple(open_.coordinate_ring().polynomial_ring(variable) for open_ in cover.opens())
    left = cover.restrict_algebra(local_algebras[0], 0, 1)
    right = cover.restrict_algebra(local_algebras[1], 1, 0)
    transition = left.Mor(right)({variable: right.algebra_generator(variable)})
    return cover.glue_algebras(local_algebras, {(0, 1): transition})


def test_relative_spec_of_the_glued_polynomial_algebra_is_the_affine_plane() -> None:
    r"""Gluing `\mathcal{O}[z]` on `D(x) \cup D(1-x)` gives `\mathcal{O}_{\mathbb{A}^1}[z]`,
    whose relative Spec is `\mathbb{A}^2 \to \mathbb{A}^1`, of relative dimension 1."""
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    cover = line.distinguished_open_cover(x, 1 - x)

    relative = _glued_polynomial_algebra(cover, "z").relative_spectrum()

    assert relative.codomain() is line
    assert relative.domain().is_isomorphic(QQ.polynomial_ring(("x", "z")).affine_spectrum())
    assert relative.relative_dimension() == 1


def test_relative_spec_sends_z_to_w_squared_to_a_finite_map_of_degree_two() -> None:
    r"""The algebra map `\mathcal{O}[z] \to \mathcal{O}[w]`, `z \mapsto w^2`, induces
    `\mathbb{A}^1_X \to \mathbb{A}^1_X`, `w \mapsto w^2`, finite of degree 2 over `X`."""
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    cover = line.distinguished_open_cover(x, 1 - x)
    source = _glued_polynomial_algebra(cover, "z")
    target = _glued_polynomial_algebra(cover, "w")
    squaring = source.Mor(target)(
        tuple(
            source.local_algebra(index).Mor(target.local_algebra(index))(
                {"z": target.local_algebra(index).algebra_generator("w") ** 2}
            )
            for index in cover.atlas()
        )
    )

    induced = squaring.relative_spectrum_morphism()

    assert source.relative_spectrum() * induced == target.relative_spectrum()
    assert induced.is_finite()
    assert induced.degree() == 2
