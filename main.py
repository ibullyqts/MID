import os
import time
import random
from instagrapi import Client
from concurrent.futures import ThreadPoolExecutor

# --- ⚙️ OVERDRIVE SETTINGS ---
SESSION_ID = os.environ.get("INSTA_COOKIE")
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
TARGET_NAME = os.environ.get("TARGET_NAME", "TARGET")

AGENTS = 10         
BLOCK_COUNT = 5     
DELAY = 0.1         # Slightly increased for better delivery success

def rapid_agent(cl, thread_id, target_name, agent_id):
    emojis = ["💠", "💮", "🌀", "🚨", "⭕"]
    print(f"⚡ [Agent {agent_id}] Ready.")
    while True:
        try:
            emo = random.choice(emojis)
            line = f"【﻿ {target_name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀᴅᴅ𝐘 {emo}\n"
            message_payload = (line * BLOCK_COUNT) + f"⚡ ID: {random.randint(100, 999)}"

            # 2026 Fix: We use thread_ids as a LIST
            cl.direct_send(message_payload, thread_ids=[str(thread_id)])
            print(f"💥 [Agent {agent_id}] Sent!")
            time.sleep(DELAY)
        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Blocked: {e}")
            time.sleep(10)

def main():
    if not SESSION_ID or not THREAD_ID:
        print("❌ MISSING SECRETS")
        return

    cl = Client()
    
    # 🛠️ 2026 DEVICE SIMULATION
    # We generate a unique device ID so Instagram doesn't think it's a generic bot
    print("📡 Simulating Physical Device...")
    cl.set_device({
        "app_version": "410.0.0.0.96",
        "android_version": 33,
        "android_release": "13",
        "dpi": "480dpi",
        "resolution": "1080x2400",
        "manufacturer": "Xiaomi",
        "device": "surya",
        "model": "M2007J20CG",
        "cpu": "qcom",
        "version_code": "641123490",
    })

    # Injecting session with established device state
    cl.set_settings({
        "authorization_data": {
            "sessionid": SESSION_ID.strip(),
        },
        "ua": cl.user_agent
    })

    try:
        # TESTING THE PIPE: If this fails, the sessionid is dead
        print("🔓 Checking Pipe Connectivity...")
        cl.get_timeline_feed() 
        print(f"✅ Pipe Warm. Firing at Thread: {THREAD_ID}")
        
        with ThreadPoolExecutor(max_workers=AGENTS) as executor:
            for i in range(AGENTS):
                executor.submit(rapid_agent, cl, THREAD_ID, TARGET_NAME, i+1)
    except Exception as e:
        print(f"❌ Session Rejected by Instagram: {e}")
        print("💡 Hint: Your sessionid might be expired. Get a fresh one from Incognito.")

if __name__ == "__main__":
    main()
