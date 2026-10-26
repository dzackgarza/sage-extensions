r"""Finite presented torsion modules equipped with exact forms.

The underlying module and its chosen presentation are first-class data.  A
Gram array defines a form on the quotient exactly when it annihilates the
relation submodule in the appropriate sense; these constructors check that
descent before equipping the module with the form.
"""

from sage.categories.map import Map
from sage.categories.category import Category
from sage.misc.cachefunc import cached_method
from sage.misc.classcall_metaclass import typecall
from sage.matrix.constructor import matrix as _engine_matrix
from sage.rings.finite_rings.finite_field_constructor import GF as _engine_GF
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ

from sage_extensions.categories.abstract_categories.arrow_categories import (
    CategoricalIsomorphism,
    CoreMor,
)
from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    IsoCategoryConstruction,
    _distinct_supercategories,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.group.g_sets import FiniteGSets
from sage_extensions.tensors._finite_form_engine import _engine_odd_orthogonal_generators
from sage_extensions.categories.group.groups import (
    OwnedFiniteGroups,
    OwnedGroups,
)
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
    _module_invariant_factor_form,
    _relation_images,
)
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphism,
    ModuleMorphismMethods,
    _integral_preimage_solver,
)
from sage_extensions.categories.modules.pure.modules import (
    MatrixSpaces,
    ModuleSubobjects,
    Modules,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import (
    Sets,
)
from sage_extensions.refine import realize_owned_category
from sage_extensions.tensors.tensor import (
    Tensor,
    _engine_component_matrix,
    _engine_dual_row_family,
    _engine_row_family_gram,
    tensor,
)
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def _gram_rows(gram, rank):
    match gram:
        case ModuleMorphismMethods():
            parent = gram.parent()
            if parent not in MatrixSpaces(parent.base_ring()):
                raise TypeError("a morphism Gram presentation must be an owned matrix Mor element")
            rows = tuple(
                tuple(gram[row, column] for column in range(parent.ncols()))
                for row in range(parent.nrows())
            )
        case Tensor():
            shape = gram.tensor_shape()
            rows = tuple(
                tuple(gram[row, column] for column in range(int(shape[1])))
                for row in range(int(shape[0]))
            )
        case _:
            rows = tuple(tuple(row) for row in gram)
    if len(rows) != rank or any(len(row) != rank for row in rows):
        raise ValueError(
            f"a Gram matrix on {rank} generators must be {rank} x {rank}, but the given rows have lengths "
            f"{tuple(len(row) for row in rows)}"
        )
    return rows


def _coerced_gram(value_module, gram, rank):
    return tuple(tuple(value_module(entry) for entry in row) for row in _gram_rows(gram, rank))


def _linear_combination(value_module, coefficients, values):
    return sum(
        (coefficient * value for coefficient, value in zip(coefficients, values, strict=True) if coefficient),
        value_module.zero(),
    )


def _bilinear_descends(relation_images, gram, value_module) -> bool:
    r"""Decide ``b(r, x) = b(x, r) = 0`` for each relation ``r`` and generator ``x``.

    ``relation_images`` holds the coordinates of each ``r(e_i)`` in the
    module generators, read by application of the relation morphism.
    """
    rank = len(gram)
    for relation in relation_images:
        for j in range(rank):
            if _linear_combination(value_module, relation, tuple(gram[i][j] for i in range(rank))) != value_module.zero():
                return False
        for i in range(rank):
            if _linear_combination(value_module, relation, tuple(gram[i][j] for j in range(rank))) != value_module.zero():
                return False
    return True


def _quadratic_descends(relation_images, gram, value_module) -> bool:
    r"""Decide ``q(r) = 0`` and ``2 b(x, r) = 0`` for each relation ``r`` and generator ``x``."""
    rank = len(gram)
    two = value_module.base_ring()(2)
    for relation in relation_images:
        # q(x+r)-q(x)-q(r) is the polar value 2*x^T G r.
        for j in range(rank):
            pairing = _linear_combination(
                value_module,
                relation,
                tuple(gram[i][j] for i in range(rank)),
            )
            if value_module.scalar_multiple(two, pairing) != value_module.zero():
                return False
        norm = sum(
            (relation[i] * relation[j] * gram[i][j] for i in range(rank) for j in range(rank) if relation[i] and relation[j]),
            value_module.zero(),
        )
        if norm != value_module.zero():
            return False
    return True


class TorsionFormIsometry(CategoricalIsomorphism):
    r"""An explicit isomorphism of finite framed torsion modules preserving a form."""

    def __init__(self, parent, forward, inverse, *, quadratic: bool, check: bool = False) -> None:
        r"""Store the mutually inverse module maps and the form flavour (``OWN-22``).

        ``check=True``, or strict checking, runs the validators
        :meth:`validate_inverse` and :meth:`validate_form_preservation`.
        """
        super().__init__(parent, forward, lambda: inverse, verify=False)
        self._quadratic = bool(quadratic)
        self.validate_inverse(check=check)
        self.validate_form_preservation(check=check)

    @validator
    def validate_inverse(self) -> None:
        r"""Check that the stored inverse composes to the identity on both sides, on the selected generators."""
        forward = self.forward()
        inverse = self.inverse_morphism()
        source = self.domain()
        target = self.codomain()
        if any(
            inverse(forward(generator)) != generator
            for generator in source.module_generators()
        ):
            raise ValueError(
                f"{inverse} is not a left inverse of {forward}: their composition "
                f"does not fix every selected generator of {source}"
            )
        if any(
            forward(inverse(generator)) != generator
            for generator in target.module_generators()
        ):
            raise ValueError(
                f"{inverse} is not a right inverse of {forward}: their composition "
                f"does not fix every selected generator of {target}"
            )

    @validator
    def validate_form_preservation(self) -> None:
        r"""Check that the forward map preserves ``q`` (quadratic) or ``b`` (bilinear) on generator probes."""
        forward = self.forward()
        source = self.domain()
        target = self.codomain()
        generators = tuple(source.module_generators())
        if self._quadratic:
            probes = generators + tuple(
                left + right
                for index, left in enumerate(generators)
                for right in generators[index + 1 :]
            )
            if any(source.q(element) != target.q(forward(element)) for element in probes):
                raise ValueError(
                    f"{forward} is not an isometry {source} -> {target}: it does not preserve the quadratic form q"
                )
            return
        if any(
            source.b(left, right) != target.b(forward(left), forward(right))
            for left in generators
            for right in generators
        ):
            raise ValueError(
                f"{forward} is not an isometry {source} -> {target}: it does not preserve the bilinear form b"
            )

    def is_quadratic(self) -> bool:
        return self._quadratic

    def is_isomorphism(self) -> bool:
        r"""Return ``True``: membership in this Core Mor carries the inverse pair."""
        return True

    def inverse_morphism(self):
        r"""Return the underlying inverse module morphism."""
        return self._inverse_morphism()

    def inverse(self):
        r"""Return the inverse in the same specialized torsion-form Iso family."""
        reverse = self.parent().mor_family().Of(self.codomain(), self.domain())
        return reverse._from_known_inverse_pair(
            self.inverse_morphism(), self.forward()
        )


class TorsionFormIsometryMor(CoreMor):
    r"""The Core Mor of isometries between two finite torsion forms."""

    Element = TorsionFormIsometry

    def __init__(self, family, domain, codomain) -> None:
        self._quadratic = bool(family.quadratic)
        super().__init__(family, domain, codomain)

    def _element_constructor_(self, forward, inverse=None, *, check=False):
        if isinstance(forward, TorsionFormIsometry) and inverse is None:
            if forward.parent() is self:
                return forward
            raise TypeError(
                f"{forward} belongs to another Mor; apply the functor between the categories"
            )
        if inverse is None:
            forward, inverse = forward
        self._require_base_morphisms(forward, inverse)
        return self.element_class(
            self,
            forward,
            inverse,
            quadratic=self._quadratic,
            check=check,
        )

    def _from_known_inverse_pair(self, forward, inverse):
        self._require_base_morphisms(forward, inverse)
        return self.element_class(
            self,
            forward,
            inverse,
            quadratic=self._quadratic,
        )

    def _from_inverse_computation(self, forward, inverse_computation):
        return self._from_known_inverse_pair(forward, inverse_computation())


def _torsion_form_isometry(forward, inverse, *, quadratic: bool):
    r"""Return the form isometry represented by mutually inverse module maps."""
    from sage_extensions.categories.modules.framed.formed.form_modules import (
        FormedModuleMorphism,
        _represented_value_module,
    )

    source, target = forward.domain(), forward.codomain()
    category = _torsion_form_modules(source.base_ring(), quadratic=quadratic)
    values = _represented_value_module(source)
    assert _represented_value_module(target) is values, "an isometry preserves one value module"
    value_identity = values.module_category().Mor(values, values).identity()
    forward_component = forward.module_morphism() if isinstance(forward, FormedModuleMorphism) else forward
    inverse_component = inverse.module_morphism() if isinstance(inverse, FormedModuleMorphism) else inverse
    formed_forward = category.Mor(source, target)((forward_component, value_identity))
    formed_inverse = category.Mor(target, source)((inverse_component, value_identity))
    return category.Core().Mor(source, target)._from_known_inverse_pair(
        formed_forward,
        formed_inverse,
    )


def _representative_gram(form, *, quadratic: bool):
    r"""Return owned rational representatives as a type-``(0,2)`` tensor."""
    values = form.form().lift_coordinate_values() if quadratic else None
    value_module = form.value_module()
    rationals = value_module.fraction_field()
    labels = form.module_generating_set()
    rank = int(labels.cardinality())

    def representative(i, j):
        if not quadratic:
            # The tensor product underlying a bilinear form may have a
            # smaller presentation than the formed module (in particular,
            # no generators when that module is zero).  Evaluate on the
            # module's actual generators instead of identifying the two
            # unrelated framing index sets.
            return value_module.lift(form.b(
                form.module_generator(labels[i]),
                form.module_generator(labels[j]),
            ))
        pair = values.index_set()(
            lambda index: labels[i] if int(index) == 0 else labels[j]
        )
        return value_module.lift(values[pair])

    return tensor(
        rationals,
        (),
        (rank, rank),
        (
            representative(i, j)
            for i in range(rank)
            for j in range(rank)
        ),
    )


def _engine_torsion_form(normalized_form, *, quadratic: bool):
    r"""Build the private Sage finite-form engine on a minimal framing.

    The engine is scratch data only.  Its cover basis is identified with the
    invariant-factor framing of ``normalized_form``; public automorphisms are
    transported back through the explicit normalization isometry.
    """
    from sage.modules.torsion_quadratic_module import (
        TorsionQuadraticForm,
        TorsionQuadraticModule,
    )

    engine = TorsionQuadraticForm(
        _engine_component_matrix(
            _representative_gram(normalized_form, quadratic=quadratic)
        )
    )
    if int(engine.cardinality()) != int(normalized_form.cardinality()):
        raise ArithmeticError(
            f"the finite quadratic module built from the Gram matrix of {normalized_form} has order "
            f"{engine.cardinality()}, not the order {normalized_form.cardinality()} of {normalized_form}"
        )
    if not quadratic:
        # Sage's orthogonal group preserves both b and q.  Setting the
        # quadratic modulus equal to the bilinear modulus makes q(x)=b(x,x)
        # derived data, so preserving it imposes no condition beyond b.
        engine = TorsionQuadraticModule(
            engine.V(),
            engine.W(),
            gens=engine.gens(),
            modulus=engine._modulus,
            modulus_qf=engine._modulus,
            check=False,
        )
    return engine


def _even_lattice_genus_engine(form, signature):
    r"""Return Sage's finite quadratic form of ``form`` and the engine signature.

    The pair is private scratch for the existence and representative
    computations of [nikulin1979integral, Thm. 1.10.1]; it never leaves this
    module's callers.
    """
    engine = _engine_torsion_form(form.invariant_factor_form().codomain(), quadratic=True)
    return engine, (SageZZ(int(signature.first())), SageZZ(int(signature.second())))


def _even_lattice_genus_exists(form, signature) -> bool:
    r"""Decide whether an even lattice of ``signature`` has discriminant form ``form``."""
    engine, pair = _even_lattice_genus_engine(form, signature)
    return bool(engine.is_genus(pair, even=True))


def _even_lattice_genus_gram(form, signature):
    r"""Return the private Gram matrix of one even lattice with these invariants."""
    engine, pair = _even_lattice_genus_engine(form, signature)
    return engine.genus(pair).representative()


def _value_module(form, *, quadratic: bool):
    r"""Return the value module through the owned form interface."""
    return form.value_module()


def _underlying_presented_module(form):
    return form.unformed_module()


def _underlying_element(form, element):
    return form.unformed_module()(element)

def _generator_and_relation_map(form, generators):
    r"""Return ``F(generators) + F(relations) -> F(S)`` for the framing ``F(S) ->> form``.

    The ``i``-th generator goes to the framing coordinates of
    ``generators[i]`` and the ``j``-th relation to the ``j``-th selected
    relation of the underlying presented module.  An element of the kernel,
    read on the first summand, is a relation among ``generators``; a preimage
    of a framing generator, read on the first summand, writes it in
    ``generators``.
    """
    module = _underlying_presented_module(form)
    ring = module.base_ring()
    framing_labels = tuple(module.module_generating_set())
    relation_images = _relation_images(module)
    lift_space = ring.matrix_space(len(framing_labels), len(generators))
    coordinate_module = lift_space.codomain()
    coordinate_labels = tuple(coordinate_module.module_generating_set())

    def coordinate_vector(values):
        return coordinate_module.linear_combination(
            {
                label: value
                for label, value in zip(coordinate_labels, values, strict=True)
                if value
            }
        )

    lifts = lift_space(
        tuple(
            coordinate_vector(tuple(coordinates(label) for label in framing_labels))
            for coordinates in (
                module.framing_morphism().lift(_underlying_element(form, generator))
                for generator in generators
            )
        )
    )
    known = ring.matrix_space(len(framing_labels), len(relation_images))(
        tuple(coordinate_vector(image) for image in relation_images)
    )
    summands = Modules(ring).biproduct((lifts.domain(), known.domain()))
    return summands.from_summands(lifts, known)


def _relations_among_generators(form, generators):
    r"""Return the relation morphism ``F(relations) -> F(generators)`` of a generating family of ``form``.

    Its image is the module of relations among ``generators``: the kernel of
    the generator-and-relation map, projected onto the generator summand.
    """

    combined = _generator_and_relation_map(form, generators)
    kernel = combined.kernel()
    relations = (
        combined.domain().left_projection() * kernel.inclusion()
    ).image()
    inclusion = relations.inclusion()
    return inclusion.domain().module_category().Mor(
        inclusion.domain(), inclusion.codomain()
    )(inclusion)


def _quadratic_gram_on(form, generators):
    quadratic_values = _value_module(form, quadratic=True)
    rows = []
    for i, left in enumerate(generators):
        row = []
        for j, right in enumerate(generators):
            if i == j:
                row.append(form.q(left))
            else:
                row.append(quadratic_values(form.b(left, right).lift()))
        rows.append(tuple(row))
    return tuple(rows)


def _torsion_form_modules(base_ring, *, quadratic: bool):
    r"""Return the category of finite forms of the stated flavour over ``base_ring``."""
    from sage_extensions.categories.modules.framed.formed.form_modules import (
        BilinearFormModules,
        QuadraticFormModules,
    )

    classifier = QuadraticFormModules if quadratic else BilinearFormModules
    return classifier(base_ring).FinitelyPresented().Torsion()


def _torsion_form_subobject_on(form, generators, *, quadratic: bool):
    r"""Return the finite torsion submodule spanned by ``generators`` with restricted form."""

    generators = tuple(form(generator) for generator in generators)
    unformed = form.unformed_module()
    unformed_generators = tuple(unformed(generator) for generator in generators)
    underlying_subobject = unformed.subobject_on(unformed_generators)
    underlying_inclusion = underlying_subobject.inclusion()

    def ambient_image(label):
        underlying_generator = underlying_subobject.module_generator(label)
        return form(underlying_inclusion(underlying_generator))

    selected = tuple(
        ambient_image(label)
        for label in underlying_subobject.module_generating_set()
    )
    gram = _form_gram_on(form, selected, quadratic=quadratic)
    category = _torsion_form_modules(form.base_ring(), quadratic=quadratic)

    def inclusion_factory(source):
        return source.Mono(form)(ambient_image, quadratic=quadratic)

    def lift_from_ambient(source, element):
        unformed_element = unformed(form(element))
        if underlying_inclusion.has_selected_lift():
            lifted = underlying_inclusion.lift(unformed_element)
        else:
            lifted = next(
                (
                    candidate
                    for candidate in underlying_subobject.elements()
                    if underlying_inclusion(candidate) == unformed_element
                ),
                None,
            )
            if lifted is None:
                raise ValueError(
                    f"{element} does not lie in the submodule {source} of {form}"
                )
        return source(lifted)

    return category.from_module(
        underlying_subobject,
        gram,
        form.value_module(),
        _subobject_ambient=form,
        _subobject_generator_images=ambient_image,
        _subobject_lift=lift_from_ambient,
        _subobject_inclusion_factory=inclusion_factory,
    )


def _torsion_form_primary_part(form, prime, *, quadratic: bool):
    r"""Return the ``prime``-primary form-bearing subobject."""

    prime = form.base_ring()(prime)
    generators = []
    for generator in form.smith_form_module_generators():
        order = generator.additive_order()
        valuation = int(order.valuation(prime))
        if valuation:
            primary_order = prime**valuation
            generators.append(form.scalar_multiple(order // primary_order, generator))
    return _torsion_form_subobject_on(form, generators, quadratic=quadratic)


def _embedded_elements(subobject):
    inclusion = subobject.inclusion()
    return frozenset(inclusion(element) for element in subobject.elements())


def _torsion_form_isotropic_subobjects(form, *, quadratic: bool):
    r"""Return all form-bearing subobjects on which the selected form vanishes."""
    return finite_ordered_set(
        tuple(
            subobject
            for subobject in _torsion_form_all_subobjects(
                form, quadratic=quadratic
            )
            if form.form_vanishes_on(_embedded_elements(subobject))
        )
    )


def _torsion_form_maximal_isotropic_subobjects(form, *, quadratic: bool):
    isotropic = _torsion_form_isotropic_subobjects(form, quadratic=quadratic)
    by_elements = tuple((subobject, _embedded_elements(subobject)) for subobject in isotropic)
    return finite_ordered_set(
        tuple(
            subobject
            for subobject, elements in by_elements
            if not any(elements < larger for _other, larger in by_elements)
        )
    )


def _torsion_form_all_subobjects(form, *, quadratic: bool):
    r"""Return every finite form-bearing subobject of ``form`` exactly once.

    The owned finite-torsion enumeration itself is the ``ZZ`` Smith
    specialization.  On that exact frontier Sage's finite-quadratic-module
    backend owns the complete subgroup enumeration: ``ZZ``-submodules are
    additive subgroups, and ``all_submodules()`` delegates the finite abelian
    subgroup lattice to GAP.  We cross only its returned generators through
    the invariant-factor normalization.
    """
    integers = _owned_integers()
    assert form.base_ring() is integers, (
        f"the submodules of the torsion form {form} are enumerated only over ZZ, "
        f"but {form} is over {form.base_ring()}"
    )
    normalization = form.invariant_factor_form()
    normalized = normalization.codomain()
    engine = _engine_torsion_form(normalized, quadratic=quadratic)
    cover = engine.V()
    labels = tuple(normalized.module_generating_set())
    ring = normalized.base_ring()

    def owned_engine_generator(engine_generator):
        coordinates = cover.coordinates(engine(engine_generator).lift())
        normalized_element = normalized.linear_combination(
            {
                label: _owned_engine_element(ring, SageZZ(coefficient))
                for label, coefficient in zip(labels, coordinates, strict=True)
                if coefficient
            }
        )
        return normalization.inverse()(normalized_element)

    return finite_ordered_set(
        tuple(
            _torsion_form_subobject_on(
                form,
                tuple(
                    owned_engine_generator(generator)
                    for generator in engine_submodule.gens()
                ),
                quadratic=quadratic,
            )
            for engine_submodule in engine.all_submodules()
        )
    )


def _torsion_form_orthogonal_subobject(form, subobject, *, quadratic: bool):
    r"""Return ``S^perp`` as a form-bearing subobject of ``form``."""
    inclusion = subobject.inclusion()
    if inclusion.codomain() is not form:
        raise ValueError(
            f"the orthogonal complement in {form} is taken of a submodule of {form}, but {subobject} "
            f"is a submodule of {inclusion.codomain()}"
        )
    generators = tuple(subobject.embedded_module_generators())
    zero = form.associated_bilinear_form().value_module().zero() if quadratic else form.value_module().zero()
    selected = tuple(
        element
        for element in form.elements()
        if all(form.b(element, generator) == zero for generator in generators)
    )
    return _torsion_form_subobject_on(form, selected, quadratic=quadratic)


def _torsion_form_lagrangian_subobjects(form, *, quadratic: bool):
    r"""Return isotropic ``S`` satisfying ``S=S^perp``."""
    return finite_ordered_set(
        tuple(
            subobject
            for subobject in _torsion_form_isotropic_subobjects(
                form, quadratic=quadratic
            )
            if _embedded_elements(subobject)
            == _embedded_elements(
                _torsion_form_orthogonal_subobject(
                    form, subobject, quadratic=quadratic
                )
            )
        )
    )


def _torsion_form_element_action(form, acting):
    r"""Return the represented finite ``acting``-set of elements of ``form``."""
    return FiniteGSets(acting)(
        form.elements(),
        lambda automorphism, element: automorphism(element),
    )


def _torsion_form_subobject_action(form, family, acting):
    r"""Return the represented action on one invariant finite subobject family.

    The points of the G-set are the already selected form-bearing subobjects in
    ``family``.  Acting on a point changes only its embedded element set; the
    corresponding selected point of ``family`` is then recovered.  Thus the
    torsion-form layer supplies the mathematical action while orbit and
    stabilizer structure is owned by :class:`FiniteGSets`.
    """
    points = finite_ordered_set(tuple(family))
    by_embedded_elements = {
        _embedded_elements(subobject): subobject
        for subobject in points
    }

    def act(automorphism, subobject):
        if subobject.inclusion().codomain() is not form:
            raise ValueError(
                f"the automorphisms of {form} act on submodules of {form}, but {subobject} is a submodule "
                f"of {subobject.inclusion().codomain()}"
            )
        image = frozenset(
            automorphism(element) for element in _embedded_elements(subobject)
        )
        if image not in by_embedded_elements:
            raise ValueError(
                f"the family of submodules of {form} is not invariant under {acting}: "
                f"{automorphism} sends {subobject} outside it"
            )
        return by_embedded_elements[image]

    return FiniteGSets(acting)(points, act)


def _torsion_form_subobject_orbits(form, family, acting):
    r"""Return the orbit partition through the represented finite G-set action."""
    action = _torsion_form_subobject_action(form, family, acting)
    return finite_ordered_set(tuple(orbit.points() for orbit in action.orbits()))


def _torsion_form_subquotient(form, subobject, over, *, quadratic: bool):
    r"""Return ``K/H`` with descended form for ``H <= K <= H^perp``."""
    small_inclusion = subobject.inclusion()
    large_inclusion = over.inclusion()
    if small_inclusion.codomain() is not form or large_inclusion.codomain() is not form:
        raise ValueError(
            f"the subquotient K/H of {form} needs H={subobject} and K={over} to be submodules of {form}, "
            f"but they are submodules of {small_inclusion.codomain()} and {large_inclusion.codomain()}"
        )
    small_elements = _embedded_elements(subobject)
    large_elements = _embedded_elements(over)
    if not small_elements <= large_elements:
        raise ValueError(
            f"the subquotient K/H of {form} requires H contained in K, but H={subobject} is not contained in K={over}"
        )
    if not form.form_vanishes_on(small_elements):
        raise ValueError(
            f"the form of {form} descends to K/H only when H is isotropic, but the form does not vanish on H={subobject}"
        )
    perpendicular = _torsion_form_orthogonal_subobject(
        form, subobject, quadratic=quadratic
    )
    if not large_elements <= _embedded_elements(perpendicular):
        raise ValueError(
            f"the form of {form} descends to K/H only when K is contained in H^perp, "
            f"but K={over} is not contained in the orthogonal complement of H={subobject}"
        )

    images = {
        label: large_inclusion.lift(
            small_inclusion(subobject.module_generator(label))
        )
        for label in subobject.module_generating_set()
    }
    quotient = subobject.module_category().Mor(subobject, over)(images).cokernel()
    generators = tuple(over.module_generators())
    return _torsion_form_modules(form.base_ring(), quadratic=quadratic).from_module(
        quotient,
        _form_gram_on(over, generators, quadratic=quadratic),
        form.value_module(),
    )


def _form_gram_on(form, generators, *, quadratic: bool):
    r"""Return the Gram data of ``form`` on a selected generating family.

    The quadratic reading carries ``q`` on the diagonal and a lift of ``b``
    off it, valued in ``K/2R``; the bilinear reading is ``b`` throughout,
    valued in ``K/R``.  Which one is asked for is a fact about the
    mathematics of the caller, never about the family.
    """
    if quadratic:
        return _quadratic_gram_on(form, generators)
    return tuple(
        tuple(form.b(left, right) for right in generators)
        for left in generators
    )


def _regenerate_form_on_generators(form, generators, *, quadratic: bool):
    r"""Return ``form -> form'`` for the same finite form on a new framing."""

    generators = tuple(generators)
    if any(generator not in form for generator in generators):
        raise TypeError(
            f"new generators of {form} must be elements of {form}, but {generators} contains an element not in {form}"
        )
    module = _underlying_presented_module(form)
    ring = module.base_ring()
    regenerated_module = Modules(ring).FinitelyPresented().Torsion()(
        _relations_among_generators(form, generators)
    )
    labels = tuple(regenerated_module.module_generating_set())
    regenerated = _torsion_form_modules(form.base_ring(), quadratic=quadratic).from_module(
        regenerated_module,
        _form_gram_on(form, generators, quadratic=quadratic),
        _value_module(form, quadratic=quadratic),
    )

    inverse = regenerated.module_category().Mor(regenerated, form)(
        {label: generator for label, generator in zip(labels, generators, strict=True)}
    )

    # A framing generator e_s of form is written in the new generators by a
    # preimage of e_s under F(generators) + F(relations) -> F(S); its first
    # summand holds the coefficients of the new generators.
    system = _generator_and_relation_map(form, generators)
    generator_module = system.domain().left_projection().codomain()
    lift_labels = generator_module.module_generating_set()
    source_labels = tuple(form.module_generating_set())
    regenerated_generators = tuple(regenerated.module_generators())
    forward_images = {}
    solve = _integral_preimage_solver(system, ring)
    for position, source_label in enumerate(source_labels):
        target = [
            ring.one() if index == position else ring.zero()
            for index in range(len(source_labels))
        ]
        solution = solve(target)
        generator_coordinates = system.domain().left_projection()(solution).to_vector()
        forward_images[source_label] = sum(
            (
                regenerated.scalar_multiple(
                    generator_coordinates(lift_labels[index]),
                    generator,
                )
                for index, generator in enumerate(regenerated_generators)
                if lift_labels[index] in generator_coordinates.support()
            ),
            regenerated.zero(),
        )
    forward = form.module_category().Mor(form, regenerated)(forward_images)
    return _torsion_form_isometry(forward, inverse, quadratic=quadratic)


def _prime_indexed_generators(generators_by_prime):
    r"""Return the family \(p\mapsto\) chosen Jordan generators at \(p\).

    The primes are the index set and the chosen generators the value there.
    Two primes may carry equal-looking generating families, and the generators
    at one prime are an ordered choice, so both levels are families.
    """

    def generators_at(prime):
        chosen = generators_by_prime[prime]
        return indexed_family(
            Sets.Δ[len(chosen) - 1],
            lambda position, chosen=chosen: chosen[int(position)],
            name="Jordan generators",
        )

    primes = finite_ordered_set(tuple(sorted(generators_by_prime)))
    return indexed_family(primes, generators_at, name="p-adic Jordan generators")


def _p_adic_jordan_decomposition(form, *, quadratic: bool):
    r"""Return prime-indexed Jordan generators as elements of ``form``."""
    if not quadratic:
        return _bilinear_p_adic_jordan_decomposition(form)
    normalization = form.invariant_factor_form()
    normalized = normalization.codomain()
    engine = _engine_torsion_form(normalized, quadratic=quadratic)
    cover = engine.V()
    ring = normalized.base_ring()
    labels = tuple(normalized.module_generating_set())
    # The engine's coordinates are representatives in the cover; each is raised
    # as its class modulo the order of the generator it multiplies.
    orders = tuple(_engine_element(ring, order) for order in normalized.invariant_factors())
    result = {}
    for prime in engine.annihilator().gen().prime_divisors():
        normal = engine.primary_part(prime).normal_form()
        generators = []
        for engine_generator in normal.gens():
            coordinates = cover.coordinates(engine_generator.lift())
            normalized_element = normalized.linear_combination(
                {
                    label: _owned_engine_element(ring, SageZZ(coefficient) % order)
                    for label, coefficient, order in zip(labels, coordinates, orders, strict=True)
                    if SageZZ(coefficient) % order
                }
            )
            generators.append(normalization.inverse()(normalized_element))
        result[_owned_engine_element(normalized.base_ring(), SageZZ(prime))] = tuple(generators)
    return _prime_indexed_generators(result)


def _bilinear_p_adic_jordan_decomposition(form):
    r"""Return a symmetric-bilinear Jordan framing prime by prime.

    Sage's finite quadratic normal form is not a bilinear normal-form engine at
    ``p=2``: the extra quadratic refinement can change the chosen transformation.
    Here we use Sage's p-adic lattice reduction only as the private engine for
    the symmetric pairing, following the standard inverse-form reduction.
    """
    from sage.quadratic_forms.genera.normal_form import _normalize, p_adic_normal_form
    from sage.rings.padics.factory import Zp

    normalization = form.invariant_factor_form()
    normalized = normalization.codomain()
    ring = normalized.base_ring()
    invariants = tuple(normalized.invariant_factors())
    normalized_generators = tuple(normalized.module_generators())
    exponent = ring.one()
    for invariant in invariants:
        exponent = exponent.lcm(invariant)

    result = {}
    for prime in exponent.prime_divisors():
        primary_generators = []
        primary_orders = []
        for order, generator in zip(invariants, normalized_generators, strict=True):
            valuation = int(order.valuation(prime))
            if valuation:
                coefficient = order // (prime**valuation)
                primary_generators.append(
                    normalized.scalar_multiple(coefficient, generator)
                )
                primary_orders.append(_engine_element(ring, prime) ** valuation)
        primary_generators = tuple(primary_generators)
        primary_orders = tuple(primary_orders)
        values = normalized.value_module()
        rationals = values.fraction_field()
        representative = tensor(
            rationals,
            (),
            (len(primary_generators), len(primary_generators)),
            [
                [
                    values.lift(normalized.b(left, right))
                    for right in primary_generators
                ]
                for left in primary_generators
            ],
        )
        engine = _engine_component_matrix(representative)

        rank = engine.rank()
        if rank == engine.ncols():
            split = engine.parent().identity_matrix()
        else:
            integral = (engine * engine.denominator()).change_ring(SageZZ)
            split = integral.hermite_form(transformation=True)[1]
        degenerate = split[rank:, :]
        nondegenerate = split[:rank, :]
        nondegenerate_form = _engine_row_family_gram(engine, nondegenerate)

        if rank:

            backend_prime = _engine_element(ring, prime)
            precision = int(exponent.valuation(prime)) + 5
            padics = Zp(backend_prime, type="fixed-mod", prec=precision)
            _diagonal, transform = p_adic_normal_form(
                nondegenerate_form.inverse(),
                backend_prime,
                precision=precision + 5,
            )
            # The engine reduced the inverse form; its dual family reduces the form.
            transform = _engine_dual_row_family(transform.change_ring(SageZZ))
            transform = transform.change_ring(padics).change_ring(SageZZ)
            scaled = (
                _engine_row_family_gram(nondegenerate_form, transform)
                * backend_prime ** nondegenerate_form.denominator().valuation(backend_prime)
            )
            transform = (
                _normalize(scaled.change_ring(padics), normal_odd=False)[1].change_ring(SageZZ)
                * transform
            )
            transform = transform * nondegenerate
        else:
            transform = nondegenerate
        transform = transform.stack(degenerate).change_ring(SageZZ)

        # The engine's coefficients are representatives modulo the p-adic
        # precision; each is raised as its class modulo the order p^v of the
        # primary generator it multiplies.
        jordan_generators = []
        for row in transform.rows():
            classes = tuple(
                SageZZ(coefficient) % order
                for coefficient, order in zip(row, primary_orders, strict=True)
            )
            normalized_element = sum(
                (
                    normalized.scalar_multiple(
                        _owned_engine_element(ring, coefficient), generator
                    )
                    for coefficient, generator in zip(
                        classes, primary_generators, strict=True
                    )
                    if coefficient
                ),
                normalized.zero(),
            )
            jordan_generators.append(normalization.inverse()(normalized_element))
        result[prime] = tuple(jordan_generators)
    return _prime_indexed_generators(result)


def _p_adic_jordan_module_generators(form, *, quadratic: bool):
    r"""Return the selected Jordan generators, prime by prime, inside ``form``."""
    decomposition = _p_adic_jordan_decomposition(form, quadratic=quadratic)
    return tuple(
        generator
        for prime in decomposition.index_set()
        for generator in decomposition[prime]
    )


def _p_adic_jordan_form(form, *, quadratic: bool):
    generators = _p_adic_jordan_module_generators(form, quadratic=quadratic)
    return _regenerate_form_on_generators(form, generators, quadratic=quadratic)


def _twisted_torsion_form(form, scalar, *, quadratic: bool):
    generators = tuple(form.module_generators())
    value_module = _value_module(form, quadratic=quadratic)
    gram = tuple(
        tuple(value_module.scalar_multiple(scalar, entry) for entry in row)
        for row in _form_gram_on(form, generators, quadratic=quadratic)
    )
    return _torsion_form_modules(form.base_ring(), quadratic=quadratic).from_module(
        _underlying_presented_module(form),
        gram,
        _value_module(form, quadratic=quadratic),
    )


def _twisted_module_morphism(module_morphism, twisted_source, twisted_target):
    r"""Read one module map between the twisted copies of its endpoints.

    Twisting rescales the form and leaves the underlying module untouched, so
    ``twisted_source`` shares its underlying module with the source of
    ``module_morphism``, and ``twisted_target`` with its target.  The twisted
    map is therefore the same map: the generator labelled ``l`` goes to the
    image of the generator labelled ``l``, transported through that shared
    underlying module.
    """
    source = module_morphism.domain()
    return twisted_source.module_category().Mor(twisted_source, twisted_target)(
        {
            label: twisted_target(module_morphism(source.module_generator(label)))
            for label in twisted_source.module_generating_set()
        }
    )


class TorsionFormTwistFunctor(Functor):
    r"""The endofunctor ``A |-> A(s)`` rescaling a finite form by ``s``.

    On objects this is the rescale ``b |-> s*b`` (respectively ``q |-> s*q``)
    on the unchanged underlying module.  On arrows it is the identity on
    underlying maps: an isometry ``f`` from ``(A,b)`` to ``(B,b')`` has
    ``b'(f x, f y) = b(x,y)``, hence ``(s*b')(f x, f y) = (s*b)(x,y)``, so the
    same map is an isometry from ``A(s)`` to ``B(s)``.
    """

    def __init__(self, category, scalar, *, quadratic: bool) -> None:
        self._scalar = scalar
        self._quadratic = bool(quadratic)
        super().__init__(category, category)

    def scalar(self):
        r"""Return the scalar this functor multiplies the form by."""
        return self._scalar

    def _apply_object(self, form):
        return _twisted_torsion_form(form, self.scalar(), quadratic=self._quadratic)

    def _apply_morphism(self, isometry):
        source = self.object_image(isometry.domain())
        target = self.object_image(isometry.codomain())
        return _torsion_form_isometry(
            _twisted_module_morphism(isometry.forward(), source, target),
            _twisted_module_morphism(isometry.inverse().forward(), target, source),
            quadratic=self._quadratic,
        )

    def _repr_(self):
        return f"Twist by {self.scalar()} on {self.domain()}"


def _engine_normal_form_key(form, *, quadratic: bool):
    normalization = form.invariant_factor_form()
    engine = _engine_torsion_form(normalization.codomain(), quadratic=quadratic)
    normal = engine.normal_form()
    gram = normal.gram_matrix_quadratic()
    return (
        SageQQ(engine._modulus),
        SageQQ(engine._modulus_qf),
        tuple(SageZZ(invariant) for invariant in normal.invariants()),
        tuple(tuple(SageQQ(entry) for entry in row) for row in gram.rows()),
    )


def _forms_are_isomorphic(left, right, *, quadratic: bool) -> bool:
    if left.base_ring() is not right.base_ring():
        return False
    return _engine_normal_form_key(left, quadratic=quadratic) == _engine_normal_form_key(
        right, quadratic=quadratic
    )


class TorsionFormAutomorphism(TorsionFormIsometry):
    r"""A live form-preserving automorphism, parented by its orthogonal group."""

    def __init__(self, parent, forward, inverse, _engine_element) -> None:
        super().__init__(
            parent,
            forward,
            inverse,
            quadratic=parent.is_quadratic(),
        )
        self._engine_element = _engine_element

    def _engine(self):
        r"""Return the private Sage representative used by this form-group owner.

        Orthogonal-group admission and subgroup construction in this module
        may read it to ask the maintained engine about a raw group element.
        It is not a category-membership datum or a public group result.
        """
        return self._engine_element

    def inverse(self):
        return self.parent()._from_engine(~self._engine())

    def __invert__(self):
        return self.inverse()

    def __mul__(self, other):
        if not isinstance(other, TorsionFormAutomorphism):
            return NotImplemented
        if other.parent() is not self.parent():
            return NotImplemented
        # Sage's private FQF engine acts on the right.  This reversal is kept
        # entirely at the crossing: publicly ``self * other`` is ordinary
        # composition of type-(1,1) tensors/morphisms.
        return self.parent()._from_engine(
            other._engine() * self._engine()
        )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, TorsionFormAutomorphism)
            and other.parent() is self.parent()
            and other._engine() == self._engine()
        )

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(
            (
                id(self.parent()),
                tuple(int(entry) for entry in self._engine().matrix().list()),
            )
        )

    def _repr_(self):
        return f"Form automorphism of {self.domain()}"


class TorsionFormOrthogonalGroup(CategoricalMor):
    r"""The finite group of live automorphisms preserving one finite form."""

    Element = TorsionFormAutomorphism

    @staticmethod
    def __classcall__(cls, mor_family, form, **options):
        return typecall(cls, mor_family, form, **options)

    def _cache_key(self):
        r"""Cache this live fixed-form automorphism group by its canonical identity."""
        return id(self)

    def __init__(
        self,
        mor_family,
        form,
        *,
        quadratic: bool,
    ) -> None:
        r"""Store the form and the quadratic flag, and fix the category (``OWN-22``).

        The invariant-factor normalization, the engine group and the
        generating set are computed on first request and cached.  The
        selected free-group resolution is fixed on the generating set
        computed when it is first read (``CAT-29``).
        """
        self._quadratic = bool(quadratic)
        CategoricalMor.__init__(
            self,
            mor_family,
            form,
            form,
            category=OwnedFiniteGroups(),
        )
        # O(q) is an object of the category of groups (ARC-07; finiteness is a
        # property axiom, kept in category()): group actions on finite sets
        # read this ambient category.
        self._constructing_category = OwnedGroups()
        realize_owned_category(self)
        self.select_group_generators(self._computed_group_generators)

    @cached_method
    def _computed_group_generators(self):
        r"""Return the engine's generators of ``O(q)``, raised to form automorphisms."""
        return finite_ordered_set(
            tuple(self._from_engine(generator) for generator in self._engine_group().gens())
        )

    def is_quadratic(self) -> bool:
        return self._quadratic

    def super_categories(self):
        packet = self.base_category().category_packet()
        form = self.domain()
        supers = [
            packet.Mors().Of(form, form),
            packet.Monos().Of(form, form),
            packet.Epis().Of(form, form),
        ]
        supers.extend(
            superpacket.Isos().Of(form, form)
            for superpacket in packet.super_packets()
            if form in superpacket.C()
        )
        if self.aut_family() is not None:
            supers.append(packet.Ends().Of(form))
            supers.extend(
                superpacket.Auts().Of(form)
                for superpacket in packet.super_packets()
                if form in superpacket.C()
            )
        return _distinct_supercategories(supers)

    def invariant_form(self):
        return self.domain()

    @cached_method
    def normalization_isometry(self):
        r"""Return the isometry from the form to its invariant-factor normal form."""
        return self.domain().invariant_factor_form()

    def supergroup(self):
        return self

    @cached_method
    def _engine_module(self):
        r"""Return the private Sage finite form on the invariant-factor framing."""
        return _engine_torsion_form(
            self.normalization_isometry().codomain(),
            quadratic=self._quadratic,
        )

    @cached_method
    def _engine_group(self):
        r"""Return the private Sage orthogonal-group parent."""
        return _engine_orthogonal_group(self._engine_module())

    def _to_engine(self, automorphism):
        r"""Lower a live automorphism under the owned-group engine contract.

        The subgroup and G-set adapters in ``groups.py`` may use this
        crossing; the engine value stays private to those adapters.
        """
        if not self.accepts(automorphism):
            raise ValueError(f"{automorphism} is not an element of the orthogonal group {self}")
        return self._engine_group()(automorphism._engine())

    def _engine_subgroup_from_generators(self, generators):
        r"""Compute a generated subgroup without allocating another fixed Mor."""
        return self._engine_group().subgroup(
            [self._to_engine(generator) for generator in generators]
        )

    def _to_subgroup_engine(self, automorphism, engine_subgroup):
        r"""Lower an ambient automorphism into the subgroup's private engine."""
        return engine_subgroup(self._to_engine(automorphism))

    def _engine_subgroup_contains(self, automorphism, engine_subgroup):
        return self._to_engine(automorphism) in engine_subgroup

    def _from_subgroup_engine(self, engine_element):
        r"""Raise a subgroup element as an automorphism in the ambient group."""
        return self._from_engine(engine_element)

    def _normalized_map(self, engine_automorphism):
        normalized_form = self.normalization_isometry().codomain()
        engine_module = self._engine_module()
        engine_automorphism = self._engine_group()(engine_automorphism)
        cover = engine_module.V()
        labels = tuple(normalized_form.module_generating_set())
        images = {}
        for label, basis_vector in zip(labels, cover.basis(), strict=True):
            image = engine_module(basis_vector) * engine_automorphism
            coordinates = cover.coordinates(image.lift())
            images[label] = normalized_form.linear_combination(
                {
                    target_label: _owned_engine_element(normalized_form.base_ring(), SageZZ(coefficient))
                    for target_label, coefficient in zip(
                        labels,
                        coordinates,
                        strict=True,
                    )
                    if coefficient
                }
            )
        return normalized_form.module_category().Mor(normalized_form, normalized_form)(images)

    def _from_engine_matrix(self, engine_matrix):
        r"""Cross one private engine matrix to an owned form automorphism.

        Implementation endpoint of
        :func:\`_torsion_form_automorphism_from_engine_matrix\`.  No
        engine-group parent escapes this object.
        """
        return self._from_engine(self._engine_group()(engine_matrix))

    def _transported_map(self, engine_automorphism):
        r"""Return ``n^{-1} a n`` on the form, for the normalization ``n`` and engine automorphism ``a``."""
        normalization = self.normalization_isometry()
        normalized = self._normalized_map(engine_automorphism)
        original = normalization.domain()
        return original.module_category().Mor(original, original)(
            {
                label: normalization.inverse()(
                    normalized(normalization.forward()(original.module_generator(label)))
                )
                for label in original.module_generating_set()
            }
        )

    def _from_engine(self, engine_automorphism):
        r"""Raise one engine automorphism ``a``; its inverse is the transport of ``a^{-1}``."""
        engine_automorphism = self._engine_group()(engine_automorphism)
        return self.element_class(
            self,
            self._transported_map(engine_automorphism),
            self._transported_map(engine_automorphism.inverse()),
            engine_automorphism,
        )

    @cached_method
    def _normalization_homomorphism(self):
        r"""The group homomorphism from form-Core automorphisms to this finite realization."""
        category = _torsion_form_modules(self.domain().base_ring(), quadratic=self.is_quadratic())
        source = category.Core().Mor(self.domain(), self.domain())
        return OwnedGroups().Mor(source, self)(self._normalized_form_automorphism)

    def normalization_homomorphism(self):
        r"""Return the group homomorphism from the form Core to this finite realization."""
        return self._normalization_homomorphism()

    def from_morphism(self, morphism):
        r"""Apply the normalization homomorphism to an automorphism of the formed-module core."""
        homomorphism = self._normalization_homomorphism()
        if not homomorphism.domain().accepts(morphism):
            raise TypeError(f"{morphism} must be an isometry of the formed-module core before normalization")
        return homomorphism(morphism)

    def _normalized_form_automorphism(self, morphism):
        r"""Compute the normalization homomorphism on one admitted form isometry."""
        if morphism.domain() is not self.domain() or morphism.codomain() is not self.domain():
            raise ValueError(
                f"{morphism} is not an automorphism of {self.domain()}: it is a morphism "
                f"{morphism.domain()} -> {morphism.codomain()}"
            )
        normalization = self.normalization_isometry()
        normalized_form = normalization.codomain()

        original_form = normalization.domain()
        forward = normalization.forward().module_morphism()
        inverse = normalization.inverse().forward().module_morphism()
        from sage.matrix.constructor import matrix as sage_matrix

        labels = tuple(normalized_form.module_generating_set())
        engine_rows = []
        ring = normalized_form.base_ring()
        for source_label in labels:
            original = inverse(normalized_form.module_generator(source_label))
            image = forward(morphism(original))
            coordinates = normalized_form.framing_morphism().lift(image)
            engine_rows.append(
                [
                    _engine_element(ring, coordinates(target_label))
                    for target_label in labels
                ]
            )
        # Sage's finite-form engine acts on coordinate rows on the right, so
        # the generator-image rows above are already in its convention.
        engine_matrix = sage_matrix(
            _engine_ring(ring),
            len(labels),
            len(labels),
            [entry for row in engine_rows for entry in row],
        )
        return self._from_engine(self._engine_group()(engine_matrix))

    def _element_constructor_(self, datum):

        if isinstance(datum, TorsionFormAutomorphism):
            if datum.domain() is not self.domain():
                raise ValueError(
                    f"{datum} is an automorphism of {datum.domain()}, not of {self.domain()}"
                )
            if datum.parent() is self:
                return datum
            raise TypeError(f"{datum} belongs to another Mor; apply the realization functor")
        if isinstance(datum, Map):
            raise TypeError(f"{datum} is a whole arrow; apply the form-Core normalization homomorphism")
        return self._from_engine(datum)

    def accepts(self, candidate) -> bool:
        r"""Admit a raw form automorphism to this finite group of maps.

        A differently parented automorphism of the exact same form can be
        checked by the maintained engine's exact element predicate. This is
        raw-arrow admission, also used before constructing a fixed-Mor
        object, not category containment. The
        inherited containment reads placement for the constructed objects and
        delegates only raw morphisms to this operation.
        """
        match candidate:
            case TorsionFormAutomorphism() if candidate.parent() is self:
                return True
            case TorsionFormAutomorphism() if candidate.domain() is self.domain():
                return candidate._engine() in self._engine_group()
            case _:
                return False

    @cached_method
    def one(self):
        return self._from_engine(self._engine_group().one())

    @object_level
    def identity(self, *args, **kwargs):
        return self.one(*args, **kwargs)
    def identity_automorphism(self, *args, **kwargs):
        return self.one(*args, **kwargs)

    def order(self):
        return self.domain().base_ring()(int(self._engine_group().order()))

    cardinality = order

    def __iter__(self):
        return (self._from_engine(element) for element in self._engine_group())

    @cached_method
    def element_action(self):
        r"""Return the represented action of this group on the finite form."""
        return _torsion_form_element_action(self.domain(), self)

    def orbit(self, element):
        r"""Return the orbit of ``element`` through the owned G-set action."""
        element = self.domain()(element)
        action = self.element_action()
        orbits = action.orbits()
        return orbits.orbit_of(element).points()

    def subgroup_on(self, group_generators):
        r"""Return the generated subgroup with its ambient automorphisms unchanged.

        ``Subgroups(self)`` owns its inclusion. The subgroup is a group, not
        another realization of this form's fixed Iso category. Restrict the
        form action along that inclusion to obtain its action on the form.
        """
        supplied = tuple(group_generators)
        if any(generator.parent() is not self for generator in supplied):
            raise ValueError(
                f"a subgroup of {self} is generated by elements of {self}, but {supplied} contains an element "
                "of another group"
            )
        return self.subgroup(supplied)

    def stabilizer_of_element(self, element):
        r"""Return the point stabilizer through the represented G-set action."""
        element = self.domain()(element)
        return self.element_action().stabilizer(element)

    @cached_method
    def subobject_action(self):
        r"""Return the represented action of this group on the submodules of its finite form."""
        form = self.domain()
        family = _torsion_form_all_subobjects(
            form,
            quadratic=self.is_quadratic(),
        )
        return _torsion_form_subobject_action(form, family, self)

    def subobject_point(self, subgroup):
        r"""Return the point of :meth:`subobject_action` that is the submodule ``subgroup``."""
        form = self.domain()
        base_ring = form.base_ring()
        if subgroup not in ModuleSubobjects(base_ring):
            raise TypeError(
                f"the submodules of {form} acted on by {self} have inclusion morphisms, but {subgroup} "
                "has none"
            )
        if subgroup not in Modules(base_ring).Subobjects(form):
            raise ValueError(
                f"{self} acts on submodules of {form}, but {subgroup} "
                f"is a submodule of {subgroup.inclusion().codomain()}"
            )
        by_embedded_elements = {
            _embedded_elements(candidate): candidate
            for candidate in self.subobject_action().point_set()
        }
        embedded = _embedded_elements(subgroup)
        if embedded not in by_embedded_elements:
            raise ValueError(
                f"{subgroup} does not match any submodule of {form}, so it is no point of the action of {self}"
            )
        return by_embedded_elements[embedded]

    def stabilizer_of_subgroup(self, subgroup):
        r"""Return the setwise stabilizer through the owned subobject G-set."""
        return self.subobject_action().stabilizer(self.subobject_point(subgroup))

    stabilizer_of_subobject = stabilizer_of_subgroup

    def _repr_(self):
        return f"Orthogonal group of {self.domain()}"


def _torsion_form_automorphism_from_engine_matrix(orthogonal_group, engine_matrix):
    r"""Raise one exact backend matrix to an owned torsion-form automorphism.

    Protected torsion-form contract (\`OWN-05\`--\`OWN-07\`).  The
    permitted caller is the lattice centralizer-image adapter, which receives
    exact matrices from OSCAR in the common Smith-generator row convention.
    The matrix is consumed by this torsion-form owner and the returned value is
    an owned automorphism; neither the private orthogonal-group parent nor an
    engine element leaves this dispatcher.
    """
    if not isinstance(orthogonal_group, TorsionFormOrthogonalGroup):
        raise TypeError(
            f"an automorphism matrix is interpreted only in the orthogonal group of a torsion form, "
            f"but {orthogonal_group} is not one"
        )
    return orthogonal_group._from_engine_matrix(engine_matrix)


def _torsion_form_automorphism_group(form, *, quadratic: bool):
    category = (
        _torsion_form_modules(form.base_ring(), quadratic=True)
        if quadratic
        else _torsion_form_modules(form.base_ring(), quadratic=False)
    )
    return category.Aut(form)


class _TorsionFormIsoCategoryConstruction(IsoCategoryConstruction):
    r"""Finite torsion-form isometries with maintained orthogonal groups on the diagonal."""

    quadratic = False

    def fixed_category_class(self):
        return TorsionFormIsometryMor

    def Of(self, domain, codomain=None):
        if codomain is None:
            codomain = domain
        if domain is not codomain:
            return super().Of(domain, codomain)
        # Endpoint identity, not equality: two equal torsion forms are two
        # objects, each with its own orthogonal group.
        cached = self._cached_between(domain, domain)
        if cached is not None:
            return cached
        group = TorsionFormOrthogonalGroup(self, domain, quadratic=self.quadratic)
        return self._remember_between(domain, domain, group)


class TorsionBilinearFormIsoCategoryConstruction(_TorsionFormIsoCategoryConstruction):
    quadratic = False


class TorsionQuadraticFormIsoCategoryConstruction(_TorsionFormIsoCategoryConstruction):
    quadratic = True


def _invariant_factor_form_isomorphism(form, quadratic: bool):
    r"""Transport ``form`` to the invariant-factor framing, with its isometry.

    The underlying module normalization is the explicit Smith isomorphism
    ``M -> M_if``.  The form on ``M_if`` is obtained by pulling the selected
    bilinear lift along its inverse, so no form data are inferred from an
    abstract invariant-factor decomposition.  The pullback is one tensor
    contraction ``c^t G c`` (``OWN-24``): ``G`` holds rational representatives
    of the form on the framing of ``M``, and ``c: F(S_if) -> F(S)`` lifts the
    inverse to the framings, sending each generator of ``M_if`` to a lift of
    its image in ``M``.
    """
    module = form.unformed_module()

    module_isomorphism = _module_invariant_factor_form(module)
    normalized_module = module_isomorphism.codomain()
    inverse = module_isomorphism.inverse()
    framing = module.framing_morphism()
    normalized_cover = normalized_module.framing_morphism().domain()
    cover_inverse = normalized_cover.module_category().Mor(normalized_cover, framing.domain())(
        {
            label: framing.lift(inverse(normalized_module.module_generator(label)))
            for label in normalized_cover.module_generating_set()
        }
    )
    gram = _representative_gram(form, quadratic=quadratic).pullback(cover_inverse)
    normalized = _torsion_form_modules(form.base_ring(), quadratic=quadratic).from_module(
        normalized_module,
        gram,
        form.value_module(),
    )

    forward_images = {
        label: normalized(module_isomorphism(module(form.module_generator(label))))
        for label in form.module_generating_set()
    }
    forward = form.module_category().Mor(form, normalized)(forward_images)

    inverse_images = {
        label: form(module_isomorphism.inverse()(normalized_module(normalized.module_generator(label))))
        for label in normalized.module_generating_set()
    }
    inverse = normalized.module_category().Mor(normalized, form)(inverse_images)
    return _torsion_form_isometry(forward, inverse, quadratic=quadratic)


class CokernelTorsionFormModules(OwnedCategoryOverBaseRing):
    r"""Finite formed modules retained as literal cokernels of a selected module map."""

    def _repr_object_names(self):
        return f"cokernel torsion forms over {self.base_ring()}"

    def super_categories(self):
        from sage_extensions.categories.modules.framed.formed.form_modules import (
            FormModules,
        )

        return [FormModules(self.base_ring()).FinitelyPresented().Torsion()]

    class ParentMethods:
        def cover(self):
            r"""Return the codomain of the selected presentation map."""
            return self.presentation().codomain()

        @cached_method
        def projection(self):
            r"""Return the quotient projection from the cover to this formed cokernel."""
            unformed_projection = self.presentation().cokernel_projection()
            if unformed_projection.codomain() is not self.unformed_module():
                raise ArithmeticError(
                    f"the cokernel projection of {self.presentation()} lands in {unformed_projection.codomain()}, "
                    f"not in the module underlying {self}"
                )
            cover = unformed_projection.domain()
            return cover.module_category().Mor(cover, self)(
                {
                    label: self(unformed_projection(cover.module_generator(label)))
                    for label in cover.module_generating_set()
                }
            )

    class ElementMethods:
        def coset_representative(self):
            r"""Return the selected lift of this class to the cokernel cover."""
            formed = self.parent()
            unformed = formed.unformed_module()
            coordinates = unformed.framing_morphism().lift(unformed(self))
            cover = formed.cover()
            return cover.linear_combination(
                {label: coordinates(label) for label in coordinates.support().domain()}
            )


__all__ = [
    "CokernelTorsionFormModules",
    "TorsionFormAutomorphism",
    "TorsionFormIsometry",
    "TorsionFormOrthogonalGroup",
]


# ---------------------------------------------------------------------------
# Engine orthogonal groups of finite quadratic modules (private)
# ---------------------------------------------------------------------------



def _engine_orthogonal_group(T):
    r"""Sage's ``O(T)`` for a finite quadratic module ``T``, from generators of its primary parts.

    ``O(T)`` is the product of the ``O(T_p)``.  An elementary ``T_p`` with
    ``p`` odd has ``q`` determined by ``b``, and ``O(T_p)`` is the orthogonal
    group of the Gram matrix of ``p b`` over ``GF(p)``: GAP's
    ``GO(epsilon, n, p)`` conjugated onto that matrix by an explicit isometry
    of diagonalized forms. The other primary parts use OSCAR's normal-form
    orthogonal-group algorithm on the same presented quotient, retaining
    both value moduli and the Smith generator basis. The isometry of diagonalized
    forms is computed here because GAP's ``forms`` package, which provides
    ``BaseChangeToCanonical``, is not installed in the engine (TRAPS.md).
    """
    from sage_extensions.categories.lattice_engines import _oscar_lattices

    exponent = SageZZ(T.annihilator().gen())
    generators = []
    order = SageZZ.one()
    for p in exponent.prime_divisors():
        part = T.primary_part(p)
        gens = part.smith_form_gens()
        n = len(gens)
        if p != 2 and all(x == p for x in part.invariants()):
            field = _engine_GF(p)
            gram = _engine_matrix(field, n, n, [field(p * gens[i].b(gens[j]).lift()) for i in range(n) for j in range(n)])
            matrices, part_order = _engine_odd_orthogonal_generators(gram, p)
        else:
            gram = _engine_matrix(SageQQ, n, n, [
                gens[i].q().lift() if i == j else gens[i].b(gens[j]).lift()
                for i in range(n) for j in range(n)
            ])
            part_order, matrices = _oscar_lattices.finite_form_isometry_group(
                gram, part.invariants(), part._modulus, part._modulus_qf
            )
        order *= part_order
        for m in matrices:
            images = [sum((SageZZ(m[i, j]) * gens[j] for j in range(n)), part.zero()) for i in range(n)]
            generators.append(_extend(T, part, gens, p, exponent, images))
    group = T.orthogonal_group(gens=generators)
    group.gap().SetSize(order)
    return group


def _extend(T, part, gens, p, exponent, images):
    power = p ** exponent.valuation(p)
    cofactor = exponent // power
    idempotent = SageZZ(cofactor * cofactor.inverse_mod(power))
    result = []
    for x in T.gens():
        component = idempotent * x
        coordinates = part(component).vector()
        assert sum((SageZZ(c) * T(g) for c, g in zip(coordinates, gens, strict=True)), T.zero()) == component
        moved = sum((SageZZ(c) * T(image) for c, image in zip(coordinates, images, strict=True)), T.zero())
        result.append(moved + x - component)
    return T.hom(result)
