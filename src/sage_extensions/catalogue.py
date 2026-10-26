r"""Named integral lattices and primitive embeddings used by the research layer."""

from collections.abc import Mapping
from functools import cache

from sage.misc.lazy_attribute import lazy_class_attribute

from sage_extensions.categories.lattices import (
    EvenTwoElementaryLattices,
    Lattices,
    _register_indecomposable_gram_rows,
    nikulin_invariants,
    signature_pair,
)
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_engine_element,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.tensors.tensor import tensor

ZZ = _owned_integers()


def _block_gram(*grams):
    r"""Return the orthogonal direct sum of finite Gram tensors."""
    ranks = tuple(int(gram.tensor_shape()[0]) for gram in grams)
    total = sum(ranks)
    values = [[ZZ.zero() for _ in range(total)] for _ in range(total)]
    offset = 0
    for gram, rank in zip(grams, ranks, strict=True):
        shape = gram.tensor_shape()
        if gram.tensor_valence() != (NN**2)((0, 2)) or shape[0] != rank or shape[1] != rank:
            raise TypeError(
                f"{gram} cannot be a block of an orthogonal direct sum: a Gram block must be "
                f"a square tensor of type (0, 2), but it has type {gram.tensor_valence()} "
                f"and shape {shape}"
            )
        for i in range(rank):
            for j in range(rank):
                values[offset + i][offset + j] = ZZ(gram[i, j])
        offset += rank
    return tensor(ZZ, (), (total, total), values)


def _named_lattice(gram, names):
    return Lattices(ZZ)(gram, names=names)


_C = Lattices(ZZ)
_rank_one_2 = tensor(ZZ, (), (1, 1), [[2]])
_rank_one_m2 = tensor(ZZ, (), (1, 1), [[-2]])
_rank_one_m4 = tensor(ZZ, (), (1, 1), [[-4]])


def _Ug():
    return NamedLattices.U.gram_tensor()


def _E8g():
    return NamedLattices.E8.gram_tensor()


class NamedLattices:
    r"""The named lattices, each constructed when its name is first read.

    Every entry is a Sage ``lazy_class_attribute``: the definition stands in
    this class body, and the lattice is built once, on first access, rather
    than when the session imports the catalogue.  An alias returns the very
    object it names.
    """

    @lazy_class_attribute
    def Zero(cls):
        return _C(0)

    @lazy_class_attribute
    def Z(cls):
        return _C(1)

    @lazy_class_attribute
    def Z_2(cls):
        return cls.Z.twist(2)

    @lazy_class_attribute
    def Z_m2(cls):
        return cls.Z.twist(-2)

    @lazy_class_attribute
    def U(cls):
        return _C("U")

    @lazy_class_attribute
    def H(cls):
        return cls.U

    @lazy_class_attribute
    def U_2(cls):
        return cls.U.twist(2)

    @lazy_class_attribute
    def H_2(cls):
        return cls.U_2

    @lazy_class_attribute
    def A1(cls):
        return _C("A1")

    @lazy_class_attribute
    def A2(cls):
        return _C("A2")

    @lazy_class_attribute
    def D4(cls):
        return _C("D4")

    @lazy_class_attribute
    def D6(cls):
        return _C("D6")

    @lazy_class_attribute
    def D8(cls):
        return _C("D8")

    @lazy_class_attribute
    def E7(cls):
        return _C("E7")

    @lazy_class_attribute
    def E8(cls):
        return _C("E8")

    @lazy_class_attribute
    def E8_2(cls):
        return cls.E8.twist(2)

    @lazy_class_attribute
    def E10(cls):
        return cls.U + cls.E8

    @lazy_class_attribute
    def E10_2(cls):
        return cls.U_2 + cls.E8_2

    @lazy_class_attribute
    def Sdp(cls):
        return cls.U_2

    @lazy_class_attribute
    def SEn(cls):
        return cls.E10_2

    @lazy_class_attribute
    def Tco(cls):
        return _C(
            _block_gram(_rank_one_2, 2 * _Ug(), 2 * _E8g()),
            names="h,ep,fp,a1,a2,a3,a4,a5,a6,a7,a8",
        )

    @lazy_class_attribute
    def Sco(cls):
        return _C(_block_gram(_rank_one_m2, 2 * _Ug(), 2 * _E8g()))

    @lazy_class_attribute
    def TEn(cls):
        return _C(
            _block_gram(_Ug(), 2 * _Ug(), 2 * _E8g()),
            names="e,f,ep,fp,a1,a2,a3,a4,a5,a6,a7,a8",
        )

    @lazy_class_attribute
    def TdP(cls):
        return _C(
            _block_gram(_Ug(), 2 * _Ug(), _E8g(), _E8g()),
            names=("e,f,ep,fp,a1,a2,a3,a4,a5,a6,a7,a8,b1,b2,b3,b4,b5,b6,b7,b8"),
        )

    @lazy_class_attribute
    def L_20_2_0(cls):
        return cls.TdP

    @lazy_class_attribute
    def LK3(cls):
        return _C(
            _block_gram(_Ug(), _Ug(), _Ug(), _E8g(), _E8g()),
            names=("e1,f1,e2,f2,e3,f3,a1,a2,a3,a4,a5,a6,a7,a8,b1,b2,b3,b4,b5,b6,b7,b8"),
        )

    @lazy_class_attribute
    def LK3_2(cls):
        return _C(_block_gram(_rank_one_m2, _Ug(), _Ug(), _E8g(), _E8g()))

    @lazy_class_attribute
    def LK3_4(cls):
        return _C(_block_gram(_rank_one_m4, _Ug(), _Ug(), _E8g(), _E8g()))

    @lazy_class_attribute
    def LpNik(cls):
        return _C(_block_gram(_Ug(), _Ug(), _Ug(), 2 * _E8g()))

    @lazy_class_attribute
    def LmNik(cls):
        return cls.E8_2

    @lazy_class_attribute
    def Mukai(cls):
        return _C(_block_gram(_Ug(), _Ug(), _Ug(), _Ug(), _E8g(), _E8g()))

    @lazy_class_attribute
    def MukaiExtended(cls):
        return _C(_block_gram(_Ug(), _Ug(), _Ug(), _Ug(), _Ug(), _E8g(), _E8g()))

    @lazy_class_attribute
    def MukaiAbelian(cls):
        return _C(_block_gram(_Ug(), _Ug(), _Ug(), _Ug()))

    @lazy_class_attribute
    def MukaiAbelianExtended(cls):
        return _C(_block_gram(_Ug(), _Ug(), _Ug(), _Ug(), _Ug()))

    @lazy_class_attribute
    def U_E8_2(cls):
        return cls.U + cls.E8_2

    @lazy_class_attribute
    def BogachevKolpakovNonReflective(cls):
        return _C([[3, 7, 49], [7, 0, 0], [49, 0, 49]]).twist(-1)

    @lazy_class_attribute
    def BogachevKolpakovWithoutRoots(cls):
        return _C([[0, 0, 49], [0, 49, 7], [49, 7, 3]]).twist(-1)


