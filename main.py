import os, time, re, random, gc, sys
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚙️ HARDWARE TUNED SETTINGS ---
MAX_BROWSERS = 2        # Uses both vCPU cores of the GitHub Runner
TABS_PER_BROWSER = 3    # 3 Tabs per process (6 Agents total)
PULSE_DELAY = 100       # Hyper-speed (100ms)
SESSION_MAX_SEC = 120   # 2-Minute Restart cycle
TOTAL_DURATION = 25000 

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Critical for 8GB RAM: Prevents memory leaks from history/cache
    options.add_argument("--incognito") 
    options.page_load_strategy = 'eager'
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def run_instance(instance_id, cookie, target_id, target_name):
    """Parallel process worker"""
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Proc {instance_id}] Starting Hyper-Cycle...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            # Injection
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # Open Tabs
            for _ in range(TABS_PER_BROWSER):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(2)

            handles = driver.window_handles[1:]
            for handle in handles:
                driver.switch_to.window(handle)
                # --- ORIGINAL JS ENGINE RESTORED ---
                driver.execute_script("""
                    const name = arguments[0];
                    const delay = arguments[1];
                    
                    function getBlock(n) {
                        const emojis = ["👑", "⚡", "🔥", "🦈", "🦁", "💎", "⚔️", "🔱", "🧿", "🌪️"];
                        const emo = emojis[Math.floor(Math.random() * emojis.length)];
                        const line = `【 ${n} 】 SAY P R V R बाप ${emo} ____________________/\\n`;
                        let block = "";
                        for(let i=0; i<20; i++) { block += line; }
                        return block + "\\n⚡ ID: " + Math.random().toString(36).substring(7);
                    }

                    setInterval(() => {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            const text = getBlock(name);
                            box.focus();
                            document.execCommand('insertText', false, text);
                            box.dispatchEvent(new Event('input', { bubbles: true }));

                            const enter = new KeyboardEvent('keydown', {
                                bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                            });
                            box.dispatchEvent(enter);
                            
                            // Instant clear to keep DOM lightweight
                            setTimeout(() => { if(box.innerHTML.length > 0) box.innerHTML = ""; }, 5);
                        }
                    }, delay);
                """, target_name, PULSE_DELAY)

            print(f"🔥 [Proc {instance_id}] All Agents Active. Cycling in 120s...")
            time.sleep(SESSION_MAX_SEC)

        except Exception as e:
            print(f"⚠️ [Proc {instance_id}] Cycle Error: {e}")
        finally:
            if driver:
                driver.quit()
            gc.collect() 
            time.sleep(2)

if __name__ == "__main__":
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie or not target_id:
        print("❌ Missing Environment Secrets!")
        sys.exit(1)

    procs = []
    for i in range(MAX_BROWSERS):
        p = Process(target=run_instance, args=(i+1, cookie, target_id, target_name))
        p.start()
        procs.append(p)
        time.sleep(8) # Stagger to avoid login detection

    for p in procs:
        p.join()
