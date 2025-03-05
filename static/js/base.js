// navbar 滑動隱藏
$(document).ready(function() {
    var $navbar = $('header');
    var showThreshold = 50; // 當滑鼠在螢幕上方 100px 以內時觸發
    var hideDelay = 50;      // 離開 navbar 後等待 200 毫秒再隱藏
    var hideTimer;

    // 初始隱藏 navbar
    $navbar.hide();

    // 當滑鼠移動到螢幕上方區域時
    $(document).mousemove(function(event) {
        if (event.pageY < showThreshold) {
            // 若有先前設定的隱藏計時器，先清除
            clearTimeout(hideTimer);
            // 如果 navbar 尚未顯示，則以動畫方式滑下來
            if (!$navbar.is(':visible')) {
                $navbar.stop(true, true).slideDown(1000);
            }
        }
    });

    // 當滑鼠離開 navbar 區域時
    $navbar.mouseleave(function() {
        // 設定一個延遲，等待一段時間後再隱藏 navbar
        hideTimer = setTimeout(function() {
            $navbar.stop(true, true).slideUp(1000);
        }, hideDelay);
    });

    // 當滑鼠進入 navbar 時，取消隱藏計時器
    $navbar.mouseenter(function() {
        clearTimeout(hideTimer);
    });
});