def _catalogue_entry(name):
    r"""``Lattices.<name>``: the catalogue entry itself, read on first access."""

    def entry(cls):
        return getattr(NamedLattices, name)

    entry.__name__ = name
    return lazy_class_attribute(entry)


_NAMED_LATTICE_NAMES = frozenset(name for name, entry in vars(NamedLattices).items() if isinstance(entry, lazy_class_attribute))


def _named_lattice_block(name):
    r"""The catalogue lattice ``NamedLattices.<name>``, constructed on its first access."""
    assert name in _NAMED_LATTICE_NAMES, f"{name} is not a named lattice of the catalogue"
    return getattr(NamedLattices, name)


for _name in _NAMED_LATTICE_NAMES:
    setattr(Lattices, _name, _catalogue_entry(_name))


# Exact Gram-block names used by the represented direct-sum decomposition.
# A1 and D2 are intentionally omitted: they are scalar twists of rank-one
# blocks and should display as I_{0,1}(2), not as competing root names.
_register_indecomposable_gram_rows("I_{1,0}", ((1,),))
_register_indecomposable_gram_rows("I_{0,1}", ((-1,),))


def _register_root_gram(kind, rank):
    r"""Register the negative simple-root Gram from its Dynkin edges."""
    rows = [[0 for _column in range(rank)] for _row in range(rank)]
    for index in range(rank):
        rows[index][index] = -2
    if kind == "A":
        edges = tuple((index, index + 1) for index in range(rank - 1))
    elif kind == "D":
        edges = (
            *tuple((index, index + 1) for index in range(rank - 3)),
            (rank - 3, rank - 2),
            (rank - 3, rank - 1),
        )
    else:
        edges = (
            *tuple((index, index + 1) for index in range(rank - 2)),
            (2, rank - 1),
        )
    for left, right in edges:
        rows[left][right] = rows[right][left] = 1
    _register_indecomposable_gram_rows(f"{kind}_{{{rank}}}", rows)


for _rank in range(2, 22):
    _register_root_gram("A", _rank)
for _rank in range(3, 23):
    _register_root_gram("D", _rank)
for _rank in (6, 7, 8):
    _register_root_gram("E", _rank)
_register_indecomposable_gram_rows("U", ((0, 1), (1, 0)))


