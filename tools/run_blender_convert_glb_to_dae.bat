@echo off
REM Copyright VMC Motion Technologies Co., Ltd.
REM Licensed under the Apache-2.0 license. See LICENSE.

setlocal

where /q blender
if not %ERRORLEVEL% == 0 (
  echo Error: blender not found.
  echo Install blender and add path to environment variable PATH.
  pause
  exit /b
)

echo Start converting glb files
blender --background --python blender_convert_glb_to_dae.py
echo Done!

endlocal