r"""Affine semigroup algebras from finite lattice-generator presentations."""

from sage.matrix.constructor import column_matrix as _engine_column_matrix
from sage.rings.integer_ring import ZZ as SageZZ
from sage.schemes.toric.ideal import ToricIdeal as _SageToricIdeal

from sage_extensions.categories.algebras.algebras import (
    AlgebrasWithChosenFinitePresentation,
    Algebras,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _engine_ring,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.sets.set_categories import Sets


class _AffineSemigroupPresentation:
    r"""The selected lattice-generator presentation defining an affine semigroup algebra."""

    def __init__(self, generator_coordinates) -> None:
        self._generator_coordinates = generator_coordinates

    def _raw_generator_coordinates(self):
        return self._generator_coordinates


class AffineSemigroupAlgebras(OwnedCategoryOverBaseRing):
    r"""Affine semigroup algebras with one selected finite lattice presentation."""

    def an_object(self):
        r"""The polynomial algebra ``R[t] = R[NN]``."""
        return self(((1,),), names=("t",))

    def super_categories(self):
        return [AlgebrasWithChosenFinitePresentation(self.base_ring()).Commutative()]

    def _repr_object_names(self):
        return f"affine semigroup algebras over {self.base_ring()}"

    class ParentMethods:
        def __init__(self, _affine_semigroup_presentation, **rest):
            self._affine_semigroup_presentation = _affine_semigroup_presentation
            super().__init__(**rest)

        def _cardinality_decision(self):
            r"""Return the cardinality of ``R[S]`` from its affine semigroup.

            A finitely generated submonoid of a lattice is trivial exactly when
            all selected generators are zero; otherwise it is countably
            infinite, since a nonzero generator has pairwise distinct positive
            multiples.  The semigroup algebra is the finite-support free
            ``R``-module on ``S``.
            """
            from sage_extensions.categories.sets.cardinals import (
                Cardinalities,
                aleph0,
            )

            coordinates = self.affine_semigroup_generator_coordinates()
            trivial = all(
                all(entry == self.base_ring().zero() for entry in coordinates[label])
                for label in coordinates.index_set()
            )
            scalars = self.base_ring().cardinality()
            match trivial, scalars == Cardinalities().one():
                case True, _:
                    return scalars
                case False, True:
                    return Cardinalities().one()
                case False, False:
                    return Cardinalities().supremum(scalars, aleph0)

        def affine_semigroup_generator_coordinates(self):
            r"""Return the selected lattice-generator coordinates as an owned family."""
            raw = self._affine_semigroup_presentation._raw_generator_coordinates()
            labels = self.algebra_generating_set()
            coordinate_indices = Sets.Δ[len(raw[0]) - 1]
            integers = _owned_integers()
            return finite_indexed_family(
                labels,
                lambda label: finite_indexed_family(
                    coordinate_indices,
                    lambda coordinate: integers(
                        raw[int(labels.ranking_map()(label))][int(coordinate)]
                    ),
                    name=f"Coordinates of affine semigroup generator {label}",
                ),
                name="Affine semigroup generator coordinates",
            )

    def _call_(
        self,
        generator_coordinates,
        *,
        names=None,
        extra_categories=(),
        extra_construction_data=(),
    ):
        coordinates = tuple(
            tuple(int(entry) for entry in row)
            for row in generator_coordinates
        )
        if not coordinates:
            raise ValueError("an affine semigroup needs at least one generator, but none was given")
        ambient_rank = len(coordinates[0])
        if any(len(row) != ambient_rank for row in coordinates):
            raise ValueError(
                f"the generators of an affine semigroup must lie in one lattice Z^{ambient_rank}, but their "
                f"lengths are {tuple(len(row) for row in coordinates)}"
            )
        if names is None:
            names = tuple(f"s{position}" for position in range(len(coordinates)))
        else:
            names = tuple(names)
        if len(names) != len(coordinates):
            raise ValueError(
                f"an affine semigroup with {len(coordinates)} generators needs {len(coordinates)} variable "
                f"names, but got {len(names)}"
            )

        base = self.base_ring()
        presentation = base.polynomial_ring(names)
        # ToricIdeal reads the semigroup generators from the columns of its matrix.
        columns = _engine_column_matrix(SageZZ, coordinates)
        construction_data = (
            ("_affine_semigroup_presentation", _AffineSemigroupPresentation(coordinates)),
            *tuple(extra_construction_data),
        )
        # If the lattice generators are linearly independent over Q, the map
        # N^r -> Z^n they define is injective. Thus distinct monomials have
        # distinct semigroup degrees and the toric ideal is zero. Avoid asking
        # ToricIdeal to rediscover this exact rank fact, and retain the selected
        # polynomial algebra directly.
        if columns.rank() == len(coordinates):
            # The degree map is injective, so its toric ideal is zero. It is
            # mathematically the polynomial algebra itself, not a quotient by
            # the zero ideal: wrapping it in the presented-algebra constructor
            # makes its selected resolution ask the presentation algebra for
            # its own presentation, recursively, when its representation is
            # requested (e.g. while hashing a chart in the gluing cache).
            from sage_extensions.categories.algebras.algebras import (
                _algebra_with_structure,
            )
            from sage_extensions.categories.algebras.free_algebras import (
                FreeAlgebras,
                GradedFreeAlgebras,
                SymmetricAlgebras,
            )

            return _algebra_with_structure(
                presentation,
                base,
                names,
                FreeAlgebras(base),
                GradedFreeAlgebras(base),
                SymmetricAlgebras(base),
                self,
                *tuple(extra_categories),
                construction_data=construction_data,
            )
        else:
            engine_presentation = _engine_ring(presentation)
            engine_ideal = _SageToricIdeal(
                columns,
                names=names,
                base_ring=_engine_ring(base),
            )
            relations = tuple(
                _owned_engine_element(presentation, engine_presentation(relation))
                for relation in engine_ideal.gens()
            )
        return (presentation).quotient_by_relations(relations,
            _extra_categories=(self, *tuple(extra_categories)),
            _extra_construction_data=construction_data,
        )


__all__ = ["AffineSemigroupAlgebras"]
