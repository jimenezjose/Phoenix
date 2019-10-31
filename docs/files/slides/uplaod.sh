#!/bin/bash

SRC="/Users/josejimenez/Downloads/pdf2png"
PREFIX="Labtester-"
SUFFIX="-1.png"

for index in {1..16}
do
	cp $SRC/$PREFIX$index/$PREFIX$index$SUFFIX ./$PREFIX$index.png
done
