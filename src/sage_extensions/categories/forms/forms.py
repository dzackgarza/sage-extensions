r"""Exact pairings and quadratic forms through their universal module objects.

Whenever the universal object is represented, a pairing is an element of
``Hom_R(X tensor_R Y, W)`` and a quadratic map an element of
``Hom_R(Gamma^2(M), W)``.  Otherwise the evaluation retains the original
modules and value object; its pointwise module structure is constructed
through the module owner, without assigning it a finite presentation.
"""

from collections.abc import Iterable
from itertools import chain, combinations, product

from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.modules.framed.framed_free_modules import (
    FramedFreeModules,
)
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    TensorProductModuleMor,
    TensorProductModuleMorphism,
)
from sage_extensions.categories.modules.powers import (
    DividedSquareModules,
    QuadraticModuleMor,
    QuadraticModuleMorphism,
)
from sage_extensions.categories.modules.pure.modules import (
    InternalMorModules,
    Modules,
    ModulesWithChosenFinitePresentation,
    TensorProductModules,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
)
from sage_extensions.categories.sets.coordinate_families import (
    _coerce_family_value as _coerce_value,
)
from sage_extensions.categories.sets.coordinate_families import (
    _coordinate_family_from_family,
)
from sage_extensions.categories.sets.coordinate_families import (
    _coordinate_family_from_function,
)
from sage_extensions.categories.sets.coordinate_families import (
    _coordinate_family_from_rows,
)
from sage_extensions.categories.sets.coordinate_families import (
    _coordinate_pair,
)
from sage_extensions.categories.sets.coordinate_families import (
    _coordinate_rows,
)
from sage_extensions.categories.sets.coordinate_families import (
    _finite_framing,
)
from sage_extensions.categories.sets.indexed_families import IndexedFamily
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.logic import AtomicProposition, Predicate, conjunction, negation
from sage_extensions.owned_category import _object_of
from sage_extensions.tensors.tensor import (
    Tensor,
    _covariant_bilinear_coordinate_rows,
    tensor,
)

# Historical form vocabulary now names the universal module-Mor owners.
# These are aliases, not parallel form implementations.
PairingMorphism = TensorProductModuleMorphism
BilinearFormMorphism = TensorProductModuleMorphism
BilinearFormMor = TensorProductModuleMor
QuadraticFormMor = QuadraticModuleMor


class BilinearFormMors(OwnedCategoryOverBaseRing):
    r"""Diagonal pairing Mor objects carrying the bilinear-form operations."""

    def _repr_object_names(self):
        return f"bilinear-form Mor objects over {self.base_ring()}"

    def super_categories(self):

        return [InternalMorModules(self.base_ring())]

    class ElementMethods:
        @cached_method
        def gram_tensor(self):
            if self.left_module() is not self.right_module():
                raise TypeError(
                    f"the Gram tensor of {self} needs a form on one module, but it pairs {self.left_module()} "
                    f"with {self.right_module()}"
                )
            if self.codomain() not in OwnedRings():
                raise TypeError(
                    f"the Gram tensor of {self} needs values in a ring, but its values lie in {self.codomain()}"
                )

            return self._as_numerical_tensor()

        def descends_along(self, morphism, value_projection) -> bool:
            r"""Whether this bilinear form descends through ``coker(morphism)`` after projecting values.

            The projected form must vanish on the relation submodule in both
            arguments: ``b(r, x) = b(x, r) = 0`` for every relation ``r`` and
            every module element ``x``. This is the condition that makes the
            value independent of both chosen quotient lifts.
            """
            return _bilinear_form_descends_along(self, morphism, value_projection)

        def descend_along(self, morphism, value_projection):
            r"""Return the induced bilinear form on ``coker(morphism)``.

            Raises ``ValueError`` unless the projected form vanishes on the
            relation submodule in both arguments.
            """
            return _descended_bilinear_form(self, morphism, value_projection)


def _bilinear_classifier_is_represented(left_module, right_module, value_module) -> bool:
    r"""Whether ``X x Y -> W`` is represented by ``Hom_R(X tensor Y, W)``.

    The module owner represents the algebraic tensor product for arbitrary
    represented modules, including the unframed quotient route. A bilinear
    form is always a module-Mor, never a separate extensional form object.
    """
    ring = left_module.base_ring()
    match right_module.base_ring() == ring, value_module in Modules(ring):
        case True, True:
            return True
        case _:
            return False


