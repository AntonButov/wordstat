(function () {
  'use strict';

  // Бургер-меню
  var burger = document.getElementById('burger-btn');
  var nav = document.getElementById('nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      nav.classList.toggle('is-open');
    });
  }

  // Форма отправляется на Formspree (action в разметке)
})();
