#!/bin/sh
rsync -tvz -e ssh www@nfbdev.nfbonf.nfb.ca:.magritte/dists/* ~/.magritte/dists/
