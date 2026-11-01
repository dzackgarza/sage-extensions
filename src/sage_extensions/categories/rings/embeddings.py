r"""Embeddings of number-field orders.

A map of number fields is a ring map, an element of the ring ``Mor`` between
the fields.  An order embedding is represented by the ring map of fraction
fields that it extends to.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.logic import ask

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
            # Membership in an owned order is a proposition; ``in`` would
            # coerce it to a bool before it could be asked.
            contained = ask(codomain.is_parent_of(image))
            if contained is not True:
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

        # The map is the composite ``codomain <- fraction field <- field
        # embedding <- fraction field <- domain``.  Every factor is a ring
        # morphism or a coercions of orders, hence ZZ-linear, so the composite
        # is linear by its construction: state that as the construction's
        # premise rather than leaving the arrow merely "a function on elements",
        # which is what made ``is_injective()`` refuse to read it.
        linear = domain.module_category().Mor(domain, codomain)._from_constructed_element_map(
            evaluate, premises=()
        )
        # The composite is injective by its factors: the order includes into
        # its fraction field, the field embedding is injective, and the image
        # lies in the codomain order, where the coercion is the identity.  The
        # construction therefore retains injectivity as a premise, which
        # ``is_injective`` reads instead of asking for a kernel algorithm that
        # these modules do not supply.
        linear._injectivity_premise = True
        super().__init__(parent, linear)
        # The arrow the caller holds is this embedding, so the premise is
        # retained on it as well.
        self._injectivity_premise = True

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
