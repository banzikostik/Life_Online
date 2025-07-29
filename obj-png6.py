import bpy
import os
import math
from mathutils import Vector

models_dir = "D:/PhaserProjects/life-online/render/your_path/models/"
output_dir = "D:/PhaserProjects/life-online/render/your_path/renders/"
angles = 16
img_size = 256
cam_height = 35.264

# Теперь перебираем все obj-файлы в папке:
obj_files = [f for f in os.listdir(models_dir) if f.lower().endswith(".obj")]

for obj_file in obj_files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj_path = os.path.join(models_dir, obj_file)
    bpy.ops.import_scene.obj(filepath=obj_path)
    imported_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    # Удаляем всё, что похоже на "землю/plane/circle"
    keywords = ['plane', 'circle', 'ground', 'floor', 'земля', 'base']
    for obj in imported_meshes:
        name = obj.name.lower()
        if any(k in name for k in keywords):
            bpy.data.objects.remove(obj, do_unlink=True)
    # Оставляем только "дом" (первый оставшийся объект)
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not meshes:
        print(f"Нет объектов для рендера в {obj_file}")
        continue
    obj = meshes[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    # Удалить материалы и создать базовый (чтобы не было чёрных стен)
    mat = bpy.data.materials.new("TempMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1) # Белый цвет
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    # Камера и свет
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.data.lens = 50
    cam.data.type = 'PERSP'
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    bpy.context.scene.render.resolution_x = img_size
    bpy.context.scene.render.resolution_y = img_size
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    elevation = math.radians(cam_height)
    for angle in range(angles):
        theta = 2 * math.pi * angle / angles
        x = 4 * math.cos(theta)
        y = 4 * math.sin(theta)
        z = 4 * math.sin(elevation)
        cam.location = (x, y, z)
        cam.rotation_euler = (elevation, 0, theta + math.pi/4)
        bpy.context.view_layer.update()
        render_path = os.path.join(
            output_dir, f"{os.path.splitext(obj_file)[0]}_{angle:02d}.png"
        )
        bpy.context.scene.render.filepath = render_path
        bpy.ops.render.render(write_still=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print(f"Рендер завершён: {obj_file}")

print("Всё! Все объекты из models_dir отрендерены с прозрачным фоном.")
