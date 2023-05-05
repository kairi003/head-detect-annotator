// Set Counter
document.querySelector('#counter').textContent = +(localStorage['counter']??0);


// Define History Stack
const history = [];


// Create Annotorious Instance
const anno = Annotorious.init({
  image: 'image',
  allowEmpty: true,
  disableEditor: true,
});


// Set Default Annotations from data.json or latest
fetch('data.json').then(res=>res.json()).then(data => {
  anno.setAnnotations(data);
  document.body.classList.add('done');
  document.querySelector('#status').textContent = 'done';
  history.push(data);
}).catch(err => {
  const data = JSON.parse(localStorage['annotations'] ?? '[]');
  anno.setAnnotations(data);
  history.push(data);
});


// Before Unload, save annotations to LocalStorage
window.addEventListener('beforeunload', event => {
  anno.saveSelected();
  localStorage['annotations'] = JSON.stringify(anno.getAnnotations());
});


// Register Hotkeys


hotkeys('d,ctrl+z,space,enter', (event, handler) => {
  switch (handler.key) {
    // d: delete selected annotation
    case 'd':
      anno.removeAnnotation(anno.getSelected());
      history.push(anno.getAnnotations());
      break;
    
    // ctrl+z: undo
    case 'ctrl+z':
      if (history.length > 1) {
        history.pop();
        anno.setAnnotations(history[history.length-1]);
      }
      break;
    
    case 'space':
    case 'enter':
      document.querySelector('#submit').click();
      break
  }
});


// Set Clear Button
document.querySelector('#clear').addEventListener('click', event => {
  anno.clearAnnotations();
  history.push(anno.getAnnotations());
});

// Set Submit Button
document.querySelector('#submit').addEventListener('click', event => {
  anno.saveSelected();
  fetch('data.json', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(anno.getAnnotations())
  }).then(res => {
    localStorage['counter'] = +(localStorage['counter']??0) + 1;
    window.location.search = '?need';
  });
});

anno.on('deleteAnnotation', (annotation) => {
  console.log('deleteAnnotation', annotation);
  history.push(anno.getAnnotations());
});
anno.on('createAnnotation', (annotation, overrideId) => {
  console.log('createAnnotation', annotation);
  history.push(anno.getAnnotations());
});
anno.on('updateAnnotation', (target) => {
  console.log('updateAnnotation', target);
  history.push(anno.getAnnotations());
});