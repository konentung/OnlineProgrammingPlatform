document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('peer-review-form');
    
    form.addEventListener('submit', function (event) {
        event.preventDefault(); // 防止表單默認提交行為

        // 收集所有分數欄位
        const scoreFields = [
            { id: 'id_question_accuracy_score', label: '題目正確性' },
            { id: 'id_complexity_score', label: '複雜度' },
            { id: 'id_practice_score', label: '實踐性' },
            { id: 'id_answer_accuracy_score', label: '答案正確性' },
            { id: 'id_readability_score', label: '可讀性' }
        ];

        let hasError = false;

        // 檢查是否有分數為零
        scoreFields.forEach(fieldData => {
            const field = document.getElementById(fieldData.id);
            if (field && parseInt(field.value) === 0) {
                hasError = true;
                field.classList.add('error'); // 加入錯誤樣式
                alert(`${fieldData.label} 的分數不可為 0，請修改後再提交！`); // 顯示對應錯誤訊息
                field.focus(); // 聚焦到有問題的欄位
                return; // 終止檢查
            } else if (field) {
                field.classList.remove('error'); // 移除錯誤樣式
            }
        });

        if (hasError) {
            return; // 如果有錯誤，停止提交
        }

        const userConfirmed = confirm("確定要提交您的評分嗎？\n提交後將無法修改。");
        if (!userConfirmed) {
            // 如果用戶點擊「取消」，不進行提交
            return;
        }

        // 發送表單資料到後端
        const formData = new FormData(form);
        const url = form.action; // 獲取表單的 action URL

        fetch(url, {
            method: 'POST',
            body: new URLSearchParams(formData), // 將 FormData 轉換為 URL 編碼格式
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // 標識為 AJAX 請求
                'X-CSRFToken': formData.get('csrfmiddlewaretoken') // 提取 CSRF Token
            }
        })
        .then(response => response.json()) // 將伺服器回應解析為 JSON
        .then(data => {
            if (data.success) {
                alert(data.success); // 顯示成功訊息
                window.location.href = '/question/peer_assessment/';
            } else if (data.error) {
                // 如果後端返回錯誤，顯示在表單上方
                let errorDiv = document.getElementById('error-message');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.id = 'error-message';
                    errorDiv.className = 'alert alert-danger mt-3';
                    form.prepend(errorDiv);
                }
                errorDiv.textContent = data.error; // 顯示錯誤訊息
            }
        })
        .catch(error => {
            // 通用錯誤處理
            let errorDiv = document.getElementById('error-message');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.id = 'error-message';
                errorDiv.className = 'alert alert-danger mt-3';
                form.prepend(errorDiv);
            }
            errorDiv.textContent = "提交過程中發生錯誤，請稍後再試。";
        });
    });
});