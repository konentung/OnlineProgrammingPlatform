document.addEventListener('DOMContentLoaded', function() {
    // 限制描述顯示行數
    var descriptions = document.querySelectorAll('[id^="description-"]');
    descriptions.forEach(function(descriptionElement) {
        descriptionElement.style.display = '-webkit-box';
        descriptionElement.style.webkitBoxOrient = 'vertical';
        descriptionElement.style.webkitLineClamp = '5';
        descriptionElement.style.overflow = 'hidden';

        // 如果內容不足 5 行，則添加換行符填充顯示空間
        var lineHeight = parseFloat(window.getComputedStyle(descriptionElement).lineHeight);
        var minHeight = lineHeight * 5;
        while (descriptionElement.offsetHeight < minHeight) {
            descriptionElement.innerText += '\n';
        }
    });

    // 篩選難易度功能
    var difficultyFilters = document.querySelectorAll('.difficulty-filter');
    var questionItems = document.querySelectorAll('.question-item');

    difficultyFilters.forEach(function(filter) {
        filter.addEventListener('click', function() {
            var selectedDifficulty = this.getAttribute('data-difficulty');

            questionItems.forEach(function(item) {
                if (selectedDifficulty === 'all' || item.getAttribute('data-difficulty') === selectedDifficulty) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});