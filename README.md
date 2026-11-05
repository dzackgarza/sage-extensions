# sage-extensions

A SageMath library of owned categories: lattices, bilinear and quadratic forms,
modules, groups and the constructions on them, organized behind the mathematics
of [lean-categories](https://github.com/dzackgarza/lean-categories). It installs
into the Sage virtual environment of the shared math container
`ghcr.io/dzackgarza/sage:develop`.

## Run it

```python
>>> from sage_extensions.all import ZZ, Lattices
>>> U = Lattices(ZZ)("U")
>>> U
Integral lattice of rank 2 and signature (1, 1)
>>> U.is_isometric(Lattices(ZZ)([[0, 1], [1, 0]]))
True
>>> A2 = Lattices(ZZ)("A2")
>>> A2.discriminant_group().cardinality()
3
>>> E8 = Lattices(ZZ)("E8")
>>> E8.is_even(), E8.is_unimodular()
(True, True)

```

The block runs as a doctest on every push, in the
[README example workflow](.github/workflows/readme.yml). Locally:

```bash
"$(just -f ~/ai-review-ci/justfiles/sage.just -d . _sage-python)" -m doctest README.md
```

## Read next

- [AGENTS.md](AGENTS.md): the rules for writing the library.
- [CONTRIBUTING.md](CONTRIBUTING.md): the preamble architecture specification and the design philosophy.
- [The issue tree](https://github.com/dzackgarza/sage-extensions/issues/14): the unfinished work.
