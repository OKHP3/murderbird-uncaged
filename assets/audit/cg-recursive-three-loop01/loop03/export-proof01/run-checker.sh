#!/bin/zsh
# Run from any directory. Arguments: repository root, relative retained packet
# directory, output subdirectory under /tmp/cg-recursive-export-proof02, eras.
set -eu
if [[ -e "$3/checker-results.json" ]]; then
  print -u2 "Use a fresh output subdirectory; existing proof results will not be overwritten."
  exit 2
fi
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python-exit-code 2 --threads 2 --python /tmp/cg-recursive-export-proof02/checker.py -- --root "$1" --base "$2" --out "$3" --eras "${4:-builder}"
