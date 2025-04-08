import { scaleFactor, dialogueData } from "/static/js/constants.js";
import { k } from "/static/js/kaboomCtx.js";
import { displayDialogue, setCamScale, getChapter, getLevel, displayQuestion, displayGameOver } from "/static/js/utils.js";

async function loadChapterFlow(speaker, listener, chapterId, levelName) {
  const res = await fetch(`/api/chapterflow/?speaker=${speaker}&listener=${listener}&chapter_id=${chapterId}&level_name=${levelName}`);
  const data = await res.json();
  if (data.error === "no_flow") {
    player.isInDialogue = false;
    return { flow: [], firstTime: false };
  }
  if (data.error) {
    console.error("Error fetching flow:", data.error);
    return { flow: [], firstTime: false };
  }
  return {
    flow: data.flow || [],
    firstTime: data.first_time,  // ✅ 加上這個欄位
  };
}

function startFlow(flowArray, onFinish) {
  let currentIndex = 0;
  let gameOverHappened = false;

  async function processNext() {
    if (currentIndex >= flowArray.length) {
      if (!gameOverHappened) {
        console.log("✅ flow 全部完成，撈取下一關開頭動畫");
        await startNextChapterOpening();
      }
      if (onFinish) onFinish();
      return;
    }
    const item = flowArray[currentIndex];
    currentIndex++;
  
    if (item.type === "line") {
      const lineText = `${item.speaker}：${item.content}`;
      displayDialogue(lineText, () => {
        processNext();
      }, currentIndex === flowArray.length);
    } else if (item.type === "red_crack" || item.type === "blue_crack") {
      displayQuestion(item, (game_over) => {
        if (game_over) {
          gameOverHappened = true;
          displayGameOver();
        }
        processNext();
      });
    } else {
      processNext();
    }
  }  
  processNext();
}

