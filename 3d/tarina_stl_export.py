# exports each selected object into its own file

import bpy
import os

# export to blend file location
basedir = os.path.dirname(bpy.data.filepath) + '/'

if not basedir:
    raise Exception("Blend file is not saved")

scene = bpy.context.scene

##obj_active = scene.objects.active
selection = bpy.context.selected_objects

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Body']
o.hide_set(False)
o.select_set(True)
o = bpy.data.objects['Body Support']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-body.stl", check_existing=True, axis_forward='-Z', axis_up='-Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Left-Side']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-left-side.stl", check_existing=True, axis_forward='-Y', axis_up='X', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Right-Side']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-right-side.stl", check_existing=True, axis_forward='-Y', axis_up='-X', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Hdmi-Cap']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-hdmi-cap.stl", check_existing=True, axis_forward='X', axis_up='Z', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Button-Plate-Bottom']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-button-plate-bottom.stl", check_existing=True, axis_forward='X', axis_up='Z', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Button-Plate-Upper']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-button-plate-upper.stl", check_existing=True, axis_forward='-X', axis_up='-Z', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Screen-Lid-hyperpixel']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-screen-lid-hyperpixel.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Screen-Lid-ugeek']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-screen-lid-ugeek.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-Bridge']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-bridge.stl", check_existing=True, axis_forward='Y', axis_up='X', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-Body']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-body.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-Body-Lid']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-body-lid.stl", check_existing=True, axis_forward='-Z', axis_up='-Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-HQ-Body']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-hq-body.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Picamera-HQ-Body-Lid']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-hq-body-lid.stl", check_existing=True, axis_forward='-Z', axis_up='-Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Mic-Body']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-mic-body.stl", check_existing=True, axis_forward='-Z', axis_up='-Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['Mic-Lid']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-mic-lid.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')

bpy.ops.object.select_all(action='DESELECT')
o = bpy.data.objects['picamera-screwhandle']
o.hide_set(False)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.export_mesh.stl(filepath=basedir + "tarina-picamera-screwhandle.stl", check_existing=True, axis_forward='Z', axis_up='Y', filter_glob="*.stl", use_selection=True, global_scale=1.0, use_scene_unit=False, ascii=False, use_mesh_modifiers=True, batch_mode='OFF')
bpy.ops.object.select_all(action='DESELECT')