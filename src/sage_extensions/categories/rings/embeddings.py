r"""Embeddings of number-field orders.

A map of number fields is a ring map, an element of the ring ``Mor`` between
the fields.  An order embedding is represented by the ring map of fraction
fields that it extends to.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
)
from sage_extensions.categories.rings.ring_foundation import (
    RingMorphism,
    _engine_ring,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class OrderEmbedding:
    r"""A unital embedding of orders, represented by its fraction-field extension."""

    def __init__(self, parent, field_embedding: RingMorphism) -> None:
        domain = parent.domain()
        codomain = parent.codomain()
        source_field = domain.fraction_field()
        target_field = codomain.fraction_field()
        if _engine_ring(field_embedding.domain()) is not _engine_ring(source_field):
            raise ValueError(
                f"cannot restrict {field_embedding} to the order {domain}: "
                f"its domain is {field_embedding.domain()}, not the fraction field {source_field} of that order"
            )
        if _engine_ring(field_embedding.codomain()) is not _engine_ring(target_field):
            raise ValueError(
                f"cannot restrict {field_embedding} to a morphism into the order {codomain}: "
                f"its codomain is {field_embedding.codomain()}, not the fraction field {target_field} of that order"
            )
        for basis_element in domain.integral_basis():
            source_owned = source_field(basis_element)
            image = field_embedding(source_owned)
            if image not in codomain:
                raise ValueError(
                    f"{field_embedding} does not restrict to a morphism of orders {domain} -> {codomain}: "
                    f"it sends the basis element {basis_element} to {image}, which is not in {codomain}"
                )
        self._field_embedding = field_embedding
        domain = parent.domain()
        codomain = parent.codomain()

        def evaluate(element):
            source_owned = source_field(domain(element))
            return codomain(field_embedding(source_owned))

        linear = domain.module_category().Mor(domain, codomain).elementwise(
            evaluate
        )
        super().__init__(parent, linear)

    def field_embedding(self) -> RingMorphism:
        return self._field_embedding

    def _evaluate_field_embedding(self, element):
        source_field = self.domain().fraction_field()
        source_owned = source_field(self.domain()(element))
        image = self.field_embedding()(source_owned)
        return self.codomain()(image)

    def __mul__(self, other):
        if not isinstance(other, OrderEmbedding) or other.codomain() is not self.domain():
            return NotImplemented
        return other.domain().Mor(self.codomain())(
            self.field_embedding() * other.field_embedding()
        )


class OrderMor(CategoricalMor):
    ElementMethods = OrderEmbedding

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def _element_constructor_(self, field_embedding):
        r"""Admit the ring map of fraction fields, or any datum that ring ``Mor`` admits."""
        source_field = self.domain().fraction_field()
        target_field = self.codomain().fraction_field()
        return self.element_class(self, source_field.Mor(target_field)(field_embedding))

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(X, X), but this is Mor({self.domain()}, {self.codomain()})"
            )
        field = self.domain().fraction_field()
        identity = self(field.Mor(field).identity())
        identity._preamble_is_identity = True
        return identity

    def _repr_(self):
        return f"Emb({self.domain()}, {self.codomain()})"


__all__ = [
    "OrderEmbedding",
    "OrderMor",
]
