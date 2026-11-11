# #310: the line stabilizer's discriminant image, and its basis independence

`stabilizer_discriminant_image()` computes `rho(G_L)` by the action groupoid of
`thm:schreier-discriminant-image` (research#750, `writing/coble/computations/
discriminant-form-descent.md`, p. 15 of that chapter): over the lattice orbit at
`m = exp(M/L)` each Schreier factor `t_(s.p)^-1 s t_p` contributes

    alpha_{t_(s.p)}(L_(s.p))^-1  *  alpha_s(L_p)  *  alpha_{t_p}(L),

the composite of discriminant isometries between *integral lattice objects*
(`thm:discriminant-transport-functor` item 4). No letter is applied to `A_L` alone.

## The basis-mismatch claim: not reproducible on this tree

The claim on #310 was that `_orbit_lattice_data` stores `epimorphism(L.generator)` — the
coordinates of the transported source generators in the image module's basis, which
`_restricted_fraction_field_subobject_on` takes from Sage's `engine_span.basis()` — while the
middle map pairs the *source* basis at index `i` with those images, so the source-side
epimorphism would be applied twice, and the two readings coincide only when that epimorphism
is the identity.

That was true of `8aa2275`: its `middle_map` read `source["images"][index]` and its transport
was keyed by the *image* lattice's labels although its domain is `L`. Both halves are already
different on this tree — `middle_transport` reads `source["module"].module_generator(...)`,
the image module's own basis, and the transport is keyed by `L`'s own labels — and the
predicted wrong value does not appear:

| specimen | `div(f)` | `|A_L|` | `|image|` | `=` parabolic image |
| --- | ---: | ---: | ---: | --- |
| `U + <-6>`, named basis | 1 | 6 | 2 | yes |
| `U + <-6>`, basis `w_3 = u_1 + u_3` | 1 | 6 | 2 | yes |
| `U + <-6>`, basis `w_3 = u_2 + u_3` | 1 | 6 | 2 | yes |
| `U + <-6>`, line `<e_1>` | 1 | 6 | 2 | yes |
| `U + <-2> + <-6>` | 1 | 12 | 2 | yes |
| `U + <-6> + <-6>` | 1 | 36 | 8 | yes |
| `U(2) + <-6>` | 2 | 24 | 2 | yes |
| `U + A_2` | 1 | 3 | 2 | yes |
| `U + U + <-6>` | 1 | 6 | 2 | yes |
| `I_{1,1} + <3>` (odd) | 1 | 3 | 2 | yes |
| `I_{1,1} + <-3>` (odd) | 1 | 3 | 2 | yes |

(`.tmp/p310-probe3.log`, `.tmp/p310-probe4.log`; each row compares `stabilizer_discriminant_image()`
with `subobject.parabolic_subgroup().image_under(rho)` generator by generator, both ways.)

Why the identification cannot silently fail: the orbit lattice `L_p` is *defined* as
`Lattices(ring)(pullback_form(epimorphism.inverse()).gram_tensor())`, the Gram matrix of the
induced form **in the image module's own basis**, so the lattice's basis *is* the module's
basis, order included. `image_factorization` can present any basis it likes for the image
module and the lattice follows it. The positional transfer in
`_lattice_element_of_module_image` is therefore correct, but it is an implicit assumption
(zip of two label tuples) rather than a checked map — that is what still deserves the
explicit owner map the comment asks for, and it is not backed by a failing specimen here.

## What is landed

`tests/lattices/test_the_discriminant_image_of_a_line_stabilizer_is_basis_independent.sage`
(4 tests, **4 passed in 7.81 s**, `.tmp/p310-red.log`): the published specimen rebuilt in the
basis `w_1 = u_1 + u_2`, `w_2 = u_2`, `w_3 = u_3` through an ordinary isometric change of
basis, with the change of basis as an explicit isometry carrying one line to the other, and

* a guard that the specimens carry a **nonidentity image epimorphism** at some orbit point
  and a **nontrivial discriminant action** — the two hypotheses the passing published test
  does not establish, since its orbit points have identity epimorphisms;
* every orbit point's transporter is an isometry of the two lattice objects it is read on, so
  the composite of discriminant isometries is well typed;
* the image equals `subobject.parabolic_subgroup().image_under(rho)` in either basis;
* naturality: the rebuilt image is the named image conjugated by the change of basis's
  `discriminant_isometry()`, elementwise over `A_L` in both directions.

It is a guard, not a repair: it is green on the tree it lands on, and the report says so.

## The construction does run on `T_Co`, in 35.8 s

The operation #286/#322 lacked is available on the lattice that refused the Eichler route:

| quantity | value | cost | log |
| --- | ---: | ---: | --- |
| `|A_{T_Co}|` | 2048 | — | `.tmp/p310-probe6.log` |
| `|O(A_{T_Co})|` | 46998591897600 | 4.3 s | `.tmp/p310-probe6.log` |
| `|rho(Stab_O(T_Co)(<e_1>))|` | 89181388800 | 30.4 s | `.tmp/p310-probe5.log` |
| orbit points of the lattice orbit | 2 | 0.0 s | `.tmp/p310-probe5.log` |

`46998591897600 / 89181388800 = 527` exactly, and the image has a nonidentity epimorphism at
one of its two orbit points. The order `|O(A_{T_Co})| = 46998591897600` is the research
record's own value (`coble_isotropic_orbits.py`, `prop:coble-discriminant-group`), computed
here by the library rather than typed in.

## Not done: the consumer switch, and the two rows

The switch is not landed, and the reason is measured, not assumed. The two routes of
`_subgroup_isotropic_orbit_representatives` are:

1. `isotropic_line_stabilizer_image`, which returns `None` on `T_Co` because its criterion
   needs two *unimodular* hyperbolic planes in the lattice itself and `T_Co` has none
   (#315's ruling, `_two_hyperbolic_planes(T_Co) = False`);
2. `splitting_isometries(stabilizer)`, which reaches
   `OrthogonalCharacterQuotient._image_section -> _ambient_generators` and demands
   `O(T_Co)`'s selected finite generating set; it ran from 488 s to a 2100 s cap without
   returning (`.tmp/p322-otilde-step.log`).

Supplying the image is necessary but not sufficient: the splitting operation builds its
lifts as **words in the ambient generator family** (`_im_rho_engine_and_section`, then
`libgap.PreImagesRepresentative` on the free group over those generators), and
`_splitting_isometries_in_im_rho_from_image` uses the same family for `rho_images`. Replacing
the *image* leaves that family demanded. Making the row return therefore needs a source of
lifts that does not go through `O(T_Co)`'s generator tuple — the open half of #17 — not a
change to `stabilizer_discriminant_image`. This unit did not attempt a partial version of
that; nothing in the port was edited.

## Follow-up to file (speed, after #286)

> **#322's honest lift locus is 6x the wrong one: the `O(T_Co)` line row went 66.0 s -> 424.5 s**
>
> `integral_parameter_classes` (sage-extensions#322) now returns the union of the transvection
> cosets whose representative lifts, which is the correct locus: 131072 classes on `T_Co`
> instead of the 1024-class kernel `b9e8cfa` reported. The `O(T_Co)` line row makes 11 of
> these calls and went from 66.0 s to 424.5 s (1673 s under two other jobs on the same 4
> CPUs).
>
> One locus is 86.5 s: 36.2 s of the 256 per-coset lift tests (0.141 s each) and 46.6 s of
> `finite_ordered_set` over the 131072 classes — the hash pass of the ordered-set constructor;
> the 131072 additions themselves are 0.2 s (`.tmp/p322-probe24.log`, `.tmp/p322-probe23.log`).
>
> Two owner-level fixes, in order: (1) stop materializing the union — index it by the passing
> cosets times the transvection kernel, an `image_set` over `(cosets, kernel)` with the
> inverse read off the `w = V a` coordinates; (2) the per-coset lift test builds a full
> rational transvection per coset, so a cheaper *exact* test at the same owner would pay for
> itself 11 times per row. A time cap, a profile or a guard is not the deliverable.
