export function displayDialogue(text, onDisplayEnd, isLast = false) {
  const dialogueUI = document.getElementById("textbox-container");
  const dialogue = document.getElementById("dialogue");
  const closeBtn = document.getElementById("close");

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
  }, 1);

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

export async function getLine() {
  const lineJson = await fetch(`/api/line/`);
  const lineData = await lineJson.json();
  return lineData;
}

// 顯示問題
// export function displayQuestion(questionData, onFinish) {
//   const dialogueUI = document.getElementById("textbox-container");
//   const dialogue = document.getElementById("dialogue");
//   const questionBox = document.getElementById("question-box");
//   const questionText = document.getElementById("question-text");
//   const redChoices = document.getElementById("red-choices");
//   const blueAnswer = document.getElementById("blue-answer");
//   const feedback = document.getElementById("feedback");

//   const option1Btn = document.getElementById("option1");
//   const option2Btn = document.getElementById("option2");
//   const option3Btn = document.getElementById("option3");
//   const option4Btn = document.getElementById("option4");
//   const blueInput = document.getElementById("blue-input");
//   const blueSubmit = document.getElementById("blue-submit");
//   const closeBtn = document.getElementById("close");

//   // 初始化
//   dialogueUI.style.display = "block";
//   dialogue.innerHTML = ""; // 清空主對話
//   questionBox.style.display = "block";
//   redChoices.style.display = "none";
//   blueAnswer.style.display = "none";
//   feedback.style.display = "none";
//   questionText.innerText = questionData.question || "沒有題目";
//   closeBtn.disabled = true;

//   // 移除舊的 click handler
//   [option1Btn, option2Btn, option3Btn, option4Btn].forEach(btn => btn.onclick = null);
//   blueSubmit.onclick = null;
//   closeBtn.onclick = null;

//   function showFeedback(isCorrect) {
//     feedback.innerText = isCorrect ? "✅ 答對了！" : "❌ 答錯了！";
//     feedback.style.display = "block";
//     closeBtn.disabled = false;
  
//     // ✅ 呼叫 API 更新作答狀態
//     fetch("/api/set_question_cleared/", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         "X-CSRFToken": getCSRFToken(),
//       },
//       body: JSON.stringify({
//         question_id: questionData.id,
//       }),
//     })
//       .then((res) => {
//         if (!res.ok) {
//           console.warn("後端回傳失敗");
//         }
//       })
//       .catch((err) => {
//         console.error("API 呼叫錯誤", err);
//       });
//   }
  
//   // 🔒 CSRF token 抓法（你可以放到 utils.js）
//   function getCSRFToken() {
//     return document.cookie
//       .split(";")
//       .find((cookie) => cookie.trim().startsWith("csrftoken="))
//       ?.split("=")[1];
//   }  

//   if (questionData.type === "red_crack") {
//     redChoices.style.display = "block";
//     option1Btn.innerText = questionData.option1;
//     option2Btn.innerText = questionData.option2;
//     option3Btn.innerText = questionData.option3;
//     option4Btn.innerText = questionData.option4;

//     function check(option) {
//       const isCorrect = option === questionData.answer;
//       showFeedback(isCorrect);
//     }

//     option1Btn.onclick = () => check("option1");
//     option2Btn.onclick = () => check("option2");
//     option3Btn.onclick = () => check("option3");
//     option4Btn.onclick = () => check("option4");

//   } else if (questionData.type === "blue_crack") {
//     blueAnswer.style.display = "block";
//     blueInput.value = "";

//     blueSubmit.onclick = () => {
//       const userAns = blueInput.value.trim();
//       const isCorrect = userAns === questionData.answer;
//       showFeedback(isCorrect);
//     };
//   }

//   closeBtn.onclick = () => {
//     // 結束後清掉 UI
//     dialogueUI.style.display = "none";
//     feedback.style.display = "none";
//     questionBox.style.display = "none";
//     closeBtn.disabled = true;
//     if (onFinish) onFinish();
//   };
// }
export function displayQuestion(questionData, onFinish) {
  const dialogueUI = document.getElementById("textbox-container");
  const dialogue = document.getElementById("dialogue");
  const questionBox = document.getElementById("question-box");
  const questionText = document.getElementById("question-text");
  const redChoices = document.getElementById("red-choices");
  const blueAnswer = document.getElementById("blue-answer");
  const feedback = document.getElementById("feedback");

  const option1Btn = document.getElementById("option1");
  const option2Btn = document.getElementById("option2");
  const option3Btn = document.getElementById("option3");
  const option4Btn = document.getElementById("option4");
  const blueInput = document.getElementById("blue-input");
  const blueSubmit = document.getElementById("blue-submit");
  const closeBtn = document.getElementById("close");

  // 初始化
  dialogueUI.style.display = "block";
  dialogue.innerHTML = ""; // 清空主對話
  questionBox.style.display = "block";
  redChoices.style.display = "none";
  blueAnswer.style.display = "none";
  feedback.style.display = "none";
  questionText.innerText = questionData.question || "沒有題目";
  closeBtn.disabled = true;

  // 移除舊的 click handler
  [option1Btn, option2Btn, option3Btn, option4Btn].forEach(btn => btn.onclick = null);
  blueSubmit.onclick = null;
  closeBtn.onclick = null;

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
      const isCorrect = result.is_correct;
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
    option1Btn.innerText = questionData.option1;
    option2Btn.innerText = questionData.option2;
    option3Btn.innerText = questionData.option3;
    option4Btn.innerText = questionData.option4;

    option1Btn.onclick = () => checkAnswer("option1");
    option2Btn.onclick = () => checkAnswer("option2");
    option3Btn.onclick = () => checkAnswer("option3");
    option4Btn.onclick = () => checkAnswer("option4");

  } else if (questionData.type === "blue_crack") {
    blueAnswer.style.display = "block";
    blueInput.value = "";

    blueSubmit.onclick = () => {
      const userAns = blueInput.value.trim();
      if (!userAns) return;
      checkAnswer(userAns);
    };
  }

  closeBtn.onclick = () => {
    dialogueUI.style.display = "none";
    questionBox.style.display = "none";
    feedback.style.display = "none";
    closeBtn.disabled = true;
    if (onFinish) onFinish();
  };
}