r"""Owned ordinary characters of finite groups.

A character is kept distinct from an arbitrary class function.  Its actual
evaluation is a class function ``G -> A``, an element of
``Sets().Mor(G, A)``; this module adds the mathematical parent
``Characters(G)``, addition of characters, and exact irreducible
constituents.  GAP remains private to the finite group
engine and is used here only for conjugacy-class sizes.
"""

from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function
from sage.structure.element import Element

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.group.groups import (
    FiniteGroups,
    _conjugacy_class_size,
    _owned_group,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


class CharacterSets(OwnedParameterizedCategory):
    r"""The owned sets ``Char(G)`` of genuine ordinary characters of finite ``G``.

    These are characters of actual finite-dimensional representations, not
    virtual characters.  Direct sum and tensor product make genuine characters
    a commutative semiring; additive inverses appear only after Grothendieck
    completion to the virtual-character/representation ring.  This owner keeps
    the genuine character set, so its immediate placement remains ``Sets()``.
    """

    @staticmethod
    def __classcall__(cls, group):
        return OwnedParameterizedCategory.__classcall__(cls, _owned_group(group))

    def parameter_category(self):
        return FiniteGroups()

    def group(self):
        return self.base()

    def super_categories(self):
        return [Sets()]

    def _repr_object_names(self):
        return f"characters of {self.group()}"

    def an_object(self):
        return self.group().irreducible_characters()[0].parent()

    class ParentMethods:
        def __init__(self, group, **rest) -> None:
            self._group = group
            super().__init__(**rest)

        def group(self):
            return self._group

        def _element_constructor_(self, class_function):
            if class_function in self:
                return class_function
            if not isinstance(class_function, (Morphism, CategoricalArrow)):
                raise TypeError(
                    f"{class_function} is not a character of {self.group()}: a character is a "
                    f"class function on a finite group, and {class_function} is not a map"
                )
            if class_function.domain() is not self.group():
                raise ValueError(
                    f"{class_function} is a class function on {class_function.domain()}, so it "
                    f"is not a character of {self.group()}"
                )
            assert class_function in Sets().Mor(self.group(), class_function.codomain()), (
                f"{class_function} is not a character of {self.group()}: a class function is a map "
                f"of sets {self.group()} -> {class_function.codomain()}"
            )
            representatives = self.group().conjugacy_classes_representatives()
            character = self.group().character(
                tuple(class_function(representative) for representative in representatives)
            )
            field = character.codomain()
            if any(
                field(class_function(element)) != character(element)
                for element in self.group()
            ):
                raise ValueError(
                    f"{class_function} is not a character of {self.group()}: its values are not the "
                    "conjugacy-invariant ordinary character determined by their values on the selected classes"
                )
            return character

        def _from_known_character(self, class_function):
            r"""Construct a character whose genuineness was proved by its supplying construction."""
            if not isinstance(class_function, (Morphism, CategoricalArrow)) or class_function.domain() is not self.group():
                raise TypeError(
                    f"a known character of {self.group()} must be represented by a map with domain {self.group()}, "
                    f"but got {class_function}"
                )
            return self.element_class(self, class_function)

        def __contains__(self, candidate) -> bool:
            return isinstance(candidate, Element) and candidate.parent() is self

        def _repr_(self):
            return f"Characters of {self.group()}"

    class ElementMethods(Element):
        def __init__(self, parent, class_function) -> None:
            self._class_function = class_function
            Element.__init__(self, parent)

        def group(self):
            return self.parent().group()

        def class_function(self):
            return self._class_function

        def codomain(self):
            return self.class_function().codomain()

        def values(self):
            r"""Return the values on the conjugacy-class representatives of ``G``."""
            return finite_indexed_family(
                self.conjugacy_class_representatives(),
                self.class_function(),
                name="Class-function values",
            )

        def class_values(self):
            r"""Return the values on the retained conjugacy-class framing of ``G``.

            This is the mathematical value family of the character.  Engine
            arguments used to evaluate the underlying class function remain
            private to the class-function construction.
            """
            return self.values()

        def conjugacy_class_representatives(self):
            return self.group().conjugacy_classes_representatives()

        def __call__(self, element):
            return self.class_function()(element)

        def degree(self):
            r"""The value at the identity, the dimension of the representation."""
            return self(self.group().one())

        def __add__(self, other):
            if other not in self.parent():
                return NotImplemented
            representatives = self.conjugacy_class_representatives()
            summed = self.group().class_function(
                self.codomain(),
                tuple(self(rep) + other(rep) for rep in representatives),
                representatives=representatives,
            )
            return self.parent()(summed)

        def _inner_product(self, other):
            r"""``<chi, psi> = |G|^-1 sum_g chi(g) psi(g^-1)``, summed class by class."""
            assert other in self.parent(), (
                f"cannot form the inner product <{self}, {other}>: both must be characters of "
                f"{self.group()}, but {other} is not"
            )
            group = self.group()
            representatives = self.conjugacy_class_representatives()
            class_sizes = tuple(
                _conjugacy_class_size(group, representative)
                for representative in representatives
            )
            # For an ordinary finite-group character,
            # conjugate(chi(g)) = chi(g^{-1}).  Read the involution through
            # the character and the group rather than asking every owned
            # cyclotomic scalar for a separate complex-conjugation API.
            total = sum(
                (
                    size * self(representative) * other(representative.inverse())
                    for size, representative in zip(class_sizes, representatives, strict=True)
                ),
                self.codomain().zero(),
            )
            return total / int(group.order())

        def irreducible_constituents(self):
            r"""Return the distinct irreducible characters occurring in ``self``."""
            return finite_ordered_set(
                tuple(
                    irreducible
                    for irreducible in self.group().irreducible_characters()
                    if self._inner_product(irreducible) != 0
                )
            )

        def _repr_(self):
            return f"Character of degree {self.degree()} of {self.group()}"


@cached_function
def _character_set(group):
    r"""Return the owned character set ``Char(G)`` of a finite group."""
    group = _owned_group(group)
    if group not in FiniteGroups():
        raise TypeError(
            f"cannot form the ordinary characters of {group}: the group must be finite, but "
            f"{group} is only known to be in {group.category()}"
        )
    return _object_of(CharacterSets(group), group=group)


__all__ = [
    "CharacterSets",
]
