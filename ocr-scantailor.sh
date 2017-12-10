#!/bin/sh

scantailor-cli -l=1 doc.tiff st-out

tesseract st-out/doc.tif out -l deu

