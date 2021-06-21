from itertools import chain
from qbit import CLIENT as QBT_CLIENT
from slave import get_all_result
from flask.json import jsonify
import random

from flask import Flask, request

app = Flask(__name__)


@app.route('/opencd')
def work():
    logger = []
    header = []
    use_json = request.args.get("json", "0")
    to_qbit = request.args.get("qbit", "0")
    category = request.args.get("category", "crawler-opencd")

    result = get_all_result(logger=logger)
    for x in logger:
        app.logger.warning(x)

    if use_json == "1":
        return jsonify(result)
    if to_qbit == "1":
        logger.insert(0, f'qBittorrent: {QBT_CLIENT.app.version}')
        header.append(f"<h1>Total {len(result)} torrents:</h1>")
        if len(result) > 0:
            try:
                QBT_CLIENT.torrents_add(urls=result, category=category)
                header.append("<h2>qBittorrent added successfully!</h2>")
            except Exception as err:
                header.append(f"<h2>qBittorrent add failed {err}</h2>")
        else:
            header.append("<h2>No torrent added.</h2>")

    header.append("<h2>Log</h2>")
    return "<br/>".join(chain(header, result, logger))


@app.route('/test')
def test():
    use_json = request.args.get("json", "0")
    data = set((str(random.randint(0, 100000) + x * x) for x in range(10)))
    if use_json == "1":
        return jsonify(list(data))
    return "<br/>".join(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=25000)
