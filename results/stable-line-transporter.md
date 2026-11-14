# Finite-character adjustment of an integral transporter

## Required mathematical result

For a supplied ambient integral witness g:x->y and a complete generating family of the target stabilizer P_y, find t in P_y with tg in Gamma, or decide that none exists. Gamma is the exact preimage of its retained finite-character conditions. The returned witness must retain its endpoints, subgroup admission, inverse and full form equations.

## Observed obstruction

The independent input L=2U(2)+A2 with the named negative definite A2 has an explicit Eichler transvection taking the first opposite null line to another line in the stable component subgroup orbit. That explicit isometry is admitted by the subgroup. A public transporter search on that input reaches OrthogonalCharacterQuotient.adjust_witness_into_subgroup -> _image_section -> _ambient_generators and constructs the full O(L) generating family. The diagnostic ends under its separate 180-second bound without returning a transporter. The original Dawes missing-line-cusp exception has no saved term; this observation does not establish its cause.

## Finite-group proof

Write chi:O(L)->D for the retained finite-character map and Gamma=chi^-1(S). All selected sign factors are kernel conditions; the discriminant condition is the intersection T of the supplied targets. Thus S is T in the discriminant factor and identity in every selected sign factor. With only sign factors, S is trivial.

Let W=chi(P_y) and a=chi(g). A correction exists exactly when W intersects the right coset S a^-1. For each w in that intersection, wa belongs to S. It also belongs to chi(O(L)), because both w and a are images of supplied integral isometries. Therefore its lifted correction times g belongs to Gamma, including when chi(O(L)) is a proper subgroup of D and S is nonnormal.

The input already supplies the generators of W and the element a. The character product owns its finite GAP model. Compute the coset intersection there, lift its chosen W element through the target stabilizer's own word section, retain the existing multiplication-order comparison, and admit the resulting integral witness through the subgroup predicate. The full ambient integral generating family is not an input required by this finite problem.

The public red assertion is tests/lattices/test_stable_isotropic_line_transporter.sage. Its initial committed case uses the A2.twist(-1) variant of signature (4,2); the parameterized assertion also names A2 explicitly and verifies signature (2,4). It verifies the explicit subgroup transvection and requires a public exact transporter with both subobject inclusions, ambient inverse and every basis pairing. Its baseline and final gate results must be recorded before this unit is claimed complete. Joint proper-image, nonnormal-condition and negative transporter cases must retain their mathematical results.

## Committed baseline obligation

Provider baseline: 03649cc9b0fd9c3371c46588f98d0450111185e1. The public assertion reaches the existing 60-second test timeout and fails the unchanged 20-second call gate. The selected session ends red after 66.27 seconds. Its explicit transvection establishes the positive mathematical orbit relation; no search witness is returned at this bound. Optional local log: port `.tmp/stable-line-transporter-red.log`.

## Nonnormal correction defect

The public A1^3 assertion supplies a three-cycle g with g(f)=h and the full signed-permutation stabilizer of h. Gamma has determinant one and fixes [e/2] in the discriminant. The explicit signed exchange (-e,h,f) lies in Gamma and takes f to h. At the baseline the correction returns None, so the positive assertion fails. The separate e->h request must remain negative because Gamma fixes [e/2].

Owned group elements compose as maps. The discriminant GAP model composes in the reversed order. If a and w are the native images of g and its target correction, the native condition is a*w in S, rather than w*a in S. For a reversed model compute u in W intersect S*a and use w=u^-1. Then a*w belongs to S since u=s*a implies a*u^-1=s^-1. For a model preserving the product, retain W intersect S*a^-1. Every later sign factor is abelian, as the existing word-order guard requires, so the first factor determines the joint convention.

## Implemented finite correction

The character product retains its full condition subgroup S from the supplied discriminant targets and identity sign factors. The target stabilizer image and supplied witness are compared in a permutation model of that finite product. The correction uses the product convention of its actual first factor, then the existing target-stabilizer word section, exact image comparison and subgroup admission. The actual character image may be proper; the correction still lies in it because its word is evaluated in supplied integral stabilizer generators.

| Selected mathematical assertion | Outcome |
| --- | --- |
| A1^3 nonnormal positive f->h and negative e->h correction | Both decisions and every integral witness equation pass; call 8.19 seconds |
| Stable-component transvection, signature (4,2), full witness | All mathematical equations pass; call 38.61 seconds; existing 20-second call gate remains red |
| Joint proper image on U(3), all sign conditions on U, nonnormal full coset action/lifts | Selected assertions pass normal gates; session 20.20 seconds |
| Stable-component transvection, signature (2,4), named A2 | All mathematical equations pass; call 51.91 seconds; existing 20-second call gate remains red |

The named A2 is negative definite with Gram [[-2,1],[1,-2]]. Its twist by -1 is positive definite. The parameterized assertion states the ambient signatures explicitly. The A1^3 discriminant argument uses the actual negative root form: the three basis half-classes have square -1/2 modulo 2Z.

The original Dawes graph at 2945e78/aa9b99f0 remains a separate failed incidence condition. Its active old-pair diagnostic must retain the rejected flag and actual universe/transport decisions. The finite correction proof and these owner assertions do not establish that graph or the original O_plus_N node.

The final selected named-A2/non-normal session has both mathematical assertions pass in 58.89 seconds. The nonnormal call is 3.94 seconds. The session exits red solely on the named-A2 call gate. The exact positive/negative correction, subgroup membership, two-way line inclusions, inverse laws and full basis pairings all complete.
