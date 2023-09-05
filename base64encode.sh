


# echo $0 was called with $# arguments.
if [ $# == 2 ]; then
    openssl base64 -in $1 -out $2
else
    echo "base64encode.sh"
    echo "Usage: ./base64encode.sh <infile> <outfile>"
    exit 1
fi
