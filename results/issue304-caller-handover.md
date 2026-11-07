# #304 handover to `dzackgarza/lattice-database`

For the orchestrator to post on this repository's issue #304 and, as the dependency edge,
on the lattice-database issue that owns the caller. Neither can be written from this
agent's connection (it reads issues; it cannot post comments or edit issue metadata).

## The caller sites

Value object, in three modules (`src/latticedb/records.py:55`, `graphs.py:55`,
`hoehn_mason.py:49`; identical at the pinned published revision `406b357c7f`):

```python
_QQ_AS_ZZ_MODULE = Modules(QQ).restriction_of_scalars(
    integer_domain.fraction_field_map()
)(QQ.regular_module())
```

`derive` wraps each Gram entry into that value object before building the form
(`records.py:311`, and `records.py:506-509`). These four sites in `src/latticedb/records.py`
pass the card's Gram tensor unwrapped (current HEAD `39a920b527`; the same shape at
`406b357c7f`):

```
:560  FormModules(ZZ)(integer_ring.free_module(lattice.rank)
        .bilinear_hom_space(_QQ_AS_ZZ_MODULE)(lattice.gram_tensor))
:572  ... .bilinear_hom_space(_QQ_AS_ZZ_MODULE)(source_record.gram_tensor) ...
:596  ... .bilinear_hom_space(_QQ_AS_ZZ_MODULE)(source.gram_tensor) ...
:597  ... .bilinear_hom_space(_QQ_AS_ZZ_MODULE)(target.gram_tensor)
```

## The failure, reproduced against the published source's own line

With `_QQ_AS_ZZ_MODULE` as above:

```python
half_integral = ((1, Fraction(1, 2)), (Fraction(1, 2), 1))
FormModules(ZZ)(ZZ.free_module(2).bilinear_hom_space(_QQ_AS_ZZ_MODULE)(half_integral))
# TypeError: Fraction(1, 2) does not describe an element of Free module on {[0]} over
#            Fraction Field of Integer Ring
```

and the same construction with each entry wrapped:

```python
wrapped = tuple(tuple(_QQ_AS_ZZ_MODULE.wrap(QQ(e.numerator) / QQ(e.denominator))
                      for e in row) for row in half_integral)
FormModules(ZZ)(ZZ.free_module(2).bilinear_hom_space(_QQ_AS_ZZ_MODULE)(wrapped))
# builds; is_base_ring_valued() is False, which is right: 1/2 is not integral
```

An integral Gram survives the unwrapped form (`A2`: builds, `is_base_ring_valued()` True),
so the trace needs a card whose Gram has fractional entries -- which is what the issue's
`Fraction(2, 1)`-shaped message and the `1/2` note in this repository's records point at.

## The typed construction the caller should state

The value object's elements are module elements, not scalars, so the Gram must be stated
in it:

```python
rational_gram = tuple(
    tuple(_QQ_AS_ZZ_MODULE.wrap(QQ(entry.numerator) / QQ(entry.denominator))
          for entry in row)
    for row in gram
)
formed = FormModules(ZZ)(module.bilinear_hom_space(_QQ_AS_ZZ_MODULE)(rational_gram))
```

which is exactly what `derive` already does at `records.py:311`.

## What is not required of the provider

No change to `sage-extensions` repairs this: accepting bare `QQ` scalars for a restricted
module's entries would coerce an arbitrary scalar into a module element, which this
repository's #304 acceptance forbids ("do not accept an arbitrary scalar as a module
element"). The library refuses before that coercion and names both the entry and the value
object.

## Provider revision this was measured at

`sage-extensions` `main` = `49b401659a25f0618b639f9f167f2e9aaa542145`; the reproduction and
its log are `.tmp/issue304_page.log`, and TRAPS.md records the table of wrapped and bare
Gram shapes.
