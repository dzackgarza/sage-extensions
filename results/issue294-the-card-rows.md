# The U ⊕ U ⊕ ⟨−2d⟩ line counts, read from the cards of those five lattices

The acceptance test for the primitive isotropic line orbits of `L_d = U ⊕ U ⊕
⟨−2d⟩`, d ∈ {1, 2, 4, 9, 36}, now reads every expected count from the card of the
lattice it is about, by tag, and the derivation that stood in its docstring is
gone. Its fifteen line counts are the `O`, `Õ` and `Õ⁺` rows of cards `6JRS`
(`L_1`), `6JRT` (`L_2`), `6JRU` (`L_4`), `6JRV` (`L_9`) and `6JRW` (`L_36`).

## Item by item

| the acceptance says | how it is met |
| --- | --- |
| each row of the test reads its expected value from a card tag | the five counts per card are `card("primitive_orbit_series", tag)["rows"][group]["constant"]`; no number is typed in the file |
| the docstring derivation is gone | the docstring states what the rows are and where they are read; it derives no count, names no bibliography, and transcribes no witness |
| five lattices, three subgroups | fifteen rows, one test per (card, subgroup): `lattice.Aut()`, `lattice.stable_orthogonal_group()` and `stable.intersection(lattice.O_plus())` — `O`, `Otilde`, `Otilde+` — each compared with that card's own row, with an assertion that the card states exactly those three |
| the lattice is the card's, not a substitute | the lattice is built from the card's `gram_tensor`, and its rank, signature, determinant and full Gram matrix are compared with the card before the orbit row is read |
| expected values are card values, not brief values | the digest is generated from `dzackgarza/lattice-database` at a full commit; the rows are the database's computed ones and `certifications.integral.primitive_orbits` is the stamp they were computed under |

The rows exist since the database's `certify` run minted `integral.primitive_orbits`
on these five cards: no published source states these counts, so the card states a
computation and its stamp rather than a citation. The digest was regenerated at
`23c0f9caff4d08b1f9795bba75f45cead4fc75df`; at that ref the refresh reproduces
every other section of the committed digest byte for byte, and its diff is the
new ref plus the five cards (336 insertions, one deletion).

## What the test asserts, and what the numbers are

`6JRS`, `6JRT`, `6JRU`, `6JRV`, `6JRW` state 1, 1, 2, 2, 4 as the number of
orbits of primitive isotropic lines under each of the three subgroups, and the
library returns 1, 1, 2, 2, 4. A probe printing the card's constant beside the
library's count, read off the digest rather than through the test, is in the
`fix:` commit's body: no comparison is 0 = 0, and every card row is a computed
count on the lattice the card states (rank 5, signature (2, 3), determinants
−2, −4, −8, −18, −72).

Every row of the file is now one of the fifteen card rows. The two witness
vectors `3e + 3f + g` and its negative on `L_9` were the last row whose expected
values were not a card's — divisibility three, and divided classes of order three
— and that row is gone. Its facts stay asserted, with the same two vectors and on
the same lattice, in
`tests/lattices/test_discriminant_line_orbits.sage::test_vectors_are_not_identified_when_a_discriminant_class_differs_from_its_negative`,
which also reads the line counts there; nothing about the two classes is left
only in this file.

The card-driven alternative was rejected on cost and on what the library states.
Cards `6JRS`–`6JRW` do state `integral.discriminant_form.isotropic_classes`
(1, 1, 2, 2, 4 … 6), so a row could read it, but comparing it with the library
means counting the isotropic classes of `A_L` itself: the divided-class
enumeration that attains them (`isotropic_lines_by_divided_class`) is a residue
loop that refuses above 4·10⁶ candidates, and divisor 6 on `6JRW` (rank five)
is 1.7·10⁶ before divisor 12 and 24 are asked for. A count taken any other way
would be this file's own enumeration, not a card comparison.

## What is recorded rather than asserted

