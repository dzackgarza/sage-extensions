r"""Algebraic connections on represented modules over commutative algebras."""

from collections.abc import Mapping

from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import Element
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    _RestrictedMorCategoryOf,
    RestrictedMorCategoryParent,
    _category_mor_parent,
)
from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.algebras.differential_graded_algebras import DifferentialComponentMorphism
from sage_extensions.categories.modules.cochain_complexes import (
    CochainComplexes,
    _CochainComplexDirectSum,
)
from sage_extensions.categories.modules.dg_modules import DifferentialGradedModules
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import _relation_morphism
from sage_extensions.categories.modules.graded_direct_sums import GradedDirectSumElement
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphism,
)
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModulesWithChosenFinitePresentation,
)

from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family_from_values,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.categories.schemes.ringed_spaces import QuasiCoherentSheaves
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.logic import AtomicProposition, ask, conjunction
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.validation import validator

# ``Integrable`` is the property that the curvature of the selected connection
# vanishes.  ``Flat`` already names the flat-module axiom of ``Modules(R)``, so
# the connection property takes the name of its integrability condition.
if "Integrable" not in all_axioms:
    all_axioms.add("Integrable")


class ModulesWithConnection(OwnedParameterizedCategory):
    r"""Modules over ``A`` equipped with an ``A/R``-connection."""

    def an_object(self):
        r"""A free rank-one module over the algebra, with the zero connection.

        The zero connection is flat, so this object is a specimen of both this
        category and its flat refinement.
        """
        from sage_extensions.categories.sets.set_categories import finite_ordinal_set

        module = self.algebra().free_module(finite_ordinal_set(1))
        connections = module.connections()
        return self(
            connections(lambda _label: connections.target_module().zero())
        )

    @classmethod
    def _repr_object_names(cls):
        return "modules with connection"

    def algebra(self):
        return self.base()

    def parameter_category(self):
        r"""The commutative algebras over the parameter's own base."""
        return Algebras(self.parameter().base_ring()).Associative().Unital().Commutative()

    def super_categories(self):

        return [Modules(self.algebra())]

    def Mor(self, domain, codomain):
        r"""Return horizontal module maps between two objects with connection."""
        if domain not in self or codomain not in self:
            raise TypeError(
                f"{self}.Mor({domain}, {codomain}) needs two modules with connection over {self.algebra()}, "
                f"but {domain} is in {domain.category()} and {codomain} is in {codomain.category()}"
            )
        return ConnectionMorphismCategoryConstruction(Modules(self.algebra())).Of(
            domain,
            codomain,
        )

    def _call_(self, connection):
        r"""Equip the source module with the selected connection.

        The object is placed here and nowhere stronger: whether the connection
        is integrable is a property asked of the object
        (:meth:`ParentMethods.is_flat_connection`), never a placement that
        construction computes (``CON-07``, ``OWN-22``).
        """
        return _equip_with_connection(self, connection)

    class SubcategoryMethods:
        def algebra(self):
            return self.base_category().algebra()

        def Integrable(self) -> Category:
            r"""Modules whose selected connection has zero curvature.

            A connection ``nabla: E -> E tensor_A Omega^1_{A/R}`` is integrable
            (flat) when its curvature ``nabla^2: E -> E tensor_A Omega^2_{A/R}``
            vanishes (Katz, *Nilpotent connections and the monodromy theorem*,
            Publ. Math. IHES 39 (1970), §1.0).
            """
            return self._with_axiom("Integrable")

    class Integrable(CategoryWithAxiom):
        r"""Modules with connection whose curvature ``nabla^2`` vanishes.

        Full: a horizontal map between integrable connections is a horizontal
        map, so this axiom declares no Mor family of its own.
        """

        def an_object(self):
            r"""A free rank-one module over the algebra, with the zero connection.

            The zero connection has zero curvature.
            """
            from sage_extensions.categories.sets.set_categories import finite_ordinal_set

            module = self.algebra().free_module(finite_ordinal_set(1))
            connections = module.connections()
            return self(connections(lambda _label: connections.target_module().zero()))

        @classmethod
        def _repr_object_names(cls):
            return "modules with flat connection"

        def _call_(self, connection):
            r"""Equip the source module with ``connection``, placed here.

            The caller states that the connection is integrable; construction
            computes nothing (``CON-07``, ``OWN-22``).
            """
            return _equip_with_connection(self, connection)

        def __contains__(self, candidate):
            r"""Placement, else the proposition that the curvature vanishes, asked (``CON-07``).

            The answer goes to the caller and never changes the object's
            placement.
            """
            base = self.base_category()
            match candidate:
                case _ if Category.__contains__(self, candidate):
                    return True
                case _ if Category.__contains__(base, candidate):
                    return ask(candidate.connection().is_flat()) is True
                case _:
                    return False

        class ParentMethods:
            def is_flat_connection(self) -> bool:
                r"""``True``: the curvature vanishes by placement."""
                return True

    class ParentMethods:
        def __init__(self, source_connection, unformed_module, **rest) -> None:
            assert source_connection.module() is unformed_module, (
                f"{unformed_module} cannot carry {source_connection}: that is a connection on "
                f"{source_connection.module()}, a different module"
            )
            self._preamble_source_connection = source_connection
            self._preamble_unformed_module = unformed_module
            super().__init__(**rest)

        def unformed_module(self):
            r"""Return the module on which the selected connection was stated."""
            return self._preamble_unformed_module

        def _element_of_unformed_module(self, element):
            module = self.unformed_module()
            coordinates = self._framing_lift(self(element))
            return module.linear_combination({label: coordinates(label) for label in coordinates.support().domain()})

        def _element_from_unformed_module(self, element):
            coordinates = self.unformed_module().framing_morphism().lift(element)
            return self.linear_combination({label: coordinates(label) for label in coordinates.support().domain()})

        @cached_method
        def connection(self):
            r"""Return the selected connection datum on :meth:`unformed_module`."""
            return self._preamble_source_connection

        def is_flat_connection(self):
            r"""Whether the curvature ``nabla^2`` of :meth:`connection` vanishes.

            Decided on the chosen finite generators where they exist, else the
            proposition ``is_flat`` (:meth:`Connection.is_flat`).
            """
            return self.connection().is_flat()

        def _Hom_(self, codomain, category=None):
            return self.Mor(codomain, category=category)


