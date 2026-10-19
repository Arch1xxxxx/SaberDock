"""Translate application-owned messages without changing user content or paths."""
import json
import os
from pathlib import Path

MESSAGES = json.loads(Path(__file__).with_name('messages.json').read_text(encoding='utf-8'))

def tr(message):
    if os.environ.get('SABERDOCK_LANGUAGE', 'en') == 'zh-Hans':
        return message
    return MESSAGES[message]
