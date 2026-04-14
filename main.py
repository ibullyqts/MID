import asyncio
import aiohttp
import random
import time
import os
import re

# --- 🚀 GOD MODE CONFIG ---
# Each "Worker" fires messages independently. 
# 10 Workers x 100 Messages = 1,000 requests in a burst.
WORKERS = 10 
DELAY_BETWEEN_MESSAGES = 0.05  # 50ms (Insane Speed)

async def get_dynamic_block(target_name):
    """Generates the 20-line block format."""
    emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠"]
    emo = random.choice(emojis)
    line = f"【 {target_name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀ𝐃𝐃𝐘 {emo} ____________________/\n"
    block = line * 20
    return f"{block}\n⚡ ID: {random.getrandbits(24)}"

async def send_request(session, thread_id, target_name, worker_id):
    """The core firing function hitting the internal Instagram API."""
    url = f"https://www.instagram.com/api/v1/direct_v2/threads/{thread_id}/items/send_text/"
    
    # Instagram's internal API headers are required to bypass security
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "X-CSRFToken": "missing", # Set via cookies later
        "X-IG-App-ID": "1217981644879628", # Global IG App ID
        "X-Instagram-AJAX": "1",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.instagram.com",
        "Referer": f"https://www.instagram.com/direct/t/{thread_id}/",
    }

    while True:
        try:
            text = await get_dynamic_block(target_name)
            
            # Internal IG payload format
            data = {
                "text": text,
                "client_context": str(random.getrandbits(64)),
                "mutation_token": str(random.getrandbits(64)),
                "offline_threading_id": str(random.getrandbits(64))
            }

            async with session.post(url, data=data, headers=headers) as response:
                status = response.status
                if status == 200:
                    print(f"🚀 [Worker {worker_id}] STRIKE SUCCESS | {status}")
                elif status == 429:
                    print(f"⚠️ [Worker {worker_id}] RATE LIMITED (429). Sleeping 5s...")
                    await asyncio.sleep(5)
                else:
                    res_text = await response.text()
                    print(f"❌ [Worker {worker_id}] FAILED | {status} | {res_text[:50]}")
            
            await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
            
        except Exception as e:
            print(f"⚠️ [Worker {worker_id}] Connection Error: {e}")
            await asyncio.sleep(1)

async def main():
    cookie_raw = os.environ.get("INSTA_COOKIE")
    thread_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie_raw or not thread_id:
        print("❌ Missing Secrets!")
        return

    # Extract sessionid and csrftoken for the handshake
    session_id = re.search(r'sessionid=([^;]+)', cookie_raw).group(1) if 'sessionid=' in cookie_raw else cookie_raw
    
    # Map cookies into the session jar
    cookies = {
        "sessionid": session_id.strip(),
        "csrftoken": "abcd123" # Dummy token, IG often fills this or uses the session
    }

    async with aiohttp.ClientSession(cookies=cookies) as session:
        # Launch workers simultaneously
        tasks = []
        for i in range(WORKERS):
            tasks.append(send_request(session, thread_id, target_name, i+1))
        
        print(f"🔥 PHOENIX OVERLORD ACTIVE: {WORKERS} Async Workers Firing...")
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