def _equip_with_connection(category, connection):
    r"""The module of ``connection`` equipped with it, as an object of ``category``."""
    source = connection.module()
    algebra = connection.algebra()
    assert element_parent(connection) is source.connections(), (
        f"an object of {category} is constructed from a connection E -> E tensor_A Omega^1 on E, "
        f"but {connection!r} is not an element of {source.connections()}"
    )
    assert algebra is category.algebra(), (
        f"{connection} cannot equip an object of {category}: it is a connection over {algebra}, "
        f"not over {category.algebra()}"
    )
    assert source.has_selected_module_resolution(), (
        f"{connection} cannot equip {source} with a connection: the connection is given by its values on "
        f"module generators, so {source} must have chosen generators over {algebra}, but it is in "
        f"{source.category()}"
    )
    return source._module_with_structure(
        (category,),
        {
            "source_connection": connection,
            "unformed_module": source,
        },
    )


# ``Integrable`` is an owned axiom unknown to Sage's axiom names; register the
# nested refinement explicitly, as for ``Algebras.Lie``.
ModulesWithConnection.__dict__["Integrable"]._base_category_class_and_axiom = (
    ModulesWithConnection,
    "Integrable",
)

ModulesWithFlatConnection = ModulesWithConnection.Integrable


class VectorBundlesWithConnection(OwnedParameterizedCategory):
    r"""Vector bundles on a scheme ``X`` over ``S`` with an ``S``-connection.

    An object is a pair ``(E, nabla)``: ``E`` a locally free ``O_X``-module of
    finite rank, and ``nabla: E -> Omega^1_{X/S} tensor_{O_X} E`` a map of
    abelian sheaves satisfying the Leibniz rule
    ``nabla(g e) = dg tensor e + g nabla(e)`` for local sections ``g`` of
    ``O_X`` and ``e`` of ``E``.  A morphism is a horizontal ``O_X``-linear map
    (Katz, *Nilpotent connections and the monodromy theorem*, Publ. Math.
    IHES 39 (1970), (1.0)).  ``S`` is the base scheme of ``X``.

    On an affine ``X = Spec A`` over ``S = Spec R`` the global sections of
    ``(E, nabla)`` are an object of ``ModulesWithConnection(A)``.

    Forgetting ``nabla`` lands in the locally free ``O_X``-modules of finite
    rank, ``QuasiCoherentSheaves(X).FiniteLocallyFree()``, the one immediate
    supercategory (``CAT-15``).
    """

    def super_categories(self):
        return [QuasiCoherentSheaves(self.scheme()).FiniteLocallyFree()]

    def _repr_object_names(self):
        return f"vector bundles with connection on {self.scheme()}"

    def scheme(self):
        r"""The scheme ``X`` on which the bundles live."""
        return self.base()

    def base_scheme(self):
        r"""The base ``S`` of ``X``, relative to which ``nabla`` differentiates."""
        return self.scheme().base_scheme()

    def _call_(self, bundle, connection):
        r"""The pair ``(E, nabla)`` of a locally free ``O_X``-module and an ``S``-connection on it."""
        assert False, "construction of a vector bundle with connection on VectorBundlesWithConnection: not implemented"

    class SubcategoryMethods:
        def scheme(self):
            return self.base_category().scheme()

        def Integrable(self) -> Category:
            r"""Vector bundles whose connection has zero curvature.

            The curvature of ``nabla`` is the ``O_X``-linear map
            ``K = nabla_1 o nabla: E -> Omega^2_{X/S} tensor E``; ``nabla`` is
            integrable when ``K = 0`` (Katz 1970, (1.0)).  The integrable
            objects form Katz's category ``MIC(X/S)`` restricted to locally
            free ``E`` (Katz 1970, (1.2)).
            """
            return self._with_axiom("Integrable")

    class Integrable(CategoryWithAxiom):
        r"""Vector bundles with an integrable ``S``-connection.

        Full: a horizontal map between integrable connections is a horizontal
        map, so this axiom declares no morphisms of its own.
        """

        def _repr_object_names(self):
            return f"vector bundles with integrable connection on {self.base_category().scheme()}"

        class ParentMethods:
            def is_integrable(self) -> bool:
                return True

            def de_rham_complex(self):
                r"""The de Rham complex ``Omega^*_{X/S} tensor E`` of ``(E, nabla)``.

                Integrability ``K = 0`` makes the extensions
                ``nabla_i: Omega^i tensor E -> Omega^{i+1} tensor E`` square to
                zero, so they form a complex of abelian sheaves on ``X``
                (Katz 1970, (1.0), (1.3)).
                """
                assert False, "de_rham_complex on VectorBundlesWithConnection.Integrable: not implemented"

    class ParentMethods:
        def underlying_vector_bundle(self):
            r"""The locally free ``O_X``-module ``E``, an object of ``QuasiCoherentSheaves(X)``."""
            assert False, "underlying_vector_bundle on VectorBundlesWithConnection: not implemented"

        def connection(self):
            r"""The ``S``-connection ``nabla: E -> Omega^1_{X/S} tensor_{O_X} E``."""
            assert False, "connection on VectorBundlesWithConnection: not implemented"

        def curvature(self):
            r"""The ``O_X``-linear curvature ``K: E -> Omega^2_{X/S} tensor_{O_X} E`` (Katz 1970, (1.0))."""
            assert False, "curvature on VectorBundlesWithConnection: not implemented"

        def is_integrable(self):
            r"""Whether the curvature ``K`` vanishes, else the proposition that it does."""
            assert False, "is_integrable on VectorBundlesWithConnection: not implemented"


