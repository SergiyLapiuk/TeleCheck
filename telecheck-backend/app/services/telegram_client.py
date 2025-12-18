from telethon.sync import TelegramClient
from telethon.tl.types import User, Channel
from datetime import datetime
from typing import List, Dict
import pytz
import os

api_id = *****
api_hash = '*****************'

client = TelegramClient("session_name", api_id, api_hash)


async def get_posts_from_channel(channel, start_date: str, end_date: str) -> List[str]:
    client = TelegramClient("anon", api_id, api_hash)
    await client.start()

    start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)

    posts = []
    async for msg in client.iter_messages(channel):
        if msg.date < start:
            break
        if start <= msg.date <= end and msg.message:
            posts.append(msg.message)

    await client.disconnect()
    return posts

async def get_channel_info(channel_username: str) -> Dict[str, str]:
    await client.start()
    entity = await client.get_entity(channel_username)

    title = entity.title if isinstance(entity, Channel) else entity.first_name

    avatar_name = channel_username.replace("t.me/", "") + ".jpg"
    avatar_path = f"static/{avatar_name}"

    os.makedirs("static", exist_ok=True)

    if not os.path.exists(avatar_path):
        await client.download_profile_photo(entity, file=avatar_path)

    return {
        "username": channel_username,
        "title": title,
        "photo_url": f"/static/{avatar_name}"
    }