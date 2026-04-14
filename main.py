import asyncio
import os
import re
import random
from playwright.async_api import async_playwright

# --- ⚙️ IRONCLAD CONFIG ---
WORKERS = 2            # 2 Browsers per machine (10 total) to avoid CPU lag
PULSE_DELAY = 150      # 150ms - The "Safety Limit" for real emulation
RESTART_CYCLE = 200    # Frequent restarts to clear Instagram's anti-bot cache

def get_branding_payload(target_name):
    emojis = ["⭕", "💢", "☣️", "🛑", "🌀", "🚨", "💠", "💮"]
    emo = random.choice(emojis)
    line = f"【 {target_name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀ𝐃𝐃𝐘 {emo} ____________________/\\n"
    # Reduced to 15 lines to avoid "Message too long" silent drops
    branding = line * 15 
    salt = f"\\n⚡ ID: {random.getrandbits(16)}"
    return branding + salt

async def hyper_worker(context, thread_id, target_name, worker_id):
    page = await context.new_page()
    
    try:
        print(f"🚀 [Worker {worker_id}] Syncing Human Emulation...")
        # Mobile view is faster and has fewer anti-bot checks
        await page.goto(f"https://www.instagram.com/direct/t/{thread_id}/", wait_until="networkidle")
        
        # Locate the real message box
        msg_box = page.locator('div[role="textbox"], textarea[placeholder*="Message"]').first
        
        if await msg_box.is_visible():
            print(f"🔥 [Worker {worker_id}] TARGET LOCKED. Firing...")
            
            while True:
                payload = get_branding_payload(target_name)
                
                # 🛠️ THE FIX: Real Human Action
                # 1. Focus the box
                await msg_box.click()
                # 2. Use 'fill' to simulate a "Paste" (Faster than typing, safer than fetch)
                await msg_box.fill(payload)
                # 3. Press Enter like a human
                await page.keyboard.press("Enter")
                
                # Dynamic delay to break the "robot" pattern
                await asyncio.sleep(random.uniform(PULSE_DELAY/1000, (PULSE_DELAY+50)/1000))
        else:
            print(f"❌ [Worker {worker_id}] Box not found. Check Thread ID.")

    except Exception as e:
        print(f"⚠️ [Worker {worker_id}] Error: {e}")
    finally:
        await page.close()

async def main():
    cookie_raw = os.environ.get("INSTA_COOKIE")
    thread_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie_raw or not thread_id:
        return

    sid = re.search(r'sessionid=([^;]+)', cookie_raw)
    sid_value = sid.group(1) if sid else cookie_raw

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use an iPhone User Agent (Instagram trusts mobile users more)
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
