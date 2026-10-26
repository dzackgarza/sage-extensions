r"""Graded-commutative algebras under their plural names.

``GradedCommutativeAlgebras(R, M, parity)`` is the axiom category
``GradedAlgebras(R, M, parity).Supercommutative()``, whose Koszul sign is read
through the parity stated with the grading, and
``StrictlyGradedCommutativeAlgebras(R, M, parity)`` is its ``Alternating()``
refinement (Bourbaki, Algebra III §4.9).
"""

from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras

GradedCommutativeAlgebras = GradedAlgebras.Supercommutative
StrictlyGradedCommutativeAlgebras = GradedAlgebras.Supercommutative.Alternating


__all__ = [
    "GradedCommutativeAlgebras",
    "StrictlyGradedCommutativeAlgebras",
]
