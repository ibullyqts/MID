import asyncio
import os
import re
import random
from playwright.async_api import async_playwright

# --- ⚙️ NITRO SETTINGS ---
WORKERS = 3            # 3 Windows per machine (15 total)
PULSE_DELAY = 95       # 95ms (Adjust between 80-120 if you get blocked)
RESTART_CYCLE = 240    

async def hyper_worker(context, thread_id, target_name, worker_id):
    page = await context.new_page()
    
    try:
        print(f"🚀 [Worker {worker_id}] Syncing...")
        await page.goto(f"https://www.instagram.com/direct/t/{thread_id}/", wait_until="networkidle")
        
        # ⚡ THE HYBRID ENGINE
        # This bypasses Playwright's slow 'fill' and uses high-speed JS
        await page.evaluate("""
            async ({name, delay}) => {
                const box = document.querySelector('div[role="textbox"], textarea[placeholder*="Message"]');
                if (!box) return;

                setInterval(() => {
                    const emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠"];
                    const emo = emojis[Math.floor(Math.random() * emojis.length)];
                    const line = `【 ${name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀ𝐃𝐃𝐘 ${emo} ____________________/\\n`;
                    const payload = line.repeat(20) + "\\n⚡ ID: " + Math.random().toString(36).substring(7);

                    // 1. Instant Text Injection
                    box.focus();
                    document.execCommand('insertText', false, payload);
                    
                    // 2. Native Event Dispatch (Tells IG a message is ready)
                    box.dispatchEvent(new Event('input', { bubbles: true }));

                    // 3. High-Speed Enter Trigger
                    const enter = new KeyboardEvent('keydown', {
                        bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                    });
                    box.dispatchEvent(enter);

                    // 4. Zero-Latency Clear
                    setTimeout(() => { if(box.innerHTML.length > 0) box.innerHTML = ""; }, 5);
                }, delay);
            }
        """, {"name": target_name, "delay": PULSE_DELAY})

        print(f"🔥 [Worker {worker_id}] NITRO ACTIVE. Firing at {PULSE_DELAY}ms")
        await asyncio.sleep(RESTART_CYCLE)

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
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