def _quadratic_classifier_is_represented(module, value_module) -> bool:
    r"""Whether ``M -> W`` is represented by ``Hom_R(Gamma^2(M), W)``."""
    ring = module.base_ring()
    match value_module in Modules(ring):
        case True:
            pass
        case False:
            return False
    return (
        module in FramedFreeModules(ring)
        or module in ModulesWithChosenFinitePresentation(ring)
    )


def _form_value_image(form):
    r"""Return the represented submodule generated by a finite form-value table."""

    codomain = form.codomain()
    value_module = codomain.regular_module() if codomain in OwnedRings() else codomain
    return value_module.subobject_on(
        tuple(
            value_module(value) for value in form.values_matrix()
        )
    )


def _bilinear_form_descends_along(form, morphism, value_projection) -> bool:
    r"""Decide whether the projected pairing descends through a represented cokernel.

    Write ``i:N -> M`` for ``morphism`` and ``p:W -> V`` for
    ``value_projection``. The induced pairing on ``coker(i)`` exists exactly
    when ``p(b(i(n),m)) = p(b(m,i(n))) = 0`` for every ``n`` and ``m``:
    changing either quotient lift then leaves the value unchanged. Since
    ``b`` and ``p`` are linear in each relevant argument, it suffices to test
    the selected finite generating families of ``N`` and ``M``. The framing
    requirement is deliberate; this routine does not claim a decision
    procedure for infinitely generated modules.
    """
    module = form.module()
    if morphism.codomain() is not module:
        raise ValueError(
            f"the form {form} on {module} descends to a quotient only along a map into {module}, but "
            f"{morphism} ends at {morphism.codomain()}"
        )
    if value_projection.domain() is not form.codomain():
        raise ValueError(
            f"the values of {form} lie in {form.codomain()}, so the projection of values must start there, "
            f"but {value_projection} starts at {value_projection.domain()}"
        )

    relation_labels = _finite_framing(morphism.domain())
    module_labels = _finite_framing(module)
    zero = value_projection.codomain().zero()
    relations = tuple(
        morphism(morphism.domain().module_generator(label))
        for label in relation_labels
    )
    generators = tuple(module.module_generator(label) for label in module_labels)
    return all(
        value_projection(form(relation, generator)) == zero
        and value_projection(form(generator, relation)) == zero
        for relation in relations
        for generator in generators
    )


def _descended_bilinear_form(form, morphism, value_projection):
    r"""Construct the descended form on the actual represented cokernel.

    The selected preimages are taken through the actual cokernel projection,
    not by identifying the quotient's generator labels with those of the
    source. The two-slot criterion checked below makes the projected value
    independent of either selected preimage.
    """
    if not _bilinear_form_descends_along(form, morphism, value_projection):
        raise ValueError(
            f"the form {form} does not descend to coker({morphism}): after value projection, the form must "
            f"vanish on the image of {morphism} in both arguments"
        )

    quotient = morphism.cokernel()
    quotient_projection = morphism.cokernel_projection()

    def selected_lift(element):
        return quotient_projection.lift(element)

    return quotient.bilinear_forms(value_projection.codomain())(
        lambda left, right: value_projection(
            form(selected_lift(left), selected_lift(right))
        )
    )


