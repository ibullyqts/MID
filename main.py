import os
import re
import sys
import asyncio
import subprocess

# --- 🛠️ AUTO-INSTALLER ---
def install_dependencies():
    print("📦 Installing Playwright and dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    print("✅ Installation Complete.\n")

# --- ⚙️ CONFIGURATION ---
TOTAL_AGENTS = 6        # Number of parallel tabs
PULSE_DELAY = 100       # 100ms firing rate
SESSION_MAX_SEC = 120   # 2-Minute Life Cycle
TOTAL_DURATION = 25000  # Total run time

async def run_agent(context, target_id, target_name):
    """Parallel Agent Worker"""
    page = await context.new_page()
    try:
        print(f"📡 Agent Joining Thread: {target_id}")
        # 'commit' wait_until is faster for high-speed tasks
        await page.goto(f"https://www.instagram.com/direct/t/{target_id}/", wait_until="domcontentloaded")
        
        # --- ORIGINAL HYPER-ENGINE ---
        await page.evaluate(f"""
            () => {{
                const name = "{target_name}";
                const delay = {PULSE_DELAY};
                
                function getBlock(n) {{
                    const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️"];
                    const emo = emojis[Math.floor(Math.random() * emojis.length)];
                    const line = `【 ${{n}} 】 SAY P R V R बाप ${{emo}____________________/\\n`;
                    let block = "";
                    for(let i=0; i<20; i++) {{ block += line; }}
                    return block + "\\n⚡ ID: " + Math.random().toString(36).substring(7);
                }}

                setInterval(() => {{
                    const box = document.querySelector('div[aria-label="Message"], div[contenteditable="true"]');
                    if (box) {{
                        const text = getBlock(name);
                        box.focus();
                        // Direct DOM injection to bypass React's block
                        document.execCommand('insertText', false, text);
                        
                        const enter = new KeyboardEvent('keydown', {{
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                        }});
                        box.dispatchEvent(enter);
                        
                        // Keeps RAM low on 8GB Runner
                        setTimeout(() => {{ if(box.innerHTML.length > 0) box.innerHTML = ""; }}, 5);
                    }}
                }}, delay);
            }}
        """)
        await asyncio.sleep(SESSION_MAX_SEC)
    except Exception as e:
        print(f"⚠️ Agent Error: {e}")
    finally:
        await page.close()

async def main():
    # Install before importing playwright to avoid ModuleNotFoundError
    install_dependencies()
    from playwright.async_api import async_playwright

    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie or not target_id:
        print("❌ CRITICAL: Missing Environment Variables!")
        return

    sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie

    async with async_playwright() as p:
        print("🚀 Launching Master Browser...")
        browser = await p.chromium.launch(headless=True)
        
        # Context allows all tabs to share one login session in memory
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            viewport={'width': 1024, 'height': 1366}
        )
        
        await context.add_cookies([{
            'name': 'sessionid',
            'value': sid.strip(),
            'domain': '.instagram.com',
            'path': '/'
        }])

        start_run = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_run) < TOTAL_DURATION:
            print(f"♻️ Starting Parallel Burst (Duration: {SESSION_MAX_SEC}s)")
            
            # This triggers all agents at the exact same time
            tasks = [run_agent(context, target_id, target_name) for _ in range(TOTAL_AGENTS)]
            await asyncio.gather(*tasks)
            
            print("🧹 Session complete. Refreshing agents...")
            
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Script stopped by user.")
