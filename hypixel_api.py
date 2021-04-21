import requests
import json
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
key = os.getenv("hypixel_api_key")

api_request_count = 0
max_request_per_min = 30


async def manage_api_limit(add=False):
    global api_request_count
    if add:

        time_wait = int(api_request_count / max_request_per_min)
        api_request_count += 1
        for i in range(30):
            if api_request_count >= max_request_per_min:
                await asyncio.sleep(time_wait)
    else:
        await asyncio.sleep(60)
        api_request_count -= 1


async def get_uuid(username):
    try:
        content = json.loads(
            requests.get(
                f"https://api.mojang.com/users/profiles/minecraft/{username}").
            content)
    except json.decoder.JSONDecodeError:
        return None
    return content.get("id")


async def is_player_online(username):
    if len(username) < 17:
        username = await get_uuid(username)
    await manage_api_limit(add=True)
    resp = requests.get(
        f"https://api.hypixel.net/status?key={key}&uuid={username}")
    asyncio.create_task(manage_api_limit())
    resp = json.loads(resp.content)
    if resp["success"]:
        if resp["session"]["online"]:
            # if resp["session"]["gameType"] == "SKYBLOCK":
            #    print("playing sb")
            # else:
            #    print("online but not playing sb")
            return True
        else:
            # print("offline")
            return False
    else:
        print(f"possible bug in system\nCause : {resp['cause']}")
        return False


async def get_player_discord(username):
  if len(username) < 17:
      username = await get_uuid(username)
  await manage_api_limit(add=True)
  resp = requests.get(
      f"https://api.hypixel.net/player?key={key}&uuid={username}")
  asyncio.create_task(manage_api_limit())
  resp = json.loads(resp.content)
  if resp["success"]:
      social_media = resp.get("player").get("socialMedia")
      if social_media == None:
          return None
      links = social_media.get("links")
      discord_name = links.get("DISCORD")
      return discord_name
  else:
      return None


async def run_with_no_exception(function, args, if_exception=False):

    try:
        result = await function(*args)
    except Exception as error_info:
        print(
            f"got this exception while trying to run this function: {function} with arguements {args}\n{error_info}"
        )
        return if_exception
    else:
        if result == None:
            result = if_exception
        return result
