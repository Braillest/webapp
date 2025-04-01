import sys
import os
import errno
import math
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

    positive_mold = Box(220, 280, 0.6)
    negative_mold = Box(220, 280, 1).translate((0, 0, 1.2))

    slot_tool = Box(4, 10, 4)
    pin_tool = Box(1.9, 9.9, 1.8)
    dot_tool = Sphere(0.75).translate((0, 0, 0.6))
    hole_tool = Cylinder(0.95, 1.6).translate((0, 0, 1.2))

    for line_index in range(cell_y_count + 1):
        y = (cell_y_count - line_index) * cell_h
        if line_index % 2 == 0:
            print(f"slot {line_index}", end="\r")
            positive_mold += pin_tool.translate((-109, y, 0))
            positive_mold += pin_tool.translate((109, y, 0))
            negative_mold -= slot_tool.translate((-110, y, 0))
            negative_mold -= slot_tool.translate((110, y, 0))

    print(cell_y_count)

    for line_index in range(cell_y_count + 1):
        line = lines[line_index]

        print(line)
        print(f"line {line_index}", end="\r")

        x_offset = -98 + cell_padding_x
        y_offset = (26 - line_index) * 10 + cell_padding_y
        text = line.rstrip()

        for character_index, character in enumerate(text):

            print(f"character {character_index}", end="\r")
            delta = ord(character) - ord(space_character)
            binary = f"{delta:06b}"[::-1]

            for i, (dx, dy) in enumerate([(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)]):
                if binary[i] == "1":
                    positive_mold += dot_tool.translate((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, 0))
                    negative_mold -= hole_tool.translate((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, 0))
            x_offset += 6

    negative_mold = negative_mold.rotate(Axis.Y, 180)

    exporter = Mesher()
    exporter.add_shape(scale(negative_mold, scaling_factor))
    exporter.write(negative_mold_file_path)

    exporter = Mesher()
    exporter.add_shape(scale(positive_mold, scaling_factor))
    exporter.write(positive_mold_file_path)

if __name__ == "__main__":
    braille_file_path = str(sys.argv[-1])
    print(f"Processing: {braille_file_path}")
    generate_braille_molds(braille_file_path)
