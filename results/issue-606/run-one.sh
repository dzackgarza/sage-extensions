#!/usr/bin/env bash
# Run one test file of the checkout $1 in the research image; output under /home/dzack.
set -euo pipefail
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
checkout=$(realpath "$1"); shift
timeout 600 ~/bin/docker run --rm -v "$checkout":/k -v "$HOME/ai-review-ci/tool-artifacts/pytest_plugins":/plugins:ro \
  -e PYTHONPATH=/k/src:/plugins -e TMPDIR=/k/.pytest-tmp ghcr.io/dzackgarza/sage:develop \
  bash -lc 'mkdir -p /k/.pytest-tmp && cd /k && /sage/.venv/bin/python -c "import sage.all, sys, pytest; sys.exit(pytest.main(sys.argv[1:]))" -p qc_sage_session -p no:cacheprovider -o addopts= -q --tb=short "$@"; s=$?; rm -rf /k/.pytest-tmp; exit $s' _ "$@"
