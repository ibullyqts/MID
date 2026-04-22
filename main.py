# -*- coding: utf-8 -*-
import asyncio, os, sys, random, re, gc
from playwright.async_api import async_playwright

# --- ⚙️ V100 HYBRID SETTINGS ---
AGENTS_PER_MACHINE = 2    
TABS_PER_AGENT = 2        
PULSE_DELAY = 100         
SESSION_MAX_SEC = 120     # 2-Minute RAM Flush

# The Broken Record Pattern
DADDY_PATTERN = r"({target}) 𝚂ᴀ𝚈 【﻿ＰＲＶ𝐑】 𝐃ᴀᴅᴅ𝐘 ~⭕"

async def setup_stealth(page):
    """Uses CDP to harden the browser and block tracking"""
    client = await page.context.new_cdp_session(page)
    # Block Instagram's logging/tracking to save CPU and hide activity
    await client.send("Network.setBlockedURLs", {
        "urls": ["*graph.instagram.com*", "*logging.instagram.com*", "*/logging/*", "*.facebook.com*"]
    })
    # Disable JS source maps to save RAM
    await client.send("Page.addScriptToEvaluateOnNewDocument", {
        "source": "delete window.cdc_adoQbh7K7L06el6ONX0W_Array; delete window.cdc_adoQbh7K7L06el6ONX0W_Promise;"
    })

async def run_tab(context, target_id, target_name, agent_id, tab_id):
    page = await context.new_page()
    try:
        # 🛡️ Step 1: Apply CDP Shield
        await setup_stealth(page)

        # 🚀 Step 2: Navigate to Target
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="commit", timeout=60000)
        await asyncio.sleep(8) 
        
        # ⚡ Step 3: API Injection Strike
        await page.evaluate("""
            ([tName, mDelay]) => {
                const pattern = `(${tName}) 𝚂ᴀ𝚈 【﻿ＰＲＶ𝐑】 𝐃ᴀᴅᴅ𝐘 ~⭕`;
                const fullBlock = Array(24).fill(pattern).join('\\n');
                setInterval(() => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        document.execCommand('insertText', false, fullBlock);
                        const enter = new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 });
                        box.dispatchEvent(enter);
                        setTimeout(() => { if(box.innerText.length > 0) box.innerHTML = ""; }, 5);
                    }
                }, mDelay);
            }
        """, [target_name, PULSE_DELAY])
        
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
            
            sid_match = re.search(r'sessionid=([^;]+)', cookie)
            sid = sid_match.group(1) if sid_match else cookie
            await context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])
            
            tabs = [run_tab(context, target_id, target_name, agent_id, i+1) for i in range(TABS_PER_AGENT)]
            await asyncio.gather(*tabs)
            
            await context.close()
            gc.collect()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "TARGET")
    
    if not cookie or not target_id:
        return

    agents = [run_agent(i + 1, cookie, target_id, target_name) for i in range(AGENTS_PER_MACHINE)]
    await asyncio.gather(*agents)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(main())
