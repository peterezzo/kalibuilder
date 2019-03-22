#!/bin/sh
# this file is added to ensure that git calls from noninterative sessions (aka ansible) use dynamic proxy

if [ -z "$http_proxy" ] && [ -z "$https_proxy" ]; then
    proxy=$(proxy-checker.py -q) || true
    export http_proxy=${proxy}
    export https_proxy=${proxy}
fi

/usr/bin/git "$@"