# Nikulin, Math. USSR-Izv. 14 (1980), DOI
# 10.1070/IM1980v014n01ABEH001060; the 75 K3-involution types are displayed
# in Alexeev--Engel--Han, arXiv:2208.10383, Figure 1.
_TWO_ELEMENTARY_RECIPES = {
    (1, 1, 1): (("Z_2", 1),),
    (2, 0, 0): (("U", 1),),
    (2, 2, 0): (("U_2", 1),),
    (2, 2, 1): (("Z_2", 1), ("Z_m2", 1)),
    (3, 1, 1): (("U", 1), ("A1", 1)),
    (3, 3, 1): (("U_2", 1), ("A1", 1)),
    (4, 2, 1): (("U", 1), ("A1", 2)),
    (4, 4, 1): (("U_2", 1), ("A1", 2)),
    (5, 3, 1): (("U", 1), ("A1", 3)),
    (5, 5, 1): (("U_2", 1), ("A1", 3)),
    (6, 2, 0): (("U", 1), ("D4", 1)),
    (6, 4, 0): (("U_2", 1), ("D4", 1)),
    (6, 4, 1): (("U", 1), ("A1", 4)),
    (6, 6, 1): (("U_2", 1), ("A1", 4)),
    (7, 3, 1): (("U", 1), ("D4", 1), ("A1", 1)),
    (7, 5, 1): (("U_2", 1), ("A1", 1), ("D4", 1)),
    (7, 7, 1): (("U_2", 1), ("A1", 5)),
    (8, 2, 1): (("U", 1), ("D6", 1)),
    (8, 4, 1): (("U_2", 1), ("D6", 1)),
    (8, 6, 1): (("U_2", 1), ("A1", 2), ("D4", 1)),
    (8, 8, 1): (("U_2", 1), ("A1", 6)),
    (9, 1, 1): (("U", 1), ("E7", 1)),
    (9, 3, 1): (("U_2", 1), ("E7", 1)),
    (9, 5, 1): (("U_2", 1), ("A1", 1), ("D6", 1)),
    (9, 7, 1): (("U", 1), ("A1", 7)),
    (9, 9, 1): (("U_2", 1), ("A1", 7)),
    (10, 0, 0): (("E10", 1),),
    (10, 2, 0): (("U", 1), ("D8", 1)),
    (10, 2, 1): (("U", 1), ("E7", 1), ("A1", 1)),
    (10, 4, 0): (("U_2", 1), ("D8", 1)),
    (10, 4, 1): (("U", 1), ("D6", 1), ("A1", 2)),
    (10, 6, 0): (("U_2", 1), ("D4", 2)),
    (10, 6, 1): (("U_2", 1), ("D6", 1), ("A1", 2)),
    (10, 8, 0): (("U", 1), ("E8_2", 1)),
    (10, 8, 1): (("U", 1), ("A1", 8)),
    (10, 10, 0): (("E10_2", 1),),
    (10, 10, 1): (("U_2", 1), ("A1", 8)),
    (11, 1, 1): (("U", 1), ("E8", 1), ("A1", 1)),
    (11, 3, 1): (("U", 1), ("D8", 1), ("A1", 1)),
    (11, 5, 1): (("U", 1), ("D6", 1), ("A1", 3)),
    (11, 7, 1): (("U_2", 1), ("D6", 1), ("A1", 3)),
    (11, 9, 1): (("U", 1), ("A1", 1), ("E8_2", 1)),
    (11, 11, 1): (("U_2", 1), ("A1", 1), ("E8_2", 1)),
    (12, 2, 1): (("U", 1), ("E8", 1), ("A1", 2)),
    (12, 4, 1): (("U", 1), ("D8", 1), ("A1", 2)),
    (12, 6, 1): (("U_2", 1), ("D4", 1), ("D6", 1)),
    (12, 8, 1): (("U_2", 1), ("D6", 1), ("A1", 4)),
    (12, 10, 1): (("U", 1), ("A1", 2), ("E8_2", 1)),
    (13, 3, 1): (("U", 1), ("E7", 1), ("D4", 1)),
    (13, 5, 1): (("U_2", 1), ("D4", 1), ("E7", 1)),
    (13, 7, 1): (("U", 1), ("D6", 1), ("A1", 5)),
    (13, 9, 1): (("U_2", 1), ("D6", 1), ("A1", 5)),
    (14, 2, 0): (("U", 1), ("D4", 1), ("E8", 1)),
    (14, 4, 0): (("U", 1), ("D4", 1), ("D8", 1)),
    (14, 4, 1): (("U", 1), ("D6", 2)),
    (14, 6, 0): (("U_2", 1), ("D4", 1), ("D8", 1)),
    (14, 6, 1): (("U_2", 1), ("D6", 2)),
    (14, 8, 1): (("U_2", 1), ("D6", 1), ("D4", 1), ("A1", 2)),
    (15, 3, 1): (("U", 1), ("E7", 1), ("D6", 1)),
    (15, 5, 1): (("U_2", 1), ("D6", 1), ("E7", 1)),
    (15, 7, 1): (("U_2", 1), ("D8", 1), ("D4", 1), ("A1", 1)),
    (16, 2, 1): (("U", 1), ("D6", 1), ("E8", 1)),
    (16, 4, 1): (("U", 1), ("D6", 1), ("D8", 1)),
    (16, 6, 1): (("U_2", 1), ("D6", 1), ("D8", 1)),
    (17, 1, 1): (("U", 1), ("E7", 1), ("E8", 1)),
    (17, 3, 1): (("U", 1), ("D8", 1), ("E7", 1)),
    (17, 5, 1): (("U_2", 1), ("D8", 1), ("E7", 1)),
    (18, 0, 0): (("U", 1), ("E8", 2)),
    (18, 2, 0): (("U", 1), ("D8", 1), ("E8", 1)),
    (18, 2, 1): (("U", 1), ("E8", 1), ("E7", 1), ("A1", 1)),
    (18, 4, 0): (("U", 1), ("D8", 2)),
    (18, 4, 1): (("U_2", 1), ("E8", 1), ("E7", 1), ("A1", 1)),
    (19, 1, 1): (("U", 1), ("E8", 2), ("A1", 1)),
    (19, 3, 1): (("U_2", 1), ("E8", 2), ("A1", 1)),
    (20, 2, 1): (("U", 1), ("E8", 2), ("A1", 2)),
}