class _CallableFormMethods:
    r"""A bilinear or quadratic map given by its Gram tensor or by its evaluation.

    Used only when no universal classifier is represented.  On finitely
    framed modules with values in a ring, a bilinear form is its Gram tensor
    ``G`` in ``X^* \otimes Y^*``, and ``b(x, y) = G(x, y)`` is one contraction
    (`OWN-24`); a quadratic map given by coordinates is ``q(x) = G(x, x)`` for
    its chosen symmetric bilinear lift ``G``.  Any other map is given by its
    evaluation, and for a quadratic map built from coordinates with values
    outside a ring, also by the evaluation of its chosen lift.
    """

    def _coordinate_vector(self, module, element):
        r"""The coordinates of ``element`` on the finite framing of ``module``, over the values."""
        return tensor.vector(self.codomain(), tuple(module.framing_morphism().lift(element)))

    def _contract_gram_tensor(self, left, right):
        r"""``G(x, y)``: the defining Gram tensor contracted with the coordinates of ``x`` and ``y``."""
        return self._defining_gram_tensor.contract(
            self._coordinate_vector(self.left_module(), left),
            self._coordinate_vector(self.right_module(), right),
        )

    def _evaluate(self, *arguments):
        r"""The value of this map: a contraction of its Gram tensor, else its evaluation."""
        match self._defining_gram_tensor, self.parent().kind():
            case None, _:
                return self._evaluation(*arguments)
            case _, "quadratic":
                (element,) = arguments
                return self._contract_gram_tensor(element, element)
            case _:
                return self._contract_gram_tensor(*arguments)

    def _evaluate_lift(self, left, right):
        r"""The chosen bilinear lift of this quadratic map at ``(x, y)``."""
        match self._defining_gram_tensor:
            case None:
                return self._lift_evaluation(left, right)
            case _:
                return self._contract_gram_tensor(left, right)

    def _gram_coordinate_values(self):
        r"""The entries ``G[i, j]`` of the defining Gram tensor, indexed by the two framings."""
        gram = self._defining_gram_tensor
        left_labels = _finite_framing(self.left_module())
        right_labels = _finite_framing(self.right_module())
        return _coordinate_family_from_rows(
            left_labels,
            right_labels,
            self.codomain(),
            (
                (gram[i, j] for j in range(int(right_labels.cardinality())))
                for i in range(int(left_labels.cardinality()))
            ),
            name=f"Gram tensor of a {self.parent().kind()} form",
        )

    def left_module(self):
        return self.parent().left_module()

    def right_module(self):
        return self.parent().right_module()

    def module(self):
        if self.parent().kind() == "quadratic":
            return self.left_module()
        if self.left_module() is not self.right_module():
            raise TypeError(
                f"{self} pairs {self.left_module()} with {self.right_module()}, so it is not a form on one module"
            )
        return self.left_module()

    def codomain(self):
        return self.parent().codomain()

    def classifying_morphism(self):
        r"""The linear map out of the tensor product or divided square."""
        match self.parent().kind():
            case "bilinear":
                tensor_product = self.left_module().module_category().tensor_product(
                    (self.left_module(), self.right_module())
                )
                return tensor_product.from_bilinear_map(self.codomain(), self)
            case "quadratic":
                square = self.module().divided_square()
                return square.from_quadratic(self, self.codomain())

    def __call__(self, *arguments):
        if self.parent().kind() == "quadratic":
            if len(arguments) != 1:
                raise TypeError(
                    f"the quadratic form {self} takes one element of {self.module()}, but got {len(arguments)} arguments"
                )
            element = arguments[0]
            if element not in self.module():
                raise TypeError(
                    f"the quadratic form {self} is defined on {self.module()}, and {element} is not in it"
                )
            return _coerce_value(self.codomain(), self._evaluate(element))
        if len(arguments) != 2:
            raise TypeError(f"the pairing {self} takes two arguments, but got {len(arguments)}")
        left, right = arguments
        if left not in self.left_module() or right not in self.right_module():
            raise TypeError(
                f"the pairing {self} takes an element of {self.left_module()} and an element of "
                f"{self.right_module()}, but got {left} and {right}"
            )
        return _coerce_value(self.codomain(), self._evaluate(left, right))

    def norm(self, element):
        if self.parent().kind() != "bilinear" or self.left_module() is not self.right_module():
            raise TypeError(
                f"the norm b(x, x) needs a bilinear form on one module, but {self} is not one"
            )
        return self(element, element)

    def coordinate_values(self):
        if self.parent().kind() != "bilinear":
            raise TypeError(
                f"{self} is a quadratic form, so it has no bilinear coordinate values; use lift_coordinate_values()"
            )
        if self._defining_gram_tensor is not None:
            return self._gram_coordinate_values()
        labels = _finite_framing(self.module())
        return _coordinate_family_from_function(
            labels,
            labels,
            self.codomain(),
            lambda left_label, right_label: self(
                self.module().module_generator(left_label),
                self.module().module_generator(right_label),
            ),
            name="Extensional bilinear coordinate values",
        )

    def has_selected_bilinear_lift(self) -> bool:
        r"""Whether this quadratic map retains a chosen bilinear lift."""
        return self.parent().kind() == "quadratic" and (
            self._defining_gram_tensor is not None or self._lift_evaluation is not None
        )

    def lift_coordinate_values(self):
        if not self.has_selected_bilinear_lift():
            raise TypeError(
                f"{self} is not a quadratic form with a chosen bilinear lift, so it has no lift coordinate values"
            )
        if self._defining_gram_tensor is not None:
            return self._gram_coordinate_values()
        labels = _finite_framing(self.module())
        return _coordinate_family_from_function(
            labels,
            labels,
            self.codomain(),
            lambda left_label, right_label: self._lift_evaluation(
                self.module().module_generator(left_label),
                self.module().module_generator(right_label),
            ),
            name="Extensional quadratic-lift coordinate values",
        )

    def lift_pairing(self, left, right):
        if not self.has_selected_bilinear_lift():
            raise TypeError(f"{self} is not a quadratic form with a chosen bilinear lift")
        return _coerce_value(self.codomain(), self._evaluate_lift(left, right))

    def lift_form(self):
        r"""Return the chosen bilinear lift of this quadratic form.

        This is defined only when the quadratic form was constructed from
        finite symmetric bilinear coordinate data.  It is the actual bilinear
        form whose diagonal recovers the quadratic form, and is distinct from
        :meth:`polar_form`, which is twice this lift in the ordinary
        characteristic-not-two situation.
        """
        if not self.has_selected_bilinear_lift():
            raise TypeError(f"{self} is not a quadratic form with a chosen bilinear lift")
        forms = self.module().bilinear_forms(self.codomain())
        match self._defining_gram_tensor:
            case None:
                return forms(lambda left, right: self._lift_evaluation(left, right))
            case gram:
                return forms(gram)

    @cached_method
    def gram_tensor(self):
        r"""The Gram tensor ``G[i, j] = b(e_i, e_j)`` on the finite framing.

        For a form defined by its Gram tensor, that tensor.  For a form given
        by its evaluation, pairing the framing generators is the definition.
        """
        if self._defining_gram_tensor is not None:
            return self._defining_gram_tensor
        if self.codomain() not in OwnedRings():
            raise TypeError(
                f"the Gram tensor of {self} needs values in a ring, but its values lie in {self.codomain()}"
            )
        values = (
            self.lift_coordinate_values()
            if self.parent().kind() == "quadratic"
            else self.coordinate_values()
        )
        labels = _finite_framing(self.module())
        rank = int(labels.cardinality())
        return tensor(
            self.codomain(),
            (),
            (rank, rank),
            (
                _coordinate_pair(values, labels[i], labels[j])
                for i in range(rank)
                for j in range(rank)
            ),
        )

    def values_matrix(self):
        r"""Return the finite values indexed by the selected framing square."""
        if self.parent().kind() != "bilinear":
            raise TypeError(
                f"{self} is a quadratic form; its matrix of values is computed from its morphism on the "
                "divided square"
            )
        return self.coordinate_values()

    def image(self):
        r"""Return the owned submodule generated by all values of this form."""
        return _form_value_image(self)

    def polar_form(self):
        if self.parent().kind() == "quadratic":
            return self.module().bilinear_forms(self.codomain())(
                lambda left, right: self(left + right) - self(left) - self(right)
            )
        if self.left_module() is not self.right_module():
            raise TypeError(
                f"the polar form needs a bilinear form on one module, but {self} pairs {self.left_module()} "
                f"with {self.right_module()}"
            )
        return self.module().bilinear_forms(self.codomain())(
            lambda left, right: 2 * self(left, right)
        )

    def b(self, left, right):
        if self.parent().kind() == "quadratic":
            return self.polar_form()(left, right)
        return self(left, right)

    def pullback(self, morphism):
        if morphism.codomain() is not self.module():
            raise ValueError(
                f"the pullback f^* b of the form {self} needs f to end at {self.module()}, but {morphism} ends "
                f"at {morphism.codomain()}"
            )
        if self.parent().kind() == "quadratic":
            return morphism.domain().quadratic_map(
                self.codomain(),
                lambda element: self(morphism(element)),
            )
        return morphism.domain().bilinear_forms(self.codomain())(
            lambda left, right: self(morphism(left), morphism(right))
        )

    def descends_along(self, morphism, value_projection) -> bool:
        r"""Whether this bilinear form descends to the cokernel after value projection.

        Descent requires both ``b(i(n), x) = 0`` and ``b(x, i(n)) = 0`` for
        all relation elements ``i(n)`` and all ``x``.
        """
        assert self.parent().kind() == "bilinear", (
            f"descent of {self} along {morphism} is computed here only for a bilinear form, but {self} is "
            "quadratic"
        )
        return _bilinear_form_descends_along(self, morphism, value_projection)

    def descend_along(self, morphism, value_projection):
        r"""Construct the descended form, requiring relations to vanish in both slots."""
        assert self.parent().kind() == "bilinear", (
            f"descent of {self} along {morphism} is computed here only for a bilinear form, but {self} is "
            "quadratic"
        )
        return _descended_bilinear_form(self, morphism, value_projection)

    def __eq__(self, other) -> bool | Predicate:
        r"""Equality of two maps of this space, decided on finitely many generators.

        A bilinear map is determined by its values on pairs of module generators,
        and a quadratic map ``q`` by ``q(s)`` and ``q(s + t)`` on generators, because
        ``q(\sum_s a_s s) = \sum_s a_s^2 q(s) + \sum_{s<t} a_s a_t (q(s+t) - q(s) - q(t))``.
        So equality is decided when the modules carry finite framings.  Equality of
        arbitrary extensional maps is not decidable, and otherwise the answer is
        the proposition ``equal(b, c)`` unless the two evaluations are one
        (`DEV-52`); undecided value comparisons make the answer their conjunction.
        """
        if self is other:
            return True
        if element_parent(other) is not self.parent():
            return False
        match self._defining_gram_tensor, other._defining_gram_tensor, self.parent().kind():
            case None, None, _ if self._evaluation is other._evaluation:
                return True
            case left, right, "bilinear" if left is not None and right is not None:
                return left == right
            case _:
                pass
        left_module = self.left_module()
        right_module = self.right_module()
        ring = left_module.base_ring()
        framed = left_module.has_selected_module_resolution() and right_module.has_selected_module_resolution()
        if not framed:
            return AtomicProposition("equal", self, other)
        left_labels = left_module.module_generating_set()
        right_labels = right_module.module_generating_set()
        if not (left_labels.cardinality().is_finite() and right_labels.cardinality().is_finite()):
            return AtomicProposition("equal", self, other)
        match self.parent().kind():
            case "quadratic":
                generator = left_module.module_generator
                probes = chain(
                    map(generator, left_labels),
                    (generator(left) + generator(right) for left, right in combinations(left_labels, 2)),
                )
                answers = (self(probe) == other(probe) for probe in probes)
            case _:
                answers = (
                    self(left_module.module_generator(left), right_module.module_generator(right))
                    == other(left_module.module_generator(left), right_module.module_generator(right))
                    for left, right in product(left_labels, right_labels)
                )
        return conjunction(answers)

    def __ne__(self, other) -> bool | Predicate:
        return negation(self == other)

    def _repr_(self):
        return f"Extensional {self.parent().kind()} form with values in {self.codomain()}"