VectorBundlesWithConnection.__dict__["Integrable"]._base_category_class_and_axiom = (
    VectorBundlesWithConnection,
    "Integrable",
)


class _GaussManinConnection:
    r"""``(H^k_dR(X/S), nabla_GM)`` for a smooth proper ``f: X -> S``.

    The defining data are the arrow ``f`` and the degree ``k``.  The bundle is
    the hyperdirect image ``R^k f_*(Omega^*_{X/S})`` and ``nabla_GM`` is the
    Gauss-Manin connection relative to the base of ``S``; it is integrable
    (Katz, *Nilpotent connections and the monodromy theorem*, Publ. Math.
    IHES 39 (1970), (3.0)).  The caller supplies a smooth proper ``f``.
    """

    def __init__(self, family_morphism, degree, underlying_vector_bundle, **rest) -> None:
        self._family_morphism = family_morphism
        self._degree = degree
        self._underlying_vector_bundle = underlying_vector_bundle
        super().__init__(**rest)

    def family_morphism(self):
        r"""The smooth proper arrow ``f: X -> S``."""
        return self._family_morphism

    def degree(self):
        r"""The cohomological degree ``k``."""
        return self._degree

    def scheme(self):
        return self.family_morphism().codomain()

    def underlying_vector_bundle(self):
        r"""``R^k f_*(Omega^*_{X/S})``, an object of ``QuasiCoherentSheaves(S).FiniteLocallyFree()``."""
        return self._underlying_vector_bundle

    def connection(self):
        r"""``nabla_GM: H^k_dR(X/S) -> Omega^1_{S/T} tensor H^k_dR(X/S)``, for ``T`` the base of ``S``.

        Katz and Oda compute ``nabla_GM`` as the connecting map of the
        filtration of ``Omega^*_X`` by pullbacks of forms on ``S`` (Katz,
        Oda, *On the differentiation of de Rham cohomology classes with
        respect to parameters*, J. Math. Kyoto Univ. 8 (1968)).
        """
        assert False, "connection on the Gauss-Manin connection of a scheme morphism: not implemented"

    def _repr_(self) -> str:
        f = self.family_morphism()
        return (
            f"Gauss-Manin connection on H^{self.degree()}_dR(X/S) of the family "
            f"X = {f.domain()} over S = {f.codomain()}"
        )


