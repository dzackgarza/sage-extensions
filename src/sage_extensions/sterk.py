r"""Sterk cusp and root configurations for degree-two Enriques moduli."""

from sage.rings.rational_field import QQ

from sage_extensions.categories.sets.indexed_families import finite_indexed_family_from_values
from sage_extensions.catalogue import NamedLattices
from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set


def _named_generators(lattice):
    return {str(label): lattice.module_generator(label) for label in lattice.module_generating_set()}


_STERK_DIAGRAM_LAYOUTS = {
    "Sterk_1": {
        0: (0, 0),
        1: (4, 0),
        2: (8, 0),
        3: (8, -4),
        4: (8, -8),
        5: (4, -8),
        6: (0, -8),
        7: (0, -4),
        8: (2, -6),
        9: (QQ(13) / 4, -QQ(19) / 4),
        10: (QQ(9) / 2, -QQ(7) / 2),
        11: (6, -2),
    },
    "Sterk_2": {
        0: (0, 0),
        1: (-4, 0),
        2: (-8, 0),
        3: (-7, 4),
        4: (-6, 8),
        5: (-5, 12),
        6: (-4, 16),
        7: (-3, 20),
        8: (-2, 24),
        9: (-2, 6),
    },
    "Sterk_3": {
        0: (0, -4),
        1: (0, 4),
        2: (0, 8),
        3: (0, 12),
        4: (0, 16),
        5: (4, 16),
        6: (8, 16),
        7: (12, 16),
        8: (20, 16),
        9: (4, 12),
        10: (6, 2),
        11: (14, 10),
    },
    "Sterk_4": {
        0: (0, 0),
        1: (0, 4),
        2: (0, 8),
        3: (4, 8),
        4: (8, 8),
        5: (12, 8),
        6: (16, 8),
        7: (16, 4),
        8: (16, 0),
        9: (4, 4),
        10: (12, 4),
    },
    "Sterk_5": {
        0: (0, 0),
        1: (10, 0),
        2: (20, 0),
        3: (20, -10),
        4: (20, -20),
        5: (10, -20),
        6: (0, -20),
        7: (0, -10),
        8: (4, -4),
        9: (16, -4),
        10: (16, -16),
        11: (4, -16),
        12: (8, -8),
        13: (8, -12),
    },
}


