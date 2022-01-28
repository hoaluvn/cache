#!/bin/sh

for f in *.py; do
    cat -n $f | sed 's/\t/ /' > .tmp.$$
    leading_space=$(tail -n 1 .tmp.$$ | awk '{ match($0, /^ */); printf(RLENGTH) }')
    start_pos=$(expr $leading_space + 1)
    cut -b ${start_pos}- .tmp.$$ > .tmp2.$$.py
    pygmentize -f html -O full -o html/${f%py}html .tmp2.$$.py
done
rm -f .tmp*$$*
