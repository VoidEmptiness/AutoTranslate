import asyncio 
from telethon import TelegramClient, events
import re
import requests

api_id = 12345678
api_hash = "you_api_hash"
client = TelegramClient("session", api_id, api_hash)
TARGET_CHAT = 123456789

layout = {
    '`':'ё','q':'й','w':'ц','e':'у','r':'к','t':'е','y':'н','u':'г',
    'i':'ш','o':'щ','p':'з','[':'х',']':'ъ',
    'a':'ф','s':'ы','d':'в','f':'а','g':'п','h':'р','j':'о','k':'л','l':'д',
    ';':'ж',"'":'э',
    'z':'я','x':'ч','c':'с','v':'м','b':'и','n':'т','m':'ь',
    ',':'б','.':'ю','&':'?'
}

EN_SHORT_STOPWORDS = {
    "of", "in", "at", "on", "to", "by", "up", "an", "is", "it", "as", "be", "or", "if", "and", "the"
}

def convert(text):
    result = []
    for c in text:
        lower = c.lower()
        if lower in layout:
            new_char = layout[lower]
            if c.isupper():
                new_char = new_char.upper()
            result.append(new_char)
        else:
            result.append(c)
    return ''.join(result)

def is_english_word(word):
    try:
        clean_word = re.sub(r"[^\w]", "", word.lower())
        if not clean_word:
            return False
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{clean_word}", timeout=2)
        return response.status_code == 200
    except:
        return False

def is_layout(word):
    if len(word) < 1:
        return False
    if not re.fullmatch(r"[a-zA-Z`\[\];',.&\-!]+", word):
        return False
    has_mapped_chars = any(c.lower() in layout for c in word)
    if not has_mapped_chars:
        return False

    word_lower = word.lower()
    if len(word) <= 2:
        if word_lower in EN_SHORT_STOPWORDS:
            return False
        return True

    if is_english_word(word):
        return False

    converted = convert(word)
    vowels = "аеёиоуыэюя"
    vowel_count = sum(1 for c in converted if c in vowels)
    changed = sum(1 for c in word if c.lower() in layout)
    conversion_rate = changed / len(word)
    return vowel_count >= 1 and conversion_rate > 0.5

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
