document.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('.menu-button');
  const nav = document.querySelector('.nav-links');
  if (menu && nav) menu.addEventListener('click', () => nav.classList.toggle('open'));

  const answer = document.querySelector('#answer');
  const count = document.querySelector('#char-count');
  if (answer && count) {
    const update = () => { count.textContent = `${answer.value.length} / 5000`; };
    answer.addEventListener('input', update); update();
  }

  const timer = document.querySelector('#timer');
  if (timer) {
    let seconds = 120;
    const tick = () => { const minutes = String(Math.floor(seconds / 60)).padStart(2, '0'); const rest = String(seconds % 60).padStart(2, '0'); timer.textContent = `${minutes}:${rest}`; if (seconds > 0) seconds -= 1; };
    tick(); window.setInterval(tick, 1000);
  }
});