class _CallableForm(_CallableFormMethods):
    r"""The defining datum held by the private set realization of forms.

    Exactly one of the Gram tensor and the evaluation is the defining datum.
    """

    def __init__(self, parent, evaluation=None, lift_evaluation=None, *, gram_tensor=None) -> None:
        self._evaluation = evaluation
        self._lift_evaluation = lift_evaluation
        self._defining_gram_tensor = gram_tensor
        super().__init__(parent)


class _CallableFormSpace:
    r"""The ``R``-bilinear maps ``X x Y -> W``, or the quadratic maps ``M -> W``, by evaluation.

    This is the underlying set used by the module of forms below.  The
    input callable states a bilinear or quadratic map, not an arbitrary
    function whose laws can be decided on an infinite domain.  Finite
    presented modules use their universal classifier instead.
    """

    def __init__(self, left_module, right_module, value_module, kind, **rest) -> None:
        self._left_module = left_module
        self._right_module = right_module
        self._value_module = value_module
        self._kind = kind
        super().__init__(**rest)

    def left_module(self):
        return self._left_module

    def right_module(self):
        return self._right_module

    def module(self):
        if self.kind() == "quadratic" or self.left_module() is self.right_module():
            return self.left_module()
        raise TypeError(
            f"{self} pairs {self.left_module()} with {self.right_module()}, so it is not a space of forms "
            "on one module"
        )

    def codomain(self):
        return self._value_module

    def kind(self):
        return self._kind

    def __call__(self, datum):
        return self._element_constructor_(datum)

    def _element_constructor_(self, datum):
        r"""Admit a map of this space: one of its elements, finite coordinates, or an evaluation.

        This is the one boundary that reads the shape of foreign data.  A
        type-``(0, 2)`` tensor, an indexed family over the two framings or an
        iterable of rows is finite coordinate data; any other callable is the
        evaluation itself.
        """
        if element_parent(datum) is self:
            return datum
        match datum:
            case Tensor():
                rows = _covariant_bilinear_coordinate_rows(
                    datum,
                    _finite_framing(self.left_module()).cardinality(),
                    _finite_framing(self.right_module()).cardinality(),
                )
                match datum.base_ring() is self.codomain():
                    case True:
                        return self._from_gram_tensor(datum)
                    case False:
                        return self._from_coordinate_rows(rows)
            case _:
                pass
        if isinstance(datum, IndexedFamily):
            return self._from_coordinate_values(
                _coordinate_family_from_family(
                    _finite_framing(self.left_module()),
                    _finite_framing(self.right_module()),
                    self.codomain(),
                    datum,
                    name=f"Callable {self.kind()} coordinate input",
                )
            )
        if isinstance(datum, Iterable) and not isinstance(datum, (str, bytes)):
            return self._from_coordinate_rows(datum)
        if not callable(datum):
            raise TypeError(
                f"cannot build an element of {self} from {datum!r}: give a function to evaluate it or its "
                "values on the generators"
            )
        return self.element_class(self, datum)

    def _from_gram_tensor(self, gram):
        r"""The map with Gram tensor ``gram``: ``b(x, y) = G(x, y)``, or ``q(x) = G(x, x)``.

        For a quadratic space ``G`` is the chosen bilinear lift, which must be
        symmetric.
        """
        if self.kind() == "quadratic" and not gram.is_symmetric():
            raise ValueError(
                f"the bilinear lift of a quadratic form must be symmetric, but the Gram tensor {gram} is not"
            )
        return self.element_class(self, gram_tensor=gram)

    def _from_coordinate_rows(self, rows):
        r"""The map whose values on pairs of framing generators are the rows ``rows``.

        With values in a ring these rows are the Gram tensor of the map.
        """
        left_labels = _finite_framing(self.left_module())
        right_labels = _finite_framing(self.right_module())
        name = f"Callable {self.kind()} coordinate input"
        match self.codomain() in OwnedRings():
            case True:
                return self._from_gram_tensor(
                    tensor(
                        self.codomain(),
                        (),
                        (int(left_labels.cardinality()), int(right_labels.cardinality())),
                        _coordinate_rows(left_labels, right_labels, self.codomain(), rows, name=name),
                    )
                )
            case False:
                return self._from_coordinate_values(
                    _coordinate_family_from_rows(left_labels, right_labels, self.codomain(), rows, name=name)
                )

    def _from_coordinate_values(self, values):
        r"""The map whose values on pairs of framing generators are the family ``values``.

        With values in a ring the family is read once into the Gram tensor of
        the map.  Otherwise the map is the bilinear extension
        ``b(x, y) = \sum_{s,t} x_s y_t\, b(s, t)`` over the two framings; for a
        quadratic space the coordinates are the chosen bilinear lift ``b``,
        which must be symmetric, and the map is ``q(x) = b(x, x)``.
        """
        left_module = self.left_module()
        right_module = self.right_module()
        left_labels = _finite_framing(left_module)
        right_labels = _finite_framing(right_module)
        match self.codomain() in OwnedRings():
            case True:
                return self._from_coordinate_rows(
                    (
                        (_coordinate_pair(values, left_label, right_label) for right_label in right_labels)
                        for left_label in left_labels
                    )
                )
            case False:
                pass
        zero = self.codomain().zero()

        def bilinear(left, right):
            left_coordinates = left_module.framing_morphism().lift(left)
            right_coordinates = right_module.framing_morphism().lift(right)
            return sum(
                (
                    scalar * _coordinate_pair(values, left_label, right_label)
                    for left_label in left_coordinates.support().domain()
                    for right_label in right_coordinates.support().domain()
                    if (scalar := left_coordinates(left_label) * right_coordinates(right_label))
                ),
                start=zero,
            )

        if self.kind() != "quadratic":
            return self.element_class(self, bilinear)
        if not all(
            _coordinate_pair(values, left, right) == _coordinate_pair(values, right, left)
            for left, right in combinations(left_labels, 2)
        ):
            raise ValueError(
                f"the bilinear lift of a quadratic form must be symmetric, but the values {values} are not"
            )
        return self.element_class(self, lambda element: bilinear(element, element), bilinear)

    def from_quadratic_map(self, quadratic, **_options):
        if self.kind() != "quadratic":
            raise TypeError(
                f"{self} is a space of bilinear forms; a quadratic map defines an element of a space of quadratic forms"
            )
        return self(quadratic)

    def __contains__(self, candidate):
        return element_parent(candidate) is self

    def _repr_(self):
        return f"{self.kind().capitalize()} maps from {self.left_module()} to {self.codomain()}"


