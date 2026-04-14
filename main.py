import os
import time
import random
from instagrapi import Client
from concurrent.futures import ThreadPoolExecutor

# --- ⚙️ NITRO-BURST CONFIGURATION ---
SESSION_ID = os.environ.get("INSTA_COOKIE")      # Your sessionid
THREAD_ID = os.environ.get("TARGET_THREAD_ID")   # The numeric Chat ID
TARGET_NAME = os.environ.get("TARGET_NAME", "EZRA")
THREADS = 4                                      # Simultaneous shooters
BLOCK_COUNT = 15                                 # Lines per message

def burst_worker(cl, thread_id, target_name, worker_id):
    """Fires heavy-duty message blocks directly to the API"""
    emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠", "💮"]
    
    print(f"🔥 [Worker {worker_id}] Engine Synchronized.")
    
    while True:
        try:
            emo = random.choice(emojis)
            
            # --- THE MEGA-BLOCK CONSTRUCTION ---
            # Bold unicode styling with visual separators
            line = f"【﻿ {target_name} 】 𝚂ᴀ𝚈 【﻿ＰＲＶＲ】 𝐃ᴀᴅᴅ𝐘 {emo}\n"
            border = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            
            # Combine into a single massive wall of text
            message_payload = (line + border) * BLOCK_COUNT
            message_payload += f"\n⚡ BURST-ID: {random.randint(10000, 99999)}"

            # Direct API Broadcast
            cl.direct_send(message_payload, thread_ids=[thread_id])
            print(f"✅ [Worker {worker_id}] Sent 15-Block Wall.")
            
            # Small jitter to prevent instant socket closure by server
            time.sleep(random.uniform(0.3, 0.8))
            
        except Exception as e:
            print(f"⚠️ [Worker {worker_id}] Error: {e}")
            # If rate limited, wait longer before retrying
            time.sleep(15)

def main():
    if not SESSION_ID or not THREAD_ID:
        print("❌ ERROR: Set INSTA_COOKIE and TARGET_THREAD_ID environment variables!")
        return

    cl = Client()
    
    try:
        print("📡 Establishing API Connection...")
        cl.login_by_sessionid(SESSION_ID)
        print(f"🚀 AUTHENTICATED: Target Thread {THREAD_ID}")
    except Exception as e:
        print(f"❌ LOGIN FAILED: {e}")
        return

    print(f"🔥 STARTING NITRO BURST ({THREADS} THREADS)...")

    # Parallel execution for maximum velocity
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(burst_worker, cl, THREAD_ID, TARGET_NAME, i+1)

if __name__ == "__main__":
    main()
