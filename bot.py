from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder
import requests
from bs4 import BeautifulSoup
import asyncio
import random
import json
import os

TOKEN = "7988165969:AAEH9_B0L9vN6rKiDCo2ABaiAaYJpxvIli8"
CHANNEL_ID = "@Pspfiles_bot"

BASE_URL = "https://www.gamebrew.org"
LIST_URL = "https://www.gamebrew.org/wiki/List_of_all_PSP_homebrew"

POSTED_FILE = "posted_games.json"

# Load already posted games
if os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "r") as f:
        posted = set(json.load(f))
else:
    posted = set()

def save_posted():
with open(POSTED_FILE, "w") as f:
json.dump(list(posted), f)

def get_game_links():
games = []
try:
res = requests.get(LIST_URL)
soup = BeautifulSoup(res.text, "html.parser")

for link in soup.find_all("a"):
name = link.text.strip()
href = link.get("href")
if href and "/wiki/" in href and name:
full_link = BASE_URL + href
if full_link not in posted:
games.append({
"name": name,
"link": full_link
})
except Exception as e:
print("List error:", e)
return games

def get_download_info(game):
try:
res = requests.get(game["link"])
soup = BeautifulSoup(res.text, "html.parser")

# Download link detection
download = None
for a in soup.find_all("a"):
href = a.get("href", "")
if any(x in href.lower() for x in ["download", "mediafire", "github", ".zip", ".rar"]):
download = href
break

# Description
desc_tag = soup.find("p")
description = desc_tag.text.strip() if desc_tag else "No description available"

# Optional thumbnail
img_tag = soup.find("img")
image_url = BASE_URL + img_tag["src"] if img_tag and img_tag.get("src") else None

return {
"name": game["name"],
"description": description[:120],
"download": download if download else game["link"],
"image": image_url
}

except Exception as e:
print("Page error:", e)
return None

async def auto_post(app):
while True:
games = get_game_links()

if games:
game = random.choice(games)
info = get_download_info(game)

if info:
posted.add(game["link"])
save_posted() # Save permanently

message = f"🎮 *{info['name']}*\n\n📝 {info['description']}..."

keyboard = [
[InlineKeyboardButton("📥 Download", url=info["download"])]
]
reply_markup = InlineKeyboardMarkup(keyboard)

if info["image"]:
await app.bot.send_photo(
chat_id=CHANNEL_ID,
photo=info["image"],
caption=message,
parse_mode="Markdown",
reply_markup=reply_markup
)
else:
await app.bot.send_message(
chat_id=CHANNEL_ID,
text=message,
parse_mode="Markdown",
reply_markup=reply_markup
)

# Random sleep 4-10 mins
sleep_time = random.randint(240, 600)
print(f"Sleeping for {sleep_time//60} mins...")
await asyncio.sleep(sleep_time)

app = ApplicationBuilder().token(TOKEN).build()

async def on_startup(app):
app.create_task(auto_post(app))

app.post_init = on_startup

app.run_polling()
