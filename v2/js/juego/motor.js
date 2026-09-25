/**
 * **Super Wordle Bros. — el motor del juego. Autor: Joel.**
 *
 * Copiado de su prototipo del 2026-09-23 (`wordlebros.html`) **sin tocar la física, las texturas ni los
 * controles**. Solo cambia lo imprescindible para que viva dentro de la pestaña en vez de en una página
 * suelta, y cada cambio va marcado con `ADAPTACIÓN`:
 *
 *   1. el nivel llega por parámetro — lo genera `domain/superbros.js` a partir de la tabla;
 *   2. se monta en el lienzo de la pestaña y encaja en su ancho;
 *   3. al terminar avisa a la página con el evento `superbros:fin`;
 *   4. **PROPUESTA, no es de Joel**: el pisotón con rebote e impulso. Ver `velocidadParaAltura` e
 *      `impulsoDelRebote`;
 *   5. **PROPUESTA, no es de Joel**: avisa a la página justo antes del primer muro que el salto normal no
 *      sube, para que enseñe el tutorial. Ver `primerMuroQueNecesitaPisoton`.
 *
 * Los PR de Joel sustituyen este fichero. Mientras respeten esas tres costuras —recibir el nivel, montarse
 * donde se le dice, avisar al terminar—, puede cambiar todo lo demás sin que la web se entere.
 * El contrato completo está en `docs/juego-contrato.md`.
 */

/**
 * **ADAPTACIÓN 4 · PROPUESTA, no es de Joel.** La velocidad de salto que sube una altura dada, en píxeles, con
 * el botón mantenido.
 *
 * Existe porque con la física de Joel el salto máximo es 3,52 casillas y una cuadrícula levanta hasta 6, así
 * que un escalón de 4 era un muro: el nivel del 24 de septiembre no se podía terminar. El dueño probó primero
 * con una casilla más y la subió a **5 casillas en total**: con +1 la torre de 6 de Luis solo se pasaba
 * rebotando en el último bloque de Juan con media casilla de margen, y en la práctica no salía.
 *
 * Se calcula en vez de escribirse a mano para que siga subiendo 5 casillas aunque Joel cambie la gravedad:
 * `h = v² / 2g`, así que `v = √(2·g·h)`.
 */
export function velocidadParaAltura(gravedadSubiendo, altura) {
  return -Math.sqrt(2 * gravedadSubiendo * altura);
}

/**
 * **ADAPTACIÓN 4 · PROPUESTA.** El impulso del rebote: sale disparado **hacia delante** a velocidad de
 * carrera, hacia donde se pulsa o, si no se pulsa nada, hacia donde mira el personaje.
 *
 * Sin esto el rebote solo empujaba hacia arriba. Como el pisotón deja caer en vertical sobre el bloque, se
 * salía del rebote parado en horizontal, y el personaje tardaba 0,27 s en coger velocidad: para entonces ya
 * estaba bajando. Medido en la parte de Luis del 24 de septiembre: solo se pasaba pulsando →, Shift y Espacio
 * en la misma décima de segundo. Con el impulso basta con correr, y la dirección puede llegar hasta 0,3 s
 * tarde.
 */
export function impulsoDelRebote(direccion, mirandoALaIzquierda, velocidadDeCarrera) {
  const hacia = direccion !== 0 ? direccion : mirandoALaIzquierda ? -1 : 1;
  return hacia * velocidadDeCarrera;
}

/**
 * **ADAPTACIÓN 5 · PROPUESTA.** La primera columna con un muro que el salto normal no sube, o `null` si el
 * salto normal basta para todo el nivel. Es donde hace falta el pisotón por primera vez.
 *
 * **Muro es lo apilado desde el suelo sin huecos.** Un bloque que flota encima de un hueco es plataforma, no
 * pared: se pasa por debajo. Contarlo como muro fue el error que hizo creer, al analizar los niveles, que casi
 * todos eran imposibles. Y una columna vacía devuelve al suelo, porque así llega el jugador a cada tramo.
 *
 * Lo calcula el motor con **su propia física** (`escalonMaximo`) y no el generador: si el salto cambia, el
 * aviso sigue saliendo delante del muro correcto.
 */
