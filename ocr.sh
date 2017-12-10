#!/bin/sh

rm -f unscan.pnm
unpaper scan.pnm unscan.pnm

convert unscan.pnm unscan.tif
tesseract unscan.tif out -l deu

