import os
from dotenv import load_dotenv
from flask import Flask
from pyngrok import ngrok

# .envファイルから環境変数を読み込む
load_dotenv()

auth_token = os.environ.get("NGROK_AUTH_TOKEN")
if not auth_token:
    raise ValueError("環境変数 NGROK_AUTH_TOKEN が設定されていません。")

# ngrokの認証トークンを設定
ngrok.set_auth_token(auth_token)

# Flaskアプリを定義
app = Flask(__name__)

# "/"パスでシンプルなHTMLを返す
@app.route("/")
def index():
    return """
    <html>
        <head><title>Simple Page</title></head>
        <body>
            <h1>Hello, Flask!</h1>
            <p>This is a simple HTML page served by Flask.</p>
        </body>
    </html>
    """

# ---- Flaskサーバー起動 (port=5000) ----
public_url = ngrok.connect(5000)
print(" * ngrok tunnel URL:", public_url.public_url)

# Flaskアプリを起動
app.run(port=5000)
