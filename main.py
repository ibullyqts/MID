# -*- coding: utf-8 -*-
import asyncio, os, sys, random, re, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 "AGGRESSIVE" SETTINGS ---
AGENTS_PER_MACHINE = 2    
TABS_PER_AGENT = 2        
PULSE_DELAY = 100         # 100ms Strike Speed
SESSION_MAX_SEC = 120     # 2-Minute RAM Flush

# 🔥 THE AGGRESSIVE PAYLOAD LIST
ABUSIVE_TEXTS = [
    "RANDI KA BACHA", 
    "TERI MAA KI CHUT", 
    "BHADWE KI OLAD", 
    "KUTTE KA JANA", 
    "NAJAYAZ OLAD",
    "GASHTI KA JANA"
]

async def setup_stealth(page):
    """Uses CDP to harden the browser and block Meta's tracking"""
    try:
        client = await page.context.new_cdp_session(page)
        # Block Meta's reporting endpoints to extend account life
        await client.send("Network.setBlockedURLs", {
            "urls": ["*graph.instagram.com*", "*logging.instagram.com*", "*/logging/*", "*.facebook.com*"]
        })
        # Wipe automation traces
        await client.send("Page.addScriptToEvaluateOnNewDocument", {
            "source": "delete window.navigator.webdriver; window.chrome = { runtime: {} };"
        })
    except Exception:
        pass

async def run_tab(context, target_id, target_name, agent_id, tab_id):
    page = await context.new_page()
    try:
        await setup_stealth(page)
        
        # Navigate to target chat
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=60000)
        await asyncio.sleep(8) 
        
        # ⚡ AGGRESSIVE INJECTION STRIKE
        await page.evaluate("""
            ([tName, mDelay, abuseList]) => {
                const frames = ["⭕", "🌀", "🔴", "💠", "🧿", "🔘"];
                let frameIndex = 0;

                setInterval(() => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        // Pick random abuse and rotating emoji
                        const currentEmoji = frames[frameIndex % frames.length];
                        const randomAbuse = abuseList[Math.floor(Math.random() * abuseList.length)];
                        
                        // Construct the 24-line high-impact block
                        const pattern = `(${tName}) ${randomAbuse} 𝚂ᴀ𝚈 【﻿ＰＲＶ𝐑】 𝐃ᴀᴅᴅ𝐘 ~${currentEmoji}`;
                        const fullBlock = Array(24).fill(pattern).join('\\n');

                        // Execute injection
                        document.execCommand('insertText', false, fullBlock);
                        box.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // Force Enter key
                        const enter = new KeyboardEvent('keydown', { 
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13 
                        });
                        box.dispatchEvent(enter);
                        
                        frameIndex++; 
                        
                        // Clean DOM immediately to prevent memory leak
                        setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                    }
                }, mDelay);
            }
        """, [target_name, PULSE_DELAY, ABUSIVE_TEXTS])
        
        await asyncio.sleep(SESSION_MAX_SEC)
    except Exception as e:
        print(f"⚠️ [M-A{agent_id}-T{tab_id}] Error: {e}")
    finally:
        await page.close()

async def run_agent(agent_id, cookie, target_id, target_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox", 
            "--disable-dev-shm-usage",
            "--js-flags='--max-old-space-size=1024'" 
        ])
        
        while True:
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            
            # Extract and clean sessionid
            sid_match = re.search(r'sessionid=([^;]+)', cookie)
            sid = sid_match.group(1) if sid_match else cookie
            await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
            
            # Run parallel tabs (4 strike points total per runner)
            tabs = [run_tab(context, target_id, target_name, agent_id, i+1) for i in range(TABS_PER_AGENT)]
            await asyncio.gather(*tabs)
            
            await context.close()
            gc.collect()

async def main():
    # GitHub Secrets / Env Vars
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "TARGET")
    
    if not cookie or not target_id:
        print("❌ Critical: Secrets Missing!")
        return

    print(f"🔥 PHOENIX V100 CLUSTER IGNITED (Aggressive Mode)")
    
    agents = [run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)]
    await asyncio.gather(*agents)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
