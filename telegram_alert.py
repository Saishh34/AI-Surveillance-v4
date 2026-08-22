import requests

import config


def send_telegram_photo(photo_path, caption):
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"

    try:
        with open(photo_path, "rb") as photo:

            files = {
                "photo": photo
            }

            data = {
                "chat_id": config.CHAT_ID,
                "caption": caption
            }

            response = requests.post(
                url,
                files=files,
                data=data
            )

            print("Status Code:", response.status_code)
            print("Response:", response.text)

            if response.status_code == 200:
                print("Telegram Alert Sent")
            else:
                print("Telegram Error:", response.text)

    except Exception as e:
        print("Telegram Exception:", e)