class Sterk:
    @staticmethod
    def roots_18_2_0():
        TdP = NamedLattices.TdP
        b = _named_generators(TdP)
        dual = tuple(TdP.dual_lattice().module_generators())
        _, _, _, _, w1, w2, w3, w4, w5, w6, w7, w8, w1t, w2t, w3t, w4t, w5t, w6t, w7t, w8t = dual
        c = TdP.correlation()
        vectors = {
            "v1": b["b8"],
            "v2": c.lift(c(b["ep"] + b["fp"]) + w1 + w8t),
            "v3": b["a1"],
            "v4": b["a3"],
            "v5": b["a4"],
            "v6": b["a5"],
            "v7": b["a6"],
            "v8": b["a7"],
            "v9": b["a8"],
            "v10": c.lift(c(b["ep"] + b["fp"]) + w8 + w1t),
            "v11": b["b1"],
            "v12": b["b3"],
            "v13": b["b4"],
            "v14": b["b5"],
            "v15": b["b6"],
            "v16": b["b7"],
            "v17": c.lift(c(b["ep"]) + w8t),
            "v18": b["a2"],
            "v19": c.lift(c(b["ep"]) + w8),
            "v20": b["b2"],
            "v21": b["fp"] - b["ep"],
            "v22": c.lift(c(5 * b["ep"] + 3 * b["fp"]) + 2 * w2 + 2 * w2t),
        }
        assert len(vectors) == 22
        return vectors

    @staticmethod
    def roots_18_0_0():
        TdP = NamedLattices.TdP
        b = _named_generators(TdP)
        dual = tuple(TdP.dual_lattice().module_generators())
        _, _, _, _, w1, w2, w3, w4, w5, w6, w7, w8, w1t, w2t, w3t, w4t, w5t, w6t, w7t, w8t = dual
        c = TdP.correlation()
        vectors = {
            "w1": b["a1"],
            "w2": b["a3"],
            "w3": b["a4"],
            "w4": b["a5"],
            "w5": b["a6"],
            "w6": b["a7"],
            "w7": b["a8"],
            "w8": c.lift(c(b["e"]) + w8),
            "w9": b["f"] - b["e"],
            "w10": c.lift(c(b["e"]) + w8t),
            "w11": b["b8"],
            "w12": b["b7"],
            "w13": b["b6"],
            "w14": b["b5"],
            "w15": b["b4"],
            "w16": b["b3"],
            "w17": b["b1"],
            "w18": b["a2"],
            "w19": b["b2"],
        }
        assert len(vectors) == 19
        return vectors

    @staticmethod
    def sterk_roots():
        v = Sterk.roots_18_2_0()
        w = Sterk.roots_18_0_0()

        def reflect(x):
            half = x.parent().base_ring()(v["v22"].b(x) / 2)
            return x + half * v["v22"]

        def orbit_sum(x):
            return x + reflect(x)

        configurations = {
            "Sterk_1": (
                v["v3"] + v["v11"],
                v["v4"] + v["v12"],
                v["v5"] + v["v13"],
                v["v6"] + v["v14"],
                v["v7"] + v["v15"],
                v["v8"] + v["v16"],
                v["v9"] + v["v1"],
                v["v10"] + v["v2"],
                v["v17"] + v["v19"],
                v["v21"],
                v["v22"],
                v["v18"] + v["v20"],
            ),
            "Sterk_2": (
                w["w1"] + w["w17"],
                w["w2"] + w["w16"],
                w["w3"] + w["w15"],
                w["w4"] + w["w14"],
                w["w5"] + w["w13"],
                w["w6"] + w["w12"],
                w["w7"] + w["w11"],
                w["w8"] + w["w10"],
                w["w9"],
                w["w18"] + w["w19"],
            ),
            "Sterk_3": (
                v["v13"],
                v["v14"] + v["v12"],
                v["v15"] + v["v11"],
                v["v16"] + v["v10"],
                v["v1"] + v["v9"],
                v["v2"] + v["v8"],
                v["v3"] + v["v7"],
                v["v4"] + v["v6"],
                v["v5"],
                v["v17"] + v["v19"],
                orbit_sum(v["v20"]),
                orbit_sum(v["v18"]),
            ),
            "Sterk_4": (
                v["v15"],
                v["v16"] + v["v14"],
                v["v1"] + v["v13"],
                v["v2"] + v["v12"],
                v["v3"] + v["v11"],
                v["v4"] + v["v10"],
                v["v5"] + v["v9"],
                v["v6"] + v["v8"],
                v["v7"],
                v["v17"] + v["v20"],
                v["v18"] + v["v19"],
            ),
            "Sterk_5": (
                v["v16"] + 2 * v["v1"] + v["v2"],
                v["v2"] + 2 * v["v3"] + v["v4"],
                v["v4"] + 2 * v["v5"] + v["v6"],
                v["v6"] + 2 * v["v7"] + v["v8"],
                v["v8"] + 2 * v["v9"] + v["v10"],
                v["v10"] + 2 * v["v11"] + v["v12"],
                v["v12"] + 2 * v["v13"] + v["v14"],
                v["v14"] + 2 * v["v15"] + v["v16"],
                v["v17"],
                v["v18"],
                v["v19"],
                v["v20"],
                v["v21"],
                v["v22"],
            ),
        }
        configurations = {
            name: finite_ordered_set(roots) for name, roots in configurations.items()
        }
        for name, roots in configurations.items():
            for root in roots:
                assert root.q() in (-2, -4), (
                    f"the configuration {name} contains {root}, which is not a root: "
                    f"its square is {root.q()}, not -2 or -4"
                )
        assert reflect(reflect(v["v20"])) == v["v20"]
        assert reflect(reflect(v["v18"])) == v["v18"]
        assert orbit_sum(v["v20"]) == v["v22"] + 2 * v["v20"]
        assert orbit_sum(v["v18"]) == v["v22"] + 2 * v["v18"]
        return configurations

    @staticmethod
    def selected_isotropic_vectors():
        TEn = NamedLattices.TEn
        b = _named_generators(TEn)
        dual = tuple(TEn.dual_lattice().module_generators())
        _, _, _, _, w1, w2, w3, w4, w5, w6, w7, w8 = dual
        c = TEn.correlation()
        omega = 2 * w8
        alpha = 2 * w1
        vectors = {
            "Sterk_1": b["e"],
            "Sterk_2": b["ep"],
            "Sterk_3": c.lift(c(b["ep"] + b["fp"]) + omega),
            "Sterk_4": c.lift(c(b["ep"] + 2 * b["fp"]) + alpha),
            "Sterk_5": c.lift(c(2 * b["e"] + 2 * b["f"]) + alpha),
        }
        assert all(vector.q() == 0 for vector in vectors.values())
        return vectors

    @staticmethod
    def sterk5_in_U_E8_2():
        r"""Return Sterk 5's fourteen roots in ``U + E8(2)`` coordinates."""
        lattice = NamedLattices.U_E8_2
        generators = tuple(lattice.module_generators())
        e, f = generators[:2]
        a = {index: generators[index + 1] for index in range(1, 9)}
        dual = tuple(lattice.dual_lattice().module_generators())
        ad = {index: dual[index + 1] for index in range(1, 9)}
        c = lattice.correlation()
        roots = (
            a[2],
            a[4],
            a[5],
            a[6],
            a[7],
            a[8],
            c.lift(2 * ad[8]),
            c.lift(c(2 * e) + 2 * (ad[2] - ad[3])),
            f - e,
            c.lift(c(e + f) + 2 * (ad[6] - ad[3])),
            c.lift(c(e + f) + 2 * (ad[1] + ad[8] - ad[3])),
            e + f + a[3],
            a[1],
            2 * e - a[1],
        )
        assert len(roots) == 14
        assert all(root.q() in (-2, -4) for root in roots)
        return lattice, roots

    @staticmethod
    def sterks_in_TEn():
        r"""Return the alternative Sterk 1--3 roots in ``TEn`` coordinates."""
        lattice = NamedLattices.TEn
        b = _named_generators(lattice)
        e, f, ep, fp = b["e"], b["f"], b["ep"], b["fp"]
        a = {index: b[f"a{index}"] for index in range(1, 9)}
        dual = tuple(lattice.dual_lattice().module_generators())
        ad2 = {index: 2 * dual[index + 3] for index in range(1, 9)}
        ad1 = {index: dual[index + 3] for index in range(1, 9)}
        c = lattice.correlation()
        configurations = {
            "Sterk_1": tuple(a[index] for index in range(1, 9))
            + (
                fp - ep,
                c.lift(c(2 * ep) + ad2[8]),
                c.lift(c(2 * ep + 2 * fp) + ad2[1] + ad2[8]),
                c.lift(c(5 * ep + 3 * fp) + 2 * ad2[2]),
            ),
            "Sterk_2": tuple(a[index] for index in range(1, 9))
            + (
                c.lift(c(2 * f) + ad2[8]),
                e - f,
            ),
            "Sterk_3": tuple(a[index] for index in range(1, 8))
            + (
                f - e,
                c.lift(c(2 * fp) + 2 * ad1[8]),
                c.lift(c(2 * e - 2 * fp) - 2 * ad1[8]),
                c.lift(c(2 * e) + 2 * (ad1[1] - ad1[8])),
                e + f + a[8] - fp,
            ),
        }
        assert tuple(map(len, configurations.values())) == (12, 10, 12)
        assert all(root.q() in (-2, -4) for roots in configurations.values() for root in roots)
        return configurations

    @staticmethod
    def isotropic_vectors():
        v = Sterk.roots_18_2_0()
        s = v["v22"] + v["v21"]
        assert s.q() == 0
        return {"s4_12": s}

    @staticmethod
    def diagrams():
        return {
            name: CoxeterDiagrams().from_roots(
                finite_indexed_family_from_values(None, tuple(roots)),
                # The source diagrams and the retained layouts both index
                # simple roots from zero. Naming them r1,...,rn silently
                # shifted every label relative to the dissertation's layout
                # and to the indexed family used by the Coxeter diagram.
                names=finite_ordered_set(tuple(f"r{i}" for i in range(len(roots)))),
                positions=_STERK_DIAGRAM_LAYOUTS[name],
            )
            for name, roots in Sterk.sterk_roots().items()
        }

    @staticmethod
    def diagram_layouts():
        r"""Return copies of the optional exact presentation coordinates."""
        return {name: dict(positions) for name, positions in _STERK_DIAGRAM_LAYOUTS.items()}


__all__ = ["Sterk"]