**The rank-five plane count lost its row.** The file also asserted one orbit of
primitive isotropic planes on `L_1`, with the number derived in the docstring from
Scattone's degree-two boundary (four Type II curves and one Type III point on the
rank-19 period lattice `U² ⊕ E8(−1)² ⊕ ⟨−2⟩`): the rank-five shadow sees one of
them. No card of the five states a plane count — their `integral.primitive_orbits`
rows carry `constant` and the empty `z` and `w`, not `planes` — so that row had no
card to read and is not asserted. It is the same shape as the ask the orbit rows
themselves were.

Issue-body draft, to be filed against `dzackgarza/lattice-database` (this
connection reads issues and pushes commits; it cannot create one):

> **Title:** The `planes` row of the five U ⊕ U ⊕ ⟨−2d⟩ cards, once the plane call
> returns on them
>
> **Body:** Cards `6JRS`–`6JRW` state `integral.primitive_orbits.<group>.constant`
> and leave `z` and `w` empty. They state no `planes` row, so
> `sage-extensions`' rank-five test asserts no orbit count of primitive isotropic
> planes: the one orbit it used to assert on `L_1` came from Scattone's degree-two
> boundary on the rank-19 period lattice, which is not a statement about the
> shadow. When `certify` mints `integral.primitive_orbits.<group>.planes` for
> `6JRS`–`6JRW`, the row can be read by tag like the line counts now are.

The comparisons of the published known families — Scattone, `T_En` under `O`,
`Õ⁺` and `Γ_{En,2}`, the Dutour Sikirić–Hulek strata and the 87 polarization
groups — are part of #286's acceptance through the same call, and are not touched
here.

## The runs

Adopted runtime (`~/sage-image/run.sh`, Sage 11.0.beta5,
`/sage/.venv/bin/python`), the worktree bound at `/work`, its `.git` bound where
the gitdir pointer names it (the timing record resolves the checkout through git,
and a bare `/work` bind leaves it unattributable):

```
~/sage-image/run.sh -w /work -b <worktree>:/work -b <repo>/.git:<repo>/.git -b ~/ai-review-ci:/ci -- \
  /bin/sh -c 'export HOME=/root; git config --global --add safe.directory "*";
    export PYTHONPATH=/ci/tool-artifacts/pytest_plugins:/work/src:/work:/repos/sage-extensions/src;
    exec /sage/.venv/bin/python -u -m pytest -o addopts= -p qc_sage_session \
      -p sage_extensions.testing.suite_budget -p sage_extensions.testing.test_lint --durations=0 -q \
      tests/lattices/test_isotropic_line_orbits_of_small_indefinite_lattices.sage \
      tests/lattices/test_primitive_orbit_series_on_indefinite_lattices.sage'
```

With the digest still at `1e1cadc…` — the parent of the pair, and every commit
before the digest refresh — the file is red before any orbit is computed: the
digest holds no primitive-orbit row for those five tags, so `card` raises for the
first one it is asked for.

```
section = 'primitive_orbit_series', tag = '6JRV'
    return json.loads(DIGEST.read_text(encoding="utf-8"))[section][tag]
E       KeyError: '6JRV'
tests/lattices/conftest.py:42: KeyError
16 failed in 0.96s
```

At the `fix:` commit the same file is green: `16 passed in 23.33s` on its own,
with no call over the 20 s ceiling. Together with the sibling module that
compares the series against the orbit call, `18 passed in 24.20s`, the sibling's
slowest call `8.89s` — that module's code is unchanged here, only its docstring.
The single test over all five cards that this replaces took 25.09 s at the parent
and printed the call-ceiling line.

The cost of one row is the library's orbit call, not the lattice: building the
lattice and its three subgroups is 0.01–0.36 s per card, while one orbit call is
0.17–4.18 s (`6JRW` under `Otilde` the dearest). One test per row is what keeps
every call inside the ceiling: with one test per card the `L_36` call reached
20.49 s in a run made under unrelated load (load average 6.4 on four CPUs), while
the same work split by row stayed at 10.24 s in a run under the same load.

The runtime at `/work` needed `-b <repo>/.git:<repo>/.git`: a worktree's `.git` is
a gitdir pointer at an absolute path, and without the bind
`sage_extensions.timing` cannot resolve the source checkout and fails every test
that records a timing. That is a run-setup detail, not a repository change.
