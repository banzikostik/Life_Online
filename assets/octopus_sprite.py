from PIL import Image, ImageDraw
import math

def draw_hero(frame, direction):
    frame_size = 64
    img = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Центр тела и смещение по направлению (кадр полностью вписывается!)
    center = {
        'down': (32, 35),
        'up': (32, 31),
        'left': (30, 33),
        'right': (34, 33)
    }[direction]
    cx, cy = center

    # "Подпрыгивание" — оживляем походку
    bounce = int(3 * math.sin(frame * math.pi / 3))

    # Наклон — поворот героя влево/вправо
    tilt = {
        'down': 0,
        'up': 0,
        'left': -0.18,
        'right': 0.18
    }[direction]

    # Ушки казуально-мультяшные, меньше и ближе к голове
    for sign in [-1, 1]:
        ex = cx + sign * 15 + int(sign * 5 * math.sin(tilt))
        ey = cy - 18 + bounce
        # внешнее ухо (овал)
        draw.ellipse([ex-10, ey-8, ex+8, ey+18], fill=(120, 185, 255, 240), outline=(80, 135, 220, 255))
        # внутреннее ухо
        draw.ellipse([ex-7, ey-2, ex+4, ey+13], fill=(255, 190, 230, 220))

    # Голова — чуть меньше, мультяшно-казуально
    draw.ellipse([cx-15, cy-19+bounce, cx+15, cy+13+bounce], fill=(90,170,255,255), outline=(80,135,220,255))

    # Тело — округлое, чуть вытянуто
    draw.ellipse([cx-10, cy+6+bounce, cx+10, cy+24+bounce], fill=(110,210,255,255), outline=(80,135,220,255))

    # Руки — казуальные, покачиваются при ходьбе
    hand_angle = math.pi/4 + 0.22 * math.sin(frame*1.2)
    for sign in [-1, 1]:
        hx = cx + sign * 12 + int(sign*2*math.sin(frame*1.2 + sign))
        hy = cy + 6 + bounce + int(4*math.cos(frame*1.3 + sign))
        draw.ellipse([hx-4, hy, hx+4, hy+12], fill=(90,170,255,255), outline=(80,135,220,255))

    # Ноги — двигаются в такт
    for sign in [-1, 1]:
        foot_x = cx + sign*4 + int(sign * 2 * math.sin(frame + sign))
        foot_y = cy + 20 + bounce + int(2*math.sin(frame*2 + sign))
        draw.ellipse([foot_x-3, foot_y, foot_x+3, foot_y+10], fill=(70,130,210,255), outline=(80,135,220,255))

    # Глаза — большие, мультяшные
    if direction == 'left':
        draw.ellipse([cx-10, cy-9+bounce, cx-3, cy+4+bounce], fill=(255,255,255,255))
        draw.ellipse([cx-6, cy-4+bounce, cx-2, cy+1+bounce], fill=(0,0,0,255))
    elif direction == 'right':
        draw.ellipse([cx+3, cy-9+bounce, cx+10, cy+4+bounce], fill=(255,255,255,255))
        draw.ellipse([cx+6, cy-4+bounce, cx+10, cy+1+bounce], fill=(0,0,0,255))
    else:
        draw.ellipse([cx-7, cy-9+bounce, cx, cy+4+bounce], fill=(255,255,255,255))
        draw.ellipse([cx+1, cy-9+bounce, cx+8, cy+4+bounce], fill=(255,255,255,255))
        draw.ellipse([cx-5, cy-4+bounce, cx-1, cy+1+bounce], fill=(0,0,0,255))
        draw.ellipse([cx+3, cy-4+bounce, cx+7, cy+1+bounce], fill=(0,0,0,255))

    # Мультяшная улыбка
    draw.arc([cx-7, cy+2+bounce, cx+7, cy+11+bounce], start=10, end=170, fill=(180,70,110,255), width=2)
    # Зубки
    for dx in range(-5, 6, 4):
        draw.rectangle([cx+dx-1, cy+9+bounce, cx+dx+1, cy+11+bounce], fill=(255,255,255,230))

    return img

frame_size = 64
frames = 6
directions = ['down', 'left', 'right', 'up']

for direction in directions:
    sprite_sheet = Image.new("RGBA", (frame_size * frames, frame_size), (0, 0, 0, 0))
    for f in range(frames):
        img = draw_hero(f, direction)
        sprite_sheet.paste(img, (f * frame_size, 0))
    sprite_sheet.save(f"casual_hero_{direction}.png")
    print(f"Saved casual_hero_{direction}.png")

print("\nГотово! Файлы: casual_hero_down.png, casual_hero_left.png, casual_hero_right.png, casual_hero_up.png\n")
