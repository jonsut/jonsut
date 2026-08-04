#!/bin/bash
# Consistency check for the public profile repo.
#
# Usage: scripts/check-profile-readme.sh
#   JONSUT_LIBRARY=/path/to/content-library.md  to override the library location
#
# Exit 0 = clean. Exit 1 = something published here is superseded or breaks a house rule.
#
# This repo is public and the README is often the first thing a recruiter opens, so it
# is held to the same rules as the CV and jonsut.co.uk. The banned-string list is not
# stored here: it names internal project names, so publishing it would defeat it. It is
# declared once in the private content library in the jonsut repo and read at runtime.
# When the library is not present the check degrades to the house-rule scans only.

set -u
cd "$(dirname "$0")/.." || exit 1

fail=0
say_fail() { echo "FAIL: $1"; fail=1; }

# Path is derived from a sibling checkout rather than an absolute home directory,
# for the same reason build_panel.py avoids one: this file is public, and a
# hard-coded home path discloses a username and local layout for no benefit.
library="${JONSUT_LIBRARY:-}"
if [ -z "$library" ]; then
  for cand in ../jonsut/cv/content-library.md ../jonsut-site/cv/content-library.md; do
    if [ -f "$cand" ]; then library="$cand"; break; fi
  done
fi

# Text that ships: the README, the generators that write alt text into the SVGs, and
# the contract tests that pin that alt text. An em dash reaches the page from any of them.
targets=()
for f in README.md tools/*.py tests/*.py; do
  [ -f "$f" ] && targets+=("$f")
done
if [ "${#targets[@]}" = "0" ]; then say_fail "no README or tools found"; fi

for f in "${targets[@]}"; do
  if grep -qn "—" "$f"; then
    say_fail "$f contains an em dash (house rule: never):"
    grep -n "—" "$f" | sed 's/^/      /'
  fi
  if grep -qE '[’‘“”]' "$f"; then
    say_fail "$f contains curly quotes (house rule: straight only):"
    grep -nE '[’‘“”]' "$f" | sed 's/^/      /'
  fi
done

# En dashes are allowed only in date ranges (2025-26), never as an em-dash substitute.
for f in "${targets[@]}"; do
  hits=$(grep -nE '–' "$f" | grep -vE '[0-9]–[0-9]') || true
  if [ -n "$hits" ]; then
    say_fail "$f uses an en dash outside a date range:"
    echo "$hits" | sed 's/^/      /'
  fi
done

if [ -f "$library" ]; then
  banned=$(awk '/^```banned-strings$/{f=1;next} /^```$/{f=0} f' "$library" \
           | sed 's/ :: .*$//' | sed '/^[[:space:]]*$/d')
  if [ -z "$banned" ]; then
    echo "note: no banned-strings fence in $library; superseded-fact check skipped"
  else
    while IFS= read -r bad; do
      [ -n "$bad" ] || continue
      for f in "${targets[@]}"; do
        if grep -qiF -- "$bad" "$f"; then
          reason=$(awk -v v="$bad" -F ' :: ' '$1==v{print $2; exit}' "$library")
          say_fail "$f contains a superseded or private string: \"$bad\" ($reason)"
          grep -niF -- "$bad" "$f" | sed 's/^/      /'
        fi
      done
    done <<< "$banned"
  fi
else
  echo "note: content-library.md not found at $library; superseded-fact check skipped"
  echo "      (set JONSUT_LIBRARY to run the full check)"
fi

echo
if [ "$fail" = "0" ]; then echo "PROFILE CHECK PASS"; exit 0; fi
echo "PROFILE CHECK FAIL"
exit 1
