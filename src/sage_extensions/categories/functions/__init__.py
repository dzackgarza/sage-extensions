r"""Function spaces \(C^k(X,Y)\), Lebesgue spaces \(L^p\), and sequence spaces \(\ell^p\)."""

from sage.misc.lazy_import import lazy_import

from sage_extensions.categories.functions.real_functions import (
    Lp,
    C,
    ell,
)

# The graded Lebesgue module constructs its algebras and the convolution
# pairing when it loads; Sage's lazy_import defers that to first use.
lazy_import(
    "sage_extensions.categories.functions.lebesgue_graded",
    (
        "GradedLebesgueModule",
        "GradedTensorProductModules",
        "GradedTensorSquare",
        "LebesgueGradedModules",
        "LebesgueConvolution",
        "LebesgueConvolutionModule",
        "graded_lebesgue_algebra",
        "lebesgue_convolution_algebra",
        "GradedLebesgueAlgebra",
        "LebesgueConvolutionAlgebra",
    ),
)

__all__ = [
    "C",
    "GradedLebesgueAlgebra",
    "GradedLebesgueModule",
    "GradedTensorProductModules",
    "GradedTensorSquare",
    "LebesgueConvolution",
    "LebesgueConvolutionAlgebra",
    "LebesgueConvolutionModule",
    "LebesgueGradedModules",
    "Lp",
    "ell",
    "graded_lebesgue_algebra",
    "lebesgue_convolution_algebra",
]
