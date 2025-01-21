document.addEventListener('DOMContentLoaded', function () {
    // 初始化 CodeMirror 編輯器，保存實例
    var editor = CodeMirror.fromTextArea(document.getElementById("answer-editor"), {
        lineNumbers: true,
        mode: "python",
        indentUnit: 4,
        tabSize: 4,
        matchBrackets: true
    });

    // 保存到全局變數以便在其他地方訪問
    window.answerEditor = editor;
});