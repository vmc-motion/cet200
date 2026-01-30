# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# AGX Dynamics imports
import agx
import agxSDK

from agxPythonModules.utils.callbacks import (
    KeyboardCallback as Input,
    GamepadCallback as Gamepad,
)
from agxPythonModules.utils.environment import simulation

max_speeds = {
    'Hinge_Slew': 1.256637,
    'Prismatic_Boom': 0.648409027 * 0.5,
    'Prismatic_Arm': 0.59757376,
    'Prismatic_Bucket': 0.706018147,
    'Hinge_Sprocket': 4.074104494,
}

HINGE_SLEW_BRAKE_MULTIPLIER = 4
HINGE_SLEW_MOTOR_TORQUE: agx.RangeReal
HINGE_SLEW_BRAKE_TORQUE: agx.RangeReal


def _set_speed(joint: agx.Constraint1DOF, throttle: float):
    target_speed = throttle * max_speeds[joint.getName()]
    motor1d: agx.Motor1D = joint.getMotor1D()
    motor1d.setSpeed(target_speed)

    if joint.getName() == "Hinge_Slew":
        motor1d.setForceRange(HINGE_SLEW_MOTOR_TORQUE)
        if target_speed == 0.0:
            motor1d.setForceRange(HINGE_SLEW_BRAKE_TORQUE)


def _set_sprocket_speed(joint: agx.Hinge, throttle: float):
    speed = throttle * max_speeds['Hinge_Sprocket']
    joint.getMotor1D().setSpeed(speed)


def handle_stick_dead_zone(raw_value):
    dead_zone = 0.3
    abs_raw_value = abs(raw_value)
    if abs_raw_value <= dead_zone:
        return 0
    sign = 1.0 if raw_value > 0.0 else -1.0
    return sign * (abs_raw_value - dead_zone) / (1 - dead_zone)


def is_stick_moved(value, delta_value):
    if abs(value) > 0.0:
        return True
    if abs(delta_value) > 0.0:
        return True
    return False


def _set_speed_by_gamepad(joint: agx.Constraint1DOF, throttle: float, delta_throttle):
    throttle = handle_stick_dead_zone(throttle)
    if not is_stick_moved(throttle, delta_throttle):
        return
    _set_speed(joint, throttle)


def _set_sprocket_speed_by_gamepad(joint: agx.Hinge, throttle: float, delta_throttle: float):
    throttle = handle_stick_dead_zone(throttle)
    if not is_stick_moved(throttle, delta_throttle):
        return
    _set_sprocket_speed(joint, throttle)


class ExcavatorKeyboardControl(agxSDK.GuiEventListener):
    def __init__(self, excavator):
        super().__init__(agxSDK.GuiEventListener.KEYBOARD)
        self.slew_joint = excavator.getConstraint1DOF("Hinge_Slew")
        self.boom_joint = excavator.getConstraint1DOF("Prismatic_Boom")
        self.arm_joint = excavator.getConstraint1DOF("Prismatic_Arm")
        self.bucket_joint = excavator.getConstraint1DOF("Prismatic_Bucket")
        self.sprocket_joint_l = excavator.getConstraint1DOF("Hinge_Sprocket_L")
        self.sprocket_joint_r = excavator.getConstraint1DOF("Hinge_Sprocket_R")

    def keyboard(self, key, x, y, alt, down):
        handled = False
        throttle = 0.6 if down else 0
        # Slew
        if key == ord('a'):
            _set_speed(self.slew_joint, throttle)
            handled = True
        if key == ord('s'):
            _set_speed(self.slew_joint, -throttle)
            handled = True
        # Arm
        if key == ord('z'):
            _set_speed(self.arm_joint, -throttle)
            handled = True
        if key == ord('x'):
            _set_speed(self.arm_joint, throttle)
            handled = True
        # Boom
        if key == ord('m'):
            _set_speed(self.boom_joint, throttle)
            handled = True
        if key == ord(','):
            _set_speed(self.boom_joint, -throttle)
            handled = True
        # Bucket
        if key == ord('j'):
            _set_speed(self.bucket_joint, throttle)
            handled = True
        if key == ord('k'):
            _set_speed(self.bucket_joint, -throttle)
            handled = True

        # Move forward
        if key == Input.KEY_Up:
            _set_sprocket_speed(self.sprocket_joint_l, throttle)
            _set_sprocket_speed(self.sprocket_joint_r, throttle)
            handled = True
        # Move backward
        if key == Input.KEY_Down:
            _set_sprocket_speed(self.sprocket_joint_l, -throttle)
            _set_sprocket_speed(self.sprocket_joint_r, -throttle)
            handled = True
        # Turn left
        if key == Input.KEY_Left:
            _set_sprocket_speed(self.sprocket_joint_l, -throttle)
            _set_sprocket_speed(self.sprocket_joint_r, throttle)
            handled = True
        # Turn right
        if key == Input.KEY_Right:
            _set_sprocket_speed(self.sprocket_joint_l, throttle)
            _set_sprocket_speed(self.sprocket_joint_r, -throttle)
            handled = True

        return handled


