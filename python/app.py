# Python health check example using Flask
from flask import Flask, Response
import os

app = Flask(__name__)
port = 8080


@app.route('/')
def index():
    return 'Hello, this is code from Python!'


def is_file_exists(file_path):
    return os.path.exists(file_path)


@app.route('/health/readiness')
def readiness():
    if is_file_exists('/tmp/ready'):
        headers = {
            "Content-Type": "application/json",
            "Description": "200 OK, it's ready!"
        }
        return Response("200 OK, it's ready!", status=200, headers=headers)
    else:
        headers = {
            "Content-Type": "application/json",
            "Description": "503 Service unavailable, it's not ready!"
        }
        return Response(
            "503 Service unavailable, it's not ready!",
            status=503,
            headers=headers
        )


@app.route('/health/liveness')
def liveness():
    if is_file_exists('/tmp/ready'):
        headers = {
            "Content-Type": "application/json",
            "Description": "200 OK, it lives!"
        }
        return Response("200 OK, it lives!", status=200, headers=headers)
    else:
        headers = {
            "Content-Type": "application/json",
            "Desscription": "503 Service unavailable, it doesn't live!"
        }
        return Response(
            "503 Service unavailable, it doesn't live!",
            status=503,
            headers=headers
        )


if __name__ == '__main__':
    print(f"Server running on port {port}")
    app.run(host='0.0.0.0', port=port)
