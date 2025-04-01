import sys
import os
import errno
import math
from build123d import *

# Control globals
SCALING_FACTOR = 1.005
SPACE_CHARACTER = "\u2800"
PAPER_W, PAPER_H, PAPER_D = 216, 280, 0.2
CELL_W, CELL_H = 6, 10
CELL_PADDING_X, CELL_PADDING_Y = 1.75, 2.5
MAX_CELL_X_COUNT = math.floor(PAPER_W / CELL_W)
CELL_X_COUNT = MAX_CELL_X_COUNT - 4
MAX_CELL_Y_COUNT = math.floor(PAPER_H / CELL_H)
CELL_Y_COUNT = MAX_CELL_Y_COUNT - 2
CELL_SPACING = 2.5
POSITIVE_MOLD_FILE_PATH = "/data/positive_mold.stl"
NEGATIVE_MOLD_FILE_PATH = "/data/negative_mold.stl"

def export_shape(shape, file_path):
    """Exports a shape to an STL file."""
    exporter = Mesher()
    exporter.add_shape(scale(shape, SCALING_FACTOR))
    exporter.write(file_path)

def generate_braille_molds(braille_file_path):
    """Generates positive and negative molds for Braille text."""
    if not os.path.isfile(braille_file_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), braille_file_path)

    with open(braille_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Create base molds
    positive_mold = Box(220, 280, 0.6)
    negative_mold = Box(220, 280, 1).translate((0, 0, 1.2))

    # Define tools
    slot_tool = Box(4, 10, 4)
    pin_tool = Box(1.9, 9.9, 1.8)
    dot_tool = Sphere(0.75).translate((0, 0, 0.6))
    hole_tool = Cylinder(0.95, 1.6).translate((0, 0, 1.2))

    # Precompute pin and slot placements
    pin_x_positions = [-109, 109]
    slot_x_positions = [-110, 110]

    # Add pin and slot tools
    for line_index in range(CELL_Y_COUNT + 1):
        y = (CELL_Y_COUNT - line_index) * CELL_H
        if line_index % 2 == 0:
            print(f"Adding slots at line {line_index}", end="\r")
            for px in pin_x_positions:
                positive_mold += pin_tool.translate((px, y, 0))
            for sx in slot_x_positions:
                negative_mold -= slot_tool.translate((sx, y, 0))

    print(f"Processing {CELL_Y_COUNT} lines")

    # Process Braille characters
    for line_index, line in enumerate(lines[:CELL_Y_COUNT + 1]):  # Avoid reading extra lines
        print(f"Processing line {line_index}", end="\r")

        x_offset = -98 + CELL_PADDING_X
        y_offset = (26 - line_index) * 10 + CELL_PADDING_Y
        text = line.rstrip()

        for character_index, character in enumerate(text):
            print(f"Processing character {character_index}", end="\r")
            delta = ord(character) - ord(SPACE_CHARACTER)
            binary = f"{delta:06b}"[::-1]

            for i, (dx, dy) in enumerate([(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)]):
                if binary[i] == "1":
                    tx, ty = x_offset + dx * CELL_SPACING, y_offset + dy * CELL_SPACING
                    positive_mold += dot_tool.translate((tx, ty, 0))
                    negative_mold -= hole_tool.translate((tx, ty, 0))

            x_offset += CELL_W

    negative_mold = negative_mold.rotate(Axis.Y, 180)

    # Export molds
    export_shape(positive_mold, POSITIVE_MOLD_FILE_PATH)
    export_shape(negative_mold, NEGATIVE_MOLD_FILE_PATH)

if __name__ == "__main__":
    braille_file_path = str(sys.argv[-1])
    print(f"Processing: {braille_file_path}")
    generate_braille_molds(braille_file_path)
