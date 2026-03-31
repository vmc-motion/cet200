# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# Enables keyboard and gamepad control, with following key mapping:
# Keyboard:
#   Slew: a/s
#   Arm: z/x
#   Boom: m/, (comma)
#   Bucket: j/k
#   Move forward/backward: up/down arrow
#   Turn left/right: left/right arrow


# Python imports
from dataclasses import dataclass

# AGX Dynamics imports
import agx
import agxSDK
import agxOpenPLX
import openplx
from openplx.Physics.Signals import RealInputSignal
from agxPythonModules.utils.callbacks import (
    KeyboardCallback as Input,
    GamepadCallback as Gamepad,
)
from agxPythonModules.utils.environment import simulation


class MaxSpeeds:
    HINGE_SLEW = 1.256637
    PRISMATIC_BOOM = 0.648409027 * 0.5
    PRISMATIC_ARM = 0.59757376
    PRISMATIC_BUCKET = 0.706018147
    HINGE_SPROCKET = 4.074104494


@dataclass
class ExcavatorInputs:
    import openplx
    sprocket_R_vel: openplx.Physics.Signals.Input  # openplx.Physics._OPENPLX_Physics_Signals_AngularVelocity1DInput
    sprocket_L_vel: openplx.Physics.Signals.Input  # openplx.Physics._OPENPLX_Physics_Signals_AngularVelocity1DInput
    slew_vel: openplx.Physics.Signals.Input  # openplx.Physics._OPENPLX_Physics_Signals_AngularVelocity1DInput
    boom_vel: openplx.Physics.Signals.Input  # openplx.Physics._OPENPLX_Physics_Signals_LinearVelocity1DInput
    arm_vel: openplx.Physics.Signals.Input  # openplx.Physics._OPENPLX_Physics_Signals_LinearVelocity1DInput
    bucket_vel: openplx.Physics.Signals.Input  # openplx.Physics._OPENPLX_Physics_Signals_LinearVelocity1DInput


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


def _set_speed_by_gamepad(input_signal, 
                          input_queue: agxOpenPLX.InputSignalQueue,
                          throttle: float, delta_throttle: float, scale: float = 1.0):
    if input_signal is not None:
        throttle = handle_stick_dead_zone(throttle)
        if not is_stick_moved(throttle, delta_throttle):
            return
        value = throttle * scale
        input_queue.send(RealInputSignal.create(value, input_signal))

    
def _set_speed_by_keyboard(input_signal, 
                          input_queue: agxOpenPLX.InputSignalQueue,
                          throttle: float, scale: float = 1.0):
    if input_signal is not None:
        value = throttle * scale
        input_queue.send(RealInputSignal.create(value, input_signal))


class ExcavatorKeyboardControl(agxSDK.GuiEventListener):
    def __init__(self, inputs: ExcavatorInputs, input_queue: agxOpenPLX.InputSignalQueue):
        super().__init__(agxSDK.GuiEventListener.KEYBOARD)
        self.inputs = inputs
        self.input_queue = input_queue

    def keyboard(self, key, x, y, alt, down):
        handled = False
        throttle = 0.6 if down else 0
        # Slew
        if key == ord('a'):
            _set_speed_by_keyboard(self.inputs.slew_vel, self.input_queue, throttle, MaxSpeeds.HINGE_SLEW)
            handled = True
        if key == ord('s'):
            _set_speed_by_keyboard(self.inputs.slew_vel, self.input_queue, -throttle, MaxSpeeds.HINGE_SLEW)
            handled = True
        # Arm
        if key == ord('z'):
            _set_speed_by_keyboard(self.inputs.arm_vel, self.input_queue, -throttle, MaxSpeeds.PRISMATIC_ARM)
            handled = True
        if key == ord('x'):
            _set_speed_by_keyboard(self.inputs.arm_vel, self.input_queue, throttle, MaxSpeeds.PRISMATIC_ARM)
            handled = True
        # Boom
        if key == ord('m'):
            _set_speed_by_keyboard(self.inputs.boom_vel, self.input_queue, throttle, MaxSpeeds.PRISMATIC_BOOM)
            handled = True
        if key == ord(','):
            _set_speed_by_keyboard(self.inputs.boom_vel, self.input_queue, -throttle, MaxSpeeds.PRISMATIC_BOOM)
            handled = True
        # Bucket
        if key == ord('j'):
            _set_speed_by_keyboard(self.inputs.bucket_vel, self.input_queue, throttle, MaxSpeeds.PRISMATIC_BUCKET)
            handled = True
        if key == ord('k'):
            _set_speed_by_keyboard(self.inputs.bucket_vel, self.input_queue, -throttle, MaxSpeeds.PRISMATIC_BUCKET)
            handled = True

        # Move forward
        if key == Input.KEY_Up:
            _set_speed_by_keyboard(self.inputs.sprocket_L_vel, self.input_queue, throttle, MaxSpeeds.HINGE_SPROCKET)
            _set_speed_by_keyboard(self.inputs.sprocket_R_vel, self.input_queue, throttle, MaxSpeeds.HINGE_SPROCKET)
            handled = True
        # Move backward
        if key == Input.KEY_Down:
            _set_speed_by_keyboard(self.inputs.sprocket_L_vel, self.input_queue, -throttle, MaxSpeeds.HINGE_SPROCKET)
            _set_speed_by_keyboard(self.inputs.sprocket_R_vel, self.input_queue, -throttle, MaxSpeeds.HINGE_SPROCKET)
            handled = True
        # Turn left
        if key == Input.KEY_Left:
            _set_speed_by_keyboard(self.inputs.sprocket_L_vel, self.input_queue, -throttle, MaxSpeeds.HINGE_SPROCKET)
            _set_speed_by_keyboard(self.inputs.sprocket_R_vel, self.input_queue, throttle, MaxSpeeds.HINGE_SPROCKET)
            handled = True
        # Turn right
        if key == Input.KEY_Right:
            _set_speed_by_keyboard(self.inputs.sprocket_L_vel, self.input_queue, throttle, MaxSpeeds.HINGE_SPROCKET)
            _set_speed_by_keyboard(self.inputs.sprocket_R_vel, self.input_queue, -throttle, MaxSpeeds.HINGE_SPROCKET)
            handled = True

        return handled


