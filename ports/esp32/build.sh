#!/usr/bin/env bash
if [ -z "$1" ]; then
	echo "Must provide board name..Exiting"
	exit 1
fi

BOARDNAME="$1"
echo "Building board $BOARDNAME"

make BOARD="$BOARDNAME" clean
make BOARD="$BOARDNAME" submodules
make BOARD="$BOARDNAME"

if [ ! -z "$2" ]; then
	PORTNAME="$2"
	echo "Installing to board connected to port: $PORTNAME"

	PORT="$PORTNAME" make BOARD="$BOARDNAME" erase
	PORT="$PORTNAME" make BOARD="$BOARDNAME" deploy
fi
