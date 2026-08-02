import os
import json
from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key) if api_key else None

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
        if not client:
            # Demo modunda simüle edilmiş akış yanıtı ver
            user_message = messages[-1]["content"] if messages else ""
            demo_response = (
                f"Merhaba! Ben **semihcim4.0**.\n\n"
                f"Şu anda `.env` dosyasında geçerli bir API anahtarı tanımlanmadığı için **Demo (Simülasyon) Modunda** çalışıyorum. "
                f"Arayüzün ve akış (streaming) yapısının ne kadar akıcı çalıştığını görmeniz için bu yanıtı simüle ediyorum.\n\n"
                f"Yazdığınız mesajı aldım: *\"{user_message}\"*\n\n"
                f"Gerçek Claude yapay zeka yanıtlarını almak için lütfen projenin ana dizinine bir `.env` dosyası oluşturup "
                f"içine `ANTHROPIC_API_KEY=sizin_anahtariniz` şeklinde API anahtarınızı ekleyin ve uygulamayı yeniden başlatın!"
            )
            import time
            # Kelime kelime simüle ederek akış efekti yarat
            words = demo_response.split(" ")
            current_text = ""
            for i, word in enumerate(words):
                space = " " if i > 0 else ""
                current_text += space + word
                yield f"data: {json.dumps({'text': space + word})}\n\n"
                time.sleep(0.05) # Okuma hızında akış simülasyonu
            yield "data: [DONE]\n\n"
            return

        try:
            with client.messages.stream(
                model="claude-3-5-sonnet-20240620",
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
