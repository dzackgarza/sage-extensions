#!/usr/bin/env bash
# Run selected pytest node ids from the k606 worktree inside the research image.
set -euo pipefail
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
cd "$(dirname "$0")/.."
timeout 600 ~/bin/docker run --rm -v "$PWD":/k -v "$HOME/ai-review-ci/tool-artifacts/pytest_plugins":/plugins:ro \
  -e PYTHONPATH=/k/wt/src:/plugins ghcr.io/dzackgarza/sage:develop \
  bash -lc 'cd /k/wt && /sage/.venv/bin/python -c "import sage.all, sys, pytest; sys.exit(pytest.main(sys.argv[1:]))" -p qc_sage_session -p no:cacheprovider -o addopts= -q --tb=short "$@"' _ "$@"
