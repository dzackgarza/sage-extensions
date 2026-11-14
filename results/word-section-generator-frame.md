# Finite orthogonal word sections

The public pointed stabilizer of the primitive null vector (1,0,0,1,0,0) in IsotropicCases_8716 returns integral isometries fixing the vector in both directions. Its positive-definite quotient is <1,1> plus the positive A2 form scaled by five. The quotient group has order 96.

The retained quotient generator family has 14 entries. GAP's permutation image stores four generators. `_GapWordSection` factors elements in those four generators and interprets their indices as indices in the original family. An evaluated returned word fails to map to its requested permutation. Thus this section cannot certify integral lifts or Schreier kernel generators.

GAP's reference manual, [39.5-1 and 39.5-2](https://gap-system.github.io/gap/doc/ref/chap39.html#X7E19F92284F6684E), binds factorization words to `GeneratorsOfGroup` and recommends an explicit epimorphism for algorithmic word preimages. It states that `Factorization` forms all elements to seek short words. The section needs valid words in its supplied family; no minimal-length word is required.

The owning assertion evaluates every returned word in a finite A2 orthogonal group, for the supplied ordered generator family, and checks the exact requested matrix. It also checks the permutation entry point. The complete parabolic kernel of the retained rank-six specimen still requires proof after this section is repaired. The full A7 and Dawes computations use immutable earlier revisions and remain separate results.

The owner doctest fails on the actual ordered rank-four quotient family: its words do not evaluate to all requested finite-group elements. `sage-docker-python -m doctest src/sage_extensions/categories/orthogonal_quotients.py` reports the expected True and actual False. The separate public scaled-A2 discriminant-lift assertion passes at the baseline (12.50-second call); that is a positive control and does not establish this different word-section presentation.

## Repair and exact verification

The section now creates a free group on the supplied generator positions and an explicit homomorphism to their actual permutation images. `PreImagesRepresentative` supplies words in that free group. Both matrix and permutation entry points retain the same ordered family. The owning complete finite-word doctest passes.

The ordinary public discriminant-lift control and the complete nonnormal based-pair splitting/right-transversal assertion pass together under normal owner gates (21.51 seconds total). One earlier attempt ended at the star-import time ceiling before running assertions; the recorded passing run follows completion of the other short diagnostics.

Using the corrected section, the complete Schreier family for the retained rank-six pointed stabilizer has translation module with Hermite basis [[1,1,0,0],[0,2,0,0],[0,0,1,0],[0,0,0,1]]. Every full integral Schreier action equals the independently derived null-line translation formula. Together with the full positive-definite quotient group this proves the complete pointed stabilizer for this supplied null vector. It does not establish every primitive null orbit of IsotropicCases_8716.
