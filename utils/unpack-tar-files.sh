SOURCE_TAR="./app/new_recordings.tar"
DEST_DIR="./"

if [ ! -d "$DEST_DIR" ]; then
    echo "Directory not found"
    exit 1
fi

# Extract the main tar file
echo "Extracting $SOURCE_TAR..."
tar -xf "$SOURCE_TAR" -C .

# Find all .tar files extracted and extract recordings from each into the destination directory
for inner_tar in ./*.tar; do
    echo "Extracting $inner_tar into $DEST_DIR..."
    tar -xf "$inner_tar" -C "$DEST_DIR"
    rm "$inner_tar"  # Remove the inner tar after extraction
done

echo "All recordings extracted to $DEST_DIR."