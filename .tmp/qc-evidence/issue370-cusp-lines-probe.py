"""#370 probe H: which isotropic line carries Sterk's printed 4.3.8 and 4.3.9 roots?

Card 029J's `cusp_chambers` row and the library's `Sterk.selected_isotropic_vectors()` agree at cusps
1--3 and 5 and disagree at cusp 4 (their pairing is 2, so they span different isotropic lines).  This
prints both lines, their pairings, and the pairing of every transported printed root with the card's
line.
"""
import json
import time
from pathlib import Path

T0 = time.time()


def stamp(message):
    print(f"[{time.time() - T0:8.2f}s] {message}", flush=True)


from sage_extensions.all import (  # noqa: E402
    Embeddings,
    NamedLattices,
    Sterk,
    ZZ,
)

TEn = NamedLattices.TEn
Tco = NamedLattices.Tco

names = ["e", "f", "ep", "fp", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8"]


def card(section, tag):
    digest = Path("/repos/sage-extensions/tests/cards/lattice-database-enriques.json")
    return json.loads(digest.read_text(encoding="utf-8"))[section][tag]


def tco_vector(row):
    ring = Tco.base_ring()
    coefficients = {"h": ring(int(row[0]))} if int(row[0]) else {}
    for name, value in zip(names[2:], row[2:]):
        if int(value):
            coefficients[name] = ring(int(value))
    return Tco.linear_combination(coefficients)


rows = card("cusp_chambers", "029J")["rows"]["gamma-en-2"]
library = Sterk.selected_isotropic_vectors()
labels_ten = tuple(TEn.module_generating_set())
into_ten = Embeddings.TCo_into_TEn
for number in (1, 2, 3, 4, 5):
    row = tuple(int(value) for value in rows[number - 1]["cusp"])
    card_vector = into_ten(tco_vector(row))
    eta = library[f"Sterk_{number}"]
    coordinates = eta.to_vector()
    print(f"cusp {number}: library eta e,f = {int(coordinates('e'))}, {int(coordinates('f'))}; "
          f"q {TEn.q(eta)}; pairing with the card's vector {TEn.b(card_vector, eta)}")
    print(f"  card vector in T_En {[int(card_vector.to_vector()(label)) for label in labels_ten]}")
    print(f"  library eta in T_En {[int(coordinates(label)) for label in labels_ten]}")
    print(f"  equal up to sign: {card_vector == eta or card_vector == -eta}")

# ---- the transported printed roots against the card's line -------------------------
for number, name in ((4, "Sterk_4"), (5, "Sterk_5")):
    row = tuple(int(value) for value in rows[number - 1]["cusp"])
    card_vector = into_ten(tco_vector(row))
    roots = tuple(Sterk.cusp_roots_in_TEn(name))
    print(f"cusp {number}: pairings of the {len(roots)} printed roots with the card's line",
          [TEn.b(root, card_vector) for root in roots])
    print(f"  with the library's line", [TEn.b(root, library[name]) for root in roots])
stamp("done")
