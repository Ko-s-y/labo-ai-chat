import os
from dotenv import load_dotenv
from flask import Flask, request, session
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

# OpenAIクライアント初期化
client = OpenAI(api_key=api_key)

# ngrok設定
ngrok.set_auth_token(auth_token)
public_url = ngrok.connect(5000)
print(" * ngrok tunnel URL:", public_url.public_url)

# Flaskアプリ
app = Flask(__name__)
app.secret_key = "test-key"  

# フォーム画面
@app.route("/", methods=["GET"])
def index():
    if "messages" not in session:
        session["messages"] = []

    conversation_html = ""
    for msg in session["messages"]:
        role = "あなた" if msg["role"] == "user" else "AI"
        conversation_html += f"<p><strong>{role}:</strong> {msg['content']}</p>"

    return f"""
    <html>
        <body>
            <h2>OpenAIと対話する</h2>
            {conversation_html}
            <form method="post" action="/chat">
                <input type="text" name="message" placeholder="質問を入力してください" style="width:300px;">
                <input type="submit" value="送信">
            </form>
            <form method="post" action="/reset" style="margin-top:10px;">
                <input type="submit" value="会話をリセット">
            </form>
        </body>
    </html>
    """

# チャット処理
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("message")
    if not user_input:
        return "メッセージが入力されていません。", 400

    # 初期化されてなければ履歴作成
    if "messages" not in session:
        session["messages"] = []

    # ユーザーの入力を履歴に追加
    session["messages"].append({"role": "user", "content": user_input})

    try:
        # OpenAIに履歴ごと送信
        response = client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=session["messages"]
        )
        reply = response.choices[0].message.content

        # AIの返信を履歴に追加
        session["messages"].append({"role": "assistant", "content": reply})
        session.modified = True  # セッションを更新

        return "<script>window.location.href='/'</script>"  # リダイレクトして表示更新
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 500

# 履歴をクリアするエンドポイント
@app.route("/reset", methods=["POST"])
def reset():
    session.pop("messages", None)
    return "<script>window.location.href='/'</script>"

# アプリ起動
app.run(port=5000)
