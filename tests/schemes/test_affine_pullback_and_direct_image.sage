r"""Pullback and direct image of quasi-coherent sheaves along ``Spec Q[s] -> Spec Q[x]``, ``x -> s^2``.

Source: Stacks Project, Tag 01I9 (Lemma 26.7.3, checked): for ``f: Spec B -> Spec A``,
``f^* M~ = (M (x)_A B)~`` and ``f_* N~ = (N_A)~``, ``N`` viewed as an ``A``-module.  Here
``Q[s]`` is free over ``Q[x] = Q[s^2]`` with basis ``1, s``, so ``f_* O = O^2`` and
``f^* O = O``; ``f^*`` is left adjoint to ``f_*``.
"""

from sage_extensions.all import *


def _squaring():
    x_ring = QQ["x"]
    s_ring = QQ["s"]
    s = s_ring.algebra_generator("s")
    target = AffineSchemes(QQ)(x_ring)
    source = AffineSchemes(QQ)(s_ring)
    return x_ring, s_ring, target, source, source.Mor(target)(x_ring.Mor(s_ring)({"x": s**2}))


def test_pullback_is_left_adjoint_to_direct_image() -> None:
    r"""The adjunction ``f^* -| f_*`` has ``f^*`` and ``f_*`` as its two functors."""
    x_ring, s_ring, target, source, squaring = _squaring()
    adjunction = squaring.quasi_coherent_adjunction()

    assert adjunction.left_adjoint() == squaring.module_pullback_functor()
    assert adjunction.right_adjoint() == squaring.direct_image_functor()


def test_the_direct_image_of_the_structure_sheaf_is_the_ring_upstairs_over_the_ring_downstairs() -> None:
    r"""``Gamma(f_* O) = Q[s]`` as a ``Q[x]``-module, which is free of rank 2."""
    x_ring, s_ring, target, source, squaring = _squaring()
    structure = QuasiCoherentSheaves(source).associated_sheaf(s_ring.free_module(1))

    pushed = squaring.direct_image(structure)

    assert pushed in QuasiCoherentSheaves(target)
    assert QuasiCoherentSheaves(target).global_sections(pushed).base_ring() == x_ring
    assert QuasiCoherentSheaves(target).global_sections(pushed).module_rank() == 2


def test_the_pullback_of_the_structure_sheaf_is_the_structure_sheaf() -> None:
    r"""``f^* O_{A^1} = (Q[x] (x)_{Q[x]} Q[s])~ = O``: its sections are free of rank 1 over ``Q[s]``."""
    x_ring, s_ring, target, source, squaring = _squaring()
    structure = QuasiCoherentSheaves(target).associated_sheaf(x_ring.free_module(1))

    pulled = squaring.module_pullback(structure)

    assert QuasiCoherentSheaves(source).global_sections(pulled).module_rank() == 1
