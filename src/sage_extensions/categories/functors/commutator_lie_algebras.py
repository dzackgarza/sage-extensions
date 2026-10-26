r"""The commutator functor \((-)^-\colon\mathbf{AssAlg}_R\to\mathbf{Lie}_R\).

An associative \(R\)-algebra \(A\) over commutative \(R\) is a Lie algebra
under \([x,y]=xy-yx\).  The bracket is determined by the product, so \(A^-\)
is the algebra ``Algebras(R)(A, [-,-])`` built through the one construction on
the data of \(A\); its elements pass to and from \(A\) by coercion.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.algebras.algebras import (
    Algebras,
    _algebra_on_module,
    _algebra_tensor_square_functor,
)
from sage_extensions.categories.algebras.lie_algebras import (
    CommutatorLieAlgebras,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.rings.ring_foundation import _owned_ring


class CommutatorLieAlgebraFunctor(Functor):
    r"""\((-)^-\colon\mathbf{AssAlg}_R\to\mathbf{CommLie}_R\)."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            Algebras(self._base_ring).Associative(),
            CommutatorLieAlgebras(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, algebra):
        r"""The Lie algebra on ``A`` whose bracket is ``[x, y] = xy - yx``."""
        return _commutator_lie_algebra(algebra)

    def _apply_morphism(self, morphism):
        r"""The linear map of an associative-algebra morphism, read between the commutator Lie algebras.

        A morphism of associative algebras preserves the commutator, since
        \(f(xy-yx)=f(x)f(y)-f(y)f(x)\) follows from multiplicativity, and it
        is \(R\)-linear.  ``A^-`` is built on the data of ``A``, so an element
        of ``A^-`` passes to ``A``, is mapped, and passes to ``B^-`` by
        coercion.
        """
        source = self(morphism.domain())
        target = self(morphism.codomain())
        domain = morphism.domain()
        underlying = Algebras(self.base_ring()).underlying_module()(morphism)
        linear = source.module_category().Mor(source, target)._from_constructed_element_map(
            lambda element: target(underlying(domain(element))),
            premises=(underlying,),
        )
        return Algebras(self.base_ring()).Lie().Mor(source, target)(linear)

    def _repr_(self):
        return f"Commutator Lie-algebra functor on associative {self.base_ring()}-algebras"


@cached_function(key=lambda algebra: id(algebra))
def _commutator_lie_algebra(algebra):
    r"""``A^-``: the algebra on ``A`` with bracket ``[x, y] = xy - yx``, one object per ``A``.

    The bracket is bilinear, so it is the map out of ``A (x)_R A``
    induced by the difference of its two product evaluations, without
    requiring a chosen module framing.  The
    commutator of an associative product is alternating and satisfies the
    Jacobi identity (Bourbaki, *Lie Groups and Lie Algebras* I §1.2), so that
    theorem is the placement.
    """
    ring = algebra.algebra_base_ring()
    tensor = _algebra_tensor_square_functor(ring)(algebra)
    bracket = tensor.from_bilinear_map(
        algebra, lambda left, right: algebra.product(left, right) - algebra.product(right, left),
    )
    return _algebra_on_module(
        algebra,
        bracket,
        placement=(CommutatorLieAlgebras(ring),),
        law_decisions={
            "alternation": True,
            "jacobi": algebra.associativity_decision(),
        },
    )


@cached_function
def _commutator_lie_algebra_functor(base_ring) -> CommutatorLieAlgebraFunctor:
    return CommutatorLieAlgebraFunctor(base_ring)


__all__ = [
    "CommutatorLieAlgebraFunctor",
]
