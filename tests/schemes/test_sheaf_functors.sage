r"""The adjunction `f^* \dashv f_*` of quasi-coherent sheaves along the cusp parametrization.

Derivation: for `f: \mathbb{A}^1 \to \mathbb{A}^2`, `t \mapsto (t^2, t^3)`, the unit
`\mathcal{O}_{\mathbb{A}^2} \to f_* f^* \mathcal{O}_{\mathbb{A}^2} = f_*
\mathcal{O}_{\mathbb{A}^1}` is the ring map `\mathbb{Q}[x, y] \to \mathbb{Q}[t]`, whose
kernel is the ideal `(y^2 - x^3)` of the cusp; the counit `f^* f_* \mathcal{O} \to
\mathcal{O}` is multiplication `\mathbb{Q}[t] \otimes \mathbb{Q}[t] \to \mathbb{Q}[t]`,
which is surjective.
"""

from sage_extensions.all import *


def test_unit_of_pullback_pushforward_on_the_structure_sheaf_has_kernel_the_cusp_ideal() -> None:
    plane = AffineSpaces(QQ)(2, names=("x", "y"))
    algebra = plane.coordinate_ring()
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    line_ring = QQ.polynomial_ring("t")
    t = line_ring.algebra_generator("t")
    line = line_ring.affine_spectrum()
    parametrization = line.Mor(plane)(algebra.Mor(line_ring)({"x": t**2, "y": t**3}))
    adjunction = parametrization.quasi_coherent_adjunction()

    unit = adjunction.unit(plane.structure_sheaf())
    counit = adjunction.counit(line.structure_sheaf())

    assert unit.kernel().global_sections() == plane.closed_subscheme(y**2 - x**3).ideal_sheaf().global_sections()
    assert counit.is_surjective()