class _CallableFormModuleElement(_CallableFormMethods):
    r"""A form as an element of the module on the retained set of forms."""

    @property
    def _evaluation(self):
        return self.underlying_element()._evaluation

    @property
    def _lift_evaluation(self):
        return self.underlying_element()._lift_evaluation

    @property
    def _defining_gram_tensor(self):
        return self.underlying_element()._defining_gram_tensor


class _CallableFormModule:
    r"""Pointwise module structure on the actual set of bilinear or quadratic maps.

    The private engine supplies the defining operations to GeneralModules.
    For central scalars, a linear combination of bilinear maps is bilinear;
    likewise a linear combination of quadratic maps has the same quadratic
    homogeneity and a bilinear polar map.  These identities follow termwise
    from the supplied maps' identities.  Module arithmetic is inherited,
    not implemented separately on the form elements.
    """

    def __init__(self, form_set, **rest) -> None:
        value_module = form_set.codomain()
        ring = form_set.left_module().base_ring()
        super().__init__(
            underlying_set=form_set,
            addition=lambda left, right: form_set(lambda *args: left(*args) + right(*args)),
            zero=form_set(lambda *args: value_module.zero()),
            negation=lambda form: form_set(lambda *args: -form(*args)),
            scalar_action=lambda scalar, form: form_set(
                lambda *args: value_module.scalar_multiple(ring(scalar), form(*args))
            ),
            verify=False,
            **rest,
        )

    def left_module(self):
        return self.underlying_set().left_module()

    def right_module(self):
        return self.underlying_set().right_module()

    def module(self):
        return self.underlying_set().module()

    def codomain(self):
        return self.underlying_set().codomain()

    def kind(self):
        return self.underlying_set().kind()

    def _element_constructor_(self, datum):
        match element_parent(datum):
            case parent if parent is self:
                return datum
            case _:
                return super()._element_constructor_(self.underlying_set()(datum))

    def from_quadratic_map(self, quadratic, **_options):
        assert self.kind() == "quadratic", (
            f"{self} is a space of bilinear forms; a quadratic map defines an element of a space of quadratic forms"
        )
        return self(quadratic)

    def _repr_(self):
        return f"Module of {self.kind()} maps from {self.left_module()} to {self.codomain()}"


