export function displayDialogue(text, onDisplayEnd, isLast = false) {
  const dialogueUI = document.getElementById("textbox-container");
  const dialogue = document.getElementById("dialogue");
  const closeBtn = document.getElementById("close");
  if (!closeBtn) {
    console.error("找不到 id 為 'close' 的元素");
    return;
  }
  closeBtn.onclick = null;
  closeBtn.disabled = false;
  closeBtn.style.display = "inline-block";
  
  dialogueUI.style.display = "block";
  dialogue.innerHTML = ""; // 清空文字
  let index = 0;
  let currentText = "";
  const intervalRef = setInterval(() => {
    if (index < text.length) {
      currentText += text[index];
      dialogue.innerHTML = currentText;
      index++;
      return;
    }
    clearInterval(intervalRef);
  }, 10);

  function onCloseBtnClick() {
    onDisplayEnd();
    if (isLast) {
      // 最後一句關閉對話框
      dialogueUI.style.display = "none";
    }
    dialogue.innerHTML = "";
    clearInterval(intervalRef);
    closeBtn.removeEventListener("click", onCloseBtnClick);
  }

  closeBtn.addEventListener("click", onCloseBtnClick);

  addEventListener("keypress", (key) => {
    if (key.code === "Enter") {
      closeBtn.click();
    }
  });
}

export function setCamScale(k) {
  const resizeFactor = k.width() / k.height();
  if (resizeFactor < 1) {
    k.camScale(k.vec2(1));
  } else {
    k.camScale(k.vec2(1.5));
  }
}

// 呼叫 API 取得與對話資料
export async function getChapter() {
  const chapterJson = await fetch(`/api/chapter/`);
  const chapterData = await chapterJson.json();
  return chapterData;
}

export async function getLevel() {
  const levelJson = await fetch(`/api/level/`);
  const levelData = await levelJson.json();
  return levelData;
}

// 顯示問題
export function displayQuestion(questionData, onFinish) {
  const dialogueUI = document.getElementById("textbox-container");
  const dialogue = document.getElementById("dialogue");
  const questionBox = document.getElementById("question-box");
  const questionText = document.getElementById("question-text");
  const redChoices = document.getElementById("red-choices");
  const blueAnswer = document.getElementById("blue-answer");
  const bigChoices = document.getElementById("big-choices");
  const feedback = document.getElementById("feedback");

  const redOptionBtns = [
    document.getElementById("red-option1"),
    document.getElementById("red-option2"),
    document.getElementById("red-option3"),
    document.getElementById("red-option4"),
  ];
  const bigOptionBtns = [
    document.getElementById("big-option1"),
    document.getElementById("big-option2"),
    document.getElementById("big-option3"),
    document.getElementById("big-option4"),
  ];
  const blueInput = document.getElementById("blue-input");
  const blueSubmit = document.getElementById("blue-submit");
  const closeBtn = document.getElementById("close");

  // 初始化介面
  dialogueUI.style.display = "block";
  dialogue.innerHTML = "";
  questionBox.style.display = "block";
  redChoices.style.display = "none";
  blueAnswer.style.display = "none";
  bigChoices.style.display = "none";
  feedback.style.display = "none";
  questionText.innerText = questionData.question || "沒有題目";
  closeBtn.disabled = true;

  // 移除舊的 click handler
  [...redOptionBtns, ...bigOptionBtns].forEach(btn => btn.onclick = null);
  blueSubmit.onclick = null;
  closeBtn.onclick = null;

  let gameOverFlag = false;
  let isCorrect = false;  // ✅ 新增：記錄是否答對

  async function checkAnswer(userAnswer) {
    try {
      const res = await fetch("/api/check/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
          question_id: questionData.id,
          question_type: questionData.type,
          user_answer: userAnswer
        })
      });

      const result = await res.json();
      isCorrect = result.is_correct;
      gameOverFlag = result.game_over || false;
      feedback.innerText = isCorrect ? "✅ 答對了！" : "❌ 答錯了！";
      feedback.style.display = "block";
      closeBtn.disabled = false;
    } catch (err) {
      feedback.innerText = "⚠️ 回傳答案失敗";
      feedback.style.display = "block";
      closeBtn.disabled = false;
    }
  }

  function getCSRFToken() {
    return document.cookie.split(";").find(c => c.trim().startsWith("csrftoken="))?.split("=")[1];
  }

  if (questionData.type === "red_crack") {
    redChoices.style.display = "block";
    redOptionBtns.forEach((btn, index) => {
      btn.innerText = questionData[`option${index + 1}`];
      btn.onclick = () => checkAnswer(`option${index + 1}`);
    });
  } else if (questionData.type === "blue_crack") {
    blueAnswer.style.display = "block";
    blueInput.value = "";
    blueSubmit.onclick = () => {
      const userAns = blueInput.value.trim();
      if (!userAns) return;
      checkAnswer(userAns);
    };
  } else if (questionData.type === "big_crack") {
    bigChoices.style.display = "block";
    bigOptionBtns.forEach((btn, index) => {
      btn.innerText = questionData[`option${index + 1}`];
      btn.onclick = () => checkAnswer(`option${index + 1}`);
    });
  }

  closeBtn.onclick = () => {
    dialogueUI.style.display = "none";
    questionBox.style.display = "none";
    feedback.style.display = "none";
    closeBtn.disabled = true;
    if (onFinish) onFinish(gameOverFlag, isCorrect); // ✅ 新增 isCorrect 傳入
  };
}

