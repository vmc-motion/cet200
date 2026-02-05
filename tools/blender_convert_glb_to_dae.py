# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# blender --background --python blender_glb_to_dae.py
import bpy
import os
from pathlib import Path


def convert_glb_to_glb(input_filepath, output_filepath):
    print("===")
    print(f"Start converting {input_filepath} -> {output_filepath}")

    if not os.path.exists(input_filepath):
        print(f"Input file not found: {input_filepath}")
        return

    # Clear current scenes
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import glb file
    try:
        print(f"Importing glb file: {input_filepath}")
        bpy.ops.import_scene.gltf(
            filepath=input_filepath,
        )
        print(f"Success!")
    except Exception as e:
        print(f"{e}")
        return

    try:
        print(f"Exporting gltf file: {output_filepath}")
        bpy.ops.export_scene.gltf(
            filepath=output_filepath,
            export_format='GLB',
        )
    except Exception as e:
        print(f"{e}")
        return


def convert_glb_to_dae(input_filepath, output_filepath):
    print("===")
    print(f"Start converting {input_filepath} -> {output_filepath}")

    if not os.path.exists(input_filepath):
        print(f"Input file not found: {input_filepath}")
        return

    # Clear current scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import glb file
    try:
        print(f"Importing glb file: {input_filepath}")
        bpy.ops.import_scene.gltf(filepath=input_filepath)
        print(f"Success!")
    except Exception as e:
        print(f"{e}")
        return

    try:
        print(f"Exporting dae file: {output_filepath}")
        bpy.ops.wm.collada_export(
            filepath=output_filepath,
            check_existing=False,
            include_children=True,
            triangulate=True,
            use_texture_copies=True,
            # use_object_instantiation=False,
            # use_blender_profile=False,
            # sort_by_name=True
        )
    except Exception as e:
        print(f"{e}")
        return


def list_files_with_extension(root_dir, extension):
    file_paths = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(extension):
                full_path = (Path(dirpath) / filename).as_posix()
                file_paths.append(full_path)
    return file_paths


def convert_glb_to_glb_all(input_dir: str):
    glb_filepaths = list_files_with_extension(input_dir, ".glb")
    for glb_filepath in glb_filepaths:
        convert_glb_to_glb(glb_filepath, glb_filepath)


def convert_glb_to_dae_all(input_dir: str, output_dir: str):
    glb_filepaths = list_files_with_extension(input_dir, ".glb")
    for glb_filepath in glb_filepaths:
        glb_path = Path(glb_filepath)
        new_dae_filepath = (Path(output_dir) / glb_path.with_suffix(".dae").name).as_posix()
        convert_glb_to_dae(glb_filepath, new_dae_filepath)


if __name__ == "__main__":
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    glb_dir = (script_dir / "../exchange_formats").resolve().as_posix()
    parts_dir = (script_dir / "../exchange_formats/parts").resolve().as_posix()
    dae_dir = (script_dir / "../cet200_description/meshes").resolve().as_posix()

    convert_glb_to_glb_all(glb_dir)
    convert_glb_to_dae_all(parts_dir, dae_dir)
