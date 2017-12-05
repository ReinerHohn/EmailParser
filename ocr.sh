#!/bin/sh

unpaper scan.pnm unscan.pnm
convert unscan.pnm unscan.tif
tesseract unscan.tif out -l deu

