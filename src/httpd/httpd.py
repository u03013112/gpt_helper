from flask import Flask, request, jsonify
from flask_cors import CORS

import sys
sys.path.append('/')

from src.askDemo import askFor2022WinterOlympics
from src.httpd.downloadFromGithub import DownloadFromGithub
from src.httpd.status import getStatus

app = Flask(__name__)
CORS(app)  # 这将使您的Flask应用支持CORS

askFor2022WinterOlympics = askFor2022WinterOlympics()

@app.route('/api/openai/chat/completions', methods=['POST'])
def handle_post_request():
    if request.method == 'OPTIONS':
        # 预检请求，直接返回200状态码
        return '', 200
    request_body = request.get_json()
    print("Received request body:", request_body)
    
    content = askFor2022WinterOlympics.ask2(request_body['messages'])

    return content

@app.route('/api/reflush', methods=['GET'])
def reflush():
    askFor2022WinterOlympics.reflush()
    return 'ok'

@app.route('/download_github_project', methods=['POST'])
def download_github_project():
    # 获取GitHub项目的URL
    github_url = request.json['github_url']
    
    # 下载项目
    downloader = DownloadFromGithub(github_url)
    downloader.start()

    return 'ok'

@app.route('/get_status', methods=['GET'])
def get_status():
    df = getStatus()
    return df.to_json(orient='records')

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8000)
