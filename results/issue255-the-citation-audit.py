r"""Resolve every file:line citation in the #255 record and its two companions, and say what it names.

The record cites tests and source by line, and those lines move whenever a test is added above them
or a function is inserted before them.  A citation that no longer names the line it claims is a false
claim in the evidence, and a citation that is merely *in range* can be the wrong line: the earlier
version of this script checked only the range, and one bare `:146` resolved to a docstring in
`coxeter_diagrams.py` rather than to the exploration test it meant.

So each cited line has an expected token here, and the script reports a citation as stale unless its
line contains that token.  The tokens are the name of the definition or the opening of the statement;
a line whose content changes deliberately is updated here with it.

Run it inside the adopted image with the checkout bound at `/work`:

    /sage/.venv/bin/python results/issue255-the-citation-audit.py
"""

import re

DOCUMENTS = (
    "results/issue255-the-fold-of-a-root-family.md",
    "results/issue255-amended-invalidating-input.md",
    "results/issue255-amended-issue-body.md",
)

FILES = {
    "test_the_sterk_configurations_are_folds_of_the_two_root_families.sage": "tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage",
    "folds_of_the_two_root_families.sage": "tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage",
    "test_the_five_sterk_root_configurations_as_foldings.sage": "tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage",
    "test_the_fold_of_a_root_family_by_a_diagram_involution.sage": "tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage",
    "coxeter_diagrams.py": "src/sage_extensions/categories/coxeter_diagrams.py",
    "sterk.py": "src/sage_extensions/sterk.py",
    "lattice_morphisms.py": "src/sage_extensions/categories/lattice_morphisms.py",
}

CITATION = re.compile(r"([a-z_0-9]+\.(?:sage|py)):(\d+)|`:(\d+)`")

EXPECTED = {
    ("src/sage_extensions/categories/coxeter_diagrams.py", 1445): 'def Aut',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2179): 'def from_roots',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2489): 'def fold',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2519): 'The relation test is not redundant with the ',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2531): 'An orbit sum that is a multiple of a point o',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2560): 'return self._folded_by_images(*_involution_i',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2562): 'def _folded_by_images',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2654): 'f"cannot fold {self} by {datum}: an image of',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2726): 'for row in sums:',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2785): 'class RootFamilyFolding',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2818): 'def isometry',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2822): 'def invariant_lattice',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2826): 'def anti_invariant_lattice',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2830): 'def roots',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2834): 'def discarded_sums',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2850): 'def two_elementary_invariants',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2880): 'def _two_elementary_invariants',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2909): 'def _involution_images',
    ("src/sage_extensions/categories/coxeter_diagrams.py", 2991): 'def _coordinate_divisor',
    ("src/sage_extensions/categories/lattice_morphisms.py", 2002): 'def invariant_lattice',
    ("src/sage_extensions/categories/lattice_morphisms.py", 2012): 'def formed_coinvariants',
    ("src/sage_extensions/sterk.py", 562): 'def _roots_18_2_0_cached',
    ("src/sage_extensions/sterk.py", 641): 'def _roots_18_0_0_cached',
    ("src/sage_extensions/sterk.py", 679): 'def _foldings_cached',
    ("src/sage_extensions/sterk.py", 689): 'foldings[name] = CoxeterDiagrams().from_root',
    ("src/sage_extensions/sterk.py", 691): 'foldings[name] = CoxeterDiagrams().from_root',
    ("src/sage_extensions/sterk.py", 697): 'def foldings',
    ("src/sage_extensions/sterk.py", 718): 'def _sterk_roots_cached',
    ("src/sage_extensions/sterk.py", 784): 'def sterk_roots',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 1): 'r"""Semantic exploration: Sterk\'s five root ',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 93): 'for name, folding in Sterk.foldings().items(',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 103): 'assert int(invariant.module_rank()) == 10',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 114): 'for name, folding in Sterk.foldings().items(',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 123): 'assert _signature(span) == (1, 17)',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 126): 'assert _signature(invariant) == _signature(w',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 129): 'def test_the_five_folded_families_carry_the_card_counts_and_squares',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 136): 'for name, folding in Sterk.foldings().items(',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 139): 'assert int(folding.roots().cardinality()) ==',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 143): 'assert folding.folded_diagram().root_realiza',
    ("tests/lattices/test_the_five_sterk_root_configurations_as_foldings.sage", 146): 'def test_the_five_folded_lattices_answer_their_two_elementary_invariants',
    ("tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage", 110): 'def test_a_permutation_that_keeps_the_pairings_and_breaks_a_relation_is_refused',
    ("tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage", 129): 'with pytest.raises(ValueError):',
    ("tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage", 133): 'def test_a_degenerate_family_of_twenty_two_roots_refuses_a_gram_preserving_permutation',
    ("tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage", 169): 'with pytest.raises(ValueError):',
    ("tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage", 173): 'def test_an_image_outside_the_span_of_the_roots_is_refused',
    ("tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage", 216): 'with pytest.raises(ValueError):',
    ("tests/lattices/test_the_fold_of_a_root_family_by_a_diagram_involution.sage", 278): 'def test_an_orbit_sum_that_is_a_multiple_of_a_root_is_rescaled',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 121): 'def test_the_stored_root_families_have_the_specimens_norm_counts_and_rank',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 147): '} == {name: _chamber(statement)["wall_count"',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 159): 'def test_the_folded_families_carry_the_card_squares_and_pairings',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 179): 'assert wall_span.module_rank() == 10',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 182): 'assert _signature(folding.invariant_lattice(',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 188): 'assert _signature(folding.span()) == (1, 17)',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 189): 'assert _signature(folding.anti_invariant_lat',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 469): 'def test_the_folded_families_are_the_printed_diagrams_vertex_by_vertex',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 192): 'def test_the_folded_configurations_are_the_constructions_sterk_returns',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 269): 'def test_the_gram_preserving_permutations_of_the_twenty_two_roots_fold_or_are_refused',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 296): 'with pytest.raises(ValueError):',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 305): 'def test_the_twenty_two_roots_refuse_a_permutation_that_moves_a_pairing',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 348): 'def test_the_eleven_root_diagrams_involution_has_five_pairs_and_one_fixed_vertex',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 372): 'def test_the_archived_permutation_is_an_automorphism_and_folds_to_the_eleven_roots',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 410): 'def test_the_two_twisted_configurations_are_folds_of_the_twenty_two_roots',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 432): 'assert int(folding.invariant_lattice().modul',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 433): 'assert _signature(folding.invariant_lattice(',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 434): 'assert _signature(folding.anti_invariant_lat',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 436): 'def test_the_five_foldings_are_read_as_records_rather_than_repeated',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 446): 'assert int(folding.invariant_lattice().modul',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 447): 'assert _signature(folding.invariant_lattice(',
    ("tests/lattices/test_the_sterk_configurations_are_folds_of_the_two_root_families.sage", 448): 'assert _signature(folding.anti_invariant_lat',
}


def main():
    lines = {path: open(path).read().splitlines() for path, _number in EXPECTED}
    stale = 0
    total = 0
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
            if named not in FILES:
                continue
            path = FILES[named]
            expected = EXPECTED.get((path, number))
            if expected is None:
                continue
            total = total + 1
            body = lines[path]
            line = body[number - 1] if 1 <= number <= len(body) else ""
            ok = expected in line
            if not ok:
                stale = stale + 1
            print(f"{'ok   ' if ok else 'stale'} {path}:{number}  {line.strip()[:90]}")
    print(f"citations checked: {total}; stale: {stale}")


if __name__ == "__main__":
    main()
