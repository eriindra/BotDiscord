import discord
from discord.ext import tasks
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

SELF_TOKEN = os.getenv("SELF_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

SOURCE_CHANNELS = [
    1316370207970820136,
    1316285821510221856,
    1316337341832495144,
]

client = discord.Client()
last_message_ids = {ch_id: None for ch_id in SOURCE_CHANNELS}

@client.event
async def on_ready():
    print(f"✅ Akun alt login: {client.user}")
    check_updates.start()

@tasks.loop(minutes=5)
async def check_updates():
    async with aiohttp.ClientSession() as session:
        for source_id in SOURCE_CHANNELS:
            source_channel = client.get_channel(source_id)
            
            if not source_channel:
                print(f"❌ Source channel {source_id} tidak ditemukan!")
                continue
            
            async for message in source_channel.history(limit=1):
                if message.id != last_message_ids[source_id]:
                    last_message_ids[source_id] = message.id

                    avatar_url = str(message.author.display_avatar.url)
                    author_name = message.author.display_name

                    embed = {
                        "title": "📨 New UPDATE Message",
                        "description": message.content or "*No text*",
                        "color": 0x2B2D31,
                        "author": {
                            "name": author_name,
                            "icon_url": avatar_url
                        },
                        "footer": {
                            "text": f"Source: Fish It! • #{source_channel.name}"
                        },
                        "timestamp": message.created_at.isoformat()
                    }

                    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp")
                    video_extensions = (".mp4", ".mov", ".webm", ".mkv")
                    
                    image_url = None
                    video_links = []

                    for attachment in message.attachments:
                        url = attachment.url
                        if any(url.lower().endswith(ext) for ext in image_extensions):
                            if not image_url:
                                image_url = url
                            else:
                                embed.setdefault("fields", []).append({
                                    "name": "🖼️ Extra Image",
                                    "value": url,
                                    "inline": False
                                })
                        elif any(url.lower().endswith(ext) for ext in video_extensions):
                            video_links.append(url)

                    if image_url:
                        embed["image"] = {"url": image_url}

                    if video_links:
                        embed.setdefault("fields", []).append({
                            "name": "🎬 Video",
                            "value": "\n".join(video_links),
                            "inline": False
                        })

                    payload = {
                        "username": "Fish It Update",
                        "avatar_url": "https://em-content.zobj.net/source/twitter/376/tropical-fish_1f420.png",
                        "embeds": [embed]
                    }

                    await session.post(WEBHOOK_URL, json=payload)
                    print(f"✅ Update dipost dari #{source_channel.name} | Attachments: {len(message.attachments)}")

client.run(SELF_TOKEN)
