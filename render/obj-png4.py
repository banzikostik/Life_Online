import bpy
import os
import math
from mathutils import Vector

# --- Папки ---
models_dir = "D:/PhaserProjects/life-online/render/your_path/models/"
output_dir = "D:/PhaserProjects/life-online/render/your_path/renders/"

angles = 16
img_size = 256
elevation = math.radians(35.264)   # изометрия

def look_at(obj_camera, target):
    direction = Vector(target) - obj_camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()

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

obj_files = [f for f in os.listdir(models_dir) if f.endswith(".obj")]

# --- Рендер через Eevee (как в игре) ---
bpy.context.scene.render.engine = 'BLENDER_EEVEE'

for obj_file in obj_files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj_path = os.path.join(models_dir, obj_file)
    mtl_path = obj_path.replace('.obj', '.mtl')  # MTL тот же путь, что и OBJ

    # --- Импорт OBJ+MTL, принудительно разрешая материалы ---
    bpy.ops.import_scene.obj(
        filepath=obj_path,
        use_smooth_groups=False,
        use_split_objects=True,
        use_split_groups=True,
        use_groups_as_vgroups=False,
        use_image_search=True,   # ищет все картинки рядом!
        split_mode='ON',
        axis_forward='-Z',
        axis_up='Y'
    )

    imported_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not imported_meshes:
        print(f"Не найдено объектов типа 'MESH' в файле {obj_file}!")
        continue
    obj = imported_meshes[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)

    center, max_dim = get_object_bounds(obj)

    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.data.lens = 50
    cam.data.type = 'PERSP'
    cam.data.lens_unit = 'MILLIMETERS'

    radius = max(4, max_dim * 1.2)
    bpy.ops.object.light_add(type='SUN', location=(0,0,10))
    bpy.context.scene.render.resolution_x = img_size
    bpy.context.scene.render.resolution_y = img_size
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

    # --- ВКЛЮЧАЕМ режим рендера "МАТЕРИАЛЫ"/Eevee ---
   # for area in bpy.context.screen.areas:
    #    if area.type == 'VIEW_3D':
     #       for space in area.spaces:
      #          if space.type == 'VIEW_3D':
       #             space.shading.type = 'MATERIAL'
        #            break

    for angle in range(angles):
        theta = 2 * math.pi * angle / angles
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        z = center[2] + radius * math.sin(elevation)
        cam.location = (x, y, z)
        look_at(cam, center)
        bpy.context.view_layer.update()
        render_path = os.path.join(
            output_dir, f"{os.path.splitext(obj_file)[0]}_{angle:02d}.png"
        )
        bpy.context.scene.render.filepath = render_path
        bpy.ops.render.render(write_still=True)

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print(f"Готово: {obj_file} — max_dim={max_dim:.2f} — PNG сохранены.")

print("Всё — все дома отрендерены!")
