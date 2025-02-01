document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const messagesList = document.getElementById('messages-list');
    const messagesBox = document.getElementById('messages-box'); // 訊息區域
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content'); // CSRF Token 引用

    // 初次載入時滾動到底部
    const initialScroll = () => {
        messagesBox.scrollTop = messagesBox.scrollHeight;
    };

    initialScroll();  // 初始化時滾動到底部

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault(); // 防止頁面刷新

        const message = messageInput.value.trim();
        if (message === '') return; // 避免空訊息

        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams({
                'question': message
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error:', data.error); // 錯誤處理
                return;
            }

            // 新增使用者訊息到畫面
            const userMessage = document.createElement('div');
            userMessage.className = 'message-pair';
            const userMessageText = document.createElement('p');
            userMessageText.className = 'message-sent';
            userMessageText.textContent = data.message;
            userMessage.appendChild(userMessageText);
            messagesList.appendChild(userMessage);

            // 新增 AI 回應到畫面
            const aiMessage = document.createElement('div');
            aiMessage.className = 'message-pair';
            const aiMessageText = document.createElement('p');
            aiMessageText.className = 'message-received';
            aiMessageText.textContent = data.response;
            aiMessage.appendChild(aiMessageText);
            messagesList.appendChild(aiMessage);

            // 清空輸入框
            messageInput.value = '';

            // 滾動到底部
            messagesBox.scrollTop = messagesBox.scrollHeight;

            // 重新設定 URL 或刷新頁面
            history.pushState(null, null, window.location.href); // 保持當前 URL
        })
        .catch(error => {
            console.error('Error:', error);
            alert('發生錯誤，請稍後再試');
        });
    });

    // 監聽訊息區域的變動，當有新訊息時滾動到底部
    const scrollToBottom = () => {
        messagesBox.scrollTop = messagesBox.scrollHeight;
    };

    // 當 DOM 變更時，滾動到最新訊息
    messagesList.addEventListener('DOMNodeInserted', scrollToBottom);
});