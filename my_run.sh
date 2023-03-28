#!/bin/bash

OUT_DIR="./out"

RESOLUTION=100
SAMPLINGS=128
ANIM_FRAMES_OPTION="--render-anim"

# Make this "true" when testing the scripts
TEST=false
if ${TEST}; then
  RESOLUTION=10
  SAMPLINGS=16
  ANIM_FRAMES_OPTION="--render-frame 1..5"
fi

# Create the output directory
mkdir -p ${OUT_DIR}

# Run the scripts
blender --background -noaudio --python ./01_cube.py --render-frame 1 -- ${OUT_DIR}/01_cube_ ${RESOLUTION} ${SAMPLINGS}
#blender --background -noaudio --python ./10_mocap.py ${ANIM_FRAMES_OPTION} -- ./assets/motion/102_01.bvh ${OUT_DIR}/10/frame_ ${RESOLUTION} ${SAMPLINGS}
#blender --background -noaudio --python ./12_cloth.py ${ANIM_FRAMES_OPTION} -- ${OUT_DIR}/12/frame_ ${RESOLUTION} ${SAMPLINGS}


# Perform ffmpeg for animations

#ffmpeg -y -r 24 -i ${OUT_DIR}/10/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/10_mocap.mp4
#ffmpeg -y -r 24 -i ${OUT_DIR}/12/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/12_cloth.mp4
