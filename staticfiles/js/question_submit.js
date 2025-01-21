$(document).ready(function () {
    $('#submit-btn').click(function () {
        if (window.answerEditor) {
            window.answerEditor.save(); // 同步 CodeMirror 的內容
        }

        var formData = $('#question-form').serialize();
        var isConfirmed = confirm("確定要提交嗎？");
        if (isConfirmed) {
            $.ajax({
                url: questionCreateUrl,
                type: "POST",
                data: formData,
                success: function (response) {
                    if (response.success) {
                        alert(response.message || "提交成功！");
                        window.location.href = '/'; // 成功後跳轉至首頁
                    } else {
                        displayFieldErrors(response.errors);
                    }
                },
                error: function (xhr) {
                    var response = xhr.responseJSON;
                    if (response && response.errors) {
                        displayFieldErrors(response.errors); // 處理具體錯誤
                    } else {
                        alert("提交過程中發生錯誤，請稍後再試！");
                    }
                }
            });
        }
    });

    // 顯示具體欄位錯誤
    function displayFieldErrors(errors) {
        let errorMessage = "提交失敗，以下欄位有錯誤：\n";
        for (const [fieldLabel, messages] of Object.entries(errors)) {
            errorMessage += `${fieldLabel}：`;
            messages.forEach(message => {
                errorMessage += `${message}\n`; // 顯示每個錯誤細節
            });
        }
        alert(errorMessage); // 使用 alert 顯示所有錯誤訊息
    }
});