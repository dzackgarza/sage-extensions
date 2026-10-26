r"""Owned categories for absolute Galois groups."""

from sage.categories.finite_fields import FiniteFields
from sage.categories.number_fields import NumberFields
from sage.misc.cachefunc import cached_method
from sage.misc.unknown import Unknown
from sage.rings.rational_field import QQ as SageQQ

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.objects import (
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.group.groups import (
    OwnedAbelianGroups,
    OwnedInfiniteGroups,
    Subgroups,
)
from sage_extensions.categories.group.profinite.profinite_groups import (
    ProfiniteGroups,
)
from sage_extensions.categories.rings.ring_foundation import (
    _engine_ring,
    _own_ring,
)
from sage_extensions.categories.sets.cardinals import continuum
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.logic import ask


def _finite_field_absolute_galois_group():
    r"""Return the selected finite-field specimen used by these categories."""
    from sage_extensions.categories.group.profinite.absolute_galois_group import (
        AbsoluteGaloisGroup,
    )
    from sage_extensions.categories.rings.ring_foundation import GF

    return AbsoluteGaloisGroup(GF(2))


class AbsoluteGaloisGroups(OwnedCategory):
    r"""Groups (G_K=\operatorname{Aut}_K(\bar K)) with a chosen base point."""

    def an_object(self):
        r"""The absolute Galois group of ``GF(2)`` with its canonical realization."""
        return _finite_field_absolute_galois_group()

    @classmethod
    def _repr_object_names(cls) -> str:
        return "absolute Galois groups"

    def super_categories(self):
        return [ProfiniteGroups()]

    class ParentMethods:
        def characteristic(self):
            return self.base_field().characteristic()

        def _conjugate_subgroup_construction(self, group_element, subgroup):
            r"""Supply ``g H g^-1`` from the retained stage of an open ``H = G_E``.

            ``G_E`` fixes the image of the chosen embedding
            ``iota : E -> Kbar``, so ``g G_E g^-1`` fixes the image of
            ``g o iota``.  It is the open subgroup of the same ``K``-extension
            ``E`` with that embedding into ``Kbar``. The admitted automorphism
            square composes with the old finite-stage square; its exact
            source object retains ``K -> E`` and its separability. No
            embedding enumeration or new separability decision is needed.
            """
            match subgroup:
                case _ if subgroup in OpenAbsoluteGaloisSubgroups(self):
                    from sage_extensions.categories.group.profinite.galois_quotient import (
                        _FiniteGaloisExtensionEngine,
                    )

                    old_stage = subgroup.fixed_extension()
                    extension = self.extension_object()
                    identity = self.base_field().Mor(self.base_field()).identity()
                    automorphism = self.slice_category().Mor(
                        extension, extension
                    )._from_commuting_edges(identity, group_element.as_morphism())
                    stage = self.stage_category().object(
                        automorphism * old_stage.arrow(),
                        _engine=_FiniteGaloisExtensionEngine,
                    )
                    return self.open_subgroup(stage)
                case _:
                    return None

        def _subgroup_conjugacy_decision(self, left, right):
            r"""Two open subgroups ``G_E`` and ``G_F`` are conjugate exactly when ``E`` and ``F`` are ``K``-isomorphic.

            By Galois theory ``g G_E g^-1 = G_{g(E)}``, and every
            ``K``-embedding ``E -> Kbar`` is ``g o iota`` for some ``g`` in
            ``G_K``.  Other subgroups are undecided.
            """
            from sage_extensions.categories.group.profinite.absolute_galois_group import (
                _same_k_extension,
            )

            open_subgroups = OpenAbsoluteGaloisSubgroups(self)
            match (left, right):
                case _ if left in open_subgroups and right in open_subgroups:
                    return ask(
                        _same_k_extension(
                            self,
                            left.fixed_field(),
                            left.fixed_extension().base_embedding(),
                            right.fixed_field(),
                            right.fixed_extension().base_embedding(),
                        )
                    )
                case _:
                    return Unknown

        def _normalizer_construction(self, subgroup):
            r"""``N_{G_K}(G_E)``; it is ``G_K`` itself when ``E/K`` is Galois.

            ``G_E`` is normal in ``G_K`` exactly when ``E/K`` is Galois, and
            then its normalizer is the open subgroup ``G_K`` of index ``1``.
            Otherwise the normalizer is the stabilizer of ``G_E`` under
            conjugation, cut out by its defining condition.
            """
            match subgroup:
                case _ if subgroup in OpenAbsoluteGaloisSubgroups(self) and subgroup.is_normal() is True:
                    return self.open_subgroup(self.base_field())
                case _:
                    return None

        def _cardinality_decision(self):
            r"""``|G_K| = 2^{aleph_0}`` for a finite field or a number field ``K``.

            ``K`` is countable, so ``\bar K`` has countably many finite
            subextensions and ``G_K`` is a second-countable profinite group.
            An infinite second-countable profinite group has cardinality
            ``2^{aleph_0}``.  ``G_K`` is infinite: over ``F_q`` it is
            ``\widehat{ZZ}``, and over a number field the cyclotomic
            character has infinite image.
            """
            computation_field = _engine_ring(self.base_field())
            match computation_field:
                case _ if (
                    computation_field is SageQQ
                    or computation_field in FiniteFields()
                    or computation_field in NumberFields()
                ):
                    return continuum
                case _:
                    assert False, (
                        f"cannot compute the cardinality of {self}: it is computed for the "
                        f"absolute Galois group of a finite field or a number field, but the "
                        f"base field is {self.base_field()}"
                    )

        def _finite_quotient_witnesses(self):
            r"""Yield restrictions ``G_K -> Gal(L/K)`` to cubic splitting fields over ``K``.

            Implements the protected contract of
            ``ProfiniteGroups.ParentMethods._finite_quotient_witnesses``.  For
            a number field ``K``, the splitting field ``L`` over ``K`` of a
            cubic with coefficients in ``K`` is a finite Galois extension of
            ``K``, so restriction ``G_K -> Gal(L/K)`` is a continuous
            surjection onto a finite group.  The cubics are ``x^3 - 2`` and
            ``x^3 - x - 1``, taken over ``K`` itself.  ``Gal(L/K)`` is ``S_3``
            when the cubic is irreducible over ``K`` and its discriminant is
            not a square in ``K``.  Over ``QQ`` the first cubic gives
            ``Gal(QQ(2^{1/3}, zeta_3)/QQ) = S_3``.  The Kummer cubic
            ``x^3 - 2`` has an abelian group over a field containing
            ``zeta_3``; the second cubic is not of Kummer form.  Other base
            fields select no quotient here.
            """
            computation_field = _engine_ring(self.base_field())
            match computation_field:
                case _ if computation_field is SageQQ or (
                    computation_field in NumberFields()
                    and computation_field.is_absolute()
                ):
                    x = computation_field["x"].gen()
                    yield self._cubic_splitting_field_restriction(x**3 - 2)
                    yield self._cubic_splitting_field_restriction(x**3 - x - 1)
                case _:
                    return

        @cached_method
        def _cubic_splitting_field_restriction(self, polynomial):
            r"""Return the restriction ``G_K -> Gal(L/K)`` to the splitting field ``L`` of ``polynomial``.

            ``polynomial`` has coefficients in the computation field of ``K``.
            The stage ``K -> L`` is the base map the splitting-field
            construction returns.
            """
            from sage_extensions.categories.rings.number_fields import (
                _engine_number_field_isomorphism,
            )

            splitting_engine, base_backend = polynomial.splitting_field(
                "s", map=True
            )
            splitting_field = _own_ring(splitting_engine)
            # K -> L on L's own realization (generator to generator).
            base_backend = (
                _engine_number_field_isomorphism(splitting_engine, _engine_ring(splitting_field))
                * base_backend
            )
            base_embedding = self.base_field().Mor(splitting_field)(base_backend)
            stage = self.extension_data(
                splitting_field, base_embedding=base_embedding
            )
            return self.restriction_map(stage)


class AbsoluteGaloisGroupsOfFiniteFields(OwnedCategory):
    r"""The procyclic absolute Galois groups of finite fields."""

    def an_object(self):
        r"""The procyclic absolute Galois group of ``GF(2)``."""
        return _finite_field_absolute_galois_group()

    @classmethod
    def _repr_object_names(cls) -> str:
        return "absolute Galois groups of finite fields"

    def super_categories(self):
        return [
            AbsoluteGaloisGroups(),
            OwnedAbelianGroups(),
            OwnedInfiniteGroups(),
        ]

    class ParentMethods:
        def _topological_generating_family(self):
            r"""Supply the distinguished dense generator ``x |-> x^q`` of ``G_Fq``.

            This supplies ``TopologicalGroups``' selected-family contract.
            Here ``q`` is the order of the exact base field, including a
            nonprime finite field. Frobenius generates a dense infinite
            cyclic subgroup, not the whole abstract group.
            """
            return finite_ordered_set((self.frobenius(),))


class OpenAbsoluteGaloisSubgroups(OwnedParameterizedCategory):
    r"""Open subgroups (G_E\subseteq G_K) carrying the embedding (E\to\bar K)."""

    @staticmethod
    def __classcall__(cls, supergroup):
        if supergroup not in AbsoluteGaloisGroups():
            raise TypeError(
                f"cannot form open subgroups of {supergroup}: open subgroups G_E of G_K "
                f"are taken inside an absolute Galois group G_K, but {supergroup} is not one"
            )
        return OwnedParameterizedCategory.__classcall__(cls, supergroup)

    def parameter_category(self):
        return AbsoluteGaloisGroups()

    def supergroup(self):
        return self.base()

    def an_object(self):
        r"""The whole ambient group, viewed as its index-one open subgroup."""
        group = self.supergroup()
        return self(group.extension_data(group.base_field()))

    @classmethod
    def _repr_object_names(cls) -> str:
        return "open subgroups of absolute Galois groups"

    def super_categories(self):
        return [AbsoluteGaloisGroups(), Subgroups(self.supergroup())]

    def _call_(self, extension):
        from sage_extensions.categories.group.profinite.absolute_galois_group import (
            _OpenAbsoluteGaloisSubgroupEngine,
            _realized_absolute_galois_group,
        )

        group = self.supergroup()
        extension = group.extension_data(extension)
        category = Cat().meet(
            (self, _absolute_galois_group_category(extension.field()))
        )
        return _realized_absolute_galois_group(
            extension.field(),
            closure=group.algebraic_closure(),
            embedding=extension.embedding(),
            category=category,
            engine=_OpenAbsoluteGaloisSubgroupEngine,
            supergroup=group,
            fixed_extension=extension,
        )

    class ParentMethods:
        def ambient(self):
            r"""Return the ambient absolute Galois group ``G_K``."""
            return self.supergroup()

        def fixed_field(self):
            return self._fixed_extension.field()

        def fixed_extension(self):
            return self._fixed_extension

        def embedding(self):
            return self._fixed_extension.embedding()

        def index(self):
            return self._fixed_extension.degree()

        @cached_method
        def inclusion(self):
            from sage_extensions.categories.group.profinite.absolute_galois_group import (
                _open_subgroup_inclusion_rule,
            )

            return self.Mor(self.supergroup())._from_realization_rule(
                _open_subgroup_inclusion_rule
            )


def _absolute_galois_group_category(field):
    return (
        AbsoluteGaloisGroupsOfFiniteFields()
        if _engine_ring(field) in FiniteFields()
        else AbsoluteGaloisGroups()
    )


__all__ = [
    "AbsoluteGaloisGroups",
    "AbsoluteGaloisGroupsOfFiniteFields",
    "OpenAbsoluteGaloisSubgroups",
]
