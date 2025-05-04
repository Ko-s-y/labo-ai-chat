import os
from dotenv import load_dotenv
from flask import Flask, request
from pyngrok import ngrok
from openai import OpenAI

# 環境変数読み込み
load_dotenv()

# APIキー取得
api_key = os.getenv("OPENAI_API_KEY")
auth_token = os.getenv("NGROK_AUTH_TOKEN")

if not api_key:
    raise ValueError("環境変数 OPENAI_API_KEY が設定されていません。")
if not auth_token:
    raise ValueError("環境変数 NGROK_AUTH_TOKEN が設定されていません。")

# OpenAIクライアント初期化（v1.x 以降用）
client = OpenAI(api_key=api_key)

# ngrok設定
ngrok.set_auth_token(auth_token)
public_url = ngrok.connect(5000)
print(" * ngrok tunnel URL:", public_url.public_url)

# Flaskアプリ
app = Flask(__name__)

# フォーム画面
@app.route("/", methods=["GET"])
def index():
    return """
    <html>
        <body>
            <h2>OpenAIと対話する</h2>
            <form method="post" action="/chat">
                <input type="text" name="message" placeholder="質問を入力してください" style="width:300px;">
                <input type="submit" value="送信">
            </form>
        </body>
    </html>
    """

# 対話エンドポイント
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")
    if not user_input:
        return "メッセージが入力されていません。", 400

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[{"role": "user", "content": user_input}]
        )
        reply = response.choices[0].message.content
        return f"<p><strong>あなた:</strong> {user_input}</p><p><strong>AI:</strong> {reply}</p><a href='/'>戻る</a>"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 500

# アプリ起動
app.run(port=5000)
