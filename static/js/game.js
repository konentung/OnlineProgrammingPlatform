import { scaleFactor } from "/static/js/constants.js";
import { k } from "/static/js/kaboomCtx.js";
import { displayDialogue, setCamScale, getChapter, getLevel, displayQuestion } from "/static/js/utils.js";

async function loadChapterFlow(speaker, listener, chapterId, levelName) {
  const res = await fetch(`/api/chapterflow/?speaker=${speaker}&listener=${listener}&chapter_id=${chapterId}&level_name=${levelName}`);
  const data = await res.json();
  if (data.error) {
    console.error("Error fetching flow:", data.error);
    return [];
  }
  return data.flow || [];
}

function startFlow(flowArray, onFinish) {
  let currentIndex = 0;

  function processNext() {
    if (currentIndex >= flowArray.length) {
      if (onFinish) onFinish();
      return;
    }
    const item = flowArray[currentIndex];
    currentIndex++;

    if (item.type === "line") {
      // 「講話者對聆聽者說：內容」
      const lineText = `${item.speaker}：${item.content}`;

      // 你原本的 displayDialogue(文字, callback, isLast)
      const isLast = (currentIndex === flowArray.length);
      displayDialogue(lineText, () => {
        processNext();
      }, isLast);

    } else if (item.type === "red_crack" || item.type === "blue_crack") {
      // 顯示題目UI (略)
      displayQuestion(item, () => {
        processNext();
      });

    } else {
      // 其他 / unknown
      processNext();
    }
  }

  processNext();
}

// 建立spritesheet
k.loadSprite("spritesheet", "/static/images/spritesheet.png", {
  sliceX: 39,
  sliceY: 31,
  anims: {
    "idle-down": 936,
    "walk-down": { from: 936, to: 939, loop: true, speed: 8 },
    "idle-side": 975,
    "walk-side": { from: 975, to: 978, loop: true, speed: 8 },
    "idle-up": 1014,
    "walk-up": { from: 1014, to: 1017, loop: true, speed: 8 },
  },
});

// 載入地圖
k.loadSprite("map", "/static/images/map.png");

// 設定背景顏色
k.setBackground(k.Color.fromHex("#000000"));

// 設定視窗大小以及地圖的縮放比例
k.scene("main", async () => {
  const mapData = await (await fetch("/static/json/map.json")).json();
  const layers = mapData.layers;

  const map = k.add([k.sprite("map"), k.pos(0), k.scale(scaleFactor)]);

  let playerPos = k.vec2(1261, 550); // 預設玩家位置

  for (const layer of layers) {
    if (layer.name === "spawnpoints") {
      for (const entity of layer.objects) {
        if (entity.name === "player") {
          playerPos = k.vec2(
            (map.pos.x + entity.x) * scaleFactor,
            (map.pos.y + entity.y) * scaleFactor
          );
        }
      }
    }
  }

  // 只執行一次 k.add()，並且使用 spawnpoints 設定的位置
  const player = k.add([
    k.sprite("spritesheet", { anim: "idle-down" }),
    k.area({
      shape: new k.Rect(k.vec2(0, 3), 10, 10),
    }),
    k.body(),
    k.anchor("center"),
    k.pos(playerPos),
    k.scale(scaleFactor),
    {
      speed: 150,
      direction: "down",
      isInDialogue: false,
    },
    "player",
  ]);

  for (const layer of layers) {
    if (layer.name === "boundaries") {
      for (const boundary of layer.objects) {
        map.add([
          k.area({
            shape: new k.Rect(k.vec2(0), boundary.width, boundary.height),
          }),
          k.body({ isStatic: true }),
          k.pos(boundary.x, boundary.y),
          boundary.name,
        ]);
        if (boundary.name) {
          player.onCollide(boundary.name, () => {
            (async () => {
              player.isInDialogue = true;

              // 1) 取得章節
              const { chapter_id } = await getChapter();
              const { level_name } = await getLevel();

              // 2) 撈取新的 flow
              const flowData = await loadChapterFlow("player", boundary.name, chapter_id, level_name);

              // 3) 播放流程
              if (flowData.length > 0) {
                startFlow(flowData, () => {
                  player.isInDialogue = false;
                });
              } else {
                // 如果 flowData 為空，fallback 到舊的對話?
                // or 直接關閉對話
                player.isInDialogue = false;
              }
            })();
          });
        }
      }
    }
  }

  setCamScale(k);

  k.onResize(() => {
    setCamScale(k);
  });

  k.onUpdate(() => {
    k.camPos(player.worldPos().x, player.worldPos().y - 100);
  });

  k.onMouseDown((mouseBtn) => {
    if (mouseBtn !== "left" || player.isInDialogue) return;

    const worldMousePos = k.toWorld(k.mousePos());
    player.moveTo(worldMousePos, player.speed);

    const mouseAngle = player.pos.angle(worldMousePos);

    const lowerBound = 50;
    const upperBound = 125;

    if (
      mouseAngle > lowerBound &&
      mouseAngle < upperBound &&
      player.curAnim() !== "walk-up"
    ) {
      player.play("walk-up");
      player.direction = "up";
      return;
    }

    if (
      mouseAngle < -lowerBound &&
      mouseAngle > -upperBound &&
      player.curAnim() !== "walk-down"
    ) {
      player.play("walk-down");
      player.direction = "down";
      return;
    }

    if (Math.abs(mouseAngle) > upperBound) {
      player.flipX = false;
      if (player.curAnim() !== "walk-side") player.play("walk-side");
      player.direction = "right";
      return;
    }

    if (Math.abs(mouseAngle) < lowerBound) {
      player.flipX = true;
      if (player.curAnim() !== "walk-side") player.play("walk-side");
      player.direction = "left";
      return;
    }
  });

  function stopAnims() {
    if (player.direction === "down") {
      player.play("idle-down");
      return;
    }
    if (player.direction === "up") {
      player.play("idle-up");
      return;
    }
    player.play("idle-side");
  }

  k.onMouseRelease(stopAnims);
  k.onKeyRelease(stopAnims);

  k.onKeyDown((key) => {
    const keyMap = [
      k.isKeyDown("right"),
      k.isKeyDown("left"),
      k.isKeyDown("up"),
      k.isKeyDown("down"),
    ];

    let nbOfKeyPressed = 0;
    for (const key of keyMap) {
      if (key) {
        nbOfKeyPressed++;
      }
    }

    if (nbOfKeyPressed > 1) return;
    if (player.isInDialogue) return;

    if (keyMap[0]) {
      player.flipX = false;
      if (player.curAnim() !== "walk-side") player.play("walk-side");
      player.direction = "right";
      player.move(player.speed, 0);
      return;
    }

    if (keyMap[1]) {
      player.flipX = true;
      if (player.curAnim() !== "walk-side") player.play("walk-side");
      player.direction = "left";
      player.move(-player.speed, 0);
      return;
    }

    if (keyMap[2]) {
      if (player.curAnim() !== "walk-up") player.play("walk-up");
      player.direction = "up";
      player.move(0, -player.speed);
      return;
    }

    if (keyMap[3]) {
      if (player.curAnim() !== "walk-down") player.play("walk-down");
      player.direction = "down";
      player.move(0, player.speed);
    }
  });
});

k.go("main");