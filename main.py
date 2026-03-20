# --- V100 TUNED CONFIGURATION ---
THREADS = 2             # 2 Agents per machine
TOTAL_DURATION = 25000  # ~7 Hours

# ⚡ TARGET SPEED: 80ms
BURST_SPEED = (0.08, 0.08) 

# ♻️ AGGRESSIVE RESTART (Prevent 3-hour slowdown)
# Restarting every 60s clears the browser RAM before it lags.
SESSION_MIN_SEC = 60   
SESSION_MAX_SEC = 60   

# ... (Keep the rest of your imports and functions the same) ...

def run_life_cycle(agent_id, cookie, target, messages):
    global_start = time.time()
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        session_start = time.time()
        
        try:
            driver = get_driver(agent_id)
            # ... (Login and Navigation Logic) ...
            
            msg_box = find_mobile_box(driver)
            while (time.time() - session_start) < SESSION_MAX_SEC:
                msg = random.choice(messages)
                # Adding a tiny random salt to the 80ms to bypass basic pattern filters
                salt = "".join(random.choices("1234567890", k=2))
                if adaptive_inject(driver, msg_box, f"{msg} {salt}"):
                    with COUNTER_LOCK:
                        global GLOBAL_SENT
                        GLOBAL_SENT += 1
                
                time.sleep(0.08) # The 80ms heart-beat

        except Exception as e:
            pass # Silent fail for max speed
        finally:
            if driver: driver.quit()
            gc.collect()