def _setup_keyboard(excavator: agxSDK.Assembly):
    simulation().addEventListener(ExcavatorKeyboardControl(excavator))


def _setup_gamepad(excavator: agxSDK.Assembly):
    if Gamepad.instance() is None:
        print("WARNING: Gamepad controls deactivated.")

    slew_joint = excavator.getConstraint1DOF("Hinge_Slew")
    boom_joint = excavator.getConstraint1DOF("Prismatic_Boom")
    arm_joint = excavator.getConstraint1DOF("Prismatic_Arm")
    bucket_joint = excavator.getConstraint1DOF("Prismatic_Bucket")
    sprocket_joint_l = excavator.getConstraint1DOF("Hinge_Sprocket_L")
    sprocket_joint_r = excavator.getConstraint1DOF("Hinge_Sprocket_R")

    # Bind events to the pov buttons
    def bind_gamepad_axis(axis: Gamepad.Axis, callback):
        name = f"Axis.{axis.name}"
        Gamepad.bind(name=name, axis=axis, callback=callback)

    def bind_gamepad_button(button: Gamepad.Button, callback):
        name = f"Button.{button.name}"
        Gamepad.bind(name=name, button=button, callback=callback)

    # Slew
    bind_gamepad_axis(Gamepad.Axis.LeftHorizontal,
                      lambda axis_data: _set_speed_by_gamepad(slew_joint, -axis_data.value, axis_data.delta))
    # Arm
    bind_gamepad_axis(Gamepad.Axis.LeftVertical,
                      lambda axis_data: _set_speed_by_gamepad(arm_joint, axis_data.value, axis_data.delta))
    # Bucket
    bind_gamepad_axis(Gamepad.Axis.RightHorizontal,
                      lambda axis_data: _set_speed_by_gamepad(bucket_joint, -axis_data.value, axis_data.delta))
    # Boom
    bind_gamepad_axis(Gamepad.Axis.RightVertical,
                      lambda axis_data: _set_speed_by_gamepad(boom_joint, axis_data.value, axis_data.delta))

    # Left forward
    bind_gamepad_button(Gamepad.Button.LeftBumper,
                        lambda button_data: _set_sprocket_speed_by_gamepad(sprocket_joint_l,
                                                                           1.0 if button_data.down else 0.0, 1.0))
    # Right forward
    bind_gamepad_button(Gamepad.Button.RightBumper,
                        lambda button_data: _set_sprocket_speed_by_gamepad(sprocket_joint_r,
                                                                           1.0 if button_data.down else 0.0, 1.0))
    # Left backward
    bind_gamepad_axis(Gamepad.Axis.LeftTrigger,
                      lambda axis_data: _set_sprocket_speed_by_gamepad(sprocket_joint_l, -axis_data.value,
                                                                       axis_data.delta))
    # Right backward
    bind_gamepad_axis(Gamepad.Axis.RightTrigger,
                      lambda axis_data: _set_sprocket_speed_by_gamepad(sprocket_joint_r, -axis_data.value,
                                                                       axis_data.delta))


def setup_keyboard_gamepad_speed_control(excavator: agxSDK.Assembly):
    slew_joint = excavator.getConstraint1DOF("Hinge_Slew")
    boom_joint = excavator.getConstraint1DOF("Prismatic_Boom")
    arm_joint = excavator.getConstraint1DOF("Prismatic_Arm")
    bucket_joint = excavator.getConstraint1DOF("Prismatic_Bucket")
    sprocket_joint_l = excavator.getConstraint1DOF("Hinge_Sprocket_L")
    sprocket_joint_r = excavator.getConstraint1DOF("Hinge_Sprocket_R")

    global HINGE_SLEW_MOTOR_TORQUE
    global HINGE_SLEW_BRAKE_TORQUE
    slew_joint_motor1d: agx.Motor1D = slew_joint.getMotor1D()
    HINGE_SLEW_MOTOR_TORQUE = slew_joint_motor1d.getForceRange()
    HINGE_SLEW_BRAKE_TORQUE = agx.RangeReal(HINGE_SLEW_MOTOR_TORQUE.lower() * HINGE_SLEW_BRAKE_MULTIPLIER,
                                            HINGE_SLEW_MOTOR_TORQUE.upper() * HINGE_SLEW_BRAKE_MULTIPLIER)

    for joint in [slew_joint, boom_joint, arm_joint, bucket_joint, sprocket_joint_r, sprocket_joint_l]:
        joint.getMotor1D().setEnable(True)

    _setup_keyboard(excavator)
    _setup_gamepad(excavator)
