# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# AGX Dynamics imports
import agx
import agxPython
import agxCollide
import agxIO
import agxOSG
import agxUtil
import agxTerrain
from agxPythonModules.utils.environment import init_app, simulation, root, application

# Python imports
import sys
from pathlib import Path
import importlib

from cet200_agxpy_standalone import excavator_keyboard_gamepad, excavator_monitor, cet200

importlib.reload(cet200)
importlib.reload(excavator_monitor)
importlib.reload(excavator_keyboard_gamepad)


def set_camera_pose():
    app = application()
    camera_data = app.getCameraData()
    camera_data.nearClippingPlane = 0.1
    camera_data.farClippingPlane = 500
    app.applyCameraData(camera_data)

    eye = agx.Vec3(-2.4283494181646127E+01, 1.2931941843364848E+01, 1.0132067363302802E+01)
    center = agx.Vec3(-1.2156663185500085E+00, 2.2800663641677626E-01, -1.9087158882887673E-01)
    up = agx.Vec3(0.3019, -0.2078, 0.9304)
    app.setCameraHome(eye, center, up)


def add_contact_material_ground_vs_track(mat_ground, mat_track):
    cmat: agx.ContactMaterial = simulation().getMaterialManager().getOrCreateContactMaterial(mat_ground, mat_track)
    cmat.setRestitution(0)
    cmat.setFrictionCoefficient(1, agx.ContactMaterial.PRIMARY_DIRECTION)
    cmat.setSurfaceViscosity(1.0E-6, agx.ContactMaterial.PRIMARY_DIRECTION)
    cmat.setFrictionCoefficient(0.25, agx.ContactMaterial.SECONDARY_DIRECTION)
    cmat.setSurfaceViscosity(6.0E-6, agx.ContactMaterial.SECONDARY_DIRECTION)
    return cmat


def add_contact_material_wheel_vs_track(mat_wheel, mat_track):
    cmat: agx.ContactMaterial = simulation().getMaterialManager().getOrCreateContactMaterial(mat_wheel, mat_track)
    cmat.setYoungsModulus(1e10)
    cmat.setRestitution(0)
    cmat.setSurfaceViscosity(1)
    return cmat


def add_terrain(material: agx.Material):
    resolution_x = 200
    resolution_y = 200
    element_size = 0.15
    maximum_depth = 2
    terrain = agxTerrain.Terrain(resolution_x, resolution_y, element_size, maximum_depth)
    terrain.loadLibraryMaterial("dirt_1")
    terrain.setMaterial(material, agxTerrain.Terrain.MaterialType_TERRAIN)
    ecp: agxTerrain.ExcavationContactProperties = terrain.getTerrainMaterial().getExcavationContactProperties()
    ecp.setAggregateStiffnessMultiplier(0.1)
    terrain.getProperties().setDeleteSoilParticlesOutsideBounds(True)

    simulation().add(terrain)

    renderer = agxOSG.TerrainVoxelRenderer(terrain, root())
    renderer.setRenderHeightField(True)
    renderer.setRenderSoilParticlesMesh(True)
    renderer.setRenderCompaction(True, agx.RangeReal(0.85, 1.15))
    simulation().add(renderer)

    return terrain


def buildScene1():
    sim = simulation()
    agx.setNumThreads(0)
    agx.setNumThreads(int(agx.getNumThreads() / 2))

    # Add materials
    mt_ground = agx.Material("MT_Ground")
    mt_wheel = agx.Material("MT_Wheel")
    mt_track = agx.Material("MT_Track")
    sim.add(mt_ground)
    sim.add(mt_wheel)
    sim.add(mt_track)
    cm_ground_vs_track = add_contact_material_ground_vs_track(mt_ground, mt_track)
    cm_wheel_vs_track = add_contact_material_wheel_vs_track(mt_wheel, mt_track)

    # Add terrain
    terrain = add_terrain(mt_ground)

    # Add excavator
    excavator = cet200.add_excavator()
    excavator.setPosition(-10, 0, 0)
    cet200.setup_terrain_shovel(excavator)
    cet200.setup_wheel_material(excavator, mt_wheel)
    cet200.setup_track_material(excavator, mt_track, cm_ground_vs_track)

    # Keyboard, Gamepad
    excavator_keyboard_gamepad.setup_keyboard_gamepad_speed_control(excavator)
    # Monitor
    excavator_monitor.setup_excavator_monitor(excavator)

    set_camera_pose()


# Entry point when this script is used with agxViewer
def buildScene():
    scene_file = application().getArguments().getArgumentName(1)
    application().addScene(scene_file, "buildScene1", ord('1'))

    application().setAutoStepping(True)
    buildScene1()


# Entry point when this script is started with ros2
def main():
    # Colcon injects the console_scripts command name to sys.argv[0], but AGX must read this file path for loading.
    sys.argv[0] = str(Path(__file__).resolve())
    init = init_app(name="__main__", scenes=[(buildScene, '1')])


# Entry point when this script is started with python executable
if __name__ == "__main__":
    main()
