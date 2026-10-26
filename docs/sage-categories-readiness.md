# Cat/kernel readiness from execution

Assessment date: 2026-09-27. Source: `dzack@rack:~/gitclones/sage-categories`, commit `5867543fc990b017caabdb03d6d82cdf9cc7e5eb`. Runtime: Sage `10.10.beta10`, Python `3.14.3`, through the checkout's `direnv`-selected `SAGE_BIN`. `sage_categories.__file__` resolved to this checkout's `src` tree.

**The core is usable for a bounded downstream leaf integration now, but it is not ready to replace the preamble as-is.** Its central construction mechanisms execute real mathematics. However, current fixed-endpoint property construction and module coequalizer lifting fail on existing mathematical consumers. These failures occur at shared Cat interfaces, not merely in an absent lattice backend. They contradict treating the current framework as integration-complete.

This is a source-and-execution assessment. No milestone checkbox or historical gate result supplies its conclusion. It does not estimate a completion percentage or claim these are the only remaining defects.

## Executed consumers

Every row ran as a separate Sage process with `PYTHONPATH` pointing at this checkout. The test bodies were read to establish what their assertions exercise. Wall times include process startup and imports; some processes ran concurrently, so they are observations rather than isolated benchmarks.

| Consumer under `tests/` | Mathematical evidence | Result | Wall seconds |
| --- | --- | --- | ---: |
| `algebra/test_monoid_scaffold.sage` | Addition on Z/3Z, doubling automorphism, cartesian lift, inherited constructor for a commutative group, an explicit false unit equation | Pass | 80.45 |
| `kernel/test_lifted_limits.sage` | Ordered product and mediator, compatibility with nonidentity diagram arrows, pointed product, lifted coequalizer and its universal factor | Pass | 99.41 |
| `kernel/test_exact_derived_category_implementation.sage` | `Cat().implement` preserves the exact category, existing object and element, additive operations, identity morphism and retained forgetful image | Pass | 108.75 |
| `kernel/test_composite_isofibration_transport.sage` | Inherited data through a composite, retained functor images, successive cartesian lifting | Pass | 36.12 |
| `algebra/test_modules_general_complete.sage` | A presented left module over M2(F2), followed by relation-map and quotient-factor equations | Fails while constructing the quotient; later equations are not reached | 176.54 |
| `kernel/test_predicate_set_subobjects.sage` | Predicate subset of the integers and its inclusion, with known and undecided membership | Fails constructing the first inclusion; later membership assertions are not reached | 58.99 |

The passing lifted-coequalizer consumer does not contradict the failing module quotient. The latter crosses a full-subcategory dispatch path that the former does not establish.

To reproduce a row from the core checkout:

```sh
direnv exec . sh -c 'PYTHONPATH="$PWD/src" TMPDIR="$PWD/.tmp" "$SAGE_BIN" tests/algebra/test_modules_general_complete.sage'
direnv exec . sh -c 'PYTHONPATH="$PWD/src" TMPDIR="$PWD/.tmp" "$SAGE_BIN" tests/kernel/test_predicate_set_subobjects.sage'
```

## Concrete shared defects

### Fixed-endpoint constructor ownership is lost under narrowing

An additional minimal fresh-process reproduction used only:

```python
from sage_categories.sets import Sets
from sage_categories import Mor
X = Sets((0, 1))
family = Mor(Sets)
hom = family(X, X)
narrowed = hom.Monomorphisms()
owner = narrowed.construction_owner()
print(owner is hom, owner is family)  # observed: False True
narrowed(lambda datum: datum)
```

It fails with `TypeError: MorphismCategory.<lambda>() missing 1 required positional argument: 'codomain'`.

The source path is `cat/properties.py:822`, which invokes `construction_owner()`. `cat/category.py:276` walks to an ambient constructor owner. `cat/morphisms.py::FixedEndpointCategory` retains its endpoints and overrides `narrowing_base()`, but the inspected class does not override `construction_owner()`. Thus map data is passed to the endpoint-pair constructor of the Mor family. `sets/finite.py:1128` reaches exactly this path from `SetSubobjects.from_predicate`.

The required repair is at constructor ownership for fixed-endpoint categories and its interaction with property narrowing. A set-only special case would leave other narrowed morphism constructors exposed. This blocks the actual inclusion-map route needed for subgroup-to-subset integration. The recent group-constructor repair `03f6a1fd` works for the executed group consumer but does not establish this other constructor family.

### Full-subcategory colimit dispatch bypasses the supplied lift

`algebra/presented_modules.py::_new_presented_module` registers `with_colimit_lifting` on `modules.forgetful()` for `WalkingParallelPair`, then calls `modules.Colimits(shape)(diagram)`. The executed call instead reaches an ambient limit category and raises:

```text
AssertionError: Limit(Functor(L(2, 2) -> Cat)) owns no WalkingParallelPair-colimit construction; supply universal data
```

`cat/properties.py::FullSubcategory.colimit_construction` checks the local `_colimit_constructors` table, then delegates directly to the ambient. It does not consult selected-functor colimit liftings. `cat/category.py::Category.colimit_construction` does consult them. The analogous full-subcategory limit dispatch gained that selected-functor check in `e56c1f7f`.

The required repair is local-lifting precedence at the shared full-subcategory colimit owner. The leaf already supplies the mathematical lift; adding another quotient constructor to that leaf would bypass the broken extension interface. After repairing dispatch, rerun the full module consumer: its later scalar-action and universal-factor equations remain unverified here.

## Practical cost and remaining evidence

| Fresh-process measurement | Observed value |
| --- | ---: |
| `import sage_categories`, timed inside Sage | 34.025 seconds |
| Additional `from sage_categories.all import *` | 35.520 seconds |
| Whole measurement process | 75.48 seconds |
| Maximum resident memory for that process | 1,008,044 KB |

The full import loads sets, order, algebra and geometry leaves. Both imports complete, but startup is a material day-to-day and development cost. A long-lived notebook can amortize it; these observations do not identify the expensive compiler/import component. The runs also emitted Sage's warning about `_RuntimeImplementationCategory.ParentMethods` having a superclass; no failure was attributed to that warning.

The next useful work is to repair the two shared paths, rerun their existing consumers, then implement one actual preamble chain through public core interfaces: a module with a selected form and a subgroup with its retained inclusion and underlying-set map. That would test the intended downstream boundary, including the real data and maps. The passing existing consumers justify starting that work now; they do not replace it. General higher-categorical calculus, all supported engines and static consumer typing were not exhaustively validated in this assessment.

`git ls-remote origin refs/heads/main` returned `21041b2071e09dbc1d9cf8f57ecb3a172708d467`, not the tested rack revision. Therefore these results concern the local implementation, not the currently published main. No source or dependency pin in the core repository was changed.
