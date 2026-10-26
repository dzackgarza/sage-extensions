r"""Owned number fields and their selected primitive-element presentations."""

from sage.all import (
    CyclotomicField as _SageCyclotomicField,
)
from sage.all import (
    NumberField as _SageNumberField,
)
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.abc import Order as SageNumberFieldOrder
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories._lattice import signature_pair
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoryPacketMethods,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.group.groups import _own_group
from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedFreeModules,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedOrders,
    OwnedRings,
    _OwnedRingParent,
    _field_placements,
    _owned_rationals,
    _engine_element,
    _engine_numeral,
    _engine_ring,
    _own_ring,
    _owned_engine_ring,
    _set_owned_ring_display,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
def _own_number_field(engine):
    r"""Raise a Sage number-field engine met in an adapter through the number-field construction."""
    return _owned_engine_ring(engine)


def _number_field_placements():
    r"""A number field is a field, finite over ``QQ``, countably infinite, presented by its primitive element."""
    from sage_extensions.categories.sets.set_categories import CountablyInfiniteSets

    return (
        *_field_placements(),
        OwnedNumberFields(),
        NumberFieldsWithChosenPrimitiveElement(),
        CountablyInfiniteSets(),
    )


def _polynomial_in(ring, polynomial):
    r"""``polynomial`` with its coefficients kept and its variable renamed to that of ``ring``.

    This is the relabelling isomorphism ``K[x] -> K[t]`` of univariate
    polynomial rings over one coefficient ring, applied to one element.
    """
    source = element_parent(polynomial)
    assert len(source.variable_names()) == 1 and source.base_ring() is ring.base_ring(), (
        f"cannot read {polynomial} in {ring}: its coefficients lie in {source.base_ring()}, "
        f"not in {ring.base_ring()}"
    )
    coefficients = _engine_element(source, polynomial).list()
    return _owned_engine_element(ring, _engine_ring(ring)(coefficients))


def _number_field_engine(polynomial):
    r"""The private Sage realization of ``QQ[t]/(f)``, one rule for every route (``CON-12``).

    A cyclotomic ``f = Phi_n`` is realized by Sage's cyclotomic field, whose
    arithmetic converts GAP's cyclotomic numbers (the character values of
    ``groups.py``); any other ``f`` by Sage's number field with no embedding.
    """
    ring = element_parent(polynomial)
    (label,) = ring.variable_names()
    engine_polynomial = _engine_element(ring, polynomial)
    if all(coefficient in SageZZ for coefficient in engine_polynomial.list()):
        order = engine_polynomial.change_ring(SageZZ).is_cyclotomic(certificate=True)
        if order:
            # No embedding (CON-08): Sage's default cyclotomic field carries
            # zeta_n -> e^{2 pi i/n}; embedding=None is accepted by
            # CyclotomicFieldFactory.create_key (number_field.py:1122).
            # GAP conversion does not read the embedding: _coerce_from_gap
            # writes CoeffsCyc in self.gen(), and a UCF element converts
            # through _coerce_from_other_cyclotomic_field's
            # _lift_cyclotomic_element (number_field.py:11376, 11431;
            # universal_cyclotomic_field.py to_cyclotomic_field).
            return _SageCyclotomicField(int(order), label, embedding=None)
    return _SageNumberField(engine_polynomial, label)


def _engine_number_field_isomorphism(source, target):
    r"""The Sage isomorphism ``source -> target`` of two realizations of one number field, generator to generator.

    Private number-field adapter (``OWN-06``).  Both engines realize
    ``QQ[t]/(f)`` (or ``K[t]/(g)`` over realizations of one ``K``) for the
    same polynomial, so sending the class of ``t`` to the class of ``t`` is an
    isomorphism, determined by that polynomial.  Callers: the raising of a
    number-field engine's orders and maps into the owned field
    (:func:`_order_from_engine`, the Galois action in ``groups.py``, the
    splitting-field base maps in ``absolute_galois_group(s).py``).  The
    identity when the engines are one parent.
    """
    if source is target:
        return source.Hom(source).identity()
    if source.is_absolute():
        assert target.is_absolute() and source.defining_polynomial().list() == target.defining_polynomial().list(), (
            f"{source} and {target} are not realizations of one number field: their defining "
            "polynomials differ"
        )
        return source.hom([target.gen()], target)
    base = _engine_number_field_isomorphism(source.base_field(), target.base_field())
    inclusion = target.coerce_map_from(target.base_field())
    return source.hom([target.gen()], target, base_map=inclusion * base)