async function startNextChapterOpening() {
  const res1 = await fetch("/api/chapter/");
  const res2 = await fetch("/api/level/");
  const { chapter_id } = await res1.json();
  const { level_name } = await res2.json();

  const videoRes = await fetch(`/api/get_cutscene_info/?chapter_id=${chapter_id}&level_name=${level_name}`);
  const videoData = await videoRes.json();

  if (videoData.play_video) {
    await playOpeningCutsceneFromUrl(videoData.video_url);
  }
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

async function playOpeningCutsceneFromUrl(videoUrl) {
  return new Promise((resolve) => {
    const container = document.getElementById("cutscene-container");
    const video = document.getElementById("cutscene-video");

    if (!container || !video) return resolve();

    video.src = videoUrl;
    video.load();
    container.style.display = "block";
    console.log("🎬 撥放影片 URL：", videoUrl);

    video.onplay = () => console.log("✅ 影片開始播放");
    video.onended = () => {
      console.log("✅ 影片播放結束");
      container.style.display = "none";
      resolve();
    };
    video.onerror = () => {
      console.warn("❌ 影片播放失敗");
      container.style.display = "none";
      resolve();
    };

    video.onloadeddata = () => {
      video.play().catch((err) => {
        console.warn("影片播放失敗：", err);
        container.style.display = "none";
        resolve();
      });
    };
  });
}

// 載入地圖
k.loadSprite("map", "/static/images/map.png");

// 設定sprites
k.loadSprite("van", "/static/images/Van.png", {
  sliceX: 10,
  sliceY: 9,
  anims: {
    fly: { from: 65, to: 67, loop: true, speed: 3 },
  },
});

k.loadSprite("king", "/static/images/king.png");
k.loadSprite("nan", "/static/images/Nan.png");

k.loadSprite("crack_blue", "/static/images/blue_crack.png");
k.loadSprite("crack_red", "/static/images/red_crack.png");
k.loadSprite("big_crack", "/static/images/big_crack.png");

// 設定背景顏色
k.setBackground(k.Color.fromHex("#000000"));

// 設定視窗大小以及地圖的縮放比例
k.scene("main", async () => {
  const crackRes = await fetch("/api/user_completed_cracks/");
  const crackData = await crackRes.json();
  const completedCracks = crackData.completed_cracks || [];

  const mapData = await (await fetch("/static/json/map.json")).json();
  const layers = mapData.layers;

  const map = k.add([k.sprite("map"), k.pos(0), k.scale(scaleFactor)]);

  let playerPos = k.vec2(0, 0);
  let kingPos = k.vec2(0, 0);
  let nanPos = k.vec2(0, 0);

  for (const layer of layers) {
    if (layer.name === "spawnpoints") {
      for (const entity of layer.objects) {
        if (entity.name === "player") {
          playerPos = k.vec2(
            (map.pos.x + entity.x) * scaleFactor,
            (map.pos.y + entity.y) * scaleFactor
          );
        }
        if (entity.name === "King") {
          // 取得國王的 x 和 y 坐標，並根據 scaleFactor 計算位置
          kingPos = k.vec2(
            (map.pos.x + entity.x) * scaleFactor,
            (map.pos.y + entity.y) * scaleFactor
          );
        }
        if (entity.name === "Nan") {
          // 取得國王的 x 和 y 坐標，並根據 scaleFactor 計算位置
          nanPos = k.vec2(
            (map.pos.x + entity.x) * scaleFactor,
            (map.pos.y + entity.y) * scaleFactor
          );
        }
      }
    }
    if (layer.name === "cracks") {
      for (const entity of layer.objects) {
        if (entity.name.startsWith("crack_blue_")) {
          const crackName = entity.name;
          // ✅ 如果已經完成，就跳過不顯示
          if (completedCracks.includes(crackName)) continue;
          const crackNumber = parseInt(crackName.split("_")[2]);
          if (crackNumber >= 1 && crackNumber <= 4) {
            k.add([
              k.sprite("crack_blue"),
              k.pos(
                (map.pos.x + entity.x) * scaleFactor,
                (map.pos.y + entity.y) * scaleFactor
              ),
              k.scale(0.5),
              k.anchor("center"),
            ]);
          }
        }
    
        if (entity.name.startsWith("crack_red_")) {
          const crackName = entity.name;
          // ✅ 如果已經完成，就跳過不顯示
          if (completedCracks.includes(crackName)) continue;
          const crackNumber = parseInt(crackName.split("_")[2]);
          if (crackNumber >= 1 && crackNumber <= 4) {
            k.add([
              k.sprite("crack_red"),
              k.pos(
                (map.pos.x + entity.x) * scaleFactor,
                (map.pos.y + entity.y) * scaleFactor
              ),
              k.scale(0.55),
              k.anchor("center"),
            ]);
          }
        }
    
        if (entity.name === "big_crack" && entity.visible === true) {
          const crackName = entity.name; // Define crackName here for "big_crack"
          // ✅ 如果已經完成，就跳過不顯示
          if (completedCracks.includes(crackName)) continue;
          k.add([
            k.sprite("big_crack"),
            k.pos(
              (map.pos.x + entity.x) * scaleFactor,
              (map.pos.y + entity.y) * scaleFactor
            ),
            k.scale(0.6),
            k.anchor("center"),
          ]);
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

  // 創建國王
  const king = k.add([
    k.sprite("king"),
    k.pos(kingPos),
    k.scale(0.06),
    k.anchor("center"),
    "king",
  ]);

  const nan = k.add([
    k.sprite("nan"),
    k.pos(nanPos),
    k.scale(0.1), 
    k.anchor("center"),
    "nan",
  ]);

  const van = k.add([
    k.sprite("van", { anim: "fly" }),
    k.pos(playerPos.add(50, 50)), // 設定在玩家右後方
    k.scale(1),
    k.anchor("center"),
    "van",
  ]);

  for (const layer of layers) {
    if (layer.name === "boundaries") {
      for (const boundary of layer.objects) {
        // 若物件不可見則跳過處理
        if (boundary.visible === false) continue;

        map.add([
          k.area({
            shape: new k.Rect(k.vec2(0), boundary.width, boundary.height),
          }),
          k.body({ isStatic: true }),
          k.pos(boundary.x, boundary.y),
          boundary.name,
        ]);

        // 判斷是否已完成對應裂縫，若是則隱藏該邊界物件
        if (completedCracks.includes(boundary.name)) {
          boundary.visible = false;
          continue;
        }

        if (boundary.name) {
          player.onCollide(boundary.name, () => {
            if (player.isInDialogue) return;

            (async () => {
              player.isInDialogue = true;

              // 優先使用本地 dialogueData
              if (dialogueData && dialogueData[boundary.name]) {
                console.log(`✅ 使用 dialogueData["${boundary.name}"]`);
                const flowData = dialogueData[boundary.name];
                startFlow(flowData, () => {
                  player.isInDialogue = false;
                });
                return;
              }

              // 若本地無資料，則從 API 獲取
              const { chapter_id } = await getChapter();
              const { level_name } = await getLevel();

              const flowData = await loadChapterFlow(
                "player",
                boundary.name,
                chapter_id,
                level_name
              );

              if (flowData.length > 0) {
                startFlow(flowData, () => {
                  player.isInDialogue = false;
                });
              } else {
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

    // 計算目標位置（玩家右後方30像素）
    const targetPos = player.pos.add(-50, -50);

    // 平滑移動到目標位置
    const moveSpeed = 0.03;
    van.pos = van.pos.lerp(targetPos, moveSpeed);

    if (player.direction === "left") {
      van.flipX = true;
    } else if (player.direction === "right") {
      van.flipX = false;
    }
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

  // ✅ 地圖、角色、相機全部就緒後才開始開場對話流程
  async function startAnimation() {
    player.isInDialogue = true;

    const { chapter_id } = await getChapter();
    const { level_name } = await getLevel();
    const res = await fetch(`/api/get_cutscene_info/?chapter_id=${chapter_id}&level_name=${level_name}`);
    const data = await res.json();

    if (data.play_video) {
      await playOpeningCutsceneFromUrl(data.video_url);
    }

    player.isInDialogue = false;
  }

  // ✅ 所有內容載入完才呼叫
  await startAnimation();
});

k.go("main");