@cached_function(key=lambda left_module, right_module, value_module, kind: (id(left_module), id(right_module), id(value_module), kind))
def _callable_form_space(left_module, right_module, value_module, kind):
    from sage_extensions.categories.modules.general_modules import GeneralModules

    form_set = _object_of(
        Sets(),
        _engine=(Sets(), _CallableFormSpace, _CallableForm),
        left_module=left_module,
        right_module=right_module,
        value_module=value_module,
        kind=kind,
    )
    ring = left_module.base_ring()
    match value_module:
        case _ if value_module in Modules(ring):
            scalars = ring.ring_center()
            modules = GeneralModules(scalars)
            return _object_of(
                modules,
                _engine=(modules, _CallableFormModule, _CallableFormModuleElement),
                base_ring=scalars,
                form_set=form_set,
            )
        case _:
            return form_set


def _is_bilinear_form(form) -> bool:
    r"""Whether ``form`` is a bilinear form on its module ``M``.

    A bilinear form on ``M`` classified by a represented tensor square is an
    arrow out of ``M \otimes_R M``; otherwise it is an element of the space of
    bilinear maps.  Which of the two applies is the routing that built the
    form's space.  A pairing of two
    distinct modules is not a form on one module, and ``form.module()``
    refuses it.
    """
    module = form.module()
    forms = element_parent(form)
    match module:
        case _ if _bilinear_classifier_is_represented(module, module, form.codomain()):
            return forms.domain() in TensorProductModules(module.base_ring())
        case _:
            return forms.kind() == "bilinear"