def _setup_keyboard(inputs: ExcavatorInputs, input_queue: agxOpenPLX.InputSignalQueue):
    simulation().addEventListener(ExcavatorKeyboardControl(inputs, input_queue))


def _setup_gamepad(inputs: ExcavatorInputs, input_queue: agxOpenPLX.InputSignalQueue):
    if Gamepad.instance() is None:
        print("WARNING: Gamepad controls deactivated.")

    # Bind events to the pov buttons
    def bind_gamepad_axis(axis: Gamepad.Axis, callback):
        name = f"Axis.{axis.name}"
        Gamepad.bind(name=name, axis=axis, callback=callback)

    def bind_gamepad_button(button: Gamepad.Button, callback):
        name = f"Button.{button.name}"
        Gamepad.bind(name=name, button=button, callback=callback)

    # Slew
    bind_gamepad_axis(Gamepad.Axis.LeftHorizontal,
                      lambda axis_data: _set_speed_by_gamepad(inputs.slew_vel, input_queue,
                                                              -axis_data.value, axis_data.delta, 
                                                              MaxSpeeds.HINGE_SLEW))
    # Arm
    bind_gamepad_axis(Gamepad.Axis.LeftVertical,
                      lambda axis_data: _set_speed_by_gamepad(inputs.arm_vel, input_queue,
                                                              axis_data.value, axis_data.delta,
                                                              MaxSpeeds.PRISMATIC_ARM))
    # Bucket
    bind_gamepad_axis(Gamepad.Axis.RightHorizontal,
                      lambda axis_data: _set_speed_by_gamepad(inputs.bucket_vel, input_queue,
                                                              -axis_data.value, axis_data.delta,
                                                              MaxSpeeds.PRISMATIC_BUCKET))
    # Boom
    bind_gamepad_axis(Gamepad.Axis.RightVertical,
                      lambda axis_data: _set_speed_by_gamepad(inputs.boom_vel, input_queue,
                                                              axis_data.value, axis_data.delta,
                                                              MaxSpeeds.PRISMATIC_BOOM))

    # Left forward
    bind_gamepad_button(Gamepad.Button.LeftBumper,
                        lambda button_data: _set_speed_by_gamepad(inputs.sprocket_L_vel, input_queue,
                                                                  -1.0 if button_data.down else 0.0, 1.0,  # TODO: What about delta for buttons?
                                                                  MaxSpeeds.HINGE_SPROCKET))
    # Right forward
    bind_gamepad_button(Gamepad.Button.RightBumper,
                        lambda button_data: _set_speed_by_gamepad(inputs.sprocket_R_vel, input_queue,
                                                                  -1.0 if button_data.down else 0.0, 1.0,  # TODO: What about delta for buttons?
                                                                  MaxSpeeds.HINGE_SPROCKET))
    # Left backward
    bind_gamepad_axis(Gamepad.Axis.LeftTrigger,
                      lambda axis_data: _set_speed_by_gamepad(inputs.sprocket_L_vel, input_queue,
                                                              axis_data.value, axis_data.delta,
                                                              MaxSpeeds.HINGE_SPROCKET))
    # Right backward
    bind_gamepad_axis(Gamepad.Axis.RightTrigger,
                      lambda axis_data: _set_speed_by_gamepad(inputs.sprocket_R_vel, input_queue,
                                                              axis_data.value, axis_data.delta,
                                                              MaxSpeeds.HINGE_SPROCKET))


def setup_keyboard_gamepad_speed_control(openplx_model: agxOpenPLX.LoadResult, keyboard_enabled: bool = True, gamepad_enabled: bool = True):

    # TODO: Can we use openplx_model.scene().getSignalInterfaces() instead?
    assert (signal_interface := openplx_model.scene().getObject("CET200.signal_interface"))  # type: openplx.Physics._OPENPLX_Physics_Signals_SignalInterface
    assert (input_queue := openplx_model.getInputSignalQueue())
    assert (input_signals := signal_interface.getInputs())

    exavator_inputs = ExcavatorInputs(
        sprocket_R_vel=input_signals.get("sprocket_R_vel_input", None),
        sprocket_L_vel=input_signals.get("sprocket_L_vel_input", None),
        slew_vel=input_signals.get("slew_vel_input", None),
        boom_vel=input_signals.get("boom_vel_input", None),
        arm_vel=input_signals.get("arm_vel_input", None),
        bucket_vel=input_signals.get("bucket_vel_input", None),
    )

    assert(exavator_inputs.sprocket_R_vel != None)
    assert(exavator_inputs.sprocket_L_vel != None)
    assert(exavator_inputs.slew_vel != None)
    assert(exavator_inputs.boom_vel != None)
    assert(exavator_inputs.arm_vel != None)
    assert(exavator_inputs.bucket_vel != None)

    if keyboard_enabled:
        _setup_keyboard(exavator_inputs, input_queue)
    if gamepad_enabled:
        _setup_gamepad(exavator_inputs, input_queue)
    
    # TODO: Implement HINGE_SLEW_BRAKE_MULTIPLIER found in the agx-file based version
    # TODO: Implement Slew Lock System foundin the agx-file based version
    
