import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
import anthropic

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Sen semihcim4.0'sın — ileri teknoloji ile inşa edilmiş, son derece zeki ve çok yönlü bir yapay zeka asistanısın.

Özellikler:
- Adın: semihcim4.0
- Kişiliğin: Profesyonel, samimi, yardımcı ve zeki
- Yeteneklerin: Kod yazma, analiz, yaratıcı yazarlık, soru cevaplama, problem çözme ve çok daha fazlası
- Dil: Kullanıcının diline göre yanıt ver (Türkçe veya İngilizce)
- Stil: Net, anlaşılır ve bilgilendirici yanıtlar ver

Her zaman kibar, yardımsever ve profesyonel ol. Karmaşık konuları sade bir dille açıkla."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])

    def generate():
        try:
            with client.messages.stream(
                model="claude-opus-4-7",
                max_tokens=4096,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=messages,
                thinking={"type": "adaptive"},
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'text': text})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
