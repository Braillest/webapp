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
max_cell_x_count = math.floor(paper_w / cell_w)
cell_x_count = max_cell_x_count - 3 - 1
max_cell_y_count = math.floor(paper_h / cell_h)
cell_y_count = max_cell_y_count - 2
cell_spacing = 2.5
positive_mold_file_path = "/data/positive_mold.stl"
negative_mold_file_path = "/data/negative_mold.stl"


def generate_braille_molds(braille_file_path):
    if not os.path.isfile(braille_file_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), braille_file_path)

    with open(braille_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    positive_mold = Box(220, 280, 0.8).translate((110, 140, 0.4))
    negative_mold = Box(220, 280, 1).translate((110, 140, 0.5))

    slot_tool = Box(4, 10, 4).translate((2, 5, 0))
    pin_tool = Box(1.9, 9.9, 1.8).translate((1.9/2, 9.9/2, 1.8/2))
    # dot_tool = Sphere(radius=0.75, arc_size1=0, arc_size2=90).translate((0, 0, 0.8))
    dot_tool = Cylinder(0.75, 0.6).translate((0, 0, 0.8))
    hole_tool = Cylinder(0.95, 1.6)

    union_objects = []
    difference_objects = []

    print("generating geometry")
    start = time.time()

    for line_index in range(cell_y_count + 1):
        y = (cell_y_count - line_index) * cell_h
        if line_index % 2 == 0:
            union_objects.append(pin_tool.translate((0, y + 0.05, 0)))
            union_objects.append(pin_tool.translate((220 - 1.9, y + 0.05, 0)))
            difference_objects.append(slot_tool.translate((-2, y, 0)))
            difference_objects.append(slot_tool.translate((218, y, 0)))

    x_offset = 0
    y_offset = 0

    for line_index, line in enumerate(lines[0:cell_y_count]):
        x_offset = 2 + (3 * cell_w) + cell_padding_x
        y_offset = (cell_y_count - line_index) * cell_h + cell_padding_y
        text = line.rstrip()

        for character in text:
            delta = ord(character) - ord(space_character)
            binary = f"{delta:06b}"[::-1]

            for i, (dx, dy) in enumerate([(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)]):
                if binary[i] == "1":
                    union_objects.append(dot_tool.translate((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, 0)))
                    difference_objects.append(hole_tool.translate((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, 0)))
            x_offset += cell_w

    print(time.time() - start)

    print("making positive mold")
    start = time.time()
    positive = positive_mold + union_objects
    print(time.time() - start)

    print("making negative mold")
    start = time.time()
    negative = negative_mold - difference_objects
    negative = negative.rotate(Axis.Y, 180)
    print(time.time() - start)

    print("exporting positive mold")
    start = time.time()
    export_stl(positive, positive_mold_file_path, tolerance = 0.1, angular_tolerance = 1)
    print(time.time() - start)

    print("exporting negative mold")
    start = time.time()
    export_stl(negative, negative_mold_file_path, tolerance = 0.1, angular_tolerance = 1)
    print(time.time() - start)

if __name__ == "__main__":
    braille_file_path = str(sys.argv[-1])
    print(f"Processing: {braille_file_path}")
    generate_braille_molds(braille_file_path)