class Connection(Element):
    r"""An ``R``-connection ``E -> E tensor_A Omega^1_{A/R}``."""

    def __init__(self, parent, generator_values) -> None:
        r"""The connection with value ``generator_values(s)`` on the module generator ``s``.

        ``generator_values`` is an indexed family on the module generating
        set; :meth:`ConnectionSpace._element_constructor_` reads the caller's
        callable or table into it (``CON-17``).
        """
        Element.__init__(self, parent)
        labels = self.module().module_generating_set()
        target = self.target_module()

        def image(label):
            value = generator_values.value(labels(label))
            return value if value.parent() is target else target(value)

        self._generator_images = indexed_family(
            labels,
            image,
            name=f"Connection generator values of {self.module()}",
        )

    def module(self):
        return self.parent().module()

    def algebra(self):
        return self.parent().algebra()

    def one_forms(self):
        return self.parent().one_forms()

    def target_module(self):
        return self.parent().target_module()

    def generator_image(self, label):
        return self._generator_images[label]

    def _from_coefficients(self, coefficients):
        target = self.target_module()
        universal = self.one_forms().universal_derivation()
        result = target.zero()
        for label, coefficient in coefficients.items():
            if not coefficient:
                continue
            result += target.scalar_multiple(
                coefficient,
                self.generator_image(label),
            )
            d_coefficient = universal(self.algebra()(coefficient))
            if (d_coefficient == self.one_forms().zero()) is not True:
                result += target.pure_tensor(
                    self.module().module_generator(label),
                    d_coefficient,
                )
        return result

    @validator
    def validate_relations(self) -> None:
        r"""Raise ``ValueError`` unless ``nabla`` sends every presentation relation to zero (``OWN-22``).

        For a relation ``sum_i a_i e_i = 0`` the Leibniz rule gives
        ``nabla(sum_i a_i e_i) = sum_i (a_i nabla(e_i) + e_i tensor d a_i)``,
        which must vanish for ``nabla`` to be well defined on the module.
        """
        module = self.module()
        if module not in ModulesWithChosenFinitePresentation(self.algebra()):
            return
        relations = _relation_morphism(module)
        for relation_label in relations.domain().module_generating_set():
            relation = relations(relations.domain().module_generator(relation_label)).to_vector()
            value = self._from_coefficients(
                {label: relation(label) for label in relation.support().domain()}
            )
            if (value == self.target_module().zero()) is False:
                raise ValueError(
                    f"the proposed connection is not well defined on {module}: it must send every relation "
                    f"among the module generators to zero, but it sends the relation {relation} to {value}"
                )

    def __call__(self, element):
        if element.parent() is not self.module():
            element = self.module()(element)
        coordinates = self.module().framing_morphism().lift(element)
        return self._from_coefficients({label: coordinates(label) for label in coordinates.support().domain()})

    def _call_(self, element):
        return self.__call__(element)

    def underlying_linear_morphism(self):
        r"""The image of this connection under ``Conn(E) -> Mor_R(E, E tensor_A Omega^1)``."""
        return self.parent().inclusion()(self)

    as_morphism = underlying_linear_morphism

    def curvature_target(self):
        target_forms = self.one_forms().exterior_power(2)
        return Modules(self.module().base_ring()).tensor_product(
            (self.module(), target_forms)
        )

    def _wedge_connection_value(self, value, one_form):
        omega = self.one_forms()
        omega_two = omega.exterior_power(2)
        target_two = self.curvature_target()
        result = target_two.zero()
        coordinates = self.target_module().framing_morphism().lift(value)
        for label in coordinates.support().domain():
            module_label, form_label = label
            coefficient = coordinates(label)
            wedge = omega.exterior_power_product(
                1,
                omega.module_generator(form_label),
                1,
                one_form,
            )
            if wedge != omega_two.zero():
                result += target_two.scalar_multiple(
                    coefficient,
                    target_two.pure_tensor(
                        self.module().module_generator(module_label),
                        wedge,
                    ),
                )
        return result

    def curvature_on_generator(self, label):
        omega = self.one_forms()
        omega_two = omega.exterior_power(2)
        target_two = self.curvature_target()
        universal = omega.universal_derivation()
        result = target_two.zero()
        coordinates = self.target_module().framing_morphism().lift(self.generator_image(label))
        for image_label in coordinates.support().domain():
            module_label, form_label = image_label
            coefficient = coordinates(image_label)
            one_form = omega.module_generator(form_label)
            result += target_two.scalar_multiple(
                coefficient,
                self._wedge_connection_value(
                    self.generator_image(module_label),
                    one_form,
                ),
            )
            d_coefficient = universal(self.algebra()(coefficient))
            if d_coefficient != omega.zero():
                wedge = omega.exterior_power_product(
                    1,
                    d_coefficient,
                    1,
                    one_form,
                )
                if wedge != omega_two.zero():
                    result += target_two.pure_tensor(
                        self.module().module_generator(module_label),
                        wedge,
                    )
        return result

    def is_flat(self):
        r"""Decide flatness on the chosen finite generators, else answer the proposition ``is_flat``."""
        module = self.module()
        ring = module.base_ring()
        match module in ModulesWithChosenFinitePresentation(ring):
            case False:
                return AtomicProposition("is_flat", self)
            case True:
                pass
        labels = module.module_generating_set()
        match labels.cardinality().is_finite():
            case True:
                pass
            case _:
                return AtomicProposition("is_flat", self)
        zero = self.curvature_target().zero()
        return conjunction(
            self.curvature_on_generator(label) == zero
            for label in labels
        )

    def de_rham_module(self):
        r"""Return the DG-module de Rham complex attached to this flat connection."""
        return ConnectionDeRhamModule(self)