@cached_function(key=lambda polynomial: (id(element_parent(polynomial)), polynomial))
def _number_field_of(polynomial):
    r"""``QQ(theta) = QQ[t]/(f)``: the number field of an irreducible ``f`` in ``QQ[t]``, ``theta`` the class of ``t``.

    The defining datum is ``f`` in the one polynomial ring ``QQ[t]``, so the
    field is one object for ``f`` (``OWN-02``); the label ``t`` names the
    chosen primitive element.  Irreducibility of ``f`` is the caller's claim
    (``OWN-22``).  The field is placed by this construction, never by the
    class of its engine (``ARC-08``).

    The quotient map ``QQ[t] ->> QQ[t]/(f)`` out of the free commutative
    algebra ``QQ[t] = Sym(QQ^{t})`` is part of this construction, so the
    field is constructed with it as its chosen degree-zero algebra resolution
    (``CAT-29``): the generating set is ``{t}`` and ``t`` goes to ``theta``.
    """
    from sage_extensions.categories.algebras.algebras import _OwnedAlgebraParent

    ring = element_parent(polynomial)
    assert ring in OwnedRings() and ring.base_ring() is _owned_rationals() and len(ring.variable_names()) == 1, (
        f"a number field QQ[t]/(f) is constructed from a polynomial f in one variable over QQ, but {polynomial} "
        f"lies in {ring}"
    )
    field = _OwnedAlgebraParent(
        _number_field_engine(polynomial),
        ring.base_ring(),
        ring.algebra_generating_set(),
        algebra_framing_source=ring,
        ring_placement=_number_field_placements,
        constructing_category=OwnedRings(),
    )
    _set_owned_ring_display(field, f"Number field defined by {polynomial}")
    return field


@cached_function(key=lambda base, polynomial: (id(base), id(element_parent(polynomial)), polynomial))
def _number_field_extension(base, polynomial):
    r"""``K(theta) = K[t]/(g)``: the finite extension of the number field ``K`` by an irreducible ``g`` in ``K[t]``.

    The defining datum is ``(K, g)``; it is a number field, finite over ``QQ``
    by the tower law.  Irreducibility of ``g`` is the caller's claim.  The
    quotient map ``K[t] ->> K[t]/(g)`` is its chosen degree-zero resolution
    as a ``K``-algebra (``CAT-29``), as for :func:`_number_field_of`.
    """
    from sage_extensions.categories.algebras.algebras import _OwnedAlgebraParent

    ring = element_parent(polynomial)
    assert ring.base_ring() is base and len(ring.variable_names()) == 1, (
        f"an extension of {base} is constructed from a polynomial in one variable over {base}, but {polynomial} "
        f"lies in {ring}"
    )
    (label,) = ring.variable_names()
    engine = _engine_ring(base).extension(_engine_element(ring, polynomial), label)
    field = _OwnedAlgebraParent(
        engine,
        base,
        ring.algebra_generating_set(),
        algebra_framing_source=ring,
        ring_placement=_number_field_placements,
        constructing_category=OwnedRings(),
    )
    _set_owned_ring_display(field, f"Number field defined by {polynomial} over {base}")
    return field


def _number_field_from_engine(engine):
    r"""The owned number field a Sage number-field engine presents: its defining polynomial and label."""
    label = engine.variable_name()
    if engine.is_absolute():
        ring = _owned_rationals().polynomial_ring(label)
        polynomial = _owned_engine_element(ring, _engine_ring(ring)(engine.defining_polynomial().list()))
        return _number_field_of(polynomial)
    base = _owned_engine_ring(engine.base_field())
    ring = base.polynomial_ring(label)
    polynomial = _owned_engine_element(ring, _engine_ring(ring)(engine.relative_polynomial().list()))
    return _number_field_extension(base, polynomial)


