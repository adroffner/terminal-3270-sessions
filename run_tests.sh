#! /bin/bash
#
# Run Unit Tests
# ============================================================================
# Run the unittests with nose & coverage.py
# ============================================================================

PYTHON=/usr/local/bin/python3

$PYTHON ./setup.py nosetests

echo
echo 'See unit test coverage:'
echo "file://$PWD/htmlcov/index.html"
echo