def _orthogonal_sum(recipe):
    r"""Realize a recipe of named blocks with multiplicities as one sum.

    The blocks are the mathematical content of a two-elementary realization,
    so the sum is taken over the index set that has one index per block: a
    realization by five blocks has five summands, not a nest of two-summand
    sums that ``indecomposable_summands`` would have to walk back apart.
    """
    blocks = tuple(_named_lattice_block(name) for name, multiplicity in recipe for _index in range(multiplicity))
    match blocks:
        case ():
            return NamedLattices.Zero
        case (only,):
            return only
        case _:
            return Lattices(ZZ).orthogonal_sum(blocks)


@cache
def _two_elementary_lattice(key):
    return _orthogonal_sum(_TWO_ELEMENTARY_RECIPES[key])


class _TwoElementaryTable(Mapping):
    r"""Lazy read-only form of the 75-row Nikulin table."""

    def __getitem__(self, key):
        key = tuple(SageZZ(entry) for entry in key)
        if key not in _TWO_ELEMENTARY_RECIPES:
            raise KeyError(key)
        return _two_elementary_lattice(key)

    def __iter__(self):
        return iter(_TWO_ELEMENTARY_RECIPES)

    def __len__(self):
        return len(_TWO_ELEMENTARY_RECIPES)

    def cardinality(self):
        return cardinal(len(self))

    def validate(self):
        r"""Validate each Nikulin row's signature and 2-elementary invariants."""
        for triple in self:
            lattice = self[triple]
            rank, length, delta = triple
            expected_signature = signature_pair(1, rank - 1)
            actual_signature = lattice.signature_pair()
            # Compare the owned cardinal components themselves. Equality of
            # product points may remain a three-valued proposition even when
            # each inertia index is decidable.
            signature_matches = (
                (actual_signature.first() == expected_signature.first()) is True
                and (actual_signature.second() == expected_signature.second()) is True
            )
            if not signature_matches:
                raise ValueError(
                    f"TwoElementary[{triple}] has signature {actual_signature}, "
                    f"expected {expected_signature}"
                )
            actual_invariants = EvenTwoElementaryLattices(ZZ)(lattice).two_elementary_invariants()
            expected_invariants = nikulin_invariants(rank, length, delta)
            # Nikulin's triple lives in the owned product NN^3. Decide each
            # natural-number coordinate rather than asking product equality
            # for a Boolean decision it need not provide.
            invariants_match = all(
                (actual_invariants.component(index) == expected_invariants.component(index)) is True
                for index in actual_invariants.parent().index_set()
            )
            if not invariants_match:
                raise ValueError(
                    f"TwoElementary[{triple}] has invariants {actual_invariants}, "
                    f"expected {expected_invariants}"
                )
        return True

TwoElementary = _TwoElementaryTable()


def _sum_spec(*parts):
    return ("sum", parts)


def _glue_spec(coefficients, *parts):
    return ("glue", parts, tuple(coefficients))


