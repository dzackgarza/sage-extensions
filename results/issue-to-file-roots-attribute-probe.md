# To file: the Vinberg cell probes its own `roots` with `getattr(..., None)`

**Where.** `src/sage_extensions/categories/hyperbolic_lattices.py:764`, in
`_filtered_vinal_class().cell()`:

```python
            if self._cell is not _NO_CELL:
                return self._cell
            roots = getattr(self, "roots", None)
            if not roots:
                # ``FundCone`` is cutting the cell itself and asks the layer
                # enumeration on the way; there is nothing to cache yet.
                return None
```

**What is wrong.** The class declares the field: its own `__init__` sets
`self.roots = []` (`hyperbolic_lattices.py:638`), before `check_validity()` and
therefore before any `FundCone`. So the probe never takes its `None` arm: the
value is always a list, and `if not roots` is what actually decides. An
attribute the class owns and sets is being read as if it might be absent, which
hides the state the code is really testing — "no root has been written down
yet" — behind a fallback that cannot happen.

**Repair.** `roots = self.roots` and `if not roots:` (or `if not self.roots:`),
with the comment moved to the empty case: the cell is `None` because the walk
has written no root yet, and `FundCone` is asking on the way. If the empty state
should be named, name it: a sentinel or a boolean that the class sets where the
walk begins, rather than an emptiness test on a list that is empty for two
different reasons.

**Why it is its own issue.** Nothing here is wrong mathematically — `cell()`
returns `None` in exactly the cases it did before — so it must not ride along
with a naming or ownership repair; it is one probe of one's own field, in the
file the Vinberg chamber work lives in, and it is repaired where the field is
declared.
