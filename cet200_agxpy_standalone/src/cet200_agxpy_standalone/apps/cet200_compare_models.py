# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# AGX Dynamics imports
import agx
import agxPython
import agxCollide
import agxIO
import agxOSG
import agxSDK
import agxUtil
import agxModel
from agxPythonModules.utils.environment import init_app, simulation, root, application

# Python imports
import sys
from pathlib import Path
import importlib

from cet200_agxpy_standalone import cet200


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


def add_ground():
    rb_ground = agx.RigidBody(agxCollide.Geometry(agxCollide.Box(20, 20, 1)))
    rb_ground.setPosition(agx.Vec3(0, 0, -1))
    rb_ground.setMotionControl(agx.RigidBody.STATIC)
    simulation().add(rb_ground)
    agxOSG.createVisual(rb_ground, root())
    return rb_ground


def add_urdf_excavator():
    base_dir = Path(__file__).resolve().parent
    urdf_file_path = (base_dir / "../../../../cet200_description/urdf/cet200.urdf").resolve().as_posix()
    package_path = (base_dir / "../../../../").resolve().as_posix()

    urdf_settings = agxModel.UrdfReaderSettings(
        fixToWorld_=False,
        disableLinkedBodies_=True,
        mergeKinematicLinks_=False
    )
    assembly_ref_excavator = agxModel.UrdfReader.read(urdf_file_path, package_path, None, urdf_settings)

    if assembly_ref_excavator.get() is None:
        print("Error reading the URDF file.")
        sys.exit(2)

    excavator: agxSDK.Assembly = assembly_ref_excavator.get()
    simulation().add(excavator)
    agxOSG.createVisual(excavator, root())

    # Create ObserverFrame and remove dummy objects
    def is_match_prefix(text: str, prefix: str):
        return text.lower().startswith(prefix.lower())

    def is_match_string(text: str, query: str):
        return text.lower() == query.lower()

    joint_removables = list()
    for joint in excavator.getConstraints():
        joint: agx.Constraint
        if is_match_prefix(joint.getName(), "dummy"):
            joint_removables.append(joint)
            rb0: agx.RigidBody = joint.getBodyAt(0)
            rb1: agx.RigidBody = joint.getBodyAt(1)

            # Add ObserverFrame
            if is_match_prefix(rb0.getName(), "tf"):
                of = agx.ObserverFrame(rb1)
                of.setTransform(rb0.getTransform())
                of.setName(rb0.getName())
                simulation().add(of)
                print(f"Add ObserverFrame: {rb0.getName()}")
            if is_match_prefix(rb1.getName(), "tf"):
                of = agx.ObserverFrame(rb0)
                of.setTransform(rb1.getTransform())
                of.setName(rb1.getName())
                simulation().add(of)
                print(f"Add ObserverFrame: {rb1.getName()}")

    for joint in joint_removables:
        print(f"Remove joint: {joint.getName()}")
        simulation().remove(joint)

    # Add base_link observer, remove dummy, tf link
    rbs = excavator.getRigidBodies()
    for rb in rbs:
        rb: agx.RigidBody
        if is_match_string(rb.getName(), "base_link"):
            of = agx.ObserverFrame(rb)
            of.setName(rb.getName())
            simulation().add(of)
            print(f"Add ObserverFrame: {rb.getName()}")
        if is_match_prefix(rb.getName(), "dummy"):
            print(f"Remove RigidBody: {rb.getName()}")
            simulation().remove(rb)
        if is_match_prefix(rb.getName(), "tf"):
            print(f"Remove RigidBody: {rb.getName()}")
            simulation().remove(rb)

    return excavator


def buildScene1():
    sim = simulation()

    agx.setNumThreads(0)
    agx.setNumThreads(int(agx.getNumThreads() / 2))
    set_camera_pose()

    # Add ground
    rb_ground = add_ground()

    # Add excavator
    urdf_excavator = add_urdf_excavator()
    # urdf_excavator.getRigidBody("RB_TrackFrame").setMotionControl(agx.RigidBody.KINEMATICS)
    for joint in urdf_excavator.getConstraints():
        j1: agx.Constraint1DOF = joint.asConstraint1DOF()
        if j1:
            j1.getMotor1D().setEnable(True)

    excavator = cet200.add_excavator()
    # excavator.getRigidBody("RB_TrackFrame").setMotionControl(agx.RigidBody.KINEMATICS)
    for joint in excavator.getConstraints():
        j1: agx.Constraint1DOF = joint.asConstraint1DOF()
        if j1:
            j1.getMotor1D().setEnable(True)
    excavator.setPosition(agx.Vec3(0, -5, 0))

    agxUtil.setEnableCollisions(urdf_excavator, excavator, False)


# Entry point when this script is used with agxViewer
def buildScene():
    scene_file = application().getArguments().getArgumentName(1)
    application().addScene(scene_file, "buildScene1", ord('1'))

    application().setAutoStepping(False)
    buildScene1()


# Entry point when this script is started with ros2
def main():
    # Colcon injects the console_scripts command name to sys.argv[0], but AGX must read this file path for loading.
    sys.argv[0] = str(Path(__file__).resolve())
    init = init_app(name="__main__", scenes=[(buildScene, '1')])


# Entry point when this script is started with python executable
if __name__ == "__main__":
    main()
