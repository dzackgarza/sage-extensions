r"""GAP routes through ``libgap``, run against the real engine.

Each test asks the owned lattice surface for an operation that GAP realizes,
so the whole route is exercised: owned tensors are lowered to GAP matrices,
GAP computes, and the result is raised back into owned values.
"""

from sage_extensions.all import *


def test_rational_spinor_norm_of_hyperbolic_plane_isometries() -> None:
    # The spinor norm of s_{v_1}...s_{v_m} is the square class of
    # prod -(v_i, v_i)/2 (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §1).
    # On U with e.f = 1: swap = s_{e-f} with (e-f)^2 = -2, class [1];
    # -1 = s_{e+f} s_{e-f} with (e+f)^2 = 2, class [-1][1] = [-1].
    lattice = Lattices(ZZ)("U")
    e, f = lattice.module_generators()
    swap = lattice.Aut()((f, e))
    minus_identity = lattice.Aut()((-e, -f))
    spinor_norm = lattice.spinor_norm()
    square_classes = QQ.square_class_group()

    assert spinor_norm(swap) == square_classes(1)
    assert spinor_norm(minus_identity) == square_classes(-1)
