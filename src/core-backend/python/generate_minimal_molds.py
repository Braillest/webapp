import sys
import bpy
import math
import os
import errno

# Control globals
scaling_factor = 1.005
space_character = "⠀"
paper_w = 216
paper_h = 280
paper_d = 0.2
# MAX : 36 x 28
# PAD : (3 + [32] + 1) x (1 + [26] + 1)
# USE : 32 x 26
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

class BlenderObject:

    def __init__(self, name, type="Cube"):

        self.name = name
        self.type = type
        self.material = None
        self.vertices = None
        self.loops = None
        self.faces = None
        self.x = 0
        self.y = 0
        self.z = 0
        self.location = (0, 0, 0)
        self.w = 1
        self.h = 1
        self.d = 1
        self.scale = (1, 1, 1)
        self.mesh = None
        self.obj = None

        # UV sphere mesh specific
        self.segments = None
        self.ring_count = None

    def set_location(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.calculate_location()

    def calculate_location(self):
        self.location = (self.x, self.y, self.z)
        if self.obj is not None:
            self.obj.location = self.location

    def set_scale(self, w, h, d):
        self.w = w
        self.h = h
        self.d = d
        self.calculate_scale()

    def calculate_scale(self):
        self.scale = (self.w / 2, self.h / 2, self.d / 2)
        if self.obj is not None:
            self.obj.scale = self.scale

    # Places the lower bottom left bounding box corner of an object on the origin
    def origin_align(self):
        self.x = self.w / 2
        self.y = self.h / 2
        self.z = self.d / 2
        self.calculate_location()

    def add_copy_to_collection(self, collection):
        collection.objects.link(self.obj.copy())

    def generate_mesh(self):

        if self.type == "Cube":
            self.mesh = bpy.ops.mesh.primitive_cube_add(location=self.location, scale=self.scale)
        elif self.type == "UVSphere":
            self.mesh = bpy.ops.mesh.primitive_uv_sphere_add(location=self.location, scale=self.scale, segments=self.segments, ring_count=self.ring_count)
        elif self.type == "Cylinder":
            self.mesh = bpy.ops.mesh.primitive_cylinder_add(location=self.location, scale=self.scale)

        self.obj = bpy.context.object
        self.obj.name = self.name
        self.obj.data.name = f"{self.name} Mesh"

class BrailleToMolds:

    def __init__(self, braille_file_path):

        self.clear_scene()

        # ==================== #
        # CREATING COLLECTIONS #
        # ==================== #

        union_collection = bpy.data.collections.new("Union Collection")
        bpy.context.scene.collection.children.link(union_collection)
        difference_collection = bpy.data.collections.new("Difference Collection")
        bpy.context.scene.collection.children.link(difference_collection)

        # ============== #
        # CREATING TOOLS #
        # ============== #

        # A tool to cut slots in the Y edges of the negative mold
        # - Oversized on x and z axis for FAST solver
        slot_tool = BlenderObject("Slot Tool", "Cube")
        slot_tool.set_scale(4, 10, 4)
        slot_tool.origin_align()
        slot_tool.generate_mesh()

        # A tool to add pins to the Y edges of the positive mold
        # - Oversized on the z axis for FAST solver
        # - Positioned to be 0.1 mm from the bottom face of the positive mold
        pin_tool = BlenderObject("Pin Tool", "Cube")
        pin_tool.set_scale(1.9, 9.9, 1.8)
        pin_tool.origin_align()
        # pin_tool.z += 0.1
        # pin_tool.calculate_location()
        pin_tool.generate_mesh()

        # A tool to add dots to the positive mold
        # - TODO: Slice off button of uvsphere? Possibly sticking through bottom of positive mold
        # - Positioned to create 0.6 mm dome on top face of positive mold
        dot_tool = BlenderObject("Dot Tool", "UVSphere")
        dot_tool.set_location(0, 0, 0.6)
        dot_tool.set_scale(1.5, 1.5, 1.2)
        dot_tool.segments = 12
        dot_tool.ring_count = 6
        dot_tool.generate_mesh()

        # A tool to cut holes in the negative mold
        # - Oversized on the z axis for FAST solver
        # - Positioned to cut a 0.8 mm hole in the negative mold
        hole_tool = BlenderObject("Hole Tool", "Cylinder")
        hole_tool.set_location(0, 0, 1.2)
        hole_tool.set_scale(1.9, 1.9, 1.6)
        hole_tool.generate_mesh()

        # ================ #
        # CREATING OBJECTS #
        # ================ #

        # Positive mold
        positive_mold = BlenderObject("Positive Mold", "Cube")
        positive_mold.set_scale(2 + 216 + 2, 280, 0.6)
        positive_mold.origin_align()
        positive_mold.generate_mesh()

        # Negative mold
        negative_mold = BlenderObject("Negative Mold", "Cube")
        negative_mold.set_scale(2 + 216 + 2, 280, 1)
        negative_mold.origin_align()
        negative_mold.z += 1.2
        negative_mold.calculate_location()
        negative_mold.generate_mesh()

        # ========================= #
        # ADDING ALIGNMENT GEOMETRY #
        # ========================= #

        for line_index in range(cell_y_count + 1):

            # SW corner
            y = (cell_y_count - line_index) * cell_h

            if line_index % 2 == 0:
                pin_tool.x = (1.9 / 2)
                pin_tool.y = y + 0.05 + (9.9 / 2)
                pin_tool.calculate_location()
                pin_tool.add_copy_to_collection(union_collection)
                pin_tool.x = 2 + 216 + 0.1 + (1.9 / 2)
                pin_tool.calculate_location()
                pin_tool.add_copy_to_collection(union_collection)
                slot_tool.x = 0
                slot_tool.y = y + 5
                slot_tool.calculate_location()
                slot_tool.add_copy_to_collection(difference_collection)
                slot_tool.x = 2 + 216 + 2
                slot_tool.calculate_location()
                slot_tool.add_copy_to_collection(difference_collection)

        # ==================================== #
        # RENDER BRAILLE TEXT TO MESH GEOMETRY #
        # ==================================== #

        # Where file_path is 32x26 braille
        if not os.path.isfile(braille_file_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), braille_file_path)

        # Read complete file into memory
        with open(braille_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Iterate over each line
        for line_index, line in enumerate(lines):

            # SW corner
            x_offset = 2 + (6 * 3) + cell_padding_x
            y_offset = (26 - line_index) * 10 + cell_padding_y
            text = line.rstrip()

            for character_index, character in enumerate(text):

                # Novelty is often beautiful
                delta = ord(character) - ord(space_character)
                binary = f"{delta:06b}"[::-1]

                if binary[0] == "1":
                    dot_tool.x = x_offset
                    dot_tool.y = y_offset + (cell_spacing * 2)
                    dot_tool.calculate_location()
                    dot_tool.add_copy_to_collection(union_collection)
                    hole_tool.x = x_offset
                    hole_tool.y = y_offset + (cell_spacing * 2)
                    hole_tool.calculate_location()
                    hole_tool.add_copy_to_collection(difference_collection)

                if binary[1] == "1":
                    dot_tool.x = x_offset
                    dot_tool.y = y_offset + cell_spacing
                    dot_tool.calculate_location()
                    dot_tool.add_copy_to_collection(union_collection)
                    hole_tool.x = x_offset
                    hole_tool.y = y_offset + cell_spacing
                    hole_tool.calculate_location()
                    hole_tool.add_copy_to_collection(difference_collection)

                if binary[2] == "1":
                    dot_tool.x = x_offset
                    dot_tool.y = y_offset
                    dot_tool.calculate_location()
                    dot_tool.add_copy_to_collection(union_collection)
                    hole_tool.x = x_offset
                    hole_tool.y = y_offset
                    hole_tool.calculate_location()
                    hole_tool.add_copy_to_collection(difference_collection)

                if binary[3] == "1":
                    dot_tool.x = x_offset + cell_spacing
                    dot_tool.y = y_offset
                    dot_tool.calculate_location()
                    dot_tool.add_copy_to_collection(union_collection)
                    hole_tool.x = x_offset + cell_spacing
                    hole_tool.y = y_offset
                    hole_tool.calculate_location()
                    hole_tool.add_copy_to_collection(difference_collection)

                if binary[4] == "1":
                    dot_tool.x = x_offset + cell_spacing
                    dot_tool.y = y_offset + cell_spacing
                    dot_tool.calculate_location()
                    dot_tool.add_copy_to_collection(union_collection)
                    hole_tool.x = x_offset + cell_spacing
                    hole_tool.y = y_offset + cell_spacing
                    hole_tool.calculate_location()
                    hole_tool.add_copy_to_collection(difference_collection)

                if binary[5] == "1":
                    dot_tool.x = x_offset + cell_spacing
                    dot_tool.y = y_offset + (cell_spacing * 2)
                    dot_tool.calculate_location()
                    dot_tool.add_copy_to_collection(union_collection)
                    hole_tool.x = x_offset + cell_spacing
                    hole_tool.y = y_offset + (cell_spacing * 2)
                    hole_tool.calculate_location()
                    hole_tool.add_copy_to_collection(difference_collection)

                x_offset += 6

        # Difference
        difference_mod = negative_mold.obj.modifiers.new("Difference Collection", type="BOOLEAN")
        difference_mod.operation = "DIFFERENCE"
        difference_mod.solver = "EXACT"
        difference_mod.operand_type = "COLLECTION"
        difference_mod.collection = difference_collection
        bpy.ops.object.modifier_apply(modifier=difference_mod.name)
        # for object in list(difference_collection.objects):
        #     bpy.data.objects.remove(object, do_unlink=True)
        # bpy.data.collections.remove(difference_collection)

        # Flip the negative mold over prior to STL export for ease of printing
        negative_mold.obj.rotation_euler.y += math.radians(180)

        # Export negative mold
        bpy.context.view_layer.objects.active = negative_mold.obj
        negative_mold.obj.select_set(True)
        bpy.ops.wm.stl_export(filepath=negative_mold_file_path, export_selected_objects=True, global_scale=scaling_factor)
        negative_mold.obj.select_set(False)

        # Union
        union_mod = positive_mold.obj.modifiers.new("Union Collection", type="BOOLEAN")
        union_mod.operation = "UNION"
        union_mod.solver = "EXACT"
        union_mod.operand_type = "COLLECTION"
        union_mod.collection = union_collection
        bpy.ops.object.modifier_apply(modifier=union_mod.name)
        # for object in list(union_collection.objects):
        #     bpy.data.objects.remove(object, do_unlink=True)
        # bpy.data.collections.remove(union_collection)

        # Export positive mold
        bpy.context.view_layer.objects.active = positive_mold.obj
        positive_mold.obj.select_set(True)
        bpy.ops.wm.stl_export(filepath=positive_mold_file_path, export_selected_objects=True, global_scale=scaling_factor)
        positive_mold.obj.select_set(False)

    # Removes all objects from a scene
    def clear_scene(self):

        if len(bpy.data.objects) > 0:
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.object.delete()

if __name__ == "__main__":
    braille_file_path = str(sys.argv[-1])
    print(braille_file_path)
    BrailleToMolds(braille_file_path)