// 遊戲結束
export function displayGameOver() {
  const gameOverText = "遊戲結束\n感謝您的挑戰！"; // 可自行調整內容
  // 注意：這裡 isLast 設為 false，讓對話框不會自動隱藏
  displayDialogue(gameOverText, () => {
    // 對話播完後顯示選項
    const btnContainer = $(".btn-container");
    btnContainer.empty(); // 清空按鈕容器
    
    // 設定按鈕容器的位置（絕對定位到對話框的左上角）
    btnContainer.css({
      position: "absolute",
      top: "10px",
      left: "10px",
      zIndex: 1000  // 確保在最上層
    });
    
    // 建立並美化按鈕
    const restartBtn = $("<button id='restart-btn'>遊戲重來</button>").css({
      margin: "5px",
      padding: "10px 15px",
      backgroundColor: "#4CAF50",
      color: "#fff",
      border: "none",
      borderRadius: "5px",
      cursor: "pointer"
    });
    
    const homeBtn = $("<button id='home-btn'>回首頁</button>").css({
      margin: "5px",
      padding: "10px 15px",
      backgroundColor: "#2196F3",
      color: "#fff",
      border: "none",
      borderRadius: "5px",
      cursor: "pointer"
    });
    
    const aboutBtn = $("<button id='about-btn'>About</button>").css({
      margin: "5px",
      padding: "10px 15px",
      backgroundColor: "#f44336",
      color: "#fff",
      border: "none",
      borderRadius: "5px",
      cursor: "pointer"
    });
    
    btnContainer.append(restartBtn, homeBtn, aboutBtn);
    
    // 使用者點擊按鈕後先隱藏對話框，然後直接重新載入頁面
    restartBtn.click(async () => {
      $("#textbox-container").hide(); // 隱藏對話框
      try {
        await fetch("/api/reset");
      } catch (e) {
        console.warn("重置失敗：", e);
      }
      window.location.reload(); // 重新載入頁面
    });    
    
    homeBtn.click(async() => {
      $("#textbox-container").hide();
      try {
        await fetch("/api/reset");
      } catch (e) {
        console.warn("重置失敗：", e);
      }
      window.location.href = "/";
    });
    
    aboutBtn.click(async() => {
      $("#textbox-container").hide();
      try {
        await fetch("/api/reset");
      } catch (e) {
        console.warn("重置失敗：", e);
      }
      window.location.href = "/about";
    });
    
  }, false); // isLast 設為 false，避免自動隱藏對話框
}

// 抓取提示詞
export async function getHint(chapter_id, level_name, speaker, listener) {
  try {
    const res = await fetch(`/api/get_hint/?chapter_id=${chapter_id}&level_name=${level_name}&speaker=${speaker}&listener=${listener}`);
    const data = await res.json();
    const hintBox = document.getElementById("game-hint");

    if (data.hint) {
      hintBox.style.opacity = 0; // 先透明
      setTimeout(() => {
        hintBox.textContent = `💡提示：${data.hint}`;
        hintBox.style.transition = "opacity 0.5s ease-in-out";
        hintBox.style.opacity = 1;
      }, 100);
    }
  } catch (err) {
    console.error("❌ 取得提示失敗", err);
  }
}

export async function loadChapterFlow(speaker, listener, chapterId, levelName) {
  const res = await fetch(`/api/chapterflow/?speaker=${speaker}&listener=${listener}&chapter_id=${chapterId}&level_name=${levelName}`);
  const data = await res.json();
  if (data.error === "no_flow") {
    player.isInDialogue = false;
    return { flow: [] };
  }
  if (data.error) {
    console.error("Error fetching flow:", data.error);
    return { flow: []};
  }
  return {
    flow: data.flow || [],
  };
}