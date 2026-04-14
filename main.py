import asyncio
import os
import re
import random
from playwright.async_api import async_playwright

# --- 🛰️ RELAYER SETTINGS ---
WORKERS = 2            
PULSE_DELAY = 180      # 180ms - Slower but avoids the "Silent Drop"
RESTART_CYCLE = 200    

def get_payload(target_name):
    emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠"]
    emo = random.choice(emojis)
    # Reduced line count to 12 to ensure it doesn't trigger "Wall of Text" filters
    line = f"【 {target_name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀ𝐃𝐃𝐘 {emo} ____________________/\\n"
    return line * 12 + f"\\n⚡ ID: {random.getrandbits(16)}"

async def hyper_worker(context, thread_id, target_name, worker_id):
    page = await context.new_page()
    
    try:
        print(f"🚀 [Worker {worker_id}] Establishing Socket Relay...")
        # Use a real user-flow: Home -> Direct -> Thread
        await page.goto("https://www.instagram.com/", wait_until="networkidle")
        await asyncio.sleep(2)
        await page.goto(f"https://www.instagram.com/direct/t/{thread_id}/", wait_until="networkidle")
        
        # ⚡ THE RELAY INJECTOR
        # Instead of 'filling', we use the browser's internal sequence
        await page.evaluate("""
            async ({name, delay, threadId}) => {
                const box = document.querySelector('div[role="textbox"], textarea[placeholder*="Message"]');
                if (!box) return;

                setInterval(() => {
                    const emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠"];
                    const emo = emojis[Math.floor(Math.random() * emojis.length)];
                    const line = `【 ${name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀ𝐃𝐃𝐘 ${emo} ____________________/\\n`;
                    const text = line.repeat(12) + "\\n⚡ ID: " + Math.random().toString(36).substring(5);

                    // TRIGGER NATIVE BROWSER EVENTS IN SEQUENCE
                    box.focus();
                    
                    // 1. Simulate a 'BeforeInput' event (What real browsers do)
                    const dataTransfer = new DataTransfer();
                    dataTransfer.setData('text/plain', text);
                    box.dispatchEvent(new ClipboardEvent('paste', {
                        clipboardData: dataTransfer,
                        bubbles: true
                    }));

                    // 2. Trigger the Internal React/V-DOM update
                    box.dispatchEvent(new Event('input', { bubbles: true }));

                    // 3. Dispatch the final 'Enter'
                    const enter = new KeyboardEvent('keydown', {
                        bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                    });
                    box.dispatchEvent(enter);

                    // 4. Force Clear
                    box.innerText = "";
                }, delay);
            }
        """, {"name": target_name, "delay": PULSE_DELAY, "threadId": thread_id})

        print(f"🔥 [Worker {worker_id}] RELAY ACTIVE. Monitoring Socket...")
        await asyncio.sleep(RESTART_CYCLE)

    except Exception as e:
        print(f"⚠️ [Worker {worker_id}] Connection Dropped: {e}")
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
        # Using a Very Specific Chrome Fingerprint
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
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
