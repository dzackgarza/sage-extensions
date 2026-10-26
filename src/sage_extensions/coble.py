r"""Coble lattice cusp candidates and a rank-ten Coxeter configuration."""

from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values
from sage_extensions.catalogue import Embeddings, NamedLattices
from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams


def _named_generators(lattice):
    return {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}


class Coble:
    @staticmethod
    def isotropic_vectors():
        Tco = NamedLattices.Tco
        b = _named_generators(Tco)
        h, ep, fp = b["h"], b["ep"], b["fp"]
        a = {i: b[f"a{i}"] for i in range(1, 9)}
        vectors = {
            "w1": ep,
            "w2": fp,
            "w3": 2 * h + a[1] + a[2],
            "w4": ep + fp + a[1],
            "w5": 2 * h - fp - a[1] - a[6] - a[7] - a[8],
            "w6": 8 * ep + fp + a[4] - 2 * a[5] - a[8],
            "w7": 2 * h + ep - a[1] - a[2],
            "w8": 2 * h + ep - a[2] - a[3],
            "w9": 2 * h - a[1] + a[2] - a[3],
            "w10": 2 * ep + fp - a[1] - a[8],
            "w11": 5 * ep + fp + a[2] + 2 * a[3],
            "w12": 2 * h + a[1] - a[4],
            "w13": 2 * h + a[2] - a[5],
            "w14": 2 * h + a[3] - a[6],
            "w15": 2 * h + a[4] - a[7],
            "w16": 2 * h + a[5] - a[8],
            "w17": 2 * h - a[6] - a[8],
        }
        assert len(vectors) == 17
        assert all(vector.q() == 0 for vector in vectors.values())
        return vectors

    @staticmethod
    def isotropic_vectors_in_TEn():
        return {name: Embeddings.TCo_into_TEn(vector) for name, vector in Coble.isotropic_vectors().items()}

    @staticmethod
    def isotropic_vectors_in_TdP():
        return {name: Embeddings.TEn_into_TdP(vector) for name, vector in Coble.isotropic_vectors_in_TEn().items()}

    @staticmethod
    def rank_ten_coxeter_roots():
        # The archived migration fixed the rank-ten configuration in the
        # Nikulin (10,10,1) model U(2) + A1^8.  Construct that model directly.
        lattice = NamedLattices.U_2
        for _ in range(8):
            lattice = lattice + NamedLattices.Z.twist(-2)
        generators = tuple(lattice.module_generators())
        rows = (
            (0, 0, 1, 0, 0, 0, 0, 0, -1, 0),
            (0, 0, 0, -1, 0, 0, 0, 0, 0, -1),
            (2, 1, 1, -1, 0, 0, -1, -1, 1, 1),
            (0, 0, -1, 0, 0, 0, 0, -1, 0, 0),
            (0, 0, 0, 0, 0, 1, 0, 0, 0, 0),
            (0, 0, 0, 0, -1, 0, 0, 1, 0, 0),
            (0, 0, 0, 1, 0, 0, 0, 0, 1, 0),
            (-2, -1, -1, 1, 1, 0, 0, 1, -1, -1),
            (-2, -1, -1, 0, 1, -1, 1, 1, -1, 0),
            (-1, 0, 0, 0, 0, 0, 1, 0, 0, 0),
            (-2, -2, -1, 1, 1, 0, 2, 1, -1, -1),
        )
        roots = tuple(sum((coefficient * generator for coefficient, generator in zip(row, generators, strict=True)), lattice.zero()) for row in rows)
        assert all(root.q() in (-2, -4) for root in roots)
        return lattice, roots

    @staticmethod
    def rank_ten_diagram():
        _lattice, roots = Coble.rank_ten_coxeter_roots()
        return CoxeterDiagrams().from_roots(
            finite_indexed_family_from_values(None, roots),
            names=finite_ordered_set(tuple(f"r{i + 1}" for i, _root in enumerate(roots))),
        )


__all__ = ["Coble"]