_NEGATIVE_TWO_ELEMENTARY_SPECS = {
    (0, 0, 0): (_sum_spec(),),
    (1, 1, 1): (_sum_spec("A1"),),
    (2, 2, 1): (_sum_spec(("A1", 2)),),
    (3, 3, 1): (_sum_spec(("A1", 3)),),
    (4, 2, 0): (_sum_spec("D4"),),
    (4, 4, 1): (_sum_spec(("A1", 4)),),
    (5, 3, 1): (_sum_spec("D4", "A1"),),
    (5, 5, 1): (_sum_spec(("A1", 5)),),
    (6, 2, 1): (_sum_spec("D6"),),
    (6, 4, 1): (_sum_spec("D4", ("A1", 2)),),
    (6, 6, 1): (_sum_spec(("A1", 6)),),
    (7, 1, 1): (_sum_spec("E7"),),
    (7, 3, 1): (_sum_spec("D6", "A1"),),
    (7, 5, 1): (_sum_spec("D4", ("A1", 3)),),
    (7, 7, 1): (_sum_spec(("A1", 7)),),
    (8, 0, 0): (_sum_spec("E8"),),
    (8, 2, 0): (_sum_spec("D8"),),
    (8, 2, 1): (_sum_spec("E7", "A1"),),
    (8, 4, 0): (_sum_spec(("D4", 2)),),
    (8, 4, 1): (_sum_spec("D6", ("A1", 2)),),
    (8, 6, 0): (_glue_spec([1, 1, 1, 1, 1, 1, 1, 1], ("A1", 8)),),
    (8, 6, 1): (_sum_spec("D4", ("A1", 4)),),
    (8, 8, 0): (_sum_spec("E8_2"),),
    (8, 8, 1): (_sum_spec(("A1", 8)),),
    (9, 1, 1): (_sum_spec("E8", "A1"),),
    (9, 3, 1): (
        _sum_spec("E7", ("A1", 2)),
        _sum_spec("D8", "A1"),
    ),
    (9, 5, 1): (
        _sum_spec("D6", ("A1", 3)),
        _sum_spec(("D4", 2), "A1"),
    ),
    (9, 7, 1): (
        _glue_spec([0, 1, 1, 1, 1, 1, 1, 1, 1], ("A1", 9)),
        _sum_spec(("A1", 5), "D4"),
    ),
    (9, 9, 1): (
        _sum_spec(("A1", 9)),
        _sum_spec("A1", "E8_2"),
    ),
    (10, 2, 1): (
        _sum_spec("D10"),
        _sum_spec("E8", ("A1", 2)),
    ),
    (10, 4, 1): (
        _sum_spec("E7", ("A1", 3)),
        _sum_spec("D8", ("A1", 2)),
        _sum_spec("D6", "D4"),
    ),
    (10, 6, 1): (
        _sum_spec(("D4", 2), ("A1", 2)),
        _glue_spec(
            [1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
            ("A1", 6),
            "D4",
        ),
        _sum_spec("D6", ("A1", 4)),
    ),
    (10, 8, 1): (
        _sum_spec("D4", ("A1", 6)),
        _glue_spec(
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            ("A1", 10),
        ),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
            "A3",
            ("E7", 1, 2),
        ),
    ),
    (11, 3, 1): (
        _sum_spec("D10", "A1"),
        _sum_spec("E8", ("A1", 3)),
        _sum_spec("E7", "D4"),
    ),
    (11, 5, 1): (
        _sum_spec("D6", "D4", "A1"),
        _sum_spec("D8", ("A1", 3)),
        _sum_spec("E7", ("A1", 4)),
        _glue_spec(
            [1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            "D6",
            ("A1", 5),
        ),
    ),
    (11, 7, 1): (
        _sum_spec("D6", ("A1", 5)),
        _glue_spec(
            [0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
            ("A1", 7),
            "D4",
        ),
        _sum_spec(("D4", 2), ("A1", 3)),
        _glue_spec(
            [1, 2, 0, 1, 2, 1, 0, 2, 0, 1, 2],
            "A5",
            ("E6", 1, 2),
        ),
    ),
    (12, 2, 0): (
        _sum_spec("E8", "D4"),
        _sum_spec("D12"),
    ),
    (12, 4, 0): (
        _glue_spec(
            [0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
            "E7",
            ("A1", 5),
        ),
        _sum_spec("D8", "D4"),
    ),
    (12, 4, 1): (
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1],
            "D8",
            ("A1", 4),
        ),
        _sum_spec("E8", ("A1", 4)),
        _sum_spec(("D6", 2)),
        _sum_spec("D10", ("A1", 2)),
        _sum_spec("E7", "D4", "A1"),
    ),
    (12, 6, 0): (
        _sum_spec(("D4", 3)),
        _glue_spec(
            [1, 0, 2, 0, 1, 2, 1, 0, 2, 0, 1, 2],
            "E6",
            ("E6", 1, 2),
        ),
        _glue_spec(
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            "D6",
            ("A1", 6),
        ),
    ),
    (12, 6, 1): (
        _glue_spec(
            [1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1],
            "D6",
            ("A1", 6),
        ),
        _sum_spec("E7", ("A1", 5)),
        _glue_spec(
            [0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            ("D4", 2),
            ("A1", 4),
        ),
        _sum_spec("D8", ("A1", 4)),
        _sum_spec("D6", "D4", ("A1", 2)),
        _glue_spec(
            [3, 2, 1, 0, 3, 2, 1, 2, 0, 2, 1, 3],
            "A7",
            ("D5", 1, 2),
        ),
    ),
    (13, 3, 1): (
        _sum_spec("D12", "A1"),
        _sum_spec("E7", "D6"),
        _sum_spec("E8", "D4", "A1"),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1],
            "D10",
            ("A1", 3),
        ),
    ),
    (13, 5, 1): (
        _sum_spec("D8", "D4", "A1"),
        _sum_spec("E7", "D4", ("A1", 2)),
        _sum_spec(("D6", 2), "A1"),
        _glue_spec(
            [0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1],
            "E7",
            ("A1", 6),
        ),
        _glue_spec(
            [1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1],
            "D6",
            "D4",
            ("A1", 3),
        ),
        _sum_spec("D10", ("A1", 3)),
        _sum_spec("E8", ("A1", 5)),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1],
            "D8",
            ("A1", 5),
        ),
        _glue_spec(
            [3, 1, 4, 2, 0, 3, 1, 4, 2, 1, 2, 3, 4],
            "A9",
            ("A4", 1, 2),
        ),
    ),
    (14, 2, 1): (
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1],
            "D12",
            ("A1", 2),
        ),
        _sum_spec("D14"),
        _sum_spec("E8", "D6"),
        _sum_spec(("E7", 2)),
    ),
    (14, 4, 1): (
        _glue_spec(
            [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1],
            ("D6", 2),
            ("A1", 2),
        ),
        _sum_spec("E8", "D4", ("A1", 2)),
        _sum_spec("E7", "D6", "A1"),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1],
            "D10",
            ("A1", 4),
        ),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1],
            "D8",
            "D4",
            ("A1", 2),
        ),
        _glue_spec(
            [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1],
            "E7",
            "D4",
            ("A1", 3),
        ),
        _sum_spec("D12", ("A1", 2)),
        _sum_spec("D10", "D4"),
        _sum_spec("D8", "D6"),
        _glue_spec(
            [1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5, 2, 4, 3],
            "A11",
            ("A2", 1, 2),
            ("A1", 1, 2),
        ),
    ),
    (15, 1, 1): (
        _sum_spec("E8", "E7"),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1],
            "D14",
            "A1",
        ),
    ),
    (15, 3, 1): (
        _sum_spec(("E7", 2), "A1"),
        _sum_spec("D8", "E7"),
        _sum_spec("D14", "A1"),
        _sum_spec("E8", "D6", "A1"),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1],
            "D12",
            ("A1", 3),
        ),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1],
            "D10",
            "D4",
            "A1",
        ),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1],
            "D8",
            "D6",
            "A1",
        ),
        _glue_spec(
            [0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1],
            "E7",
            "D6",
            ("A1", 2),
        ),
        _glue_spec(
            [8, 2, 10, 4, 12, 6, 0, 8, 2, 10, 4, 12, 6, 7, 5],
            "A13",
            ("A1", 1, 2),
            "N14",
        ),
    ),
    (16, 0, 0): (
        _sum_spec(("E8", 2)),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
            "D16",
        ),
    ),
    (16, 2, 0): (
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1],
            ("D8", 2),
        ),
        _glue_spec(
            [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1],
            ("E7", 2),
            ("A1", 2),
        ),
        _sum_spec("E8", "D8"),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1],
            "D12",
            "D4",
        ),
        _sum_spec("D16"),
        _glue_spec(
            [3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 2],
            "A15",
            ("A1", 1, 2),
        ),
    ),
    (16, 2, 1): (
        _sum_spec("E8", "E7", "A1"),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1],
            "D8",
            "E7",
            "A1",
        ),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1],
            "D10",
            "D6",
        ),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1],
            "D14",
            ("A1", 2),
        ),
        _glue_spec(
            [7, 6, 5, 4, 3, 2, 1, 0, 7, 6, 5, 4, 3, 2, 1, 3],
            "A15",
            "N8",
        ),
    ),
    (17, 1, 1): (
        _sum_spec(("E8", 2), "A1"),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0],
            "D16",
            "A1",
        ),
        _glue_spec(
            [1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
            "D10",
            "E7",
        ),
        _glue_spec(
            [2, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1],
            "A17",
        ),
    ),
}


