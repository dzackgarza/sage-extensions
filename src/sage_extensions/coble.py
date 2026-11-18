r"""Coble lattice cusp candidates, its kernel's generator certificate, and a rank-ten Coxeter configuration."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values
from sage_extensions.catalogue import Embeddings, NamedLattices
from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams

_KERNEL_GENERATOR_CERTIFICATE = "certificates/coble_kernel_fifty_six_congruence_generators.json"
_KERNEL_GENERATOR_CERTIFICATE_SHA256 = (
    "9708165fc7b7e0d5fa27c613260030935bd63146e5e1257d2dca78063886ace1"
)


@cached_function
def _kernel_generator_matrices():
    r"""The retained integral matrices of the Coble kernel's generator certificate, one tuple of rows each.

    The file is a package certificate: the digest above is checked before the
    matrices are read, so a changed or truncated file is refused rather than
    partially read.  Each entry's ``matrix_standard`` is the matrix of the
    isometry in the standard basis of
    \(T_{\mathrm{Co}} = \langle 2\rangle \oplus U(2) \oplus E_8(-2)\), whose
    columns are the images of the module generators.
    """
    from hashlib import sha256
    from importlib.resources import files
    from json import loads

    retained = files("sage_extensions").joinpath(_KERNEL_GENERATOR_CERTIFICATE).read_bytes()
    assert sha256(retained).hexdigest() == _KERNEL_GENERATOR_CERTIFICATE_SHA256, (
        f"the Coble kernel generator certificate {_KERNEL_GENERATOR_CERTIFICATE} does not "
        f"have the digest it is retained with"
    )
    certificate = loads(retained)
    assert certificate["generator_count"] == 56, (
        f"the Coble kernel generator certificate states {certificate['generator_count']} "
        f"generators, not the 56 its theorem states"
    )
    return tuple(
        tuple(tuple(int(entry) for entry in row) for row in item["matrix_standard"])
        for item in certificate["generators"]
    )


def _preserves_the_gram(gram, matrix) -> bool:
    r"""Whether the integral matrix ``matrix`` satisfies \(M^{\mathsf T} G M = G\) for ``gram`` \(= G\)."""
    order = len(gram)
    return all(
        sum(
            matrix[middle][left] * gram[middle][other] * matrix[other][right]
            for middle in range(order)
            for other in range(order)
        )
        == gram[left][right]
        for left in range(order)
        for right in range(order)
    )


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
        # The rank-ten configuration is fixed in the Nikulin (10,10,1) model
        # U(2) + A1^8.  Construct that model directly.
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
    def kernel_generators(lattice):
        r"""Return the certified ordinary integral generators of the discriminant kernel of ``lattice``.

        ``lattice`` is \(T_{\mathrm{Co}} = \langle 2\rangle \oplus U(2) \oplus
        E_8(-2)\) presented in the standard basis, which the caller establishes
        by comparing its Gram matrix (:meth:`Lattices._presents_the_coble_form`).
        The returned isometries generate
        \(\widetilde O(T_{\mathrm{Co}}) = \ker(O(T_{\mathrm{Co}}) \to
        O(A_{T_{\mathrm{Co}}}))\) as an ordinary group --- the completeness
        statement of ``thm:coble-fifty-six-ordinary-full-kernel-generation`` in
        `dzackgarza/research` --- and this call certifies of each one what a
        single element decides: that it preserves the Gram matrix of ``lattice``
        (an integral isometry), and that it is the identity modulo two, which is
        trivial action on the discriminant group here because
        \(T_{\mathrm{Co}} = 2L^{\#}\) identifies \(A_L\) with \(L/2L\).
        """
        ring = lattice.base_ring()
        labels = tuple(lattice.module_generating_set())
        gram = tuple(
            tuple(
                int(lattice.b(lattice.module_generator(left), lattice.module_generator(right)))
                for right in labels
            )
            for left in labels
        )
        order = len(gram)
        isometries = lattice.O()
        family = []
        for matrix in _kernel_generator_matrices():
            assert _preserves_the_gram(gram, matrix), (
                f"the retained kernel generator {matrix} does not satisfy M^T G M = G for "
                f"the Gram matrix of {lattice}: it is not an isometry of this lattice"
            )
            assert all(int(matrix[left][right]) % 2 == int(left == right)
                       for left in range(order) for right in range(order)), (
                f"the retained kernel generator {matrix} is not the identity modulo two, so "
                f"it does not act trivially on the discriminant group of {lattice}"
            )
            family.append(
                isometries({
                    label: lattice.linear_combination({
                        labels[right]: ring(int(matrix[right][left])) for right in range(order)
                    })
                    for left, label in enumerate(labels)
                })
            )
        return tuple(family)

    @staticmethod
    def rank_ten_diagram():
        _lattice, roots = Coble.rank_ten_coxeter_roots()
        return CoxeterDiagrams().from_roots(
            finite_indexed_family_from_values(None, roots),
            names=finite_ordered_set(tuple(f"r{i + 1}" for i, _root in enumerate(roots))),
        )


__all__ = ["Coble"]