class ConnectionSpace(RestrictedMorCategoryParent):
    Element = Connection

    def __init__(self, family, domain, codomain, *, category) -> None:
        module = domain.module_over_extension()
        algebra = module.base_ring()
        if algebra not in Algebras(algebra.base_ring()).Associative().Unital().Commutative():
            raise TypeError(
                f"{module} has no algebraic connections here: they are defined for modules over a "
                f"commutative algebra, but its base ring {algebra} is in {algebra.category()}"
            )
        self._module = module
        self._algebra = algebra
        self._one_forms = algebra.kahler_differentials()

        self._target_module = codomain.module_over_extension()
        expected_target = Modules(module.base_ring()).tensor_product(
            (module, self._one_forms)
        )
        if self._target_module is not expected_target:
            raise ValueError(
                f"a connection on {module} takes values in {expected_target} = E tensor_A Omega^1, "
                f"but the given target is {self._target_module}"
            )
        # A connection is an R-linear map E -> E (x) Omega satisfying Leibniz,
        # so this is the subcategory of the existing R-linear Mor category cut
        # out by that rule.
        RestrictedMorCategoryParent.__init__(
            self,
            family,
            domain,
            codomain,
            category=category,
        )
        # The inclusion is injective and its arrows are constructed here, so
        # its image is recorded together with its section.  The Leibniz rule
        # is not decided for an arbitrary R-linear map, so an arrow belongs to
        # this restricted Mor when it lies in that recorded image.
        self._underlying_arrows = {}
        self._inclusion_preimages = {}
        self._inclusion = Sets().Mor(self, self.arrow_set())(self._underlying_arrow)

    def _underlying_arrow(self, connection):
        arrow = self._underlying_arrows.get(id(connection))
        if arrow is not None:
            return arrow
        target = self.codomain_object()
        parent = self.arrow_set()
        arrow = parent.element_class(
            parent,
            lambda element: target(connection(element.underlying_element())),
            elementwise=True,
            linearity_premises=(),
        )
        arrow._elementwise_linearity_witness = True
        self._underlying_arrows[id(connection)] = arrow
        self._inclusion_preimages[id(arrow)] = connection
        return arrow

    def module(self):
        return self._module

    def algebra(self):
        return self._algebra

    def one_forms(self):
        return self._one_forms

    def target_module(self):
        return self._target_module

    def inclusion(self):
        return self._inclusion

    def inclusion_image_contains(self, arrow) -> bool:
        r"""Whether ``arrow`` is the image of a connection under :meth:`inclusion`."""
        return id(arrow) in self._inclusion_preimages

    def inclusion_preimage(self, arrow):
        r"""The connection whose underlying ``R``-linear map is ``arrow``."""
        assert self.inclusion_image_contains(arrow), (
            f"{arrow} is not the underlying R-linear map of a connection in {self}"
        )
        return self._inclusion_preimages[id(arrow)]

    def _element_constructor_(self, generator_images, *, check=False):
        r"""The connection given by its values on the module generators (``CON-17``).

        The values arrive as a callable on the generating set, as a table
        keyed by the generators, or as a finite sequence in the order of the
        generating set.  An arrow of the underlying ``R``-linear Mor is a
        connection when this restricted Mor admits it.
        """
        labels = self.module().module_generating_set()
        match element_parent(generator_images):
            case selected if selected is self:
                return generator_images
            case selected if selected is self.arrow_set():
                assert self.accepts(generator_images), (
                    f"{generator_images} is not known to satisfy the Leibniz rule, so it is not a connection "
                    f"in {self}; construct it from the images of the module generators instead"
                )
                return self.inclusion_preimage(generator_images)
        match generator_images:
            case Mapping() | tuple() | list():
                values = finite_indexed_family_from_values(labels, generator_images)
            case _:
                values = indexed_family(labels, generator_images)
        connection = Connection(self, values)
        connection.validate_relations(check=check)
        return connection

    def _repr_(self):
        return f"Connections on {self.module()} over {self.algebra().base_ring()}"


class ConnectionCategoryConstruction(_RestrictedMorCategoryOf):
    _declaration_name = "_ConnectionCategory"

    def fixed_category_class(self):
        return ConnectionSpace

    def accepts(self, arrow) -> bool:
        r"""Whether ``arrow`` is the underlying ``R``-linear map of a connection.

        The Leibniz rule is not decided for an arbitrary ``R``-linear map, so
        admission reads construction: ``arrow`` lies in the image of the
        inclusion of the connection space with its endpoints.
        """
        connections = self._cached_between(arrow.domain(), arrow.codomain())
        return connections is not None and connections.inclusion_image_contains(arrow)


@cached_function(key=lambda module: id(module))
def _connections(module) -> ConnectionSpace:
    algebra = module.base_ring()
    if algebra not in Algebras(algebra.base_ring()).Associative().Unital().Commutative():
        raise TypeError(
            f"{module} has no algebraic connections here: they are defined for modules over a "
            f"commutative algebra, but its base ring {algebra} is in {algebra.category()}"
        )
    one_forms = algebra.kahler_differentials()
    target = Modules(module.base_ring()).tensor_product((module, one_forms))
    ring_map = algebra.algebra_structure_morphism()
    restricted_source = module.restrict_scalars(ring_map)
    restricted_target = target.restrict_scalars(ring_map)
    return ConnectionCategoryConstruction(Modules(algebra.base_ring())).Of(
        restricted_source,
        restricted_target,
    )