@cache
def _negative_block(name, twist=1):
    if name.startswith("N") and name[1:].isdigit():
        # ``rank_one_negative(d)`` in the archived catalogue means
        # ``<-2d>``, not ``<-d>``.
        block = _C([[-2 * SageZZ(name[1:])]])
    elif name in _NAMED_LATTICE_NAMES:
        block = _named_lattice_block(name)
    else:
        block = _C(name)
    return block if twist == 1 else block.twist(SageZZ(twist))


def _negative_sum(parts):
    result = None
    for part in parts:
        if isinstance(part, str):
            name, multiplicity, twist = part, 1, 1
        elif len(part) == 2:
            name, multiplicity = part
            twist = 1
        else:
            name, multiplicity, twist = part
        block = _negative_block(name, twist)
        for _copy in range(multiplicity):
            result = block if result is None else result + block
    return NamedLattices.Zero if result is None else result


_CATALOGUE_GLUE_INCLUSIONS = []


@cache
def _negative_two_elementary_row(key):
    values = []
    for spec in _NEGATIVE_TWO_ELEMENTARY_SPECS[key]:
        kind, parts, *rest = spec
        lattice = _negative_sum(parts)
        if kind == "glue":
            coefficients = rest[0]
            labels = tuple(lattice.module_generating_set())
            if len(coefficients) != len(labels):
                raise RuntimeError(f"the Nikulin table row {key} records a glue vector with {len(coefficients)} coefficients for {lattice}, which has rank {len(labels)}")
            vector = lattice.linear_combination({label: coefficient for label, coefficient in zip(labels, coefficients, strict=True) if coefficient})
            discriminant_class = vector.divided_discriminant_class()
            if lattice.discriminant_module().q(discriminant_class) != 0:
                raise ValueError(
                    f"the Nikulin table row {key} records the glue class {discriminant_class} "
                    f"of {lattice}, which cannot define an overlattice: an overlattice needs an "
                    f"isotropic class, but its discriminant square is "
                    f"{lattice.discriminant_module().q(discriminant_class)}"
                )
            inclusion = lattice.overlattice(discriminant_class)
            lattice = inclusion.codomain()
            _CATALOGUE_GLUE_INCLUSIONS.append((lattice, inclusion))
        values.append(lattice)
    return tuple(values)


