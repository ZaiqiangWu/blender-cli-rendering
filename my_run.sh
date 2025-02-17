#!/bin/bash

OUT_DIR="./out"

RESOLUTION=100
SAMPLINGS=128
ANIM_FRAMES_OPTION="--render-anim"

# Make this "true" when testing the scripts
TEST=true
if ${TEST}; then
  RESOLUTION=30
  SAMPLINGS=16
  ANIM_FRAMES_OPTION="--render-anim" #"--render-frame 1..5"
fi

# Create the output directory
mkdir -p ${OUT_DIR}

# Run the scripts

#blender --background -noaudio --python ./10_mocap.py ${ANIM_FRAMES_OPTION} -- ./assets/motion/102_01.bvh ${OUT_DIR}/10/frame_ ${RESOLUTION} ${SAMPLINGS}
blender --background -noaudio --python ./15_smpl_cloth.py ${ANIM_FRAMES_OPTION} -- ${OUT_DIR}/15/frame_ ${RESOLUTION} ${SAMPLINGS}


# Perform ffmpeg for animations

#ffmpeg -y -r 24 -i ${OUT_DIR}/10/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/10_mocap.mp4
ffmpeg -y -r 24 -i ${OUT_DIR}/15/frame_%04d.png -pix_fmt yuv420p ${OUT_DIR}/15_smpl_cloth.mp4