def _is_quadratic_form(form) -> bool:
    r"""Whether ``form`` is a quadratic form on its module ``M``.

    A quadratic form classified by a represented divided square is an arrow
    out of ``\Gamma^2_R(M)``; otherwise it is an element of the space of
    quadratic maps.  The routing is :func:`_is_bilinear_form`'s.
    """
    module = form.module()
    forms = element_parent(form)
    match module:
        case _ if _quadratic_classifier_is_represented(module, form.codomain()):
            return forms.domain() in DividedSquareModules(module.base_ring())
        case _:
            return forms.kind() == "quadratic"


def _pairings(left_module, right_module, value_module):
    r"""Return the ``R``-bilinear maps ``X x Y -> W``.

    The tensor owner chooses a free, presented, or general quotient
    realization. The Cat-owned module Mor ingress admits ``W`` only when
    it is an object of ``Modules(R)``: there is no bypass for callables or
    a codomain merely admitting a bilinear value interpretation.
    """
    match right_module:
        case _ if right_module is left_module:
            return left_module.bilinear_forms(value_module)
        case _:
            tensor_product = left_module.module_category().tensor_product(
                (left_module, right_module)
            )
            return Modules(left_module.base_ring()).Mor(tensor_product, value_module)


def _bilinear_forms(module, value_module):
    r"""Return ``Hom_R(M \otimes_R M, W)`` through Cat's module-Mor ingress."""
    tensor_product = module.module_category().tensor_product((module, module))
    return Modules(module.base_ring()).Mor(tensor_product, value_module)


