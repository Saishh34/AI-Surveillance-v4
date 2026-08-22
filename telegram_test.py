"""
Quick manual check that your Telegram bot is configured correctly.
Reads BOT_TOKEN / CHAT_ID from config.py instead of hardcoding them
again, so there's only ever one place your credentials live.

Usage:
    python telegram_test.py            -> sends a text message
    python telegram_test.py --photo    -> also sends a test photo
                                           (needs a test.jpg in this folder)
"""

import sys

import requests

import config


def test_text_message():
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": config.CHAT_ID,
            "text": "Telegram Bot is connected successfully!"
        }
    )

    print("[Text] Status Code:", response.status_code)
    print("[Text] Response:", response.text)


def test_photo_message(photo_path="test.jpg"):
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"

    try:
        with open(photo_path, "rb") as photo:
            response = requests.post(
                url,
                data={
                    "chat_id": config.CHAT_ID,
                    "caption": "📸 Test image from Python"
                },
                files={
                    "photo": photo
                }
            )

        print("[Photo] Status Code:", response.status_code)
        print("[Photo] Response:", response.text)

    except FileNotFoundError:
        print(f"[Photo] Skipped - '{photo_path}' not found in this folder.")


if __name__ == "__main__":
    test_text_message()

    if "--photo" in sys.argv:
        test_photo_message()
