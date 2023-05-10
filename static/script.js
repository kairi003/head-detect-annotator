// Define History Stack
const history = [];

fetch('total-progress.json')
  .then(res => res.json())
  .then(({content}) => document.querySelector('#total').textContent = content);


// Create Annotorious Instance
const anno = Annotorious.init({
  image: 'image',
  allowEmpty: true,
  disableEditor: true,
});

const username = document.querySelector('meta[name="username"]')?.content;
anno.setAuthInfo({
  id: 'http://sf.cs.it-chiba.ac.jp/' + username,
  displayName: username
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
  const data = anno.getAnnotations().filter(x=>x.id);
  localStorage['annotations'] = JSON.stringify(data);
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
document.querySelector('#clear').addEventListener('click', async event => {
  await anno.cancelSelected();
  anno.clearAnnotations();
  history.push(anno.getAnnotations());
});

// Set Submit Button
document.querySelector('#submit').addEventListener('click', async event => {
  await anno.saveSelected();
  const src = document.querySelector('#image').src;
  const data = anno.getAnnotations();
  data.forEach(ant => ant.target.source = src);
  
  await fetch('data.json', {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  localStorage['counter'] = +(localStorage['counter']??0) + 1;
  window.location.search = '?next';
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