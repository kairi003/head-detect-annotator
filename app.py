#!/usr/bin/python3
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from pathlib import Path
import bisect

app = Flask(__name__)
app.config['DATA_DIR'] = 'data'

images_dir = Path(app.static_folder) / 'images'
indexes = [p.stem for p in sorted(images_dir.glob('*.png'))]


@app.before_first_request
def before_first_request():
    data_dir = Path(app.config['DATA_DIR'])
    data_dir.mkdir(exist_ok=True)


@app.route('/')
def root():
    data_dir = Path(app.config['DATA_DIR'])
    tasks = ((idx, (data_dir / f'{idx}.json').exists()) for idx in indexes)
    return render_template('root.html', tasks=tasks)


@app.route('/<string:index>/')
def task(index: str):
    images_dir = Path(app.static_folder) / 'images'
    if not (images_dir / index).with_suffix('.png').exists():
        return '', 404
    
    if len(request.args) > 0:
        i = bisect.bisect_left(indexes, index)
        n = len(indexes)
        if 'prev' in request.args:
            i = max(0, i-1)
        elif 'next' in request.args:
            i = min(n-1, i+1)
        elif 'need' in request.args:
            data_dir = Path(app.config['DATA_DIR'])
            for _ in range(n):
                i = (i + 1) % n
                if not (data_dir / f'{indexes[i]}.json').exists():
                    break
            else:
                return redirect(url_for('root'))
        return redirect(url_for('task', index=indexes[i]))

    return render_template('task.html', index=index)


@app.route('/<string:index>/data.json', methods=['GET', 'PUT'])
def data(index: str):
    data_dir = Path(app.config['DATA_DIR'])
    data_path = data_dir / f'{index}.json'

    if request.method == 'PUT':
        data = request.get_json()
        data_path.write_text(json.dumps(data))
    
    if not data_path.exists():
        return '', 404
    
    data = json.loads(data_path.read_text())
    return jsonify(data)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
