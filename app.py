from flask import Flask, request, jsonify
from stockfish import Stockfish
import concurrent.futures

from flask_cors import CORS 

stockfish = Stockfish(path="./stockfish_ubuntu/stockfish-ubuntu-x86-64")

allowed_origins = [
    "http://localhost:3000",
    "https://chess-analysis.vercel.app/",
    "https://chess-analysis-git-main-25zeeshan.vercel.app/",
    "https://chess-analysis-kckrgt0mn-25zeeshan.vercel.app/"
]

app = Flask(__name__)
CORS(app, origins=allowed_origins)
cors = CORS(app, resources={
    r"/get_moves": {
        "origins": allowed_origins
}})

@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()
        headers = resp.headers
        headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Replace with your frontend domain
        headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Specify allowed headers
        headers['Access-Control-Allow-Methods'] = 'POST'  # Specify allowed methods
        return resp

@app.route('/get_moves', methods=['POST'])
def get_moves():
    data = request.get_json()
    fen = data['position']

    print('POST called')
    # Use ThreadPoolExecutor to run Stockfish calculations concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(calculate_moves, fen)
        best_move, evaluation = future.result()

    res = {"best_moves": best_move, "eval": evaluation}

    return jsonify(res)

def calculate_moves(fen):
    stockfish.set_elo_rating(2500)
    stockfish.set_fen_position(fen)

    best_move = stockfish.get_top_moves(3)
    evaluation = stockfish.get_evaluation()

    return best_move, evaluation

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
