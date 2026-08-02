# Semihcim AI Asistanı 🤖

Merhaba! Kendi günlük işlerimde bana yardımcı olması için Anthropic API'sini (Claude) kullanarak geliştirdiğim kişisel yapay zeka asistanım **Semihcim 4.0**'a hoş geldiniz.

Sürekli farklı platformlarda sekmeler arasında kaybolmaktan sıkıldığım için, kendi arayüzümle çalışan, tamamen kendi kurallarıma (sistem promptu) uyan bir asistan yapmak istedim. Flask ile hızlıca bir arka uç yazıp, arayüzü de olabildiğince temiz tutmaya çalıştım. 

## 🌟 Özellikler

- **Kişiselleştirilmiş Sistem Promptu:** Asistan tamamen benim belirlediğim karakterde ve profesyonellikte yanıtlar veriyor.
- **Akıcı Yanıtlar (Streaming):** Uzun metinleri beklememek için yanıtları stream (akış) şeklinde alacak şekilde ayarladım. Yazıldıkça ekranda beliriyor.
- **Minimalist Arayüz:** Göz yormayan, sadece sohbete odaklanabileceğim sade bir tasarım kullandım.
- **Hafif ve Hızlı:** Flask sayesinde arkada gereksiz hiçbir ağırlık yok.

## 🚀 Kurulum

Projeyi bilgisayarınızda çalıştırmak isterseniz şu adımları izleyebilirsiniz:

1. **Gereksinimleri Yükleyin:**
   Python 3.8+ kullandığınızdan emin olun. Terminalde proje klasörüne gidip kütüphaneleri kurun:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Anahtarınızı Ayarlayın:**
   Anthropic API'sini kullandığım için bir API anahtarına ihtiyacınız var. Ortam değişkeni (environment variable) olarak sisteminize eklemeniz gerekiyor:
   - Windows (CMD): `set ANTHROPIC_API_KEY=sizin_anahtariniz`
   - Windows (PowerShell): `$env:ANTHROPIC_API_KEY="sizin_anahtariniz"`
   - Mac/Linux: `export ANTHROPIC_API_KEY=sizin_anahtariniz`

3. **Uygulamayı Başlatın:**
   ```bash
   python app.py
   ```

4. **Tarayıcıda Açın:**
   Uygulama çalıştıktan sonra tarayıcınızda `http://127.0.0.1:5000` adresine giderek asistanla konuşmaya başlayabilirsiniz.

## 🛠️ Kullandığım Teknolojiler

- **Python & Flask:** Arka uç (backend) geliştirme ve API yönlendirmeleri için.
- **Anthropic SDK:** Claude modellerine bağlanmak için.
- **HTML/CSS/JS:** Arayüz (frontend) tasarımı ve asenkron veri iletişimi için.

## 💡 Neden Geliştirdim?

Sıradan ChatGPT veya Claude web arayüzlerini kullanmak yerine, bana özel olarak yanıt veren, benim dilimi ve ihtiyaçlarımı anlayan bir asistana ihtiyacım vardı. Ayrıca API entegrasyonu ve web socket/streaming mantığını pratik etmek için çok güzel bir proje oldu. Kodları inceleyip kendi asistanınızı yapmak için dilediğiniz gibi kullanabilirsiniz!

## 📄 Lisans

Projeyi tamamen açık kaynak olarak bırakıyorum. İstediğiniz gibi kurcalayabilir, bozabilir, kendi kişisel asistanınızı yaratabilirsiniz. Kolay gelsin!
