#!/bin/sh
rsync -tvz -e ssh ~/.magritte/dists/* www@nfbdev.nfbonf.nfb.ca:.magritte/dists/
