#!/usr/bin/bash
# give std permissions to subdirs and  files in current dir
echo "changing permissions in $(pwd)"
find "$(pwd)"/ -type d -exec chmod 755 {} \;
find "$(pwd)"/ -type f -exec chmod 644 {} \;
echo "permissions standardized"
