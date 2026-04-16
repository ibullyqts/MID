import os, time, re, random, gc, sys
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚙️ OPTIMIZED CONFIG FOR 2-CORE RUNNER ---
MAX_BROWSERS = 2        # Matches GitHub Runner vCPU count
TABS_PER_BROWSER = 2    # Balanced for 8GB RAM
PULSE_DELAY = 150       # Slightly increased to prevent CPU thermal throttling
SESSION_MAX_SEC = 120   # 2-Minute Restart
TOTAL_DURATION = 25000 

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    # RAM Optimization: Disable images, CSS, and hardware acceleration
    options.add_argument("--blink-settings=imagesEnabled=false")
    prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    options.page_load_strategy = 'eager'
    options.add_experimental_option("mobileEmulation", {"deviceName": "Nexus 5"}) # Lighter than iPad
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Win32", fix_hairline=True)
    return driver

def run_instance(instance_id, cookie, target_id, target_name):
    """Each instance runs in its own dedicated OS process."""
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Proc {instance_id}] Spawning Browser Instance...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            # Extract and inject sessionid
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            # Launch Tabs
            for i in range(TABS_PER_BROWSER):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(1.5)

            # Inject the JS Engine into each tab
            handles = driver.window_handles[1:]
            for handle in handles:
                driver.switch_to.window(handle)
                driver.execute_script("""
                    const name = arguments[0];
                    const delay = arguments[1];
                    
                    function getBlock(n) {
                        const emojis = ["⚡", "🔥", "💎", "⚔️", "🧿"];
                        const emo = emojis[Math.floor(Math.random() * emojis.length)];
                        let block = `【 ${n} 】 PRVR HYPER-ENGINE ${emo}\\n`.repeat(10);
                        return block + "\\nID: " + Math.random().toString(36).substring(7);
                    }

                    setInterval(() => {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            box.focus();
                            document.execCommand('insertText', false, getBlock(name));
                            box.dispatchEvent(new Event('input', { bubbles: true }));
                            const enter = new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', keyCode: 13 });
                            box.dispatchEvent(enter);
                        }
                    }, delay);
                """, target_name, PULSE_DELAY)

            print(f"✅ [Proc {instance_id}] All tabs firing. Cycling in {SESSION_MAX_SEC}s...")
            time.sleep(SESSION_MAX_SEC)

        except Exception as e:
            print(f"⚠️ [Proc {instance_id}] Error: {e}")
        finally:
            if driver:
                driver.quit()
            gc.collect() 
            time.sleep(5)

if __name__ == "__main__":
    # Get environment variables
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    target_name = os.environ.get("TARGET_NAME", "EZRA")

    if not cookie or not target_id:
        print("❌ ERROR: Missing INSTA_COOKIE or TARGET_THREAD_ID")
        sys.exit(1)

    processes = []
    for i in range(MAX_BROWSERS):
        p = Process(target=run_instance, args=(i+1, cookie, target_id, target_name))
        p.start()
        processes.append(p)
        time.sleep(5) # Stagger start to prevent CPU spikes

    for p in processes:
        p.join()
