import asyncio
import os
import re
import random
from playwright.async_api import async_playwright

# --- ⚙️ IRONCLAD SETTINGS ---
WORKERS = 3            # Reduced to 3 per machine for better stability (15 total)
PULSE_DELAY = 150      # 150ms is the "Sweet Spot" to avoid silent drops
RESTART_CYCLE = 240    

def get_branding_payload(target_name):
    emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠"]
    emo = random.choice(emojis)
    # The 20-line block you requested
    line = f"【 {target_name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀ𝐃𝐃𝐘 {emo} ____________________/\n"
    branding = line * 20
    salt = f"\n⚡ ID: {random.randint(1000, 9999)}"
    return branding + salt

async def hyper_worker(context, thread_id, target_name, worker_id):
    page = await context.new_page()
    
    try:
        print(f"🚀 [Worker {worker_id}] Syncing with Instagram...")
        # Mobile viewport is lighter and faster for DMs
        await page.goto(f"https://www.instagram.com/direct/t/{thread_id}/", wait_until="networkidle")
        
        # Locate the message box
        # Instagram DMs use a contenteditable div or a textarea
        msg_box = page.locator('div[role="textbox"], textarea[placeholder*="Message"]').first
        
        if await msg_box.is_visible():
            print(f"🔥 [Worker {worker_id}] TARGET LOCKED. Firing...")
            
            while True:
                payload = get_branding_payload(target_name)
                
                # NATIVE EMULATION (Harder to detect than fetch)
                await msg_box.fill(payload)
                await page.keyboard.press("Enter")
                
                # Small wait to let the DOM clear
                await asyncio.sleep(PULSE_DELAY / 1000)
                
        else:
            print(f"❌ [Worker {worker_id}] Message box not found. Check Thread ID.")

    except Exception as e:
        print(f"⚠️ [Worker {worker_id}] Error: {e}")
    finally:
        await page.close()

async def main():
    cookie_raw = os.environ.get("INSTA_COOKIE")
    thread_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie_raw or not thread_id:
        print("❌ Secrets Missing!")
        return

    sid = re.search(r'sessionid=([^;]+)', cookie_raw)
    sid_value = sid.group(1) if sid else cookie_raw

    async with async_playwright() as p:
        # Launching with specific arguments to look like a real user
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            viewport={'width': 390, 'height': 844}
        )
        
        await context.add_cookies([{
            "name": "sessionid",
            "value": sid_value.strip(),
            "domain": ".instagram.com",
            "path": "/"
        }])

        workers = [hyper_worker(context, thread_id, target_name, i+1) for i in range(WORKERS)]
        await asyncio.gather(*workers)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
