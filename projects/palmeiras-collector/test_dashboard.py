"""
Palmeiras Dashboard - Simple Version
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Palmeiras Dashboard</title>
        <style>
            body { font-family: sans-serif; background: #1a1a1a; color: white; padding: 40px; text-align: center; }
            h1 { color: #0D7A3D; }
            .shield { font-size: 80px; }
        </style>
    </head>
    <body>
        <div class="shield">🏆</div>
        <h1>Palmeiras Dashboard</h1>
        <p>Carregando dados...</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Starting on http://127.0.0.1:5003")
    app.run(host="0.0.0.0", port=5003)
