import os
import time
import random
from instagrapi import Client
from concurrent.futures import ThreadPoolExecutor

# --- ⚙️ CONFIGURATION ---
SESSION_ID = os.environ.get("INSTA_COOKIE") # Your sessionid
THREAD_ID = os.environ.get("TARGET_THREAD_ID") # The chat ID
TARGET_NAME = os.environ.get("TARGET_NAME", "EZRA")
THREADS = 5  # Number of simultaneous "shooters"

def burst_worker(cl, thread_id, target_name, worker_id):
    """Fires messages as fast as the network allows"""
    emojis = ["⭕", "☣️", "🛑", "🌀", "🚨", "💠", "💮"]
    
    print(f"🔥 Worker {worker_id} initialized.")
    
    while True:
        try:
            emo = random.choice(emojis)
            # Creating the heavy-duty text block
            text = f"【 {target_name} 】 ➠➠चुदाई का बकरा {emo}\n" * 10
            text += f"⚡ ID: {random.randint(1000, 9999)}"

            # Direct API call (No browser rendering)
            cl.direct_send(text, thread_ids=[thread_id])
            print(f"✅ [Worker {worker_id}] Sent successfully.")
            
        except Exception as e:
            print(f"⚠️ [Worker {worker_id}] Blocked or Error: {e}")
            time.sleep(5)  # Wait if rate limited

def main():
    if not SESSION_ID or not THREAD_ID:
        print("❌ Missing Environment Variables!")
        return

    cl = Client()
    
    # Login via sessionid to bypass 2FA/Email verification
    print("📡 Syncing with Instagram API...")
    cl.login_by_sessionid(SESSION_ID)
    
    print(f"🚀 NITRO-BURST STARTING ON THREAD: {THREAD_ID}")

    # Launching multiple workers on different threads for parallel firing
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(burst_worker, cl, THREAD_ID, TARGET_NAME, i+1)

if __name__ == "__main__":
    main()
