const config = {
    type: Phaser.AUTO,
    width: 1280,
    height: 720,
    parent: 'game-container',
    physics: {
        default: 'arcade',
        arcade: { debug: false }
    },
    scene: {
        preload: preload,
        create: create,
        update: update
    }
};

const game = new Phaser.Game(config);

let player, cursors, camera, map, housesLayer, roadsLayer;

function preload() {
    // Карта
    this.load.tilemapTiledJSON('map', 'assets/daggerton2.json');
    // Тайлсеты
    this.load.image('Дома', 'assets/medium_1_png_1.png');
    this.load.image('дороги', 'assets/roads_test.png');
    // Спрайты героя
    this.load.spritesheet('casual_hero_down', 'assets/casual_hero_down.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('casual_hero_up', 'assets/casual_hero_up.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('casual_hero_left', 'assets/casual_hero_left.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('casual_hero_right', 'assets/casual_hero_right.png', { frameWidth: 64, frameHeight: 64 });
}

function create() {
    map = this.make.tilemap({ key: 'map' });

    let housesTileset = map.addTilesetImage('Дома', 'Дома');
    let roadsTileset = map.addTilesetImage('дороги', 'дороги');

    // Дома увеличены в 2 раза
    housesLayer = map.createLayer('Слой тайлов 1', housesTileset, 0, 0);
    housesLayer.setScale(2);

    // Дороги без масштаба
    roadsLayer = map.createLayer('Слой тайлов 2', roadsTileset, 0, 0);

    // Коллизии
    housesLayer.setCollisionByExclusion([-1]);
    this.physics.world.setBounds(0, 0, map.widthInPixels * 2, map.heightInPixels * 2);

    // Игрок
    player = this.physics.add.sprite(200, 200, 'casual_hero_down', 0);
    player.setSize(40, 50).setOffset(12, 10);
    this.physics.add.collider(player, housesLayer);

    // Камера
    camera = this.cameras.main;
    camera.startFollow(player);
    camera.setBounds(0, 0, map.widthInPixels * 2, map.heightInPixels * 2);

    // Клавиши
    cursors = this.input.keyboard.createCursorKeys();
    this.input.keyboard.addKeys('W,A,S,D');

    // Анимации
    this.anims.create({ key: 'walk_down', frames: this.anims.generateFrameNumbers('casual_hero_down', { start: 0, end: 5 }), frameRate: 10, repeat: -1 });
    this.anims.create({ key: 'walk_up', frames: this.anims.generateFrameNumbers('casual_hero_up', { start: 0, end: 5 }), frameRate: 10, repeat: -1 });
    this.anims.create({ key: 'walk_left', frames: this.anims.generateFrameNumbers('casual_hero_left', { start: 0, end: 5 }), frameRate: 10, repeat: -1 });
    this.anims.create({ key: 'walk_right', frames: this.anims.generateFrameNumbers('casual_hero_right', { start: 0, end: 5 }), frameRate: 10, repeat: -1 });
}

function update() {
    let speed = 200;
    let vx = 0, vy = 0;

    if (cursors.left.isDown || this.input.keyboard.addKey('A').isDown) {
        vx = -speed;
        player.anims.play('walk_left', true);
    } else if (cursors.right.isDown || this.input.keyboard.addKey('D').isDown) {
        vx = speed;
        player.anims.play('walk_right', true);
    } else if (cursors.down.isDown || this.input.keyboard.addKey('S').isDown) {
        vy = speed;
        player.anims.play('walk_down', true);
    } else if (cursors.up.isDown || this.input.keyboard.addKey('W').isDown) {
        vy = -speed;
        player.anims.play('walk_up', true);
    } else {
        player.anims.stop();
    }

    player.setVelocity(vx, vy);
}
