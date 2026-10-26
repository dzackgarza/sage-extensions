r"""Fraction-field quotients ``K / a`` as modules over the base ring.

The owned quotient is a parent built through the owned module chain; Sage's
``QmodnZ`` is its private engine and its elements are engine elements, the
shape of the owned ring views.
"""

from sage_extensions.categories.modules.pure.modules import ModuleSubobjects
from sage_extensions.categories.modules.pure.modules import ModulesWithChosenFinitePresentation

from sage.arith.functions import lcm
from sage.arith.misc import gcd
from sage.categories.category import Category
from sage.categories.morphism import SetMorphism
from sage.groups.additive_abelian.qmodnz import QmodnZ
from sage.misc.cachefunc import cached_function
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import ModuleElement
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.structure.richcmp import op_EQ, op_NE, richcmp
from sage.structure.sage_object import SageObject

from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import aleph0
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category import _object_of, owned_category_join


class FractionFieldQuotients(OwnedCategoryOverBaseRing):
    r"""Modules ``Frac(R) / a`` for a fractional ideal ``a`` of ``R``.

    Sage's :class:`QmodnZ` remains the native engine for ``R = ZZ``.  Over a
    general domain an element is represented by a chosen lift in ``Frac(R)``;
    equality is the defining quotient relation ``x-y in aR``.
    """

    class ElementMethods(ModuleElement):
        r"""What a class in \(\operatorname{Frac}(R)/R\) is.

        A class in \(K/R\) is an element of a module over \(R\), so it
        subtracts and is scaled like one.  ``Element`` leaves ``x - y``
        raising, and the polarization \(q(x+y)-q(x)-q(y)\) of a discriminant
        quadratic form is one of the places that reaches it.
        """

        def __init__(self, parent, backend_element) -> None:
            ModuleElement.__init__(self, parent)
            self._backend_element = backend_element

        def _backend(self):
            return self._backend_element

        def _add_(self, other):
            parent = self.parent()
            match parent._engine:
                case None:
                    return parent._from_engine_element(
                        parent._lift_backend(self._backend())
                        + parent._lift_backend(other._backend())
                    )
                case _:
                    return parent._from_engine_element(
                        self._backend() + other._backend()
                    )

        def _neg_(self):
            parent = self.parent()
            match parent._engine:
                case None:
                    return parent._from_engine_element(-parent._lift_backend(self._backend()))
                case _:
                    return parent._from_engine_element(-self._backend())

        def _lmul_(self, scalar):
            parent = self.parent()
            match parent._engine:
                case None:
                    field = parent.fraction_field()
                    return parent._from_engine_element(
                        field(parent.base_ring()(scalar)) * parent._lift_backend(self._backend())
                    )
                case _:
                    return parent._from_engine_element(
                        _engine_element(parent.base_ring(), scalar) * self._backend(),
                    )

        _rmul_ = _lmul_

        def __rmul__(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def _richcmp_(self, other, op):
            if other.parent() is not self.parent() or other.parent() is not self.parent():
                return NotImplemented
            match self.parent()._engine:
                case None:
                    match op:
                        case _ if op == op_EQ:
                            return self == other
                        case _ if op == op_NE:
                            return self != other
                        case _:
                            return NotImplemented
                case _:
                    return richcmp(self._backend(), other._backend(), op)

        def __eq__(self, other):
            return (
                other.parent() is self.parent()
                and other.parent() is self.parent()
                and self.parent()._classes_equal(self._backend(), other._backend())
            )

        def __ne__(self, other):
            return not self == other

        def __hash__(self):
            return self.parent()._class_hash(self._backend())

        def lift(self):
            r"""Return this class's representative in \(K\) under the chosen section.

            A coset of \(K/R\) has no canonical element.  ``QQ/nZZ`` retains the
            native ``QmodnZ`` section; the general quotient retains the lift used
            to construct the class.  Every equality is nevertheless quotient
            equality, not equality of these representatives.
            """
            return self.parent()._lift_backend(self._backend())

        def additive_order(self):
            parent = self.parent()
            match parent._engine:
                case None:
                    match self == parent.zero():
                        case True:
                            return _owned_engine_element(_owned_integers(), SageZZ.one())
                        case False:
                            raise TypeError(
                                f"the additive order of {self} in {parent} has no selected computation over "
                                f"{parent.base_ring()}; the represented quotient relation alone does not choose "
                                "a denominator-ideal algorithm"
                            )
                case _:
                    order = SageZZ(self._backend().additive_order())
                    return _owned_engine_element(parent.base_ring(), order)

        def _repr_(self):
            return f"[{self.lift()}] in {self.parent()}"

        def _latex_(self):
            return rf"[{self.lift()}]\in {self.parent()}"

    def an_object(self):
        r"""``Frac(R)/R``."""
        return self()

    def _call_(self, modulus=1):
        r"""Return ``Frac(R) / modulus*R``."""
        base_ring = self.base_ring()
        match _engine_ring(base_ring) is SageZZ:
            case True:
                return _from_qmodnz_backend(
                    QmodnZ(_engine_element(base_ring, base_ring(modulus)))
                )
            case False:
                return _owned_general_fraction_field_quotient(
                    base_ring,
                    base_ring(modulus),
                )

    def _repr_object_names(self):
        return f"fraction-field quotients over {self.base_ring()}"

    def super_categories(self):

        return [Modules(self.base_ring())]

    class ParentMethods:
        _derived_construction_parameters = frozenset({"base_ring"})

        def __init__(self, engine=None, base_ring=None, modulus=None, **rest) -> None:
            match engine:
                case None:
                    ring = _own_ring(base_ring)
                    field = ring.fraction_field()
                    self._engine = None
                    self._fraction_field_modulus = field(modulus)
                    super().__init__(base_ring=ring, **rest)
                case _:
                    self._engine = engine
                    ring = _owned_integers()
                    field = ring.fraction_field()
                    self._fraction_field_modulus = _owned_engine_element(field, SageQQ(engine.n))
                    super().__init__(
                        base_ring=ring,
                        module_generating_set=Sets.Δ[aleph0],
                        module_generator_function=self._divisibility_chain_generator,
                        **rest,
                    )

        def _selected_module_coefficients(self, element):
            r"""Return finite support in the chosen factorial divisibility framing."""
            element = self(element)
            if element == self.zero():
                return {}
            field = self.fraction_field()
            representative = self.lift(element)
            denominator = int(representative.denominator())
            factorial = 1
            index = 0
            while factorial % denominator:
                index += 1
                factorial *= index + 1
            coefficient = self.base_ring()(representative * field(factorial))
            label = self.module_generating_set()(index)
            return {} if coefficient == self.base_ring().zero() else {label: coefficient}

        def _from_engine_element(self, value):
            match self._engine:
                case None:
                    field = self.fraction_field()
                    match element_parent(value):
                        case parent if parent is field:
                            representative = value
                        case parent if parent is not None and parent in OwnedRings():
                            representative = field(value)
                        case _:
                            representative = _owned_engine_element(field, value)
                    return self.element_class(self, representative)
                case engine:
                    return self.element_class(self, engine(value))

        def _engine_element(self, value):
            value = self(value)
            return value._backend()

        def _element_constructor_(self, value):
            if isinstance(value, self.category().ElementType) and value.parent() is self:
                return value
            parent = element_parent(value)
            if parent is not None:
                if parent in OwnedRings():
                    return self._from_engine_element(_engine_element(parent, value))
                if isinstance(value, SageObject):
                    raise TypeError(
                        f"cannot convert {value!r} into {self}: it is an element of {parent}, "
                        "which is not a ring of this session"
                    )
            if isinstance(value, SageObject):
                raise TypeError(
                    f"cannot convert {value!r} into {self}: it is not a number or an element "
                    "of a ring of this session"
                )
            return self._from_engine_element(value)

        def __call__(self, value):
            r"""Construct a class in ``K/R`` without Sage coercion discovery.

            A session's rational is an element of the owned fraction field, which
            Sage's coercion graph has never heard of, so asking it for a conversion
            map fails before this parent's own constructor is reached.
            """
            return self._element_constructor_(value)

        def __contains__(self, value) -> bool:
            return isinstance(value, self.category().ElementType) and value.parent() is self

        def zero(self):
            match self._engine:
                case None:
                    return self._from_engine_element(self.fraction_field().zero())
                case engine:
                    return self._from_engine_element(engine.zero())

        def an_element(self):
            match self._engine:
                case None:
                    return self.zero()
                case _:
                    return self.module_generator(self.module_generating_set()(1))

        def _repr_(self):
            return f"{self.fraction_field()} / ({self.modulus()}){self.base_ring()}"

        def _latex_(self):
            return rf"{self.fraction_field()} / ({self.modulus()}){self.base_ring()}"
        def base_ring(self):
            return self.base()

        def fraction_field(self):
            return self.base_ring().fraction_field()

        def modulus(self):
            r"""Return a generator of the fractional ideal being quotiented out."""
            return self._fraction_field_modulus

        def lift(self, element):
            r"""Return the selected representative of ``element`` in the fraction field."""
            element = self(element)
            return self._lift_backend(element._backend())

        def _lift_backend(self, backend):
            match self._engine:
                case None:
                    return self.fraction_field()(backend)
                case _:
                    return _owned_engine_element(self.fraction_field(), backend.lift())

        def _classes_equal(self, left, right) -> bool:
            match self._engine:
                case _ if self._engine is not None:
                    return bool(left == right)
                case None:
                    difference = self.fraction_field()(left - right)
                    modulus = self.modulus()
                    match modulus.is_zero():
                        case True:
                            return bool(difference.is_zero())
                        case False:
                            return bool((difference / modulus) in self.base_ring())

        def _class_hash(self, backend):
            match self._engine:
                case None:
                    # Equality is modulo ``aR`` and a general domain need not
                    # expose canonical coset representatives.  A constant
                    # parent hash is therefore the correct hash contract:
                    # equal classes always hash equally, without inventing a
                    # normalization that is absent from the mathematics.
                    return hash(id(self))
                case _:
                    return hash((id(self), backend))

        def divisibility_chain(self, index):
            r"""Return the chosen cofinal divisibility chain element ``d_index``."""
            assert _engine_ring(self.base_ring()) is SageZZ, (
                f"no cofinal divisibility chain for {self}: the chain d_k = (k+1)! is "
                f"defined only over ZZ, and the base ring is {self.base_ring()}"
            )
            return self.base_ring()(int(index) + 1).factorial()

        def _divisibility_chain_generator(self, label):
            r"""Return the class of the reciprocal of the chain element at ``label``."""
            denominator = self.divisibility_chain(label)
            field = self.fraction_field()
            return self(field.one() / field(denominator))

        def projection_from_fraction_field(self):
            r"""Return the quotient map ``Frac(R) -> Frac(R) / a`` as an owned set map.

            The fraction field currently has no canonical ``R``-module structure
            for arbitrary ``R`` at this layer, so the underlying map is stated
            in the owned category of sets rather than returning Sage's coercion
            map.  Module-valued consumers should use the scalar-restricted
            fraction-field module construction.
            """

            return SetMorphism(
                Sets().Mor(self.fraction_field(), self),
                lambda element: self(element),
            )

        def subobject_on(self, module_generators):
            r"""Return the cyclic submodule generated by finitely many classes.

            For ``QQ / n ZZ`` with ``n != 0``, let ``x_1,...,x_r`` be the
            selected lifts.  The subgroup of ``QQ`` generated by these lifts
            and ``n`` is ``g ZZ`` for one positive rational ``g``.  Hence the
            generated submodule is

            ``g ZZ / n ZZ ~= ZZ / (n/g) ZZ``.

            The source is returned as an actual module subobject carrying its
            inclusion into this quotient.  This PID classification is the
            reason the operation is exact despite the ambient module's
            countable framing.
            """
            match self._engine:
                case None:
                    raise TypeError(
                        f"cannot classify the submodule of {self} generated by {tuple(module_generators)}: "
                        "the selected gcd/divisibility classification is the QQ/nZZ computation and no "
                        f"general submodule-classification algorithm for Frac({self.base_ring()})/a{self.base_ring()} "
                        "has been selected"
                    )
                case _:
                    pass
            classes = tuple(self(element) for element in module_generators)
            assert not self.modulus().is_zero(), (
                f"cannot classify the submodule of {self} generated by {classes}: the "
                "classification gZZ/nZZ ~= ZZ/(n/g)ZZ needs a nonzero modulus n, and here n = 0 "
                "(a finitely generated submodule of QQ itself is free)"
            )

            field = self.fraction_field()
            values = tuple(self.lift(element) for element in classes) + (
                self.modulus(),
            )
            denominator = lcm(tuple(int(value.denominator()) for value in values))
            numerators = tuple(
                SageZZ(_engine_element(field, value) * denominator)
                for value in values
            )
            generator_numerator = abs(gcd(numerators))
            generator = _owned_engine_element(field,
                SageQQ(generator_numerator) / SageQQ(denominator)
            )
            # ``g`` divides every lift and the modulus, so ``n/g`` is integral.
            order_in_field = self.modulus() / generator
            assert int(order_in_field.denominator()) == 1, (
                f"the submodule of {self} generated by {classes} is gZZ/nZZ with g = {generator}, "
                f"but g does not divide the modulus n = {self.modulus()}: n/g = {order_in_field} "
                "is not an integer"
            )
            order = self.base_ring()(order_in_field)
            # gZ/nZ is R/(n/g) on one generator: the cokernel of the relation
            # morphism r: R -> R, e |-> (n/g) e.
            line = self.base_ring().free_module(1)
            label = line.module_generating_set()[0]
            relations = line.module_category().Mor(line, line)(
                {label: line.scalar_multiple(order, line.module_generator(label))}
            )
            image = self(generator)

            def lift_from_ambient(subobject, element):
                # ``[x]`` lies in ``gZ/nZ`` exactly when the lift ``x`` lies in
                # ``gZ + nZ = gZ``, that is when ``x/g`` is integral.
                element = self(element)
                quotient = self.lift(element) / generator
                if int(quotient.denominator()) != 1:
                    return None
                return subobject.scalar_multiple(
                    self.base_ring()(quotient),
                    subobject.module_generator(label),
                )

            subobject = ModulesWithChosenFinitePresentation(self.base_ring())(
                relations,
                category=owned_category_join((
                    ModuleSubobjects(self.base_ring()),
                    Modules(self.base_ring()).FinitelyPresented().Torsion(),
                )),
                subobject_ambient=self,
                subobject_generator_images=lambda _label: image,
                subobject_lift=lift_from_ambient,
            )
            return subobject






@cached_function
def _owned_fraction_field_quotient(engine: QmodnZ) -> ObjectOfCategory:
    base_ring = _owned_integers()
    placement = [FractionFieldQuotients(base_ring)]
    if not engine.n.is_zero():
        placement.append(Modules(base_ring).Torsion())
    return _object_of(owned_category_join(placement), engine=engine)


@cached_function
def _owned_general_fraction_field_quotient(base_ring, modulus) -> ObjectOfCategory:
    r"""Return represented ``Frac(R)/(modulus)R`` without a specialized backend."""
    ring = _own_ring(base_ring)
    field = ring.fraction_field()
    modulus = field(modulus)
    placement = [FractionFieldQuotients(ring)]
    match modulus.is_zero():
        case True:
            pass
        case False:
            placement.append(Modules(ring).Torsion())
    return _object_of(
        owned_category_join(placement),
        engine=None,
        base_ring=ring,
        modulus=modulus,
    )


def _from_qmodnz_backend(quotient):
    r"""Return the owned ``QQ / n ZZ`` over the Sage parent ``quotient``."""
    if quotient in FractionFieldQuotients(_owned_integers()):
        return quotient
    if not isinstance(quotient, QmodnZ):
        raise TypeError(f"{quotient!r} is not a quotient QQ/nZZ")
    return _owned_fraction_field_quotient(quotient)


__all__ = [
    "FractionFieldQuotients",
]
