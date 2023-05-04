# blender --background --python 12_cloth.py --render-anim -- </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import os

print(sys.version_info)


working_dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir_path)

import utils

# Define paths for the PBR textures used in this scene
texture_paths = {
    "Fabric02": {
        "ambient_occlusion": "",
        "color": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric02/fabric02_col.jpg"),
        "displacement": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric02/fabric02_disp.jpg"),
        "metallic": "",
        "normal": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric02/fabric02_nrm.jpg"),
        "roughness": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric02/fabric02_rgh.jpg"),
    },
    "Fabric03": {
        "ambient_occlusion": "",
        "color": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric03/Fabric03_col.jpg"),
        "displacement": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric03/Fabric03_disp.jpg"),
        "metallic": "",
        "normal": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric03/Fabric03_nrm.jpg"),
        "roughness": os.path.join(working_dir_path, "assets/cc0textures.com/[2K]Fabric03/Fabric03_rgh.jpg"),
    },
}


def add_named_material(name: str, scale=(1.0, 1.0, 1.0), displacement_scale: float = 1.0) -> bpy.types.Material:
    mat = utils.add_material(name, use_nodes=True, make_node_tree_empty=True)
    utils.build_pbr_textured_nodes(mat.node_tree,
                                   color_texture_path=texture_paths[name]["color"],
                                   roughness_texture_path=texture_paths[name]["roughness"],
                                   normal_texture_path=texture_paths[name]["normal"],
                                   metallic_texture_path=texture_paths[name]["metallic"],
                                   displacement_texture_path=texture_paths[name]["displacement"],
                                   ambient_occlusion_texture_path=texture_paths[name]["ambient_occlusion"],
                                   scale=scale,
                                   displacement_scale=displacement_scale)
    return mat


def set_floor_and_lights() -> None:
    size = 200.0
    current_object = utils.create_plane(size=size, name="Floor")
    floor_mat = utils.add_material("Material_Plane", use_nodes=True, make_node_tree_empty=True)
    utils.build_checker_board_nodes(floor_mat.node_tree, size)
    current_object.data.materials.append(floor_mat)

    utils.create_area_light(location=(6.0, 0.0, 4.0),
                            rotation=(0.0, math.pi * 60.0 / 180.0, 0.0),
                            size=5.0,
                            color=(1.00, 0.70, 0.60, 1.00),
                            strength=1500.0,
                            name="Main Light")
    utils.create_area_light(location=(-6.0, 0.0, 2.0),
                            rotation=(0.0, -math.pi * 80.0 / 180.0, 0.0),
                            size=5.0,
                            color=(0.30, 0.42, 1.00, 1.00),
                            strength=1000.0,
                            name="Sub Light")


def set_scene_objects() -> bpy.types.Object:
    add_named_material("Fabric02")
    add_named_material("Fabric03")
    bpy.data.materials["Fabric02"].node_tree.nodes["Principled BSDF"].inputs["Sheen"].default_value = 4.0
    bpy.data.materials["Fabric03"].node_tree.nodes["Principled BSDF"].inputs["Sheen"].default_value = 4.0

    set_floor_and_lights()

    current_object = utils.create_smooth_monkey(location=(0.0, 0.0, 1.0))
    current_object.data.materials.append(bpy.data.materials["Fabric03"])
    bpy.ops.object.modifier_add(type='COLLISION')

    if bpy.app.version >= (2, 80, 0):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=75, y_subdivisions=75, size=3.0, location=(0.0, 0.0, 2.75))
    else:
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=75,
                                        y_subdivisions=75,
                                        radius=1.5,
                                        calc_uvs=True,
                                        location=(0.0, 0.0, 2.75))
    cloth_object = bpy.context.object
    cloth_object.name = "Cloth"
    bpy.ops.object.modifier_add(type='CLOTH')
    cloth_object.modifiers["Cloth"].collision_settings.use_collision = True
    cloth_object.modifiers["Cloth"].collision_settings.use_self_collision = True
    cloth_object.modifiers["Cloth"].settings.quality = 10
    utils.set_smooth_shading(cloth_object.data)
    utils.add_subdivision_surface_modifier(cloth_object, 2)
    cloth_object.data.materials.append(bpy.data.materials["Fabric02"])

    bpy.ops.object.empty_add(location=(0.0, -0.75, 1.05))
    focus_target = bpy.context.object
    return focus_target


def create_armature_from_bvh(bvh_path: str) -> bpy.types.Object:
    global_scale = 0.056444  # This value needs to be changed depending on the motion data

    bpy.ops.import_anim.bvh(filepath=bvh_path,
                            axis_forward='-Z',
                            axis_up='Y',
                            target='ARMATURE',
                            global_scale=global_scale,
                            frame_start=1,
                            use_fps_scale=True,
                            update_scene_fps=False,
                            update_scene_duration=True)
    armature = bpy.context.object
    return armature


def build_scene(scene: bpy.types.Scene, input_bvh_path: str) -> bpy.types.Object:

    # Build a concrete material for the floor and the wall
    add_named_material("Concrete07", scale=(0.25, 0.25, 0.25))

    # Build a metal material for the humanoid body
    mat = utils.add_material("BlueMetal", use_nodes=True, make_node_tree_empty=True)
    output_node = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.inputs['Base Color'].default_value = (0.1, 0.2, 0.7, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.9
    principled_node.inputs['Roughness'].default_value = 0.1
    mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    utils.arrange_nodes(mat.node_tree)

    # Import the motion file and create a humanoid object
    armature = create_armature_from_bvh(bvh_path=input_bvh_path)
    armature_mesh = utils.create_armature_mesh(scene, armature, 'Mesh')
    armature_mesh.data.materials.append(mat)

    # Create a floor object
    current_object = utils.create_plane(size=16.0, name="Floor")
    current_object.data.materials.append(bpy.data.materials["Concrete07"])

    # Create a wall object
    current_object = utils.create_plane(size=16.0, name="Wall")
    current_object.data.materials.append(bpy.data.materials["Concrete07"])
    current_object.location = (0.0, 6.0, 0.0)
    current_object.rotation_euler = (0.5 * math.pi, 0.0, 0.0)

    # Create a target object for camera work
    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.8))
    focus_target = bpy.context.object
    utils.add_copy_location_constraint(copy_to_object=focus_target,
                                       copy_from_object=armature,
                                       use_x=True,
                                       use_y=True,
                                       use_z=False,
                                       bone_name='Hips')

    return focus_target


# Args
output_file_path = bpy.path.relpath(str(sys.argv[sys.argv.index('--') + 1]))
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

## Animation
utils.set_animation(scene, fps=24, frame_start=1, frame_end=48)

## Object

input_bvh_path = "./assets/motion/102_01.bvh"
focus_target_object = build_scene(scene, input_bvh_path)
focus_target_object = set_scene_objects()
## Camera
camera_object = utils.create_camera(location=(0.0, -12.5, 2.2))

utils.add_track_to_constraint(camera_object, focus_target_object)
utils.set_camera_params(camera_object.data, focus_target_object)

## Background
utils.build_rgb_background(world, rgb=(0.0, 0.0, 0.0, 1.0))

## Composition
utils.build_scene_composition(scene, dispersion=0.0)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples, use_motion_blur=True)
