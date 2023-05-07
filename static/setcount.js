fetch('/user-progress.json')
  .then(res => res.json())
  .then(({content}) => document.querySelector('#counter').textContent = content);
