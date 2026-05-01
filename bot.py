# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
import sys
import shutil
import gc
import httpx
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# --- ⚙️ V100 TUNED SETTINGS ---
TABS_PER_MACHINE = 2    
PULSE_DELAY = 110       
TOTAL_STRIKE_TIME = 21000 # ~5.8 Hours
RESTART_INTERVAL = 1800   # Clears RAM every 30m

# 🔱 TELEGRAM CONFIG
TG_TOKEN = "7968897685:AAHWWUFmfRFYUFQxjV0GE_9Avhn-iRH2j7M"
TG_CHAT_ID = "1225435208"

sys.stdout.reconfigure(encoding='utf-8')

async def send_tg(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except: pass

async def run_strike(node_id, cookie, target_id, target_name):
    base_dir = os.path.join(os.getcwd(), f"node_{node_id}")
    await send_tg(f"🚀 <b>Machine {node_id} Online</b>\nTarget: {target_name}")

    elapsed = 0
    while elapsed < TOTAL_STRIKE_TIME:
        profile_path = os.path.join(base_dir, f"run_{random.randint(100,999)}")
        
        async with async_playwright() as p:
            user_agent = "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=True,
                user_agent=user_agent,
                viewport={'width': 1024, 'height': 1366},
                is_mobile=True,
                has_touch=True,
                args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu"]
            )

            stealth = Stealth()
            await stealth.apply_stealth_async(context)
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            await context.add_cookies([{
                'name': 'sessionid', 'value': sid.strip(), 
                'domain': '.instagram.com', 'path': '/', 'secure': True, 'httpOnly': True
            }])

            # ⚡ PILLAR SCRIPT (Updated 2026 Selectors & Vertical Alignment)
            strike_script = """
                (name, delay) => {
                    function getBlock(n) {
                        const lines = [
                            `[${n}] 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑨 𝑩𝑯𝑶𝑺𝑫𝑨 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑲𝑨 𝑮𝑼𝑳𝑨𝑴 🔥`,
                            `[${n}] 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑵𝑬 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑶 𝑵𝑨𝑵𝑮𝑨 𝑲𝑨𝑹 𝑫𝑰𝒀𝑨 😂`,
                            `[${n}] 𝑹𝑼𝑵𝑫𝑰 𝑲𝑬 𝑩𝑨𝑪𝑪𝑯𝑬 𝑩𝑨𝑨𝑷 𝑺𝑬 𝑷𝑨𝑵𝑮𝑨 𝑵𝑨𝑯𝑰 𝑳𝑬𝑻𝑬 🤡`,
                            `[${n}] 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑻𝑬𝑹𝑨 𝑲𝑯𝑨𝑨𝑵𝑫𝑨𝑨𝑵𝑰 𝑴𝑨𝑨𝑳𝑰𝑲 𝑯𝑨𝑰 👑`,
                            `[${n}] 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑰 𝑪𝑯𝑼𝑻 𝑴𝑨𝑰 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑲𝑨 𝑯𝑨𝑻𝑯𝑶𝑫𝑨 🔨`,
                            `[${n}] 𝑱𝑨𝑳𝑫𝑰 𝑺𝑬 𝑷 𝑹 𝑽 𝑹 𝑷𝑨𝑷𝑨 𝑲𝑨 𝑳𝑨𝑼𝑫𝑨 𝑪𝑯𝑶𝑶𝑺 𝑳𝑬 𝑲𝑨𝑻𝑻𝑬 👅`
                        ];
                        const baseLine = lines[Math.floor(Math.random() * lines.length)];
                        let block = "";
                        for(let i = 0; i < 21; i++) { block += baseLine + "\\n"; }
                        return block + "🔱 𝐏𝐇𝐎𝐄𝐍𝐈𝐗-𝐕𝟏𝟎𝟎: " + Math.random().toString(36).substring(7).toUpperCase();
                    }
                    function pulse() {
                        // 🔱 2026 Selector Update: Finding the message box
                        const box = document.querySelector('div[aria-label="Message"], div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            box.focus();
                            // Use insertHTML to maintain the vertical 'Pillar' structure
                            document.execCommand('insertHTML', false, getBlock(name).replace(/\\n/g, '<br>'));
                            box.dispatchEvent(new Event('input', { bubbles: true }));
                            box.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', code: 'Enter', keyCode: 13 }));
                            window.sentCount = (window.sentCount || 0) + 1;
                            setTimeout(() => { if(box.innerHTML.length > 0) box.innerHTML = ""; }, 5);
                        }
                        setTimeout(pulse, delay + (Math.random() * 20 - 10));
                    }
                    pulse();
                }
            """

            try:
                pages = []
                for i in range(TABS_PER_MACHINE):
                    page = await context.new_page()
                    await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded")
                    if "login" in page.url:
                        await send_tg(f"❌ <b>SESSION DEAD</b>\nMachine {node_id}\nCookie needs update.")
                        return
                    await page.evaluate(strike_script, [target_name, PULSE_DELAY])
                    pages.append(page)
                
                # 🔱 Report status to Telegram every 10 mins
                for _ in range(3):
                    await asyncio.sleep(600)
                    total_sent = 0
                    for pg in pages:
                        total_sent += await pg.evaluate("window.sentCount || 0")
                    await send_tg(f"📊 <b>Machine {node_id} Report</b>\nSent: {total_sent}\nUptime: {elapsed // 60}m")

                elapsed += RESTART_INTERVAL
                
            except Exception as e:
                await send_tg(f"⚠️ <b>Machine {node_id} Error</b>\n{str(e)[:50]}")
                await asyncio.sleep(15)
            
            await context.close()
            shutil.rmtree(profile_path, ignore_errors=True)
            gc.collect()

async def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "TARGET")
    m_id = os.environ.get("MACHINE_ID", "1")
    if cookie and target_id:
        await run_strike(m_id, cookie, target_id, target_name)

if __name__ == "__main__":
    asyncio.run(main())
