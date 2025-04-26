#!/usr/bin/env bash

set -e
set -u

pkill "hugo" || true

# Jump to directory the shell script is placed in
cd "$(dirname "$0")"
# Jump to main hugo directory
cd ..

baseURL="https://herecomesthemoon.net/" #the URL of the website e.g. https://solar.lowtechmagazine.com/
outputDir="./public/" # the directory where you export the site to.

echo "Dithering new images"
python3 utils/dither_images.py -d ./content/ --verbose

echo "Generating site"
hugo -b $baseURL --destination $outputDir --cleanDestinationDir

echo "Calculating page sizes"
python3 utils/calculate_size.py --directory $outputDir --baseURL $baseURL --verbose

# echo "Removing original media from" $outputDir
# python3 utils/clean_output.py --directory $outputDir --verbose

echo "Running prettier"
cd "$outputDir"
prettier --write .
cd ..

# https://gohugo.io/hosting-and-deployment/hugo-deploy/
# Deploys to standard cloud providers
hugo deploy --confirm --force
