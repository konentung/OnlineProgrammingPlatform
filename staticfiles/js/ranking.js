function showTab(tabId) {
    // 隱藏所有選項卡
    document.querySelectorAll('.ranking-tab').forEach(function(tab) {
        tab.style.display = 'none';
    });

    // 顯示選中的選項卡
    document.getElementById(tabId).style.display = 'block';
}