r"""Build the installed package's record of the revision it was built from.

A wheel is a copy of a source checkout whose git does not travel with it, and the
timing record (:mod:`sage_extensions.timing`) names the revision that produced
every line, so the wheel has to carry that revision from the one moment it is
known: the build.  This module writes it beside :mod:`sage_extensions.timing` as
``source_revision``, the forty hexadecimal characters of the checkout's ``HEAD``,
and the installed package reads it there.

The file is written into the build directory and not into the source tree, so a
checkout is never given a file that states what a build of it happened to record.
The library reads it under the name ``sage_extensions.timing.SOURCE_REVISION_FILE_NAME``,
and the test that installs a wheel of this checkout asserts the record it writes
names this tree's commit, so a name the two disagree on is a failing test and
never a silently unrecorded revision.
A build that cannot resolve a revision -- no git, or no checkout -- writes none,
and the installed package then refuses to write a timing record rather than
attributing one to a commit it does not know.  A working tree with uncommitted
changes is built as its ``HEAD``, which is what ``git rev-parse HEAD`` answers
for it.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

TREE = Path(__file__).resolve().parent
r"""The source checkout this build is of."""

REVISION_FILE_NAME = "source_revision"
r"""The name the revision is written under, beside :mod:`sage_extensions.timing`."""

_COMMIT_ID = re.compile(r"[0-9a-f]{40}")


def _source_revision() -> str | None:
    r"""The commit of the checkout being built, and ``None`` if git cannot state one.

    A build environment with no git, or a build of a tree that is not a
    checkout, has no revision to record; the package then answers that it knows
    none rather than recording a guess.
    """
    try:
        completed = subprocess.run(
            ("git", "-C", str(TREE), "rev-parse", "HEAD"),
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    resolved = completed.stdout.strip()
    return resolved if _COMMIT_ID.fullmatch(resolved) is not None else None


class _BuildPy(build_py):
    r"""``build_py``, and then the revision the built package was made from."""

    def run(self) -> None:
        super().run()
        if self.dry_run:
            return
        revision = _source_revision()
        if revision is None:
            return
        destination = Path(self.build_lib, "sage_extensions", REVISION_FILE_NAME)
        destination.write_text(revision + "\n", encoding="utf-8")


setup(cmdclass={"build_py": _BuildPy})
