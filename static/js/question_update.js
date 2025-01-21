$(document).ready(function () {
    // 取得當前模式
    var mode = "{{ mode|escapejs }}";

    // 初始化模式
    if (mode === "view") {
        readonlyMode();
    } else {
        editMode();
    }

    function readonlyMode() {
        if (typeof editor !== "undefined") {
            editor.setOption("readOnly", true);
        }
        $("input, textarea").prop("disabled", true);
    }

    function editMode() {
        if (typeof editor !== "undefined") {
            editor.setOption("readOnly", false);
        }
        $("input, textarea").prop("disabled", false);
    }

    // 攔截表單提交
    $("#questionForm").on("submit", function (event) {
        event.preventDefault(); // 防止默認提交

        const formData = new FormData(this);
        const url = this.action;

        fetch(url, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                if (data.status === "success") {
                    alert(data.message); // 提示成功訊息
                    window.location.href = questionListUrl; // 重定向到題目列表
                } else {
                    alert(data.message); // 提示錯誤訊息
                }
            })
            .catch((error) => {
                console.error("提交表單時發生錯誤:", error);
            });
    });
});