class ConnectionMorphism(Element):
    r"""An ``A``-linear map horizontal for the selected connections."""

    def __init__(self, parent, images, *, horizontality_premises=None) -> None:
        Element.__init__(self, parent)
        self._horizontality_premises = horizontality_premises
        arrow_parent = parent.arrow_set()
        underlying = arrow_parent(images)
        self._underlying_morphism = arrow_parent.element_class(
            arrow_parent,
            lambda element: underlying(element),
            elementwise=True,
            linearity_premises=(underlying,),
        )
        self._underlying_morphism._elementwise_linearity_witness = underlying

    def _horizontality_derivation(self):
        r"""Return a construction-derived horizontality decision, or ``None``.

        A map built by an operation of its Mor from horizontal maps (an
        identity, a composite) is horizontal when every premise is; the empty
        family means the construction alone makes it horizontal.
        """
        match self._horizontality_premises:
            case None:
                return None
            case premises:
                return conjunction(premise.horizontality_decision() for premise in premises)

    @validator
    def validate_linearity(self) -> None:
        r"""Raise ``ValueError`` unless the underlying map is known to be linear (``OWN-22``)."""
        underlying = self.underlying_linear_morphism()
        if underlying.linearity_decision() is not True:
            raise ValueError(
                f"{underlying} is not a morphism of modules with connection: it must be linear over "
                f"{underlying.domain().base_ring()}, and that is not known"
            )

    @cached_method
    def horizontality_decision(self) -> bool:
        r"""Return whether this map commutes with the connections, computed on first request."""
        match self._horizontality_derivation():
            case None:
                return self._horizontal_on_generators()
            case derived:
                return derived

    @validator
    def validate_horizontality(self) -> None:
        r"""Raise ``ValueError`` unless ``nabla_F f = (f tensor 1) nabla_E`` (``OWN-22``)."""
        if self.horizontality_decision() is False:
            raise ValueError(
                f"{self.underlying_linear_morphism()} is not a morphism of modules with connection: it "
                f"must commute with the connections of {self.domain()} and {self.codomain()}, and it does not"
            )

    def domain(self):
        return self.parent().domain_object()

    def codomain(self):
        return self.parent().codomain_object()

    def __call__(self, element):
        return self._underlying_morphism(element)

    def _call_(self, element):
        return self.__call__(element)

    def underlying_linear_morphism(self):
        return self._underlying_morphism

    as_morphism = underlying_linear_morphism

    def __mul__(self, other):
        match other:
            case ConnectionMorphism():
                pass
            case _:
                return NotImplemented
        match other.codomain() is self.domain():
            case True:
                pass
            case False:
                return NotImplemented
        underlying = self.underlying_linear_morphism() * other.underlying_linear_morphism()
        return other.domain().Mor(self.codomain())._from_horizontal_morphism(
            underlying, premises=(self, other)
        )

    def _horizontal_on_generators(self):
        domain_connection = self.domain().connection()
        codomain_connection = self.codomain().connection()
        if domain_connection.algebra() is not codomain_connection.algebra():
            raise ValueError(
                f"there are no morphisms of modules with connection {self.domain()} -> {self.codomain()}: "
                f"the connections must be over one algebra, but they are over "
                f"{domain_connection.algebra()} and {codomain_connection.algebra()}"
            )
        omega = domain_connection.one_forms()
        identity_omega = omega.module_category().Mor(omega, omega).identity()

        domain_module = domain_connection.module()
        codomain_module = codomain_connection.module()
        # The structured map read on the modules that carry the connections
        # is linear exactly when the structured map is.
        structured = self.underlying_linear_morphism()
        structured_source = self.domain()
        underlying = Modules(domain_connection.algebra()).Mor(
            domain_module, codomain_module
        )._from_constructed_element_map(
            lambda element: codomain_module(structured(structured_source(element))),
            premises=(structured,),
        )
        induced = underlying.tensor_product_map(
            identity_omega,
            source=domain_connection.target_module(),
            target=codomain_connection.target_module(),
        )

        ring = domain_module.base_ring()
        assert domain_module in ModulesWithChosenFinitePresentation(ring), (
            f"whether {underlying} commutes with the connections is checked here on module generators, "
            f"so {domain_module} must have a chosen finite presentation over {ring}, but it is in "
            f"{domain_module.category()}"
        )
        return conjunction(
            codomain_connection(underlying(generator)) == induced(domain_connection(generator))
            for generator in (
                domain_module.module_generator(label) for label in domain_module.module_generating_set()
            )
        )


