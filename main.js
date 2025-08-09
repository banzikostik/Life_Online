// ==== Псевдо-3D без модулей: поворот Q/E, масштаб по расстоянию, depth по y ====

const DIRS = [
  "back",
  "back right",
  "right",
  "front right",
  "front",
  "front left",
  "left",
  "back left",
];

// Позиции домов (просто пример — потом возьмём реальные из карты)
const HOUSES = [
  { x: 300, y: 260, id: 1 },
  { x: 520, y: 320, id: 1 },
  { x: 700, y: 380, id: 1 },
];

let viewIndex = 0;       // 0..7
let keys;
let player;
let buildings = [];
let hud;

const config = {
  type: Phaser.AUTO,
  width: 960,
  height: 540,
  backgroundColor: "#151515",
  physics: { default: "arcade" },
  scene: { preload, create, update }
};

new Phaser.Game(config);

function preload() {
  // грузим по одному варианту (№1) для всех 8 направлений
  for (const dir of DIRS) {
    const key = houseKey(dir, 1);
    const path = `city/small mansion/${dir}/scalled houses/house_${dir.replace(/ /g, "_")}1.png`;
    this.load.image(key, path);
  }
}

function create() {
  // простейший "игрок" — небольшой прямоугольник (центр сцены)
  player = this.add.rectangle(config.width/2, config.height/2, 16, 16, 0x00ff00);
  player.setDepth(player.y);

  // создаём дома с текущим направлением
  const dir = DIRS[viewIndex];
  for (const h of HOUSES) {
    const spr = this.add.image(h.x, h.y, houseKey(dir, h.id));
    spr.setOrigin(0.5, 1);            // «ноги» у земли
    buildings.push(spr);
  }
  updateDepthAndScale(this);

  // клавиши: Q/E — поворот, WASD — движение игрока
  keys = this.input.keyboard.addKeys({
    q: Phaser.Input.Keyboard.KeyCodes.Q,
    e: Phaser.Input.Keyboard.KeyCodes.E,
    w: Phaser.Input.Keyboard.KeyCodes.W,
    a: Phaser.Input.Keyboard.KeyCodes.A,
    s: Phaser.Input.Keyboard.KeyCodes.S,
    d: Phaser.Input.Keyboard.KeyCodes.D,
  });

  // HUD
  hud = this.add.text(8, 8, hudText(), { fontFamily: "monospace", fontSize: "14px", color: "#ffffff" }).setScrollFactor(0);
}

function update(time, delta) {
  // Поворот «камеры»
  if (Phaser.Input.Keyboard.JustDown(keys.q)) {
    viewIndex = (viewIndex + DIRS.length - 1) % DIRS.length;
    swapHouseTextures(this);
  }
  if (Phaser.Input.Keyboard.JustDown(keys.e)) {
    viewIndex = (viewIndex + 1) % DIRS.length;
    swapHouseTextures(this);
  }

  // Движение игрока (чтобы увидеть масштаб/глубину)
  const speed = 180 * (delta / 1000);
  if (keys.a.isDown) player.x -= speed;
  if (keys.d.isDown) player.x += speed;
  if (keys.w.isDown) player.y -= speed;
  if (keys.s.isDown) player.y += speed;
  player.setDepth(player.y);

  updateDepthAndScale(this);
  if (hud) hud.setText(hudText());
}

// ==== helpers ====

function houseKey(dir, id) {
  return `house_${dir.replace(/ /g, "_")}_${id}`;
}

function swapHouseTextures(scene) {
  const dir = DIRS[viewIndex];
  for (const spr of buildings) {
    const id = 1; // пока все дома типа 1
    const key = houseKey(dir, id);
    if (scene.textures.exists(key)) spr.setTexture(key);
  }
}

function updateDepthAndScale(scene) {
  const px = player.x, py = player.y;
  for (const spr of buildings) {
    const dx = spr.x - px, dy = spr.y - py;
    const dist = Math.sqrt(dx*dx + dy*dy);
    // ближе — больше (простая формула, можно настроить)
    const scale = Phaser.Math.Clamp(1.25 - dist / 650, 0.6, 1.25);
    spr.setScale(scale);
    // кто ниже по y — тот «сверху»
    spr.setDepth(spr.y);
  }
}

function hudText() {
  return `Q/E — поворот · WASD — движение\nview: ${DIRS[viewIndex]}`;
}
