function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('visible'));
    document.querySelectorAll('.explore-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('visible');
    document.querySelector(`.explore-btn.${id}`).classList.add('active');
  }
  