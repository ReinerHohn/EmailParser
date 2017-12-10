#!/bin/sh

ssh pi@192.168.178.25 'bash -s' < scan-tiff.sh 
scp pi@192.168.178.25:doc.tiff .
./ocr-scantailor.sh
