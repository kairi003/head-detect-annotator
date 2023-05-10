#!/usr/bin/python3
from dataclasses import dataclass
import os
import re
import json
import bisect
import random
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


def get_data_dir(username: Optional[str] = None) -> Path:
    if username is None:
        return Path(app.config['DATA_DIR'])
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

@app.route('/favicon.ico/')
def favicon():
    return '', 404

@app.route('/<string:index>/')
@auth.login_required
def task(index: str):
    username = auth.username()
    images_dir = Path(app.static_folder) / 'images'
    data_dir = get_data_dir(username)

    if index == 'random':
        candidate = [idx for idx in indexes if not (data_dir / f'{idx}.json').exists()]
        if len(candidate) == 0:
            return redirect(url_for('root'))
        idx = random.choice(candidate)
        return redirect(url_for('task', index=idx))

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
            for _ in range(n):
                i = (i + 1) % n
                if not (data_dir / f'{indexes[i]}.json').exists():
                    break
            else:
                return redirect(url_for('root'))
        return redirect(url_for('task', index=indexes[i]))

    return render_template('task.html.j2', index=index, username=username)


@app.route('/<string:index>/total-progress.json', methods=['GET'])
@auth.login_required
def total_progress(index: str):
    data_dir = get_data_dir(None)
    num = sum(1 for _ in data_dir.glob(f'./*/{index}.json'))
    return jsonify({'type': 'total-progress', 'index': index, 'content': num})


@app.route('/user-progress.json', methods=['GET'])
@auth.login_required
def user_progress():
    username = auth.username()
    data_dir = get_data_dir(username)
    num = sum(map(bool, data_dir.iterdir()))
    return jsonify({'type': 'user-progress', 'content': num})


@app.route('/ranking/', methods=['GET'])
@auth.login_required
def ranking():
    username = auth.username()
    data_dir = get_data_dir(None)

    @dataclass(order=True)
    class User:
        score: int
        name: str

        def __init__(self, dir: Path):
            self.name = dir.name
            self.score = sum(1 for _ in dir.iterdir())

    def generate_ranking(sorted_users: list[User]):
        rank = 0
        pre_score = None
        for idx, user in enumerate(sorted_users):
            if user.score != pre_score:
                rank = idx + 1
            yield rank, user.name, user.score
            pre_score = user.score

    sorted_users = sorted(map(User, data_dir.iterdir()), reverse=True)
    ranking_iter = generate_ranking(sorted_users)

    return render_template('ranking.html.j2', ranking=ranking_iter, username=username)


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
