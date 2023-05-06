#!/usr/bin/python3
import os
import re
import json
import bisect
from pathlib import Path
from typing import Optional
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_httpauth import HTTPDigestAuth

app = Flask(__name__)
app.config['DATA_DIR'] = os.environ.get('DATA_DIR', 'data')
app.config['SECRET_KEY'] = password = os.environ.get('PASSWORD', '')
auth = HTTPDigestAuth()

images_dir = Path(app.static_folder) / 'images'
indexes = [p.stem for p in sorted(images_dir.glob('*.png'))]


@auth.get_password
def get_pw(username: Optional[str]) -> Optional[str]:
    if username is None or \
            next(re.finditer(r'\W', username), None) is not None:
        return None
    return password

def get_data_dir(username: str) -> Path:
    data_dir = Path(app.config['DATA_DIR']) / username
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

@app.route('/')
@auth.login_required
def root():
    username = auth.username()
    data_dir = get_data_dir(username)
    tasks = ((idx, (data_dir / f'{idx}.json').exists()) for idx in indexes)
    return render_template('root.html.j2', tasks=tasks, username=username)


@app.route('/<string:index>/')
@auth.login_required
def task(index: str):
    username = auth.username()
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
            data_dir = get_data_dir(username)
            for _ in range(n):
                i = (i + 1) % n
                if not (data_dir / f'{indexes[i]}.json').exists():
                    break
            else:
                return redirect(url_for('root'))
        return redirect(url_for('task', index=indexes[i]))

    return render_template('task.html.j2', index=index, username=username)


@app.route('/<string:index>/data.json', methods=['GET', 'PUT'])
@auth.login_required
def data(index: str):
    username = auth.username()
    data_dir = get_data_dir(username)
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
