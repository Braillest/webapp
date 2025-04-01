import sys
import os
import errno
import math
import time
from build123d import *

# Control globals
scaling_factor = 1.005
space_character = "\u2800"

paper_w = 216
paper_h = 280
paper_d = 0.2

cell_w = 6
cell_h = 10
cell_padding_x = 1.75
cell_padding_y = 2.5
cell_spacing = 2.5

pin_w = 1.9
pin_h = 9.9
pin_d = 1.8

slot_w = 4
slot_h = 10
slot_d = 4

dot_r = 0.75
dot_d = 0.6

hole_r = 0.95 
hole_d = 1.6

positive_mold_w = paper_w + (2 * slot_w)
positive_mold_h = paper_h
positive_mold_d = 0.8

negative_mold_w = positive_mold_w
negative_mold_h = paper_h
negative_mold_d = 1

max_cell_x_count = math.floor(paper_w / cell_w)
cell_x_count = max_cell_x_count - 3 - 1

max_cell_y_count = math.floor(paper_h / cell_h)
cell_y_count = max_cell_y_count - 2

positive_mold_file_path = "/data/positive_mold.stl"
negative_mold_file_path = "/data/negative_mold.stl"

def generate_braille_molds(braille_file_path):

    if not os.path.isfile(braille_file_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), braille_file_path)

    with open(braille_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Generate pin and slot locations
    pin_coords = []
    slot_coords = []
    for line_index in range(cell_y_count + 1):
        y = (cell_y_count - line_index) * cell_h
        if line_index % 2 == 0:
            pin_coords.append((pin_w/2, y + pin_h/2, pin_d/2))
            pin_coords.append((positive_mold_w - pin_w/2, y + pin_h/2, pin_d/2))
            slot_coords.append((-2, y, 0))
            slot_coords.append((218, y, 0))

    # Generate dot and hole locations
    dot_coords = []
    hole_coords = []
    for line_index, line in enumerate(lines[0:cell_y_count]):
        x_offset = slot_w + (3 * cell_w) + cell_padding_x
        y_offset = (cell_y_count - line_index) * cell_h + cell_padding_y
        text = line.rstrip()

        for character in text:
            delta = ord(character) - ord(space_character)
            binary = f"{delta:06b}"[::-1]

            for i, (dx, dy) in enumerate([(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]):
                if binary[i] == "1":
                    dot_coords.append((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, positive_mold_d))
                    hole_coords.append((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, 0.2))
            x_offset += cell_w

    with BuildPart() as positive_mold:

        # Bottom SW corner on 0,0
        Box(positive_mold_w, positive_mold_h, positive_mold_d).translate((positive_mold_w/2, positive_mold_h/2, positive_mold_d/2))

        # Add pins
        with Locations(pin_coords):
            Box(pin_w, pin_h, pin_d, mode=Mode.ADD)

        # Add dots
        with Locations(dot_coords):
            Cylinder(dot_r, dot_d)

        export_stl(positive_mold.part, positive_mold_file_path)

    with BuildPart() as negative_mold:

        # Bottom SW corner on 0,0
        Box(negative_mold_w, negative_mold_h, negative_mold_d).translate((negative_mold_w/2, negative_mold_h/2, negative_mold_d/2))

        # Subtract slots
        with Locations(slot_coords):
            Box(slot_w, slot_h, slot_d, mode=Mode.SUBTRACT)

        # Subtract holes
        with Locations(hole_coords):
            Hole(hole_r, hole_d, mode=Mode.SUBTRACT)

        export_stl(negative_mold.part, negative_mold_file_path)

if __name__ == "__main__":
    braille_file_path = str(sys.argv[-1])
    print(f"Processing: {braille_file_path}")
    generate_braille_molds(braille_file_path)