def _quadratic_forms(module, value_module):
    r"""Return ``Hom_R(\Gamma^2(M), W)``, or the quadratic maps when the square is not represented."""
    match module:
        case _ if _quadratic_classifier_is_represented(module, value_module):
            square = module.divided_square()
            return square.module_category().Mor(square, value_module)
        case _:
            return _callable_form_space(module, module, value_module, "quadratic")


QuadraticFormMorphism = QuadraticModuleMorphism
QuadraticMapMorphism = QuadraticFormMorphism


def _quadratic_map(module, value_module, function):
    r"""Return the quadratic map ``module -> value_module`` via its classifier."""
    forms = module.quadratic_forms(value_module)
    return forms.from_quadratic_map(function)


def _quadratic_map_from_morphism(module, morphism):
    r"""Recover the quadratic map classified by ``morphism: Gamma^2(M) -> W``.

    A morphism of ``Hom_R(\Gamma^2(M), W)`` already is that quadratic map; any
    other arrow out of the divided square is read through ``q(x) = f(\gamma_2(x))``.
    """
    square = module.divided_square()
    if morphism.domain() is not square:
        raise ValueError(
            f"a quadratic form on {module} is a map out of its divided square {square}, but {morphism} starts "
            f"at {morphism.domain()}"
        )
    quadratic_maps = square.module_category().Mor(square, morphism.codomain())
    match morphism:
        case _ if element_parent(morphism) is quadratic_maps:
            return morphism
        case _:
            return module.quadratic_map(
                morphism.codomain(),
                lambda element: morphism(square.quadratic(element)),
            )
