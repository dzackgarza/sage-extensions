r"""Gluing modules on a Zariski cover of the affine line over QQ."""

from sage_extensions.all import *


def test_gluing_by_multiplication_by_x_has_section_one_x_and_not_one_one() -> None:
    r"""Glue `\mathcal{O}` on `D(x)` and on `D(1-x)` along `s \mapsto x s` on `D(x(1-x))`.

    A pair `(s_0, s_1)` is a global section exactly when `s_1 = x s_0` on the overlap,
    so `(1, x)` is one and `(1, 1)` is not.  The glued sheaf is a line bundle on
    `\mathbb{A}^1`, whose Picard group is trivial, so its global sections form a free
    `\mathbb{Q}[x]`-module of rank 1.
    """
    ring = QQ.polynomial_ring("x")
    x = ring.algebra_generator("x")
    line = ring.affine_spectrum()
    cover = line.distinguished_open_cover(x, 1 - x)
    left, right = cover.opens()
    left_module = left.coordinate_ring().free_module(("e",))
    right_module = right.coordinate_ring().free_module(("e",))
    left_overlap = cover.restrict_module(left_module, 0, 1)
    right_overlap = cover.restrict_module(right_module, 1, 0)
    x_on_overlap = line.structure_sheaf().restriction_map(line, cover.overlap(0, 1))(x)
    transition = left_overlap.Mor(right_overlap)(
        {"e": x_on_overlap * right_overlap.module_generator("e")}
    )

    sheaf = cover.glue_modules((left_module, right_module), {(0, 1): transition})
    sections = sheaf.global_sections()
    left_one = left_module.module_generator("e")
    right_one = right_module.module_generator("e")
    x_on_right = line.structure_sheaf().restriction_map(line, right)(x)

    assert (left_one, x_on_right * right_one) in sections
    assert (left_one, right_one) not in sections
    assert sections.is_free()
    assert sections.module_rank() == 1
