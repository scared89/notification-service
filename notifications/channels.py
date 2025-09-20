import random
import time


def send_email(notification):
    time.sleep(1)  # имитация задержки
    if random.random() < 0.8:  # 80% успеха
        return True, None
    return False, "SMTP error"


def send_sms(notification):
    time.sleep(1)
    if random.random() < 0.6:  # 60% успеха
        return True, None
    return False, "SMS gateway timeout"


def send_telegram(notification):
    time.sleep(1)
    if random.random() < 0.9:  # 90% успеха
        return True, None
    return False, "Telegram API error"
