#!/bin/sh
#------------------------------------------------------------------------------
# written by:   mcdaniel
#               https://lawrencemcdaniel.com
#
# date:         sep-2023
#
# usage:        Generate a base64 encoded representation of a binary file
#------------------------------------------------------------------------------

if [ $# == 1 ]; then
    # see https://www.mytecbits.com/apple/macos/image-to-base64
    base64 -i $1 -o $1-encoded

    # this is an alternate implementation that works 80% of the time
    # openssl base64 -in $1 -out $1-encoded
    exit 0
fi

if [ $# == 2 ]; then
    openssl base64 -in $1 -out $2
else
    echo "base64encode.sh"
    echo "Usage: ./base64encode.sh <infile> <outfile>"
    exit 1
fi
