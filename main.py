import os
import time
import random
from instagrapi import Client
from concurrent.futures import ProcessPoolExecutor

# --- ⚙️ OVERDRIVE CONFIGURATION ---
SESSION_ID = os.environ.get("INSTA_COOKIE")
THREAD_ID = os.environ.get("TARGET_THREAD_ID")
TARGET_NAME = os.environ.get("TARGET_NAME", "EZRA")

# INCREASE THESE FOR SPEED (Warning: Higher = Faster Ban)
PROCESSES = 6       # Number of CPU cores to use
BATCH_SIZE = 15     # Lines per message (Max visual wall)
DELAY = 0.1         # Seconds between fires (0.1 is extremely fast)

def mega_worker(worker_id):
    """Independent System Process for high-velocity firing"""
    try:
        cl = Client()
        # Prime the connection immediately
        cl.login_by_sessionid(SESSION_ID)
        print(f"🚀 [Process {worker_id}] Connection Primed & Ready.")
        
        emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠", "💮"]
        
        while True:
            try:
                emo = random.choice(emojis)
                # Build the Mega-Block
                line = f"【﻿ {TARGET_NAME} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀᴅᴅ𝐘 {emo}\n"
                border = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                message_payload = (line + border) * BATCH_SIZE
                message_payload += f"\n⚡ V-MAX ID: {random.randint(100000, 999999)}"

                # Fire directly through the established socket
                cl.direct_send(message_payload, thread_ids=[THREAD_ID])
                print(f"💥 [Process {worker_id}] Wall Injected.")
                
                if DELAY > 0:
                    time.sleep(DELAY)
                    
            except Exception as e:
                # Instagram will eventually '429' (Rate Limit) you. 
                # This catches it and attempts to resume after a short breather.
                print(f"⚠️ [Process {worker_id}] Rate Limit Hit. Cooling down...")
                time.sleep(20) 
                
    except Exception as e:
        print(f"❌ [Process {worker_id}] Critical Failure: {e}")

def main():
    if not SESSION_ID or not THREAD_ID:
        print("❌ CONFIG ERROR: Missing Environment Variables.")
        return

    print(f"⚡ INITIALIZING OVERDRIVE: {PROCESSES} PROCESSES ACTIVE")
    
    # Launching true parallel processes (Bypasses Python's Global Interpreter Lock)
    with ProcessPoolExecutor(max_workers=PROCESSES) as executor:
        for i in range(PROCESSES):
            executor.submit(mega_worker, i + 1)

if __name__ == "__main__":
    main()