def _order_placements():
    r"""An order of a number field: a Noetherian domain, free of finite rank over ``ZZ``, countably infinite.

    Its integral basis is the one its construction selects (``OrdersWithChosenIntegralBasis``).
    """
    from sage_extensions.categories.rings.ring_foundation import OwnedIntegralDomains
    from sage_extensions.categories.sets.set_categories import CountablyInfiniteSets

    return (
        OwnedIntegralDomains(),
        OwnedRings().Noetherian(),
        CountablyInfiniteSets(),
        OrdersWithChosenIntegralBasis(),
        OwnedOrders(),
    )


def _power_basis_lattice(engine_order):
    r"""The ``ZZ``-lattice of an order in ``K``'s power basis: its echelonized basis rows over ``QQ``.

    Private key of :func:`_order_in`.  Sage's ``Order.free_module()`` is the
    ``ZZ``-span of the order in ``K.vector_space()``, the coordinates in the
    power basis ``1, theta, ..., theta^{n-1}``; its echelonized basis matrix
    is determined by the lattice alone, so equal lattices give equal rows.
    """
    return tuple(
        tuple(row) for row in engine_order.free_module().echelonized_basis_matrix().rows()
    )


@cached_function(key=lambda field, engine_order: (field, _power_basis_lattice(engine_order)))
def _order_in(field, engine_order):
    r"""The order of the number field ``K`` whose underlying lattice ``engine_order`` presents.

    An order of ``K`` is a subring that is a full ``ZZ``-lattice in ``K``; it
    is determined by ``K`` and that lattice, so equal lattices give one order
    (``OWN-02``).  The cache key is ``(K, the lattice in K's power basis)``
    (:func:`_power_basis_lattice`), never the realization: two Sage orders
    with one lattice are one order.  Its integral basis is the basis the
    realization holds.  ``ZZ`` is the order of ``QQ``, and is not reached
    here (``K.ring_of_integers()`` answers it for ``QQ``).
    """
    if field is _owned_rationals():
        return _owned_integers()
    assert _engine_ring(field) is engine_order.number_field(), (
        f"{engine_order} is not an order of {field}"
    )
    return _OwnedRingParent(engine_order, named_placement=_order_placements)


def _order_from_engine(engine_order):
    r"""The owned order a Sage order engine presents, raised through its number field.

    When the engine's field is another realization of the same field (an
    embedded one, say), the lattice is carried to the field's own
    realization along the isomorphism sending primitive element to primitive
    element, both defined by the same polynomial.
    """
    field = _owned_engine_ring(engine_order.number_field())
    canonical = _engine_ring(field)
    source = engine_order.number_field()
    if source is not canonical and field is not _owned_rationals():
        transport = _engine_number_field_isomorphism(source, canonical)
        engine_order = canonical.order([transport(element) for element in engine_order.basis()])
    return _order_in(field, engine_order)


def CyclotomicField(order, name=None):
    r"""``QQ(zeta_n) = QQ[name]/(Phi_n)``, ``n`` the order; the specification's name for that number field."""
    integers = _owned_integers()
    order = int(integers(order))
    label = f"zeta{order}" if name is None else str(name)
    from sage.rings.polynomial.cyclotomic import cyclotomic_coeffs

    ring = _owned_rationals().polynomial_ring(label)
    polynomial = _owned_engine_element(ring, _engine_ring(ring)(cyclotomic_coeffs(order)))
    return _number_field_of(polynomial)


def QuadraticField(discriminant, name="a"):
    r"""``QQ(sqrt d) = QQ[name]/(name^2 - d)`` for a nonsquare ``d``; the specification's name for that number field.

    No embedding into ``RR`` or ``CC`` is part of the field (``CON-08``):
    an embedding is an element of ``K.Mor(target)`` the caller chooses.
    """
    rationals = _owned_rationals()
    ring = rationals.polynomial_ring(str(name))
    generator = ring.algebra_generator(str(name))
    return _number_field_of(generator ** 2 - ring(rationals(discriminant)))


