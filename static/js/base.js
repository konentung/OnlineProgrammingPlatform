$(document).ready(function() {
    const toggleBtn = $('.settings-toggle');
    const menu = $('.settings-menu');

    toggleBtn.on('click', function() {
    toggleBtn.toggleClass('open');
    menu.slideToggle();
    });
});