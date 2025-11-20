#!/usr/bin/env bash

# Compile and upload MicroPython projects to a pi pico


# Settings
PORT = "/dev/tty/ACM0"		# Serial port of the pico
SRC_DIR = "src"			# Directory of the .py files
BUILD_DIR = "build"		# Build folder for mpy compilation
USE_MPY = true			# Set to true when compiling

# Colors for output
GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m"


# Make build directory
mkdir -p "$BUILD_DIR"

echo -e "${GREEN}Deploying to pico on $PORT${NC}"

if [ "$USE_MPY" = true ]; then
	echo -e "${GREEN}Compiling .py -> .mpy${NC}"

	for src in "$SRC_DIR"/*.py; do
		fname = $(basename "$src")
		out = "$BUILD_DIR/${fname%.py}.mpy"
		echo "Compiling $fname -> $(basename "$out")"
		mpy-cross "$src" -o "$out"
	done
	echo -e "${GREEN}Compilation done.${NC}"
else
	echo -e "${GREEN}Skipping compilation; uploading .py files directly.${NC}"
fi

echo -e "${GREEN}Uploading to pico...${NC}"
if [  "$USE_MPY" = true ]; then
	mpremote --port "$PORT" cp "$BUILD_DIR"/* :
else
	mpremote --port "$PORT" vp "$SRC_DIR"/*.py :
fi

if [ $? -eq 0]; then
	echo -e "${GREEN}Upload succeeded!${NC}"
else
	echo -e "${RED}Upload failed. Please check the port and connection.${NC}"
	exit 1
fi

echo -e "${GREEN}Running main.py on pico...${NC}"
mpremote --port "$PORT" run main.py

echo -e "${GREEN}Opening REPL (press Ctrl-D to soft-reset)...${NC}"
mpremote --port "$PORT" repl
