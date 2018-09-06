# exports each selected object into its own file

import bpy
import os

# export to blend file location
basedir = os.path.dirname(bpy.data.filepath) + '/'

if not basedir:
    raise Exception("Blend file is not saved")

scene = bpy.context.scene

obj_active = scene.objects.active
selection = bpy.context.selected_objects

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Body']
o.select = True
o = bpy.data.objects['Body Support']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-body.stl", check_existing=True, axis_forward='-Z', axis_up='-Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Left-Side']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-left-side.stl", check_existing=True, axis_forward='-Y', axis_up='X', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Right-Side']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-right-side.stl", check_existing=True, axis_forward='-Y', axis_up='-X', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Hdmi-Cap']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-hdmi-cap.stl", check_existing=True, axis_forward='X', axis_up='Z', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Button-Plate-Bottom']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-button-plate-bottom.stl", check_existing=True, axis_forward='X', axis_up='Z', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Button-Plate-Upper']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-button-plate-upper.stl", check_existing=True, axis_forward='-X', axis_up='-Z', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Screen-Lid']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-screen-lid.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-Bridge']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-bridge.stl", check_existing=True, axis_forward='Y', axis_up='X', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-Body']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-body.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-Body-Lid']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-body-lid.stl", check_existing=True, axis_forward='-Z', axis_up='-Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Mic-Body']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-mic-body.stl", check_existing=True, axis_forward='-Z', axis_up='-Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Mic-Lid']
o.select = True
bpy.context.scene.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-mic-lid.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')