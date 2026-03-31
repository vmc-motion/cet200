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
import osg
import agxVehicle
from agxPythonModules.utils.callbacks import StepEventCallback
from agxPythonModules.utils.environment import init_app, simulation, root, application
import agxOpenPLX

# Python imports
import sys
import os
import math
from typing import Optional
from pathlib import Path
import importlib

# Local imports
import excavator_keyboard_gamepad

importlib.reload(excavator_keyboard_gamepad)

g_openplx_file_path_rel = "../../../openplx/cet200.openplx"


def add_openplx_file(file_path: str) -> agxOpenPLX.LoadResult:
    '''
    Load an openplx file from either an absolute path or path relative to current file.
    '''

    # If path was not absolute, make it absolute based on current file location
    if not os.path.isabs(file_path):
        current_file_dir = Path(__file__).resolve().parent
        file_path = (current_file_dir / file_path).resolve().as_posix()

    result = application().loadOpenPlxFile(file_path, root())

    if result:
        print (f"Successfully loaded OpenPLX file: {file_path}")
    else:
        raise Exception("Unable to load OpenPLX file: " + file_path)
    
    return result


def set_track_nodes_mass(sim: agxSDK.Simulation, mass: float, track_names: list[str] = []):
    '''
    Sets the mass of track nodes in the tracks specified by track_names, or in
    all tracks in the simulation if track_names is empty or None. This has to be
    done from Python because currently the openplx file does not support setting track
    node mass properties.
    '''
    if track_names is not None and len(track_names) > 0:
        tracks = [agxVehicle.Track.find(sim, name) for name in track_names]
    else:
        tracks = agxVehicle.Track.findAll(sim)

    for track in tracks:
        print (f"Setting mass of track nodes in track '{track.getName()}' to {mass} kg.")
        for node in track.nodes():  # type: agxVehicle.TrackNode
            body: agx.RigidBody = node.getRigidBody()
            mass_props = body.getMassProperties()
            mass_props.setMass(mass)
            # mass_props.setAutoGenerateMask(agx.MassProperties.CM_OFFSET | agx.MassProperties.INERTIA)
            # body.updateMassProperties()
    

def buildScene1():
    
    agx.setNumThreads(0)
    agx.setNumThreads(int(agx.getNumThreads() / 2))
    
    openplx_model = add_openplx_file(g_openplx_file_path_rel)

    # TODO: Trying to set track node mass below to same as the agx-file version,
    #       but that does make it even more unstable. Investigate!
    # set_track_nodes_mass(simulation(), 34.0)  # track_names=["Scene.CET200.Track_L", "Scene.CET200.Track_R"])

    application().setAutoStepping(True)
    application().setEnableCoordinateSystem(True)
    
    # Keyboard, Gamepad
    excavator_keyboard_gamepad.setup_keyboard_gamepad_speed_control(openplx_model)

    eye = agx.Vec3(2.8976305330906644E+00, 1.6718488143031252E+01, 3.8321300958064648E+00)
    center = agx.Vec3(6.4849247247395725E-01, 1.3679887760401846E-01, 2.7364818354149665E+00)
    up = agx.Vec3(0.0008, -0.0660, 0.9978)
    application().setCameraHome(eye, center, up)


# Entry point when this script is used with agxViewer
def buildScene():
    scene_file = application().getArguments().getArgumentName(1)
    application().addScene(scene_file, "buildScene1", ord('1'))

    buildScene1()


# Entry point when this script is started with ros2
def main():
    sys.argv[0] = Path(__file__).resolve()
    init = init_app(name="__main__", scenes=[(buildScene, '1')])


# Entry point when this script is started with python executable
if __name__ == "__main__":
    main()