class _NegativeDefTwoElementaryTable(Mapping):
    def __getitem__(self, key):
        key = tuple(SageZZ(entry) for entry in key)
        if key not in _NEGATIVE_TWO_ELEMENTARY_SPECS:
            raise KeyError(key)
        return _negative_two_elementary_row(key)

    def __iter__(self):
        return iter(_NEGATIVE_TWO_ELEMENTARY_SPECS)

    def __len__(self):
        return len(_NEGATIVE_TWO_ELEMENTARY_SPECS)

    def cardinality(self):
        return cardinal(len(self))


NegativeDefTwoElementary = _NegativeDefTwoElementaryTable()


_TWO_ELEMENTARY_BLOCK_NAMES = (
    "A1",
    "D4",
    "D6",
    "D8",
    "E7",
    "E8",
    "E8_2",
    "Z_2",
    "U",
    "U_2",
)


@cache
def _two_elementary_blocks():
    blocks = tuple(_named_lattice_block(name) for name in _TWO_ELEMENTARY_BLOCK_NAMES)
    return tuple(
        (
            block,
            block.signature_pair().first(),
            block.signature_pair().second(),
            block.discriminant_length(),
            EvenTwoElementaryLattices(ZZ)(block).delta(),
        )
        for block in blocks
    )


def two_elementary_orthogonal_sums(target_signature, a, delta):
    r"""Return block-orthogonal realizations of the stated 2-elementary invariants."""
    positive_target = int(target_signature.first())
    negative_target = int(target_signature.second())
    target_a = int(a)
    target_delta = int(delta)
    if min(positive_target, negative_target, target_a) < 0:
        raise ValueError(f"there is no 2-elementary lattice of signature {target_signature} and discriminant length a = {a}: the signature and a must be nonnegative")
    if positive_target + negative_target == 0:
        raise ValueError(f"cannot write a lattice of signature {target_signature} as an orthogonal sum of blocks: it is the zero lattice, and the sum must be nonempty")
    if target_delta not in (0, 1):
        raise ValueError(f"there is no 2-elementary lattice with delta = {delta}: Nikulin's invariant delta is 0 or 1")

    block_data = _two_elementary_blocks()
    realizations = []

    def extend(index, positive, negative, length, realized_delta, counts):
        if length > positive + negative:
            return
        if index == len(block_data):
            if positive == negative == length == 0 and realized_delta == target_delta:
                recipe = tuple((name, count) for name, count in zip(_TWO_ELEMENTARY_BLOCK_NAMES, counts, strict=True) if count)
                realizations.append(_orthogonal_sum(recipe))
            return
        _block, block_positive, block_negative, block_length, block_delta = block_data[index]
        count = 0
        while count * block_positive <= positive and count * block_negative <= negative and count * block_length <= length and (count == 0 or block_delta <= target_delta):
            extend(
                index + 1,
                positive - count * block_positive,
                negative - count * block_negative,
                length - count * block_length,
                max(realized_delta, block_delta) if count else realized_delta,
                counts + (count,),
            )
            count += 1

    extend(
        0,
        positive_target,
        negative_target,
        target_a,
        0,
        (),
    )
    return finite_ordered_set(tuple(realizations))


