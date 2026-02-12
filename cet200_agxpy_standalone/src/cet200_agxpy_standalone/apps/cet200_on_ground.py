# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# AGX Dynamics imports
import agx
import agxPython
import agxCollide
import agxIO
import agxOSG
import agxUtil
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

    eye = agx.Vec3(7.7989083905525947E-02, 1.3738740061511153E+01, 2.0896597500178338E+00)
    center = agx.Vec3(9.6601861454994287E-01, 3.1072512744819203E-01, 2.4927204246851895E+00)
    up = agx.Vec3(-0.0085, 0.0294, 0.9995)
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


def add_ground():
    rb_ground = agx.RigidBody(agxCollide.Geometry(agxCollide.Box(10, 10, 1)))
    rb_ground.setPosition(agx.Vec3(0, 0, -1))
    rb_ground.setMotionControl(agx.RigidBody.STATIC)
    simulation().add(rb_ground)
    agxOSG.createVisual(rb_ground, root())
    return rb_ground


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

    # Add ground
    rb_ground = add_ground()
    rb_ground.setPosition(rb_ground.getPosition() + agx.Vec3(-7, 0, 0))
    agxUtil.setBodyMaterial(rb_ground, mt_ground)

    # Add excavator
    excavator = cet200.add_excavator()
    # excavator.getRigidBody("RB_TrackFrame").setMotionControl(agx.RigidBody.KINEMATICS)
    cet200.setup_wheel_material(excavator, mt_wheel)
    cet200.setup_track_material(excavator, mt_track, cm_ground_vs_track)

    # Keyboard, Gamepad connection
    excavator_keyboard_gamepad.setup_keyboard_gamepad_speed_control(excavator)
    # Monitor
    excavator_monitor.setup_excavator_monitor(excavator)

    # observerFrame: agx.ObserverFrame = excavator.getObserverFrame("TF_Origin_Model")
    # agxOSG.createAxes(excavator.getRigidBody("RB_TrackFrame"), observerFrame.getFrame(), scene_context.scene_root)
    # agxOSG.createAxes(excavator.getRigidBody("RB_TrackFrame"), None, scene_context.scene_root)
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
