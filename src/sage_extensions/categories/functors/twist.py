r"""The lattice twist endofunctor ``L |-> L(a)``.

For a nonzero integer ``a``, the twist keeps the underlying framed module and
scales the symmetric bilinear form by ``a``.  A lattice morphism keeps the same
coordinate matrix, because ``A^t G_M A = G_L`` implies
``A^t (a G_M) A = a G_L``.  The object action delegates to the lattice owner's
existing :meth:`twist` implementation; this module adds only the categorical
morphism action required by the archived contract.
"""

from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.lattices import Lattices
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)


class TwistFunctor(Functor):
    r"""The faithful endofunctor ``L |-> L(a)`` of integral lattices.

    EXAMPLES::

        sage: from sage_extensions.categories.functors.twist import TwistFunctor
        sage: U = Lattices(ZZ)("U")
        sage: T = TwistFunctor(2)
        sage: g = T(U.Isom(U).identity())
        sage: g.domain() is T(U) and g.codomain() is T(U)
        True
        sage: g.inverse() * g == g.domain().Isom(g.domain()).identity()
        True
        sage: U.twist(-1).twist(-1) is U
        True
    """

    _faithful = True

    def __init__(self, scale) -> None:
        integers = _owned_integers()
        self._scale = integers(scale)
        if self._scale == integers.zero():
            raise ValueError(
                f"the twist L(n) of a lattice needs a nonzero integer n, but n = {scale}"
            )
        category = Lattices(integers)
        super().__init__(category, category)

    def scale(self):
        return self._scale

    def _apply_object(self, lattice):
        return lattice.twist(self.scale())

    def _apply_morphism(self, morphism):
        from sage_extensions.categories.abstract_categories.mor_categories import CategoricalIsomorphism
        from sage_extensions.categories.lattice_morphisms import (
            LatticeEmbeddingMethods,
            LatticeIsometryMethods,
        )

        source = self(morphism.domain())
        target = self(morphism.codomain())

        def transported(arrow):
            r"""The generator images of ``T(arrow)``: ``T`` keeps every module map and rescales only the form."""
            def image(label):
                original_image = arrow(arrow.domain().module_generator(label))
                coordinates = arrow.codomain().framing_morphism().lift(original_image)
                return target.linear_combination(
                    {basis_label: coordinates(basis_label) for basis_label in coordinates.support().domain()}
                )

            return image

        # ``T(f)`` is built from its defining data in its own Mor (``CON-17``):
        # an arrow of another Mor between the twisted lattices is never re-read.
        if isinstance(morphism, (LatticeIsometryMethods, CategoricalIsomorphism)):
            forward = source.Mor(target)(transported(morphism))
            return source.Isom(target)._from_inverse_computation(
                forward, lambda: self(morphism.inverse())
            )
        if isinstance(morphism, LatticeEmbeddingMethods):
            return source.Emb(target)(transported(morphism))
        return source.Mor(target)(transported(morphism))

    def _repr_(self):
        return f"Twist by {self.scale()}"


__all__ = ["TwistFunctor"]
