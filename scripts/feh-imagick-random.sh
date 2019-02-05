#!/bin/bash
#
# Redwall
#
# Example Bash script that:
# - looks for JPEG images in a directory (and its subdirectories)
# - filters results to only keep images at least as big as a given resolution
# - chooses a random image
# - detects the dominant color from this image
# - sets the image as a wallpaper using feh
#
# Literature:
# - https://wiki.archlinux.org/index.php/Feh
# - https://wiki.archlinux.org/index.php/Systemd/Timers
# - https://stackoverflow.com/questions/4670013/fast-way-to-get-image-dimensions-not-filesize
# - https://stackoverflow.com/questions/35623462/bash-select-random-string-from-list
# - https://superuser.com/questions/576949/getting-the-predominant-colour-in-an-image
# - https://stackoverflow.com/questions/47983587/how-can-imagemagick-output-hex-colours-instead-of-srgb
# - https://stackoverflow.com/questions/47982983/how-to-get-a-hex-color-code-from-a-solid-color-image-for-a-script
# - https://stackoverflow.com/questions/48300657/get-only-hex-values-from-imagemagick
# - https://www.endpoint.com/blog/2011/04/21/determining-dominant-image-color
SCREEN_WIDTH=2560
SCREEN_HEIGHT=1440

# fill | max | scale
FEH_BG_MODE="fill"

IMAGE_ROOT="${1}"

echo "Looking for JPEG images under ${IMAGE_ROOT}"
index=0
for img in $(find ${IMAGE_ROOT} -name "*.jpg")
do
    read width height < <(identify -ping -format "%w %h" "${img}")

    if (( width < SCREEN_WIDTH || height < SCREEN_HEIGHT ))
    then
        continue
    fi

    candidates[${index}]="${img}"
    ((index++))
done

cpt=${#candidates[@]}
echo "Found ${cpt} suitable images"
index=$(($RANDOM % $cpt))
wallpaper=${candidates[$index]}

echo "Setting ${wallpaper} as the new wallpaper"
background=$(convert ${wallpaper} -scale 1x1\! -format '%[hex:u]' info:-)
feh --bg-${FEH_BG_MODE} --image-bg "#${background}" "${wallpaper}"
