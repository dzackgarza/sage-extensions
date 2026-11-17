#!/bin/bash
# Rebuild the parent tree the numbers in results/issue598-the-cusp-rows-ingress-is-linear.md
# were compared against: `61b3fa1`, the commit the repair sits on.  A linked git
# worktree cannot serve as the bound tree (its .git is a file naming a host path the
# runtime cannot see), so the source is archived and committed as its own repository.
set -euo pipefail
REPO=/workspace/nucleus/work/projects/p-8c69fc7199b5456b9cfab0b695f65a6c/repo
BASE=$REPO/.scratch/base-598
rm -rf "$BASE"
mkdir -p "$BASE"
git -C "$REPO" archive 61b3fa157046d96f00630015e8165ebfa5a89574 src pyproject.toml | tar -x -C "$BASE"
git -C "$BASE" init -q .
git -C "$BASE" add -A
git -C "$BASE" -c user.email=probe@localhost -c user.name=probe commit -qm "the tree at 61b3fa1, the parent of the ingress repair"
echo "$BASE"
