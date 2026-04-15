import os, time, re, random, threading, gc, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚙️ V100 TUNED SETTINGS ---
THREADS = 2             # 2 Browsers per machine
TABS_PER_THREAD = 3     # 3 Tabs per browser (6 Agents total)
PULSE_DELAY = 100       # 100ms (Hyper-speed firing)
SESSION_MAX_SEC = 120   # 2-Minute Restart (Flush RAM)
TOTAL_DURATION = 25000  # Total Run Time

# --- 🎯 TARGET CONFIG ---
# Set these in your environment or replace the "None" values here
INSTA_COOKIE = os.environ.get("INSTA_COOKIE")
TARGET_THREAD_ID = os.environ.get("TARGET_THREAD_ID")
TARGET_NAME = os.environ.get("TARGET_NAME", "EZRA") 

sys.stdout.reconfigure(encoding='utf-8')

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager' 
    
    # Randomize User Agent slightly to help stealth
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def run_agent(agent_id, cookie, target_id, target_name):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Starting New 2-Min Cycle...")
            driver = get_driver()
            
            # Navigate to direct message thread
            driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
            
            # Cookie Injection
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            driver.refresh()
            time.sleep(5) # Wait for thread to load

            # Multi-Tab Launch
            for _ in range(TABS_PER_THREAD - 1):
                driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{target_id}/', '_blank');")
                time.sleep(1)

            handles = driver.window_handles
            for handle in handles:
                driver.switch_to.window(handle)
                
                # --- ⚡ THE JS HYPER-ENGINE ---
                driver.execute_script("""
                    const name = arguments[0];
                    const delay = arguments[1];
                    if (window.emojiFrame === undefined) window.emojiFrame = 0;

                    const textbox = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (!textbox) {
                        console.log("Waiting for textbox...");
                        return;
                    }

                    function formatLine(content) {
                        const innerWidth = 34; 
                        const padding = innerWidth - content.length;
                        return "║ " + content + " ".repeat(Math.max(0, padding)) + " ║";
                    }

                    const engine = setInterval(() => {
                        const frames = [
                            { a: "🌸", b: "✨" }, 
                            { a: "✨", b: "🌸" }
                        ];
                        
                        const f = frames[window.emojiFrame % 2];
                        window.emojiFrame++; 

                        const nameStr = name.toUpperCase();
                        const lineA = formatLine(`${nameStr}  ${f.a} P R V R पापा से CUD ${f.a}`);
                        const lineB = formatLine(`        ${f.b} P R V R पापा से CUD`);
                        
                        const msg = [
                            "╔══════════════════════════════════╗",
                            lineA, lineB, lineA, lineB, lineA, lineB, lineA,
                            "╚══════════════════════════════════╝",
                            "⚡ ID: " + Math.random().toString(36).substring(7).toUpperCase()
                        ].join("\\n");

                        // Inject & Fire
                        textbox.focus();
                        document.execCommand('insertText', false, msg);
                        textbox.dispatchEvent(new Event('input', { bubbles: true }));

                        const enter = new KeyboardEvent('keydown', {
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                        });
                        textbox.dispatchEvent(enter);
                        
                        // Buffer Cleaning (Every 5 messages)
                        if (window.emojiFrame % 5 === 0) {
                            setTimeout(() => { if(textbox.innerHTML.length > 0) textbox.innerHTML = ""; }, 5);
                        }
                    }, delay);
                """, target_name, PULSE_DELAY)

            print(f"🔥 [Agent {agent_id}] Bursting... (Reset in 120s)")
            time.sleep(SESSION_MAX_SEC)

        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Cycle Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect() # RAM Flush
            time.sleep(2)

def main():
    if not INSTA_COOKIE or not TARGET_THREAD_ID:
        print("❌ Error: INSTA_COOKIE or TARGET_THREAD_ID not found!")
        return

    print(f"📡 Initializing V100 Engines for Target: {TARGET_NAME}")
    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=run_agent, args=(i+1, INSTA_COOKIE, TARGET_THREAD_ID, TARGET_NAME))
        t.start()
        threads.append(t)
        time.sleep(10) # Staggered startup

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
