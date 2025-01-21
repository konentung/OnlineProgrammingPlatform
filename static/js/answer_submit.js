document.addEventListener('DOMContentLoaded', function () {

    document.querySelector('form').addEventListener('submit', function (event) {
        event.preventDefault();
        const isConfirmed = confirm("確定要提交答案嗎？\n提交答案之後就不可以修改了喔");
        if (isConfirmed) {
            const formData = new FormData(this);
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    window.location.href = '/question/assignment/';
                } else if (data.success) {
                    alert(data.success);
                    window.location.href = '/question/assignment/';
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });
});