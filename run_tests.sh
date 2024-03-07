#!/bin/sh

export PYTHONPATH=.

for test_file in $(find tests -type f | sort -r);
do
    echo "Running '$test_file'..."
    python $test_file
    echo "Done"
done