export function primerMuroQueNecesitaPisoton(blocks, ancho, escalonMaximo) {
  const ocupado = new Set(
    (blocks ?? []).filter((b) => b.type !== "ground").map((b) => `${b.col},${b.row}`),
  );
  let techo = 0;
  for (let col = 0; col < ancho; col += 1) {
    let alto = 0;
    while (ocupado.has(`${col},${alto + 1}`)) alto += 1;
    if (alto === 0) {
      techo = 0;
      continue;
    }
    if (alto - techo > escalonMaximo) return col;
    techo = Math.max(techo, alto);
  }
  return null;
}

/** La altura máxima, en píxeles, de un salto con el botón mantenido. */
export function alturaDeSalto(velocidad, gravedadSubiendo) {
  return (velocidad * velocidad) / (2 * gravedadSubiendo);
}

export function montar(lienzo, level, Phaser) {
  const TILE = 32;
  // ADAPTACIÓN 1 · el nivel llega por parámetro: lo genera la pestaña a partir de la tabla.
  const GROUND_Y = (level.heightTiles + 2) * TILE;
  // el suelo cubre exactamente hasta widthTiles; si el mundo fuera más
  // ancho que eso, habría un tramo sin suelo por el que el jugador podría caerse
  const WORLD_WIDTH = level.widthTiles * TILE;
  const WORLD_HEIGHT = GROUND_Y + TILE * 2;

  // Controles al estilo Super Mario Bros.: aceleración progresiva con tope
  // andando/corriendo, patinazo al girar, y salto de altura variable según
  // cuánto se mantenga pulsado el botón.
  const WALK_SPEED = 180;
  const RUN_SPEED = 300;
  const ACCEL_WALK = 800;
  const ACCEL_RUN = 1100;
  const SKID_DECEL = 1200;
  const JUMP_VELOCITY = -520;
  const RISE_GRAVITY_HELD = 1200;
  const RISE_GRAVITY_RELEASED = 2600;
  const FALL_GRAVITY = 4200;
  const MAX_FALL_SPEED = 550;

  // ADAPTACIÓN 4 · PROPUESTA — el pisotón. En el aire, ↓ o S: se cae en picado. Si al tocar suelo se pulsa
  // Espacio dentro de la ventana, el rebote sube PISOTON_CASILLAS desde donde se pisa. La ventana es corta a
  // propósito: tiene que costar, porque el muro alto es un reto que el grupo pone con sus propias partidas.
  const PISOTON_VENTANA = 0.1;
  const PISOTON_CASILLAS = 5; // decisión del dueño; el número que Joel ajustaría
  const REBOTE_VELOCITY = velocidadParaAltura(RISE_GRAVITY_HELD, PISOTON_CASILLAS * TILE);

  // Coyote time: sigue dejando saltar un instante después de dejar el
  // suelo. Input buffer: recuerda una pulsación de salto un instante antes
  // de aterrizar. Entre los dos absorben los parpadeos de detección de
  // suelo y hacen que el salto se sienta siempre fiable.
  const CONFETTI_EMOJIS = ["🍑", "🦜", "🌷", "📐", "🌀"];

  const COYOTE_TIME = 0.1;
  const JUMP_BUFFER = 0.12;

  function toPixel(col, row) {
    return { x: col * TILE + TILE / 2, y: GROUND_Y - row * TILE };
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = (seconds % 60).toFixed(1).padStart(4, "0");
    return `${m}:${s}`;
  }

  function makeTextures(scene) {
    const g = scene.add.graphics();

    const drawBlock = (fill, border) => {
      g.clear();
      g.fillStyle(fill, 1);
      g.fillRect(0, 0, TILE, TILE);
      g.lineStyle(2, border, 1);
      g.strokeRect(1, 1, TILE - 2, TILE - 2);
    };

    drawBlock(0x3fae4a, 0x276b2c);
    g.generateTexture("block-green", TILE, TILE);
    drawBlock(0xe98a2b, 0xa85e15);
    g.generateTexture("block-orange", TILE, TILE);
    drawBlock(0x6b7280, 0x3f4551);
    g.generateTexture("block-ground", TILE, TILE);

    g.clear();
    g.fillStyle(0xffe066, 1);
    g.fillCircle(TILE / 2, TILE / 2, TILE / 3);
    g.lineStyle(2, 0xb8960a, 1);
    g.strokeCircle(TILE / 2, TILE / 2, TILE / 3);
    g.generateTexture("star", TILE, TILE);

    g.clear();
    g.fillStyle(0xdd3f5b, 1);
    g.fillRect(TILE / 2 - 2, 0, 4, TILE * 2);
    g.fillTriangle(TILE / 2 + 2, 2, TILE / 2 + 2, TILE * 0.6, TILE, TILE * 0.3);
    g.generateTexture("flag", TILE, TILE * 2);

    g.clear();
    g.fillStyle(0x4c8bf5, 1);
    g.fillRoundedRect(0, 0, TILE * 0.7, TILE, 6);
    g.fillStyle(0xffffff, 1);
    g.fillCircle(TILE * 0.5, TILE * 0.25, 4);
    g.generateTexture("player", TILE * 0.7, TILE);

    g.destroy();
  }

  class MainScene extends Phaser.Scene {
    constructor() {
      super("main");
    }

    preload() {}

    create() {
      this.score = 0;
      this.finished = false;
      this.timeSinceGrounded = 999;
      this.timeSinceJumpPressed = 999;
      this.pisoteando = false; // ADAPTACIÓN 4
      this.tiempoDesdePisoton = 999; // ADAPTACIÓN 4
      // ADAPTACIÓN 5 · dónde avisar del pisotón, calculado con el salto de este mismo motor.
      const escalon = Math.floor(alturaDeSalto(JUMP_VELOCITY, RISE_GRAVITY_HELD) / TILE);
      this.colDelPrimerMuro = primerMuroQueNecesitaPisoton(level.blocks, level.widthTiles, escalon);
      this.pistaDada = false;
      this.timerStarted = false;
      this.elapsedTime = 0;

      makeTextures(this);

      this.blocksGroup = this.physics.add.staticGroup();
      // Los bloques de una torre van pegados unos a otros: si dejamos la
      // colisión activa en las caras internas (donde ya hay otro bloque
      // pegado), Phaser puede "enganchar" al jugador contra esa costura al
      // empujarlo contra la pared. Solo dejamos activa la cara expuesta.
      const blockAt = new Set(level.blocks.map((b) => `${b.col},${b.row}`));
      const hasBlock = (col, row) => blockAt.has(`${col},${row}`);
      for (const b of level.blocks) {
        const { x, y } = toPixel(b.col, b.row);
        const sprite = this.blocksGroup.create(x, y, `block-${b.type}`);
        sprite.body.checkCollision.up = !hasBlock(b.col, b.row + 1);
        sprite.body.checkCollision.down = !hasBlock(b.col, b.row - 1);
        sprite.body.checkCollision.left = !hasBlock(b.col - 1, b.row);
        sprite.body.checkCollision.right = !hasBlock(b.col + 1, b.row);
      }

      for (const l of level.labels) {
        const { x, y } = toPixel(l.col, l.row);
        this.add
          .text(x, y, l.text, {
            fontFamily: "system-ui, sans-serif",
            fontSize: "14px",
            color: "#f3f5fa",
            backgroundColor: "#00000055",
            padding: { x: 4, y: 2 },
          })
          .setOrigin(0, 1);
      }

      this.collectibles = this.physics.add.group({ allowGravity: false, immovable: true });
      for (const c of level.collectibles) {
        const { x, y } = toPixel(c.col, c.row);
        this.collectibles.create(x, y, "star");
      }

      const finishPos = toPixel(level.finish.col, level.finish.row);
      // toPixel da el centro de la celda; la base de la bandera debe ir en
      // el borde inferior de esa celda (justo encima del suelo), no en su centro.
      const flagBaseY = finishPos.y + TILE / 2;
      this.add.image(finishPos.x, flagBaseY, "flag").setOrigin(0.5, 1);
      this.finishZone = this.add.zone(finishPos.x, flagBaseY - TILE, TILE, TILE * 2);
      this.physics.add.existing(this.finishZone, true);

      const start = toPixel(1, 1);
      this.player = this.physics.add.sprite(start.x, start.y - TILE / 2, "player");
      this.player.setCollideWorldBounds(true);
      this.player.body.setSize(TILE * 0.6, TILE * 0.95);

      this.physics.add.collider(this.player, this.blocksGroup);
      this.physics.add.overlap(this.player, this.collectibles, (player, star) => {
        star.destroy();
        this.score += 1;
        this.scoreText.setText(`⭐ ${this.score} / ${level.collectibles.length}`);
      });
      this.physics.add.overlap(this.player, this.finishZone, () => this.onFinish());

      this.cursors = this.input.keyboard.createCursorKeys();
      this.keys = this.input.keyboard.addKeys("W,A,S,D,R,SHIFT");

      this.physics.world.setBounds(0, 0, WORLD_WIDTH, WORLD_HEIGHT);
      this.cameras.main.setBounds(0, 0, WORLD_WIDTH, WORLD_HEIGHT);
      this.cameras.main.startFollow(this.player, true, 0.1, 0.1);

      this.scoreText = this.add
        .text(12, 12, `⭐ 0 / ${level.collectibles.length}`, {
          fontFamily: "system-ui, sans-serif",
          fontSize: "16px",
          color: "#ffffff",
        })
        .setScrollFactor(0);

      this.timerText = this.add
        .text(12, 34, `⏱ ${formatTime(this.elapsedTime)}`, {
          fontFamily: "system-ui, sans-serif",
          fontSize: "16px",
          color: "#ffffff",
        })
        .setScrollFactor(0);
    }

    onFinish() {
      if (this.finished) return;
      this.finished = true;
      // ADAPTACIÓN 3 · avisa a la página, que es quien escribe el texto para el canal.
      lienzo.dispatchEvent(new CustomEvent('superbros:fin', {
        detail: { segundos: this.elapsedTime, estrellas: this.score },
      }));
      this.spawnConfetti();
      const text = `¡Nivel completado!\n⭐ ${this.score} / ${level.collectibles.length}\n⏱ ${formatTime(this.elapsedTime)}`;
      const msg = this.add
        .text(this.cameras.main.width / 2, this.cameras.main.height / 2, text, {
          fontFamily: "system-ui, sans-serif",
          fontSize: "28px",
          color: "#ffffff",
          backgroundColor: "#000000aa",
          padding: { x: 16, y: 10 },
          align: "center",
        })
        .setScrollFactor(0)
        .setOrigin(0.5);
      msg.setDepth(1000);
    }

    // ADAPTACIÓN 4 · el pisotón bien hecho se nota: un destello en el personaje y un abanico de chispas que
    // salen del suelo. Menos de medio segundo, para que acompañe al salto y no lo tape. Usa los tweens igual
    // que el confeti del final, así que no añade nada nuevo al motor.
    celebrarRebote() {
      // Destello: el personaje entero en blanco cálido un instante, y un pequeño estirón hacia arriba.
      this.player.setTintFill(0xfff4a3);
      this.time.delayedCall(180, () => this.player.clearTint());
      this.tweens.add({ targets: this.player, scaleY: 1.25, scaleX: 0.85, duration: 90, yoyo: true });

      const x = this.player.x;
      const y = this.player.y + this.player.displayHeight / 2;
      for (let i = 0; i < 16; i += 1) {
        // Entre 200° y 340°: un abanico hacia arriba, porque en pantalla la y crece hacia abajo.
        const angulo = Phaser.Math.DegToRad(Phaser.Math.Between(200, 340));
        const distancia = Phaser.Math.Between(26, 64);
        const chispa = this.add.rectangle(x, y, 6, 6, i % 3 ? 0xffd23f : 0xffffff).setDepth(900);
        this.tweens.add({
          targets: chispa,
          x: x + Math.cos(angulo) * distancia,
          y: y + Math.sin(angulo) * distancia,
          alpha: 0,
          scale: 0.3,
          duration: Phaser.Math.Between(380, 620),
          ease: "Quad.easeOut",
          onComplete: () => chispa.destroy(),
        });
      }
    }

    spawnConfetti() {
      const width = this.cameras.main.width;
      const height = this.cameras.main.height;

      const spawnOne = () => {
        const emoji = Phaser.Utils.Array.GetRandom(CONFETTI_EMOJIS);
        const x = Phaser.Math.Between(0, width);
        const piece = this.add.text(x, -30, emoji, { fontSize: "28px" }).setScrollFactor(0).setDepth(999);

        this.tweens.add({
          targets: piece,
          y: height + 30,
          x: x + Phaser.Math.Between(-40, 40),
          angle: Phaser.Math.Between(-180, 180),
          duration: Phaser.Math.Between(2000, 3500),
          ease: "Sine.easeIn",
          onComplete: () => piece.destroy(),
        });
      };

      this.time.addEvent({ delay: 25, repeat: 99, callback: spawnOne });
    }

    update(time, delta) {
      if (Phaser.Input.Keyboard.JustDown(this.keys.R)) {
        this.scene.restart();
        return;
      }

      const dt = delta / 1000;
      const onGround = this.player.body.blocked.down || this.player.body.touching.down;

      // ADAPTACIÓN 4 · el pisotón: en el aire se cae en picado, una sola vez por salto.
      const bajaPulsada =
        Phaser.Input.Keyboard.JustDown(this.cursors.down) || Phaser.Input.Keyboard.JustDown(this.keys.S);
      if (bajaPulsada && !onGround && !this.pisoteando) {
        this.pisoteando = true;
        this.player.setVelocityY(MAX_FALL_SPEED);
      }
      const leftDown = this.cursors.left.isDown || this.keys.A.isDown;
      const rightDown = this.cursors.right.isDown || this.keys.D.isDown;
      const running = this.cursors.shift.isDown || this.keys.SHIFT.isDown;
      const dirPressed = leftDown ? -1 : rightDown ? 1 : 0;

      if (!this.timerStarted && dirPressed !== 0) this.timerStarted = true;

      // Aceleración/deceleración: mismas reglas en suelo y en aire, como en
      // el Mario original. Girar mientras te mueves rápido frena con más
      // fuerza (patinazo) que soltar sin más la tecla.
      const maxSpeed = running ? RUN_SPEED : WALK_SPEED;
      const accel = running ? ACCEL_RUN : ACCEL_WALK;
      const vx = this.player.body.velocity.x;
      let nextVx;
      if (dirPressed === 0) {
        nextVx = vx > 0 ? Math.max(vx - accel * dt, 0) : Math.min(vx + accel * dt, 0);
      } else {
        const sameDirection = vx === 0 || Math.sign(vx) === dirPressed;
        if (sameDirection) {
          nextVx = Phaser.Math.Clamp(vx + dirPressed * accel * dt, -maxSpeed, maxSpeed);
        } else {
          nextVx = vx + dirPressed * SKID_DECEL * dt;
        }
        this.player.setFlipX(dirPressed < 0);
      }
      this.player.setVelocityX(nextVx);

      // Salto de altura variable: gravedad suave mientras subes con el
      // botón pulsado, más fuerte si lo sueltas antes de tiempo o al caer.
      // Se aplica también en el suelo (con un empujón hacia abajo minúsculo)
      // para que Phaser siga detectando el contacto con el bloque cada
      // frame; si no, "touching.down" parpadea y el salto falla a veces.
      const rising = this.player.body.velocity.y < 0;
      const holdingJump = this.cursors.space.isDown;
      const gravity = rising ? (holdingJump ? RISE_GRAVITY_HELD : RISE_GRAVITY_RELEASED) : FALL_GRAVITY;
      const nextVy = this.player.body.velocity.y + gravity * dt;
      this.player.setVelocityY(Math.min(nextVy, MAX_FALL_SPEED));

      this.timeSinceGrounded += dt;
      this.timeSinceJumpPressed += dt;
      this.tiempoDesdePisoton += dt; // ADAPTACIÓN 4
      if (this.pisoteando && onGround) {
        this.pisoteando = false;
        this.tiempoDesdePisoton = 0;
      }
      if (onGround) this.timeSinceGrounded = 0;
      if (Phaser.Input.Keyboard.JustDown(this.cursors.space)) this.timeSinceJumpPressed = 0;

      if (this.timeSinceGrounded <= COYOTE_TIME && this.timeSinceJumpPressed <= JUMP_BUFFER) {
        // ADAPTACIÓN 4 · dentro de la ventana del pisotón, el rebote sube PISOTON_CASILLAS.
        const rebote = this.tiempoDesdePisoton <= PISOTON_VENTANA;
        this.player.setVelocityY(rebote ? REBOTE_VELOCITY : JUMP_VELOCITY);
        // ADAPTACIÓN 4 · el rebote sale hacia delante a velocidad de carrera, y se nota que ha salido bien.
        if (rebote) {
          this.player.setVelocityX(impulsoDelRebote(dirPressed, this.player.flipX, RUN_SPEED));
          this.celebrarRebote();
        }
        this.tiempoDesdePisoton = 999;
        this.timeSinceGrounded = 999;
        this.timeSinceJumpPressed = 999;
      }

      // ADAPTACIÓN 5 · dos columnas antes del primer muro que pide pisotón, avisar a la página. Una vez.
      if (!this.pistaDada && this.colDelPrimerMuro !== null
          && this.player.x >= (this.colDelPrimerMuro - 2) * TILE) {
        this.pistaDada = true;
        lienzo.dispatchEvent(new CustomEvent("superbros:pista-pisoton", {
          detail: { col: this.colDelPrimerMuro },
        }));
      }

      if (this.timerStarted && !this.finished) {
        this.elapsedTime += dt;
        this.timerText.setText(`⏱ ${formatTime(this.elapsedTime)}`);
      }
    }
  }

  const config = {
    type: Phaser.AUTO,
    // ADAPTACIÓN 2 · se monta en el lienzo de la pestaña y encaja en su ancho: el prototipo era una
    // página a pantalla completa, y dentro de la web tiene que convivir con la cabecera y el móvil.
    parent: lienzo,
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    // Y el teclado se escucha **en el lienzo, no en toda la ventana**: el juego solo reacciona cuando tiene
    // el foco, y fuera de él las flechas vuelven a mover la página en vez de mover al personaje. La rueda
    // no se la queda Phaser —por defecto sí, y con el puntero encima del juego la página no se movía—: el
    // juego no la usa, y la página tiene que poder bajarse con el ratón.
    input: { keyboard: { target: lienzo }, mouse: { preventDefaultWheel: false } },
    width: Math.min(WORLD_WIDTH, 960),
    height: Math.min(WORLD_HEIGHT, 540),
    backgroundColor: "#87ceeb",
    physics: {
      default: "arcade",
      // la gravedad se gestiona a mano en MainScene.update() para poder
      // variarla según el estado del salto
      arcade: { gravity: { y: 0 }, debug: false },
    },
    scene: [MainScene],
  };

  return new Phaser.Game(config);
}
