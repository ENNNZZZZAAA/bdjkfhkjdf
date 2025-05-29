import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageService
from PIL import Image, ImageDraw, ImageFont
import pytesseract

# Указать путь к Tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'D:\PythonWork\tesseract\tesseract.exe'  # путь до tesseract.exe
os.environ['TESSDATA_PREFIX'] = r'D:\PythonWork\tesseract\tessdata'  # путь до папки с .traineddata

# 🔐 Данные Telegram API
api_id = 25003502
api_hash = '3d0b3959d5841404916fcb42aedb9a3a'

# 📥 Источник и цель
source_channels = [-1002578529589]
target_channel = '@sfsdfsffsf'

# 🛠 Папка для временных файлов
TEMP_DIR = "temp_media"
os.makedirs(TEMP_DIR, exist_ok=True)

# 🔄 Слово для замены
TEXT_TO_REPLACE = "car"
REPLACEMENT = "trippple"

# ⚙️ Инициализация клиента
client = TelegramClient('session', api_id, api_hash)

def replace_text_on_image(image_path, target_text, replacement_text):
    try:
        image = Image.open(image_path).convert("RGB")
        text = pytesseract.image_to_string(image, lang='eng')  # Используем английский язык

        if target_text.lower() in text.lower():
            draw = ImageDraw.Draw(image)
            width, height = image.size

            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()

            # Замазка верхней части
            draw.rectangle([(10, 10), (width - 10, 80)], fill='white')
            draw.text((15, 15), replacement_text, font=font, fill='black')

            new_path = os.path.join(TEMP_DIR, "edited_" + os.path.basename(image_path))
            image.save(new_path)
            return new_path

    except Exception as e:
        print(f"❌ Ошибка обработки изображения: {e}")

    return image_path

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    if isinstance(event.message, MessageService):
        return

    msg = event.message

    if msg.media:
        try:
            file_path = await msg.download_media(file=os.path.join(TEMP_DIR, "media.jpg"))
            print(f"📥 Скачан файл: {file_path}")
            edited_path = replace_text_on_image(file_path, TEXT_TO_REPLACE, REPLACEMENT)

            caption_text = msg.text if isinstance(msg.text, str) else None
            await client.send_file(target_channel, edited_path, caption=caption_text)
            print(f"✅ Отправлено: {edited_path}")

            # Удаление временных файлов
            os.remove(file_path)
            if edited_path != file_path:
                os.remove(edited_path)

        except Exception as e:
            print(f"❌ Ошибка с медиа: {e}")

    elif msg.text:
        try:
            await client.send_message(target_channel, msg.text)
            print(f"✉️ Текст: {msg.text[:30]}")
        except Exception as e:
            print(f"❌ Ошибка с текстом: {e}")

async def main():
    print("🚀 Бот запущен...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
