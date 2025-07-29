import bpy
import os
import math
from mathutils import Vector

# --- Папки ---
models_dir = "D:/PhaserProjects/life-online/render/your_path/models/"
output_dir = "D:/PhaserProjects/life-online/render/your_path/renders/"

angles = 16
img_size = 128
cam_height = 60  # угол для изометрии

obj_files = [f for f in os.listdir(models_dir) if f.endswith(".obj")]

def get_object_bounds(obj):
    local_bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    xs = [v.x for v in local_bbox]
    ys = [v.y for v in local_bbox]
    zs = [v.z for v in local_bbox]
    center = (
        (min(xs) + max(xs)) / 2,
        (min(ys) + max(ys)) / 2,
        (min(zs) + max(zs)) / 2
    )
    max_dim = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    return center, max_dim

for obj_file in obj_files:
    # Очистить сцену
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Импорт OBJ
    obj_path = os.path.join(models_dir, obj_file)
    bpy.ops.import_scene.obj(filepath=obj_path)
    
    imported_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not imported_meshes:
        print(f"Не найдено объектов типа 'MESH' в файле {obj_file}!")
        continue
    obj = imported_meshes[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Центруем объект в 0,0,0
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)

    # Найдём центр и размер объекта
    center, max_dim = get_object_bounds(obj)

    # --- Камера ---
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.data.lens = 50
    cam.data.type = 'PERSP'

    # --- Рассчитаем оптимальный радиус камеры (расстояние от центра) ---
    # Это геометрия для перспективной камеры: чтобы объект влезал — нужно radius ≈ (max_dim / 2) / tan(FOV/2)
    # В Blender "FOV" по умолчанию ≈ 50мм, а img_size — размер картинки
    fov = cam.data.angle  # поле зрения в радианах
    radius = (max_dim / 2) / math.tan(fov / 2) + 0.5  # + запас

    # --- Освещение ---
    bpy.ops.object.light_add(type='SUN', location=(0,0,10))

    # --- Рендер настройки ---
    bpy.context.scene.render.resolution_x = img_size
    bpy.context.scene.render.resolution_y = img_size
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

    # --- Рендер всех углов ---
    for angle in range(angles):
        theta = 2 * math.pi * angle / angles
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        z = center[2] + math.tan(math.radians(cam_height)) * radius

        cam.location = (x, y, z)
        cam.rotation_euler = (
            math.radians(90-cam_height), 0, theta + math.pi
        )
        bpy.context.view_layer.update()

        render_path = os.path.join(
            output_dir, f"{os.path.splitext(obj_file)[0]}_{angle:02d}.png"
        )
        bpy.context.scene.render.filepath = render_path
        bpy.ops.render.render(write_still=True)

    # --- Удаляем все объекты ---
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print(f"OBJ: {obj_file}, max_dim={max_dim}, center={center}, radius={radius}")
    print(f"Камера: ({x:.2f}, {y:.2f}, {z:.2f}), угол: {math.degrees(theta):.2f}")




