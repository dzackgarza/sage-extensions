r"""Resolve every file:line citation in the #255 record and amendment, and print the line it names.

The record and the amendment cite the tests and the source by line.  Those lines move whenever a
test is added above them, and a citation that no longer names the line it claims is a false claim in
the evidence.  This script reads both files, follows each citation (a full ``name.sage:123`` or a
bare ``:123`` relative to the file last named), and prints the line of the file it resolves to, so a
reader can see what each citation names now.

Run it inside the adopted image with the checkout bound at `/work`:

    /sage/.venv/bin/python results/issue255-the-citation-audit.py
"""

import re

FILES = {
    "test_the_sterk_configurations_are_folds_of_the_two_root_families.sage": "tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage",
    "folds_of_the_two_root_families.sage": "tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage",
    "test_the_five_sterk_root_configurations_as_foldings.sage": "tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage",
    "test_the_fold_of_a_root_family_by_a_diagram_involution.sage": "tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage",
    "coxeter_diagrams.py": "src/sage_extensions/categories/coxeter_diagrams.py",
    "sterk.py": "src/sage_extensions/sterk.py",
    "lattice_morphisms.py": "src/sage_extensions/categories/lattice_morphisms.py",
}
DOCUMENTS = (
    "results/issue255-the-fold-of-a-root-family.md",
    "results/issue255-amended-invalidating-input.md",
    "results/issue255-amended-issue-body.md",
)

CITATION = re.compile(r"([a-z_0-9]+\.(?:sage|py)):(\d+)|`:(\d+)`")


def main():
    lines = {name: open(path).read().splitlines() for name, path in FILES.items()}
    bad = 0
    for document in DOCUMENTS:
        print(f"== {document}")
        text = open(document).read()
        named = None
        for match in CITATION.finditer(text):
            if match.group(1):
                named = match.group(1)
                number = int(match.group(2))
            else:
                number = int(match.group(3))
            if named is None:
                continue
            body = lines.get(named)
            if body is None:
                continue
            resolved = body[number - 1].strip() if 1 <= number <= len(body) else "<OUT OF RANGE>"
            if resolved == "<OUT OF RANGE>":
                bad = bad + 1
            context = text[max(0, match.start() - 45) : match.start()].replace("\n", " ")
            print(f"{named}:{number}  ...{context[-42:]}")
            print(f"    {resolved}")
    print(f"citations out of range: {bad}")


if __name__ == "__main__":
    main()