class ConnectionMor(RestrictedMorCategoryParent):
    ElementMethods = ConnectionMorphism

    def __init__(self, family, domain, codomain, *, category) -> None:
        # Horizontality of an arbitrary linear map is decided only on module
        # generators under a chosen finite presentation, so an arrow of the
        # underlying linear Mor belongs here when it is the underlying map of
        # a horizontal map constructed here; that image is recorded with its
        # section.
        self._inclusion_preimages = {}
        if domain.base_ring() is not codomain.base_ring():
            raise ValueError(
                f"there are no morphisms of modules with connection {domain} -> {codomain}: both must be "
                f"over one algebra, but they are over {domain.base_ring()} and {codomain.base_ring()}"
            )
        RestrictedMorCategoryParent.__init__(
            self,
            family,
            domain,
            codomain,
            category=category,
        )

    def _element_constructor_(self, images, *, check=False):
        r"""The horizontal map given by its module-map data (``CON-17``).

        An arrow of the underlying linear Mor that this restricted Mor admits
        is the underlying map of a horizontal map, which is returned.
        """
        match element_parent(images):
            case selected if selected is self:
                return images
            case selected if selected is self.arrow_set() and self.accepts(images):
                return self.inclusion_preimage(images)
        morphism = self._recorded(self.element_class(self, images))
        morphism.validate_linearity(check=check)
        morphism.validate_horizontality(check=check)
        return morphism

    def _from_horizontal_morphism(self, underlying, premises=()):
        r"""The arrow on ``underlying``, horizontal when every premise is horizontal."""
        return self._recorded(
            self.element_class(self, underlying, horizontality_premises=premises)
        )

    def _recorded(self, morphism):
        self._inclusion_preimages[id(morphism.underlying_linear_morphism())] = morphism
        return morphism

    def inclusion_image_contains(self, arrow) -> bool:
        r"""Whether ``arrow`` is the underlying linear map of a horizontal map here."""
        return id(arrow) in self._inclusion_preimages

    def inclusion_preimage(self, arrow):
        r"""The horizontal map whose underlying linear map is ``arrow``."""
        assert self.inclusion_image_contains(arrow), (
            f"{arrow} is not the underlying linear map of a horizontal map in {self}"
        )
        return self._inclusion_preimages[id(arrow)]

    def identity(self):
        if self.domain_object() is not self.codomain_object():
            raise ValueError(
                f"{self} has no identity: an identity map needs domain = codomain, but these are "
                f"{self.domain_object()} and {self.codomain_object()}"
            )
        return self._from_horizontal_morphism(self.arrow_set().identity())


class ConnectionMorphismCategoryConstruction(_RestrictedMorCategoryOf):
    _declaration_name = "_ConnectionMorphismCategory"

    def fixed_category_class(self):
        return ConnectionMor

    def accepts(self, arrow) -> bool:
        r"""Whether ``arrow`` is the underlying linear map of a horizontal map.

        Admission reads construction: ``arrow`` lies in the recorded image of
        the forgetful map from the horizontal maps with its endpoints.
        """
        horizontal = self._cached_between(arrow.domain(), arrow.codomain())
        return horizontal is not None and horizontal.inclusion_image_contains(arrow)



def _connection_de_rham_piece(connection, degree):
    degree = int(degree)
    algebra = connection.algebra()
    match degree < 0:
        case True:
            return algebra.base_ring().free_module(0)
        case False:
            pass
    coefficient_module = connection.module()
    forms = connection.one_forms().exterior_power(degree)
    tensor = Modules(coefficient_module.base_ring()).tensor_product(
        (coefficient_module, forms)
    )
    return tensor.restrict_scalars(algebra.algebra_structure_morphism())


def _connection_de_rham_component(connection, degree, component, target):
    degree = int(degree)
    match degree < 0:
        case True:
            return target.zero()
        case False:
            pass
    coefficient_module = connection.module()
    omega = connection.one_forms()
    source_forms = omega.exterior_power(degree)
    target_forms = omega.exterior_power(degree + 1)
    modules = Modules(coefficient_module.base_ring())
    source_tensor = modules.tensor_product((coefficient_module, source_forms))
    target_tensor = modules.tensor_product((coefficient_module, target_forms))
    result = target_tensor.zero()
    underlying = component.underlying_element()
    coordinates = source_tensor.framing_morphism().lift(underlying)
    for source_label in coordinates.support().domain():
        module_label, form_label = source_label
        coefficient = coordinates(source_label)
        coefficient_vector = coefficient_module.scalar_multiple(
            coefficient,
            coefficient_module.module_generator(module_label),
        )
        connection_value = connection(coefficient_vector)
        basis_form = source_forms.module_generator(form_label)
        connection_coordinates = connection.target_module().framing_morphism().lift(connection_value)
        for connection_label in connection_coordinates.support().domain():
            output_module_label, one_form_label = connection_label
            connection_coefficient = connection_coordinates(connection_label)
            wedge = omega.exterior_power_product(
                1,
                omega.module_generator(one_form_label),
                degree,
                basis_form,
            )
            match wedge == target_forms.zero():
                case True:
                    pass
                case _:
                    result += target_tensor.scalar_multiple(
                        connection_coefficient,
                        target_tensor.pure_tensor(
                            coefficient_module.module_generator(output_module_label),
                            wedge,
                        ),
                    )
    return target(result)


