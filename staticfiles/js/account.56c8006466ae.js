// 自動附加 CSRF token 到 AJAX 請求
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // 檢查 cookie 是否以 name= 開頭
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        // 只對非 GET/HEAD/OPTIONS/TRACE 的請求附加 CSRF token
        if (!(/^GET|HEAD|OPTIONS|TRACE$/i.test(settings.type)) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function(){
    // 頁面載入後自動顯示浮動視窗
    $(".modal-overlay").fadeIn();
    $(".modal-custom").fadeIn();

    // 點擊關閉按鈕或遮罩層關閉視窗
    $(".close-btn, .modal-overlay").click(function(){
        $(".modal-overlay").fadeOut();
        $(".modal-custom").fadeOut();
        window.location.href = "/";
    });

    // 處理註冊表單，會從後端收到 JSON 格式的回應
    $('#register-form').on('submit', function(e) {
        e.preventDefault(); // 阻止表單預設提交
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serialize(),
            dataType: 'json',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success) {
                    alert("註冊成功！");
                    window.location.href = '/accounts/login/';  // 根據需求跳轉到登入頁或其他頁面
                } else if (response.message) {
                    alert(response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', error);
            }
        });
    });

    // 處理登入表單，會從後端收到 JSON 格式的回應
    $('#login-form').on('submit', function(e) {
        e.preventDefault(); // 阻止表單預設提交
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serialize(),
            dataType: 'json',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.message) {
                    alert(response.message);
                } else if (response.redirect_url) {
                    window.location.href = response.redirect_url;
                } else {
                    window.location.href = '/';
                }
            },
            error: function(xhr, status, error) {
                // 如果返回 403，可能是 CSRF token 驗證失敗
                if (xhr.status === 403) {
                    alert("CSRF token 驗證失敗，請重新整理頁面。");
                } else {
                    console.error('AJAX error:', error);
                }
            }
        });
    });
});