# Generator permutations from the retained orbit transitions

For a finite G-orbit with chosen point order x_i, the orbit sweep retains the complete table T(i,s) = rank(s*x_i) for each selected generating letter s. The permutation with position images T(i,s)+1 is exactly the action of s on that orbit. Its point set and selected generating cover are those retained by the construction, so arbitrary point labels preserve the same action and word order.

`FiniteGSets.orbit_generator_permutations` admits those images directly through the existing owned symmetric-group constructor. This is the same private engine boundary that `_from_orbit_sweep` already uses when constructing the G-set. The permutation engine checks the complete image family.

The original O_plus_N line/plane assertion at port 8e5436f/provider cfee1892 reaches its original bound while the old method reconstructs points and repeatedly ranks them in `_permutation_from_point_map`. Its plane stabilizer cannot finish its native Schreier realization until these generator permutations are available. The exact finite transition table is the supplied datum for this operation.

The defining S3 action, its conjugate under a point bijection with nonordinal labels, and a disjoint fixed orbit agree on every selected generator image and every transversal witness. The expectations call the supplied defining action directly. The normal owner gates pass in 2.71 seconds at source 87b95c5c.

A separate exact action uses the standard symmetric group on the following relabeled point set: label(i) = 3*i-127, for 0 <= i < n, with seed label(n//2). Each supplied group element acts by conjugation through this bijection. Every returned generator image is checked against that defining action.

| Complete permutation realization | Before | Retained transitions |
| --- | ---: | ---: |
| Points | 64 | 64 |
| Selected letters | 2 | 2 |
| Wall seconds | 0.077870 | 0.002708 |
| CPU seconds | 0.077844 | 0.002688 |

The measured boundary is generator permutation realization after orbit closure and Schreier-factor construction. This example establishes the exercised mathematical operation; the original O_plus_N and other full public consumers still require their own results at the published pair.

Optional reproduction in the active port checkout: `.tmp/orbit-transition-realization-benchmark.py`, its before/after logs and JSON results. The original terminal log is `.tmp/o-plus-N-8e5436f-native-stream.log`. These local files are diagnostic aids rather than cloud prerequisites.
