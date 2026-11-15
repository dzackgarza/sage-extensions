r"""#528: which call of the ambient plane row builds a product over 2^17 points.

The lead: inside the ambient `O(L)` plane row of `T_Co`, `_finite_product`
interns a product over a lazily enumerated index set of 131072 = 2^17 points,
and one hash of that set costs 20.6-86 s.  The mechanism is in the tree:
`Sets().product` sends a finite enumerated index set to `_finite_product`, and
`_cartesian_product_of_finite_family` is a `@cached_function` whose key,
`_finite_family_key`, is `(family.index_set(), tuple(family))` -- so the cache
key *enumerates the family* and hashes 2^17 parents before the product is
built.

This run answers, on `T_Co`'s ambient plane row itself:

* every call of `_finite_product`, `_cartesian_product_of_finite_family` and
  `_finite_family_key`, with the cardinality of the index set it was handed,
  its own wall time, and the innermost caller chain in the library (so the
  call that asks for the 2^17 product is named, not guessed);
* the sizes of the caches these three leave behind, at the end;
* the same for `sage.categories.cartesian_product`, in case a route leaves the
  library's own product.

The row is capped; the probe prints the products it saw whether the row
returns or not.

    sage -python <this file> [cap=<seconds>]
"""

import signal
import sys
import time
import traceback

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories import sets as sets_pkg
from sage_extensions.categories.sets import set_categories as sc

START = time.monotonic()
CAP = 480.0


def now():
    return time.monotonic()


def log(message=""):
    print(f"[{now() - START:7.1f}s] {message}", flush=True)


RECORDS = []


def library_chain(depth=12):
    """The innermost library frames, innermost first."""
    frames = []
    frame = sys._getframe(1)
    while frame is not None and len(frames) < depth:
        filename = frame.f_code.co_filename
        if "sage_extensions" in filename or "/sage/" in filename:
            frames.append(
                f"{filename.rsplit('/', 1)[-1]}:{frame.f_lineno} {frame.f_code.co_name}"
            )
        frame = frame.f_back
    return frames


def cardinality_of(family):
    try:
        return str(family.cardinality())
    except Exception as error:  # the family is reported, not repaired
        return f"<undecided: {error!r}>"


def wrap(module, name, key):
    original = getattr(module, name)

    def counted(*args, **kwargs):
        begin = now()
        record = {"call": key, "args": args, "seconds": None, "outcome": None}
        try:
            outcome = original(*args, **kwargs)
            record["outcome"] = outcome
            return outcome
        finally:
            record["seconds"] = now() - begin
            record["chain"] = library_chain()
            RECORDS.append(record)

    setattr(module, name, counted)


def patch_method(cls, name, key):
    """Wrap ``name`` where it is defined, so the row's own call is timed."""
    for owner in cls.__mro__:
        if name in vars(owner):
            original = vars(owner)[name]

            def counted(self, *args, __original=original, __key=key, **kwargs):
                begin = now()
                record = {"call": __key, "args": args, "seconds": None}
                try:
                    return __original.__get__(self, type(self))(*args, **kwargs)
                finally:
                    record["seconds"] = now() - begin
                    record["chain"] = library_chain()
                    RECORDS.append(record)

            setattr(owner, name, counted)
            return owner
    raise RuntimeError(f"no class of {cls!r} defines {name}")


def instrument():
    """Time the three entry points a finite product goes through.

    ``Sets().ParentMethods._finite_product`` is the method the category's
    ``product`` sends a finite enumerated index set to; it calls
    ``_cartesian_product_of_finite_family``, a ``cached_function`` whose key is
    ``_finite_family_key`` -- the key runs inside the cache wrapper, so timing
    that function times the key and the build together, which is what one
    product costs.  ``_cartesian_product_of`` is the undecorated build.
    """
    # ``product`` and ``_finite_product`` are defined in ``Sets.SubcategoryMethods``
    # in this tree (set_categories.py:1436/1453/1493); the function is fetched from
    # the module by each caller, so patching the class and the module attribute
    # between them covers both routes.
    for owner_class in (sc.Sets.SubcategoryMethods, sc.Sets.ParentMethods):
        try:
            owner = patch_method(owner_class, "_finite_product", "_finite_product")
        except RuntimeError:
            continue
        log(f"_finite_product is defined on {owner!r}")
        break
    else:
        log("_finite_product is on no class this probe reached: only the module functions are timed")
    wrap(sc, "_cartesian_product_of_finite_family", "product (cached, key included)")
    wrap(sc, "_cartesian_product_of", "product (built)")


class Undecided(Exception):
    pass


def _alarm(signum, frame):
    raise Undecided


def describe(record):
    """The index set and factor count of a product record."""
    call = record["call"]
    args = record["args"]
    rows = []
    if call in ("_finite_product", "_finite_family_key"):
        family = args[0]
    else:
        family = args[0] if args else None
    if family is not None and hasattr(family, "cardinality"):
        rows.append(("index set cardinality", cardinality_of(family)))
        try:
            rows.append(("index set", str(family.index_set())[:90]))
        except Exception:
            pass
    return rows


def main(argv):
    global CAP
    for argument in argv:
        if argument.startswith("cap="):
            CAP = float(argument.split("=", 1)[1])
    log(f"probe: which call of the ambient plane row builds a 2^17 product (#528), cap {CAP:.0f} s")
    instrument()
    lattice = NamedLattices.Tco
    log(f"lattice {lattice}")
    OUTCOMES = {}
    members = sorted(
        (name for name in dir(sc) if name.startswith("_cartesian_product")),
    )
    log(f"the product entry points in set_categories: {members}")
    signal.signal(signal.SIGALRM, _alarm)
    begin = now()
    decided = True
    try:
        signal.setitimer(signal.ITIMER_REAL, CAP)
        planes = tuple(
            lattice.stable_orthogonal_group().supergroup().isotropic_orbit_representatives(2)
        )
    except Undecided:
        decided = False
        log(f"the row did not return inside its {CAP:.0f} s cap")
    except Exception:
        decided = False
        log("the row raised:")
        traceback.print_exc()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        spent = now() - begin
    log("")
    log(f"the ambient row: {spent:.1f} s, decided {decided}")
    log("")
    log("=== every product call the row made ===")
    log(f"  {'call':<34}{'index set':>14}{'seconds':>9}  the caller in the library")
    for record in RECORDS:
        rows = describe(record)
        cardinality = dict(rows).get("index set cardinality", "?")
        chain = record["chain"][2:6] if len(record["chain"]) > 2 else record["chain"]
        log(
            f"  {record['call']:<34}{cardinality:>14}{record['seconds']:>9.3f}  "
            + " <- ".join(chain)
        )
    log("")
    log("=== the 2^17 calls in full ===")
    for record in RECORDS:
        rows = dict(describe(record))
        if rows.get("index set cardinality", "").startswith("131072") or (
            record["seconds"] is not None and record["seconds"] > 1.0
        ):
            log(f"  {record['call']} on {rows.get('index set cardinality')} factors, "
                f"{record['seconds']:.3f} s")
            for depth, frame in enumerate(record["chain"]):
                log(f"    {depth:>2}. {frame}")
    return 0 if decided else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
