# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# AGX Dynamics imports
from typing import Optional, Any

import agx
import agxPython
import agxCollide
import agxIO
import agxOSG
import agxSDK
import agxTerrain
import agxUtil
import osg
import agxVehicle
from agx import AGX_GET_VERSION, agxGetPythonVersion, agxGetVersion, AGX_CONVERT_VERSION, AGX_CALC_VERSION

from agxPythonModules.utils.callbacks import (
    StepEventCallback,
    KeyboardCallback as Input,
    GamepadCallback as Gamepad,
    ContactEventCallback as ContactEvent,
)

# Python imports
import sys

from agxPythonModules.utils.environment import application, simulation


def setup_excavator_monitor(excavator: agxSDK.Assembly):
    sd: agxOSG.SceneDecorator = application().getSceneDecorator()
    sd.setFontSize(0.01)

    joints: list[agx.Constraint1DOF] = list()
    slew_joint = excavator.getConstraint1DOF("Hinge_Slew")
    boom_joint = excavator.getConstraint1DOF("Prismatic_Boom")
    arm_joint = excavator.getConstraint1DOF("Prismatic_Arm")
    bucket_joint = excavator.getConstraint1DOF("Prismatic_Bucket")
    sprocket_joint_l = excavator.getConstraint1DOF("Hinge_Sprocket_L")
    sprocket_joint_r = excavator.getConstraint1DOF("Hinge_Sprocket_R")

    hinge_boom = excavator.getConstraint1DOF("Hinge_Boom")
    hinge_arm = excavator.getConstraint1DOF("Hinge_Arm")
    hinge_bucket = excavator.getConstraint1DOF("Hinge_Bucket")

    terrain = simulation().getTerrain(0)
    shovel = None
    if terrain:
        shovels = agxTerrain.Shovel.findAll(simulation())
        shovel = shovels[0] if len(shovels) > 0 else None

    # Helper functions
    def clamp_to_zero(value: float, threshold=1e-6):
        return value if abs(value) > threshold else 0

    def get_penetration_force() -> agx.Vec3:
        penetration_force = agx.Vec3()
        penetration_torque = agx.Vec3()
        shovel.getPenetrationForce(penetration_force, penetration_torque)
        return penetration_force

    def get_separation_force():
        return shovel.getSeparationContactForce()

    def get_contact_force():
        return shovel.getContactForce()

    def get_deformation_contact_force():
        return shovel.getDeformationContactForce()

    def get_bucket_soil_volume() -> float:
        agx_version = AGX_GET_VERSION()
        if agx_version > AGX_CALC_VERSION(2, 40, 1, 5):
            return shovel.getInnerSoilBulkVolume()
        else:
            return shovel.getSoilVolume()

    def get_bucket_soil_mass() -> float:
        return shovel.getDynamicMass()

    # Callback
    def update_monitor(time_stamp):
        width1 = 30
        width2 = 10
        width3 = 13

        text_list: list[str] = list()

        str_keyboard = "Key: {Slew: a, s, Arm: z, x, Bucket: j, k, Boom: m, ','}"
        str_elapsed_time = f"Elapsed time: {simulation().getTimeStamp():>.2f}"

        text_list.append(str_keyboard)
        text_list.append(str_elapsed_time)
        text_list.append(f"{'Joint':>{width1}}: {'Angle':>{width2}} {'Speed':>{width2}} {'Force(k)':>{width3}}")

        def add_joint_to_text_list(_joint):
            if _joint is None:
                return
            name = _joint.getName()
            angle = clamp_to_zero(_joint.getAngle())
            speed = clamp_to_zero(_joint.getCurrentSpeed())
            motor_force = clamp_to_zero(_joint.getMotor1D().getCurrentForce(), 100)
            motor_force = _joint.getMotor1D().getCurrentForce() * 1e-3
            text_list.append(f"{name:>{width1}}: {angle:>{width2}.6f} {speed:>{width2}.3f} {motor_force:>{width3}.3f}")

        add_joint_to_text_list(slew_joint)
        add_joint_to_text_list(boom_joint)
        add_joint_to_text_list(arm_joint)
        add_joint_to_text_list(bucket_joint)
        add_joint_to_text_list(sprocket_joint_l)
        add_joint_to_text_list(sprocket_joint_r)
        add_joint_to_text_list(hinge_boom)
        add_joint_to_text_list(hinge_arm)
        add_joint_to_text_list(hinge_bucket)

        if shovel:
            pf = get_penetration_force() * 1e-3
            sf = get_separation_force() * 1e-3
            cf = get_contact_force() * 1e-3
            dcf = get_deformation_contact_force() * 1e-3
            tf = pf + sf + cf + dcf

            text_list.append(
                f"{'Force':>{width1}}: {'Magnitude':>{width2}} {'x':>{width2}} {'y':>{width2}} {'z':>{width2}}")

            def add_force_to_text_list(_name: str, f: agx.Vec3):
                text_list.append(
                    f"{_name + '(kN)':>{width1}}: {f.length():>{width2}.3f} {f.x():>{width2}.3f} {f.y():>{width2}.3f} {f.z():>{width2}.3f}")

            add_force_to_text_list("PenetrationForce", pf)
            add_force_to_text_list("SeparationContactForce", sf)
            add_force_to_text_list("ContactForce", cf)
            add_force_to_text_list("DeformationContactForce", dcf)
            add_force_to_text_list("TotalExcavationForce", tf)

            text_list.append(f"{'BucketSoilVolume(m3)':>{width1}}: {get_bucket_soil_volume():{width2}.3f}")
            text_list.append(f"{'BucketSoilMass(kg)':>{width1}}: {get_bucket_soil_mass():{width2}.3f}")

        # Draw text
        for index, line in enumerate(text_list):
            sd.setText(index, line)

    # Register callback
    StepEventCallback.postCallback(update_monitor)
