import os
import time
import random
from instagrapi import Client
from concurrent.futures import ThreadPoolExecutor

# --- ⚙️ SPEED SETTINGS ---
SESSION_ID = os.environ.get("INSTA_COOKIE")
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
TARGET_NAME = os.environ.get("TARGET_NAME", "TARGET")

AGENTS = 8          # 8 Agents per machine x 6 Machines = 48 total agents
BLOCKS = 8          # 8 blocks per message for ultra-low latency
DELAY = 0.02        # 20ms pulse (Maximum speed)

def rapid_agent(cl, thread_id, target_name, agent_id):
    emojis = ["💠", "💮", "🌀", "🚨", "⭕", "☣️"]
    while True:
        try:
            emo = random.choice(emojis)
            line = f"【﻿ {target_name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀᴅᴅ𝐘 {emo}\n"
            # Fast-processing payload
            message = (line * BLOCKS) + f"⚡ ID: {random.randint(1000, 9999)}"

            cl.direct_send(message, thread_ids=[str(thread_id)])
            print(f"💥 [Agent {agent_id}] Hit!")
            time.sleep(DELAY)
        except Exception as e:
            if "429" in str(e):
                time.sleep(15) # Wait for rate limit
            else:
                time.sleep(2)

def main():
    if not SESSION_ID or not THREAD_ID: return
    cl = Client()
    try:
        # Standard login - works best with personal accounts
        cl.login_by_sessionid(SESSION_ID)
        with ThreadPoolExecutor(max_workers=AGENTS) as executor:
            for i in range(AGENTS):
                executor.submit(rapid_agent, cl, THREAD_ID, TARGET_NAME, i+1)
    except Exception as e:
        print(f"Login failed: {e}")

if __name__ == "__main__":
    main()