def _number_field(polynomial, name):
    r"""The number field of ``polynomial`` with its primitive element labelled ``name``.

    Over ``QQ`` this is ``QQ[name]/(f)``; over a number field ``K`` it is the
    extension ``K[name]/(f)``.
    """
    parent = element_parent(polynomial)
    if parent not in OwnedRings():
        raise TypeError(
            f"cannot construct a number field from {polynomial!r}: it must be a polynomial in a "
            f"polynomial ring of this session, but its parent is {parent!r}"
        )
    base = parent.base_ring()
    ring = base.polynomial_ring(str(name))
    transported = _polynomial_in(ring, polynomial)
    if base is _owned_rationals():
        return _number_field_of(transported)
    assert base in OwnedNumberFields(), (
        f"cannot construct a number field from {polynomial}: its coefficients lie in {base}, "
        "which is neither QQ nor a number field"
    )
    return _number_field_extension(base, transported)


class OwnedNumberFields(CategoryPacketMethods, OwnedCategory):
    r"""Finite extensions of ``QQ``.

    Number fields are a full subcategory of fields, hence of rings, so the
    maps between them are the ring maps and this category inherits the ring
    ``Mor``.
    """

    def an_object(self):
        r"""The rational field as the degree-one number field."""
        return _own_number_field(SageQQ)
    _certifying_predicate = "_preamble_is_number_field"

    @classmethod
    def _repr_object_names(cls):
        return "number fields"

    def super_categories(self):
        return [OwnedRings().Division().Commutative()]

    class ParentMethods:

        def degree(self):
            r"""Return ``[K:QQ]`` as an owned integer."""

            integers = _owned_integers()
            engine = _engine_ring(self)
            value = (
                SageZZ.one()
                if engine is SageQQ
                else SageZZ(
                    engine.degree()
                    if engine.is_absolute()
                    else engine.absolute_degree()
                )
            )
            return _owned_engine_element(integers, value)

        def discriminant(self):
            r"""Return the discriminant of the ring of integers of ``K``."""

            integers = _owned_integers()
            engine = _engine_ring(self)
            value = SageZZ.one() if engine is SageQQ else SageZZ(engine.discriminant())
            return _owned_engine_element(integers, value)

        def signature(self):
            r"""Return the signature pair ``(r_1,r_2)`` with ``r_1+2r_2=[K:QQ]``."""

            engine = _engine_ring(self)
            if engine is SageQQ:
                return signature_pair(1, 0)
            real, complex_pairs = engine.signature()
            return signature_pair(real, complex_pairs)

        def class_number(self):
            r"""Return the class number of the ring of integers."""

            integers = _owned_integers()
            engine = _engine_ring(self)
            value = SageZZ.one() if engine is SageQQ else SageZZ(engine.class_number())
            return _owned_engine_element(integers, value)

        def extension(self, polynomial, name="a"):
            r"""``K[name]/(g)``: the finite extension of this number field by an irreducible ``g`` over it."""
            polynomial_ring = element_parent(polynomial)
            if polynomial_ring not in OwnedRings() or polynomial_ring.base_ring() is not self:
                raise TypeError(
                    f"cannot form the extension of {self} defined by {polynomial!r}: it must be a polynomial "
                    f"with coefficients in {self}, but its parent is {polynomial_ring!r}"
                )
            return _number_field_extension(
                self, _polynomial_in(self.polynomial_ring(str(name)), polynomial)
            )

        def primes_above(self, prime):
            r"""Return the prime ideals of ``O_K`` above a rational prime."""

            order = self.ring_of_integers()
            integers = order.base_ring()
            prime = integers(prime)
            backend_prime = _engine_element(integers, prime)
            order_engine = _engine_ring(order)
            ideals = []
            for backend_ideal in _engine_ring(self).primes_above(backend_prime):
                generators = tuple(
                    _owned_engine_element(order, order_engine(generator))
                    for generator in backend_ideal.gens()
                )
                ideals.append(order.ideal(*generators))
            return finite_ordered_set(ideals)

        @cached_method
        def ring_of_integers(self):
            r"""``O_K``, the integral closure of ``ZZ`` in ``K``: determined by ``K``, so cached on ``K``."""
            engine = _engine_ring(self)
            if engine is SageQQ:
                return _owned_integers()
            return _order_in(self, engine.ring_of_integers())

        maximal_order = ring_of_integers

        def order_generated_by(self, *generators):
            r"""Return the order ``ZZ[generators]`` inside this number field."""
            if not generators:
                raise ValueError(
                    f"the order ZZ[a_1, ..., a_n] of {self} needs at least one element a_i of {self}, but none was given"
                )

            engine = _engine_ring(self)
            backend_generators = tuple(
                _engine_element(self, self(generator)) for generator in generators
            )
            datum = (
                backend_generators[0]
                if len(backend_generators) == 1
                else list(backend_generators)
            )
            return _order_in(self, engine.order(datum))

        def ramified_primes(self):
            r"""Return the rational primes ramified in ``K``."""

            return finite_ordered_set(abs(self.discriminant()).prime_divisors())

        @cached_method
        def embeddings(self, target):
            r"""Return the owned field embeddings ``K -> target``.

            Every embedding is a ring map, an element of ``Mor(K, target)``.
            The codomain ``AA``, ``RR`` or ``CC`` is not promoted to a finite
            extension of ``QQ``.
            """

            if target not in OwnedRings().Division().Commutative():
                raise TypeError(
                    f"cannot list the embeddings of {self} into {target}: the target must be a field, "
                    f"but {target} is not in the category of commutative division rings"
                )
            if target in OwnedNumberFields():
                return self.Mor(target).embeddings()

            source_engine = _engine_ring(self)
            from sage_extensions.rings.complex import ExactComplexField
            from sage_extensions.rings.real import ExactRealField

            from sage.rings.qqbar import AA as SageAA
            from sage.rings.qqbar import QQbar as SageQQbar

            # An embedding K -> RR (K -> CC) has image in the real (complex)
            # algebraic numbers AA (QQbar), since every element of K is
            # algebraic over QQ.
            match target:
                case ExactRealField():
                    algebraic_numbers = SageAA
                case ExactComplexField():
                    algebraic_numbers = SageQQbar
                case _:
                    algebraic_numbers = None

            match algebraic_numbers:
                case None:
                    engine_embeddings = tuple(
                        source_engine.embeddings(_engine_ring(target))
                    )

                    def embedding_at(position):
                        return self.Mor(target)(
                            engine_embeddings[int(position)]
                        )

                case _:
                    engine_embeddings = tuple(source_engine.embeddings(algebraic_numbers))

                    def embedding_at(position):
                        engine_embedding = engine_embeddings[int(position)]
                        return self.Mor(target).elementwise(
                            lambda element: target(
                                engine_embedding(
                                    _engine_element(self, self(element))
                                )
                            )
                        )

            positions = finite_ordered_set(range(len(engine_embeddings)))

            if source_engine is SageQQ:
                def embedding_position(embedding):
                    if (
                        not isinstance(embedding, (Morphism, CategoricalArrow))
                        or embedding.domain() is not self
                        or embedding.codomain() is not target
                        or positions.cardinality() != 1
                    ):
                        raise ValueError(f"{embedding} is not an embedding {self} -> {target}")
                    return positions[0]
            else:
                primitive = self.primitive_element()

                def embedding_position(embedding):
                    if (
                        not isinstance(embedding, (Morphism, CategoricalArrow))
                        or embedding.domain() is not self
                        or embedding.codomain() is not target
                    ):
                        raise ValueError(f"{embedding} is not an embedding {self} -> {target}")
                    primitive_image = embedding(primitive)
                    for position in positions:
                        if embedding_at(position)(primitive) == primitive_image:
                            return position
                    raise ValueError(
                        f"{embedding} is not one of the embeddings {self} -> {target}: it sends the primitive "
                        f"element {primitive} to {primitive_image}, which matches no embedding"
                    )

            return FiniteOrderedSets().from_indexed(
                positions,
                embedding_at,
                index_of=embedding_position,
                name=f"Embeddings of {self} into {target}",
            )

        def is_galois(self) -> bool:
            r"""Return whether ``K/QQ`` is Galois."""
            engine = _engine_ring(self)
            return True if engine is SageQQ else bool(engine.is_galois())

        def galois_group(self):
            r"""Return ``Gal(K/QQ)``; this name is reserved for Galois ``K``."""
            if not self.is_galois():
                raise ValueError(
                    f"{self} is not Galois over QQ, so Gal({self}/QQ) is not defined; "
                    "normal_closure_galois_group() gives the Galois group of its normal closure"
                )
            engine = _engine_ring(self)

            if engine is SageQQ:
                from sage.groups.perm_gps.permgroup_named import SymmetricGroup

                return _own_group(SymmetricGroup(1))
            return _own_group(engine.galois_group())

        def normal_closure(self):
            r"""Return a chosen normal closure of ``K/QQ``."""

            engine = _engine_ring(self)
            return self if engine is SageQQ else _own_ring(engine.galois_closure())

        def normal_closure_galois_group(self):
            r"""Return the Galois group of a chosen normal closure of ``K``."""
            return self.normal_closure().galois_group()

        def underlying_algebra(self, base_ring=None):
            r"""Return the selected integral form ``R[alpha]`` of this number field.

            For the currently represented archive specialization ``R=ZZ`` this
            is the order generated by the selected primitive element, not the
            maximal order.  Over ``QQ`` the selected finite algebra presentation
            is :meth:`as_algebra` itself.
            """
            integers = _owned_integers()
            rationals = _own_number_field(SageQQ)
            match base_ring:
                case None:
                    base_ring = integers
                case _:
                    pass
            match base_ring:
                case ring if ring is integers:
                    match self is rationals:
                        case True:
                            return integers
                        case False:
                            return self.order_generated_by(self.primitive_element())
                case ring if ring is rationals:
                    return self.as_algebra()
                case _:
                    assert base_ring is integers or base_ring is rationals, (
                        f"the underlying algebra of the number field {self} is defined here only over ZZ or QQ, not over {base_ring}"
                    )

        def base_change_functor(self, base_ring=None):
            r"""Return scalar extension from the selected base ring to ``QQ``.

            Applied to :meth:`underlying_algebra` over ``ZZ``, this is the
            existing algebra scalar-extension functor and reconstructs the
            selected ``QQ``-algebra presentation of the field.
            """
            from sage_extensions.categories.algebras.algebras import (
                Algebras,
            )

            integers = _owned_integers()
            rationals = _own_number_field(SageQQ)
            match base_ring:
                case None:
                    base_ring = integers
                case _:
                    pass
            match base_ring:
                case ring if ring is integers:
                    ring_map = integers.Mor(rationals)(lambda element: rationals(element))
                case ring if ring is rationals:
                    ring_map = rationals.Mor(rationals).identity()
                case _:
                    assert base_ring is integers or base_ring is rationals, (
                        f"base change of the number field {self} is defined here only from ZZ or QQ, not from {base_ring}"
                    )
            return Algebras(base_ring).Associative().Unital().Commutative().base_change_adjunction(ring_map).left_adjoint()

        def as_algebra(self):
            r"""Return this field with its selected finite ``QQ``-algebra presentation."""
            from sage_extensions.categories.algebras.free_algebras import (
                _presented_algebra_on_engine,
            )

            rationals = _own_number_field(SageQQ)
            engine = _engine_ring(self)
            if engine is SageQQ:
                return rationals

            presentation_lift = None
            finite_free_coordinates = None
            if not engine.is_absolute():
                # A relative generator need not generate K over QQ.  Sage's
                # absolute model supplies both the chosen absolute primitive
                # element in this same engine and exact conversion to its
                # one-variable QQ presentation.
                absolute = engine.absolute_field("absolute_generator")
                from_absolute, to_absolute = absolute.structure()
                primitive = from_absolute(absolute.gen())
                polynomial = absolute.defining_polynomial()
                labels = finite_ordered_set(("absolute_generator",))
                def presentation_lift(element):
                    return to_absolute(element).lift()

                def finite_free_coordinates(element):
                    return tuple(to_absolute(element))
                degree = int(engine.absolute_degree())
            else:
                primitive = engine.gen()
                polynomial = engine.defining_polynomial()
                labels = finite_ordered_set(engine.variable_names())
                degree = int(engine.degree())

            presentation = rationals.free_module(labels).symmetric_algebra()
            relation = _owned_engine_element(presentation,
                _engine_ring(presentation)(polynomial)
            )
            return _presented_algebra_on_engine(
                engine,
                presentation,
                (relation,),
                generator_values=(primitive,),
                finite_free_degree=degree,
                finite_free_generator=primitive,
                finite_free_coordinates=finite_free_coordinates,
                presentation_lift=presentation_lift,
            )

        def _module_basis_along(self, ring_map):
            r"""``K`` over ``QQ`` along the inclusion ``QQ -> K``: the basis selected by :meth:`as_algebra`.

            Implements the protected contract declared at
            ``OwnedRings.ParentMethods._module_basis_along``.  A unital ring
            map out of ``QQ`` is unique, so a ``ring_map`` starting at ``QQ``
            is the inclusion, along which :meth:`as_algebra` selects the power
            basis ``1, a, ..., a^{d-1}`` of an absolute primitive element
            ``a``.  Elements cross between ``K`` and that presentation through
            the identification :meth:`multiplication_morphism` uses.  A map
            out of any other field takes the general contract.
            """
            from sage_extensions.categories.modules.native_modules import (
                _NativeModuleBasis,
            )

            rationals = _own_number_field(SageQQ)
            match ring_map.domain() is rationals and self is not rationals:
                case False:
                    return super()._module_basis_along(ring_map)
            algebra = self.as_algebra()
            framing = algebra.framing_morphism()

            def coordinates(element):
                vector = framing.lift(_owned_engine_element(algebra, _engine_element(self, element)))
                return {label: vector(label) for label in vector.support().domain()}

            return _NativeModuleBasis(
                algebra.framing_source(),
                lambda label: _owned_engine_element(
                    self, _engine_element(algebra, algebra.module_generator(label))
                ),
                coordinates,
            )

    class ElementMethods:
        def inverse(self):
            r"""Return the multiplicative inverse of this nonzero field element."""

            return self.inverse_of_unit()

        @cached_method
        def multiplication_morphism(self):
            r"""Return multiplication by ``self`` on the selected finite ``QQ``-module presentation.

            A number field element is canonically a ``QQ``-linear endomorphism
            of its field.  The live field object keeps its ring identity, while
            :meth:`as_algebra` supplies the selected finite-free presentation
            used to represent this linear map.  No separate matrix representation is
            exposed: the matrix below is the matrix of this owned module
            morphism in that selected basis.
            """

            field = self.parent()
            algebra = field.as_algebra()
            multiplier = _owned_engine_element(algebra,
                _engine_element(field, self)
            )
            return algebra.module_category().Mor(algebra, algebra)(
                lambda label: multiplier * algebra.module_generator(label)
            )

        def multiplication_matrix(self):
            r"""Return the matrix of multiplication by ``self`` over ``QQ``."""

            return self.multiplication_morphism().matrix()


        def norm(self):
            r"""Return the field norm ``N_{K/QQ}(self)``.

            The norm is the determinant of the owned ``QQ``-linear
            multiplication endomorphism ``m_self : K -> K``.  This keeps the
            archived definition on the same mathematical map already exposed
            by :meth:`multiplication_morphism` instead of asking the private
            number-field computation for a second value.
            """

            return self.multiplication_morphism().determinant()

        def trace(self):
            r"""Return the field trace ``Tr_{K/QQ}(self)``.

            The trace is the trace of the owned ``QQ``-linear multiplication
            endomorphism ``m_self : K -> K``.
            """

            return self.multiplication_morphism().trace()

        def characteristic_polynomial(self):
            r"""Return the characteristic polynomial of multiplication by ``self`` over ``QQ``.

            Its degree is ``[K:QQ]`` even when ``self`` lies in a proper
            subfield.  This is therefore different from the minimal
            polynomial exactly in the cases where the chosen element does not
            generate the whole number field.
            """
            polynomial = self._backend().charpoly()
            return _owned_engine_element(polynomial.parent(), polynomial)

        def minimal_polynomial(self):
            r"""Return the minimal polynomial of ``self`` over ``QQ``."""
            return self.minpoly()

        def is_integral(self) -> bool:
            r"""Return whether ``self`` is an algebraic integer."""
            return bool(self._backend().is_integral())

        def conjugates(self, target):
            r"""Return the images of ``self`` under all owned embeddings into ``target``.

            The embeddings are the index set.  Two embeddings can have the
            same value on a nonprimitive element, so the result is an indexed
            family rather than a set of values; this retains multiplicity and
            the embedding that produced each conjugate.
            """
            field = self.parent()
            embeddings = field.embeddings(target)
            return finite_indexed_family(
                embeddings,
                lambda embedding: embedding(self),
                name=f"Conjugates of {self} in {target}",
            )