def signature_orthogonal_sums(target_signature, blocks):
    r"""Enumerate multisets of the supplied blocks with the target signature."""
    positive_target = int(target_signature.first())
    negative_target = int(target_signature.second())
    if min(positive_target, negative_target) < 0:
        raise ValueError(f"there is no lattice of signature {target_signature}: both entries of a signature must be nonnegative")
    if positive_target + negative_target == 0:
        raise ValueError(f"cannot write a lattice of signature {target_signature} as an orthogonal sum of blocks: it is the zero lattice, and the sum must be nonempty")
    block_data = tuple(
        (
            block,
            int(block.signature_pair().first()),
            int(block.signature_pair().second()),
        )
        for block in blocks
    )
    if any(positive + negative == 0 for _block, positive, negative in block_data):
        raise ValueError(
            f"cannot enumerate orthogonal sums of the blocks {blocks} with signature {target_signature}: some block has rank zero, so there are infinitely many such sums"
        )
    realizations = []

    def extend(index, positive, negative, selected):
        if index == len(block_data):
            if positive == negative == 0:
                result = None
                for (block, _p, _q), count in zip(block_data, selected, strict=True):
                    for _copy in range(count):
                        result = block if result is None else result + block
                realizations.append(result)
            return
        _block, block_positive, block_negative = block_data[index]
        count = 0
        while count * block_positive <= positive and count * block_negative <= negative:
            extend(
                index + 1,
                positive - count * block_positive,
                negative - count * block_negative,
                selected + (count,),
            )
            count += 1

    extend(0, positive_target, negative_target, ())
    return finite_ordered_set(tuple(realizations))


def _generators(lattice):
    return tuple(lattice.module_generators())


class Involutions:
    r"""Named involutions of the K3 lattice in its displayed block framing."""

    @lazy_class_attribute
    def I_dP(cls):
        lk3 = _generators(NamedLattices.LK3)
        return NamedLattices.LK3.Aut()(
            (
                *(-generator for generator in lk3[0:2]),
                *lk3[4:6],
                *lk3[2:4],
                *(-generator for generator in lk3[6:22]),
            )
        )

    @lazy_class_attribute
    def I_En(cls):
        lk3 = _generators(NamedLattices.LK3)
        return NamedLattices.LK3.Aut()(
            (
                *(-generator for generator in lk3[0:2]),
                *lk3[4:6],
                *lk3[2:4],
                *lk3[14:22],
                *lk3[6:14],
            )
        )

    @lazy_class_attribute
    def I_Nik(cls):
        lk3 = _generators(NamedLattices.LK3)
        return NamedLattices.LK3.Aut()(
            (
                *lk3[0:6],
                *(-generator for generator in lk3[14:22]),
                *(-generator for generator in lk3[6:14]),
            )
        )


class Embeddings:
    @lazy_class_attribute
    def E8_2_into_TdP(cls):
        tdp = _generators(NamedLattices.TdP)
        return NamedLattices.E8_2.Emb(NamedLattices.TdP)(tuple(tdp[4 + index] + tdp[12 + index] for index in range(8)))

    @lazy_class_attribute
    def TCo_into_TEn(cls):
        ten = _generators(NamedLattices.TEn)
        return NamedLattices.Tco.Emb(NamedLattices.TEn)((ten[0] + ten[1], ten[2], ten[3], *ten[4:12]))

    @lazy_class_attribute
    def TEn_into_TdP(cls):
        tdp = _generators(NamedLattices.TdP)
        return NamedLattices.TEn.Emb(NamedLattices.TdP)(
            (
                tdp[0],
                tdp[1],
                tdp[2],
                tdp[3],
                *tuple(tdp[4 + index] + tdp[12 + index] for index in range(8)),
            )
        )

    @lazy_class_attribute
    def TdP_into_LK3(cls):
        lk3 = _generators(NamedLattices.LK3)
        return NamedLattices.TdP.Emb(NamedLattices.LK3)(
            (
                lk3[0],
                lk3[1],
                lk3[2] - lk3[4],
                lk3[3] - lk3[5],
                *lk3[6:14],
                *(-generator for generator in lk3[14:22]),
            )
        )

    @lazy_class_attribute
    def TEn_into_LK3(cls):
        return cls.TdP_into_LK3 * cls.TEn_into_TdP

    @lazy_class_attribute
    def U_E8_2_into_TEn(cls):
        ten = _generators(NamedLattices.TEn)
        return NamedLattices.U_E8_2.Emb(NamedLattices.TEn)(
            (
                ten[0] + ten[2] + ten[3] - ten[4],
                ten[1] + ten[2] + ten[3] - ten[4],
                ten[2] - ten[3],
                ten[5],
                ten[3] + ten[6],
                *ten[7:12],
            )
        )


__all__ = [
    "Embeddings",
    "Involutions",
    "NamedLattices",
    "NegativeDefTwoElementary",
    "TwoElementary",
    "signature_orthogonal_sums",
    "two_elementary_orthogonal_sums",
]