def _connection_de_rham_right_action(module, module_element, algebra_element):
    module_element = module(module_element)
    dga = module.dga()
    algebra_element = dga(algebra_element)
    exterior_element = dga.realize(algebra_element)
    exterior_algebra = dga.extension_algebra()
    coefficient_module = module.coefficient_module()
    omega = module.connection().one_forms()
    result = module.zero()
    for left_degree, left_component in module_element.homogeneous_components().items():
        left_forms = omega.exterior_power(left_degree)
        modules = Modules(coefficient_module.base_ring())
        left_tensor = modules.tensor_product((coefficient_module, left_forms))
        left_underlying = left_component.underlying_element()
        for right_degree, right_component in exterior_element.homogeneous_components().items():
            target_degree = left_degree + right_degree
            target_forms = omega.exterior_power(target_degree)
            target_tensor = modules.tensor_product((coefficient_module, target_forms))
            target_value = target_tensor.zero()
            left_coordinates = left_tensor.framing_morphism().lift(left_underlying)
            right_piece = exterior_algebra.graded_piece(right_degree)
            right_coordinates = right_piece.framing_morphism().lift(right_component)
            for left_label in left_coordinates.support().domain():
                module_label, left_form_label = left_label
                left_coefficient = left_coordinates(left_label)
                left_form = left_forms.module_generator(left_form_label)
                for right_form_label in right_coordinates.support().domain():
                    right_coefficient = right_coordinates(right_form_label)
                    right_form = exterior_algebra.graded_piece(right_degree).module_generator(
                        right_form_label
                    )
                    wedge = omega.exterior_power_product(
                        left_degree,
                        left_form,
                        right_degree,
                        right_form,
                    )
                    match wedge == target_forms.zero():
                        case True:
                            pass
                        case _:
                            target_value += target_tensor.scalar_multiple(
                                left_coefficient * right_coefficient,
                                target_tensor.pure_tensor(
                                    coefficient_module.module_generator(module_label),
                                    wedge,
                                ),
                            )
            match target_value == target_tensor.zero():
                case True:
                    pass
                case _:
                    result += module.from_component(
                        target_degree,
                        module.graded_piece(target_degree)(target_value),
                    )
    return result


class _ConnectionDeRhamDirectSum(_CochainComplexDirectSum):
    r"""The cochain direct sum underlying one flat connection's de Rham DG-module."""

    def __init__(self, connection, **rest) -> None:
        self._connection = connection
        super().__init__(**rest)

    def connection(self):
        return self._connection

    def coefficient_module(self):
        return self.connection().module()

    def from_coefficient(self, element):
        omega = self.connection().one_forms()
        forms_zero = omega.exterior_power(0)
        tensor_zero = Modules(self.coefficient_module().base_ring()).tensor_product(
            (self.coefficient_module(), forms_zero)
        )
        unit = forms_zero.module_generator(0)
        return self.from_component(
            0,
            self.graded_piece(0)(tensor_zero.pure_tensor(element, unit)),
        )


class ConnectionDeRhamModule:
    r"""Factory namespace for a flat connection's de Rham DG-module."""

    def __new__(cls, connection):
        match connection.is_flat():
            case True:
                pass
            case _:
                raise ValueError(
                    f"{connection} has no de Rham complex: the de Rham differential squares to zero only "
                    f"for a flat connection, and {connection} is not known to be flat"
                )
        coefficient_module = connection.module()
        algebra = connection.algebra()
        dga = algebra.de_rham_algebra()
        integers = _owned_integers()
        match dga.grading_monoid() is integers:
            case True:
                pass
            case False:
                raise ValueError(
                    f"the de Rham complex of {connection} needs the de Rham algebra {dga} to be graded by "
                    f"the integers, but it is graded by {dga.grading_monoid()}"
                )

        pieces = indexed_family(
            integers,
            lambda degree: _connection_de_rham_piece(connection, degree),
            name="Connection de Rham pieces",
        )

        def differential(degree):
            degree = int(degree)
            source = pieces(degree)
            target = pieces(degree + 1)
            return DifferentialComponentMorphism(
                source,
                target,
                lambda component: _connection_de_rham_component(
                    connection,
                    degree,
                    component,
                    target,
                ),
            )

        differentials = indexed_family(
            integers,
            differential,
            name="Connection de Rham differentials",
        )

        def right_action(module_element, algebra_element):
            return _connection_de_rham_right_action(
                module_element.parent(),
                module_element,
                algebra_element,
            )

        return CochainComplexes(algebra.base_ring()).from_family(
            pieces,
            differentials,
            name=f"de Rham DG-module of {coefficient_module}",
            extra_categories=(DifferentialGradedModules(dga),),
            extra_construction_data={
                "connection": connection,
                "graded_algebra": dga,
                "graded_algebra_action": right_action,
                "dg_algebra": dga,
                "dg_module_leibniz_decision": True,
            },
            _realization=(_ConnectionDeRhamDirectSum, GradedDirectSumElement),
        )


__all__ = [
    "Connection",
    "ConnectionDeRhamModule",
    "ConnectionMor",
    "ConnectionMorphism",
    "ConnectionSpace",
    "ModulesWithConnection",
    "ModulesWithFlatConnection",
    "VectorBundlesWithConnection",
]
