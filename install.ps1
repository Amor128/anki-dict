$source = "src/anki_dict"
$destination = "C:\Users\yangs\scoop\persist\anki\data\addons21"

# Create destination directory if it doesn't exist
if (-Not (Test-Path -Path $destination)) {
    New-Item -ItemType Directory -Path $destination
}

# Copy the directory
Copy-Item -Path $source -Destination $destination -Recurse -Force