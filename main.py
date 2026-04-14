import os, time, re, random, threading, gc, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚙️ V100 NITRO SETTINGS ---
THREADS = 2             
TABS_PER_THREAD = 4     # Increased to 4 tabs (8 Agents total)
PULSE_DELAY = 85        # Dropped to 85ms for insane speed

# ♻️ RESTART CYCLES
SESSION_MAX_SEC = 120   
TOTAL_DURATION = 25000  

sys.stdout.reconfigure(encoding='utf-8')

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager'
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def run_agent(agent_id, cookie, target_id, target_name):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Deploying Nitro Cycle...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # Rapid Tab Launch
            for _ in range(TABS_PER_THREAD):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
            
            time.sleep(5) # Brief pause for all tabs to hit the thread

            handles = driver.window_handles[1:]
            for handle in handles:
                driver.switch_to.window(handle)
                # ⚡ NITRO JS ENGINE
                driver.execute_script("""
                    const name = arguments[0];
                    const delay = arguments[1];
                    
                    function getBlock(n) {
                        const emojis = ["⭕", "💢", "☣️", "🛑", "🌀", "🧿", "💠", "💮", "🛸", "🚨"];
                        const emo = emojis[Math.floor(Math.random() * emojis.length)];
                        const line = `【 ${n} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀ𝐃𝐃𝐘 ${emo} ____________________/\\n`;
                        return line.repeat(20) + "\\n⚡ ID: " + Math.random().toString(36).substring(5);
                    }

                    setInterval(() => {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            const text = getBlock(name);
                            
                            // Nitro Injection Logic
                            box.focus();
                            document.execCommand('selectAll', false, null);
                            document.execCommand('insertText', false, text);
                            
                            // Trigger Native Enter
                            const enter = new KeyboardEvent('keydown', {
                                bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                            });
                            box.dispatchEvent(enter);
                            
                            // Near-Instant Cleanup (1ms)
                            setTimeout(() => { box.innerHTML = ""; }, 1);
                        }
                    }, delay);
                """, target_name, PULSE_DELAY)

            print(f"🔥 [Agent {agent_id}] Nitro Burst Active at {PULSE_DELAY}ms.")
            time.sleep(SESSION_MAX_SEC) 

        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Nitro Crash: {e}")
        finally:
            if driver: driver.quit()
            gc.collect() 
            time.sleep(1)

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie or not target_id:
        print("❌ Missing Secrets!")
        return

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=run_agent, args=(i+1, cookie, target_id, target_name))
        t.start()
        time.sleep(5) # Stagger start to prevent CPU lock

if __name__ == "__main__":
    main()
