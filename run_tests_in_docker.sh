#!/bin/sh

docker run \
    --volume "$PWD:/workdir/" \
    --workdir "/workdir/" \
    -it python \
    ./run_tests.sh
