#!/bin/bash

echo build folder: $BUILD_FOLDER
echo archive file: $BUILD_FOLDER/$ARCHIVE_FILE
echo file to add: $FILE_TO_ADD

# Check if the ZIP file exists
if [ -f "$BUILD_FOLDER/$ARCHIVE_FILE" ]; then
    mkdir -p $BUILD_FOLDER/$ARCHIVE_FOLDER/
    cp "$FILE_TO_ADD" $BUILD_FOLDER/$ARCHIVE_FOLDER/
    cd $BUILD_FOLDER
    zip "$ARCHIVE_FILE" ./$ARCHIVE_FOLDER/$FILE_TO_ADD
    unzip -l "$ARCHIVE_FILE"
else
    echo "The archive file $ARCHIVE_FILE does not exist."
fi