class NumberFieldsWithChosenPrimitiveElement(OwnedCategory):
    r"""Number fields carrying the primitive element selected by their presentation."""

    _certifying_predicate = "_preamble_has_chosen_primitive_element"

    def an_object(self):
        r"""A quadratic field with its selected generator."""
        return QuadraticField(2, "a")

    @classmethod
    def _repr_object_names(cls):
        return "number fields with a chosen primitive element"

    def super_categories(self):
        return [OwnedNumberFields()]

    class ParentMethods:
        def primitive_element(self):
            r"""Return the selected primitive element ``alpha``."""
            return self._from_engine_element(_engine_ring(self).gen())

        def defining_polynomial(self):
            r"""Return the owned defining polynomial of the selected primitive element."""

            polynomial = _engine_ring(self).defining_polynomial()
            parent = _own_ring(polynomial.parent())
            return _owned_engine_element(parent, polynomial)

        def embedding_images(self, target):
            r"""Return the images of the selected primitive element under ``K -> target``."""

            primitive = self.primitive_element()
            embeddings = self.embeddings(target)
            return FiniteOrderedSets().from_indexed(
                embeddings,
                lambda embedding: embedding(primitive),
                name="Primitive-element embedding images",
            )


class OrdersWithChosenIntegralBasis(OwnedCategory):
    r"""Number-field orders carrying their selected integral basis."""

    _certifying_predicate = "_preamble_is_number_field_order"

    def an_object(self):
        r"""The maximal order of a quadratic field with its selected integral basis."""
        return QuadraticField(5, "a").ring_of_integers()

    @classmethod
    def _repr_object_names(cls):
        return "orders with a chosen integral basis"

    def super_categories(self):

        integers = _owned_integers()
        return [
            OwnedOrders(),
            FinitelyGeneratedFreeModules(integers),
        ]

    class ParentMethods:
        def base_ring(self):

            return _owned_integers()

        algebra_base_ring = base_ring

        def localization(self, *elements):
            from sage_extensions.categories.rings.commutative_algebra import _localization

            return _localization(self, *elements)

        localize = localization

        def localize_at_prime(self, prime):
            from sage_extensions.categories.rings.commutative_algebra import (
                _prime_localization_from_input,
            )

            return _prime_localization_from_input(self, prime)

        localization_at_prime = localize_at_prime

        def base_change(self, ring_map):
            if _engine_ring(ring_map.domain()) is not SageZZ:
                raise ValueError(
                    f"cannot base change the order {self} along {ring_map}: an order is a ZZ-algebra, "
                    f"so the ring map must start at ZZ, but it starts at {ring_map.domain()}"
                )
            target = _engine_ring(ring_map.codomain())
            if target is SageZZ:
                return self
            if target is SageQQ:

                field = _own_number_field(_engine_ring(self).fraction_field())
                return field.as_algebra()
            assert target is SageZZ or target is SageQQ, (
                f"base change of the order {self} is computed only along ZZ -> ZZ and ZZ -> QQ, "
                f"not along ZZ -> {ring_map.codomain()}"
            )

        def integral_basis(self):
            return self.module_generators()

        def module_rank(self):
            engine = _engine_ring(self)
            return cardinal(1 if engine is SageZZ else engine.rank())


__all__ = [
    "NumberFieldsWithChosenPrimitiveElement",
    "OrdersWithChosenIntegralBasis",
    "OwnedNumberFields",
]
