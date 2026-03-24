import asyncio
from telethon import TelegramClient, events
import re

# Telegram API credentials - replace with your own
api_id = 12345678
api_hash = "your_api_hash_here"

client = TelegramClient("session", api_id, api_hash)

#Target chat ID - replace with your desired chat ID (you can get it using @WhatChatIDBot)
TARGET_CHAT = 123456789

layout = {
    '`':'ё','q':'й','w':'ц','e':'у','r':'к','t':'е','y':'н','u':'г',
    'i':'ш','o':'щ','p':'з','[':'х',']':'ъ',
    'a':'ф','s':'ы','d':'в','f':'а','g':'п','h':'р','j':'о','k':'л','l':'д',
    ';':'ж',"'":'э',
    'z':'я','x':'ч','c':'с','v':'м','b':'и','n':'т','m':'ь',
    ',':'б','.':'ю','&':'?'
}

def convert(text):
    return ''.join(layout.get(c.lower(), c) for c in text)

def is_layout(word):
    if len(word) < 1:
        return False

    if not re.fullmatch(r"[a-zA-Z`\[\];',.&]+", word):
        return False

    has_mapped_chars = any(c.lower() in layout for c in word)
    if not has_mapped_chars:
        return False

    converted = convert(word)

    vowels = "аеёиоуыэюя"
    vowel_count = sum(1 for c in converted if c in vowels)

    changed = sum(1 for c in word if c.lower() in layout)

    conversion_rate = changed / len(word)
    
    if conversion_rate > 0.8:
        if len(word) <= 2:
            min_vowels = 0
        else:
            min_vowels = 1
    elif len(word) <= 2:
        if conversion_rate > 0.5:
            min_vowels = 0
        else:
            min_vowels = 1
    elif len(word) <= 3:
        min_vowels = 1
    else:
        min_vowels = 2
    
    return vowel_count >= min_vowels and changed / len(word) > 0.5

@client.on(events.NewMessage(chats=TARGET_CHAT))
async def handler(event):
    text = event.raw_text
    words = text.split()

    new_words = []
    changed_any = False

    for w in words:
        if is_layout(w):
            new_words.append(convert(w))
            changed_any = True
        else:
            new_words.append(w)

    if changed_any:
        await event.reply(" ".join(new_words))

async def main():
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())