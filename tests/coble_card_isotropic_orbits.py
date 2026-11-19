r"""The two orbit fields of card `6JRR`, compared by the library's own routes.

Card `6JRR` (`dzackgarza/lattice-database`, `lattices/6JRR.md`, read here by tag
through `card`) states `isotropic_classes: 528` and `isotropic_orbits: 2`.  Both
come from one computation: `O(q)`'s orbits on the classes of `A_{T_Co}`, of
which the isotropic ones are those `q` vanishes on -- and `O(q)` preserves `q`,
so one evaluation per orbit decides each.

**Not collected by pytest.** The two computations cost 34 s on the adopted
runtime (the decomposition 13.65 s of it, the rest the lattice, the form and the
engine), which is over the 20 s call ceiling; this is the acceptance tier's
script, like `tests/coble_gamma_co_2_incidence_rows.py`, and it reports instead
of gating.

Exit status: 0 both fields agree, 1 one of them does not -- the numbers printed
either way.
"""

import json
import sys
import time
from pathlib import Path

from sage_extensions.all import *  # noqa: F401,F403

CARD_TAG = "6JRR"


def log(message=""):
    print(message, flush=True)


CARD_FILE = Path(__file__).resolve().parent / "cards" / "lattice-database-enriques.json"


def card(section, tag):
    r"""The card's record, read from the generated digest by its section and tag.

    The pytest session binds this same function from `tests/lattices/conftest.py`;
    a script has no session, so it reads the file the generator writes.
    """
    return json.loads(CARD_FILE.read_text())[section][tag]


def run():
    r"""Compare the card's two orbit fields with the decomposition, and say so."""
    started = time.monotonic()
    record = card("discriminant_forms", CARD_TAG)
    group = NamedLattices.Tco.discriminant_group().O()
    log(f"[card] {CARD_TAG}: the form's orthogonal group built in {time.monotonic() - started:.1f} s")

    isotropic = group.isotropic_class_orbits()
    classes = sum(sum(1 for _position in orbit) for orbit in isotropic)
    orbits = sum(1 for _orbit in isotropic)
    sizes = tuple(sum(1 for _position in orbit) for orbit in isotropic)
    log(f"[card] the isotropic orbits: {orbits}, of sizes {sizes}, {classes} classes")

    agrees_orbits = orbits == record["isotropic_orbits"]
    agrees_classes = classes == record["isotropic_classes"]
    log(
        f"[card] isotropic_orbits: computed {orbits}, card states "
        f"{record['isotropic_orbits']} — {'agrees' if agrees_orbits else 'DIFFERS'}"
    )
    log(
        f"[card] isotropic_classes: computed {classes}, card states "
        f"{record['isotropic_classes']} — {'agrees' if agrees_classes else 'DIFFERS'}"
    )
    log(f"[card] the comparison ran in {time.monotonic() - started:.1f} s")
    return 0 if (agrees_orbits and agrees_classes) else 1


if __name__ == "__main__":
    sys.exit(run())
