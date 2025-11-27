from playwright.sync_api import sync_playwright
from pathlib import Path
import time

BRAVE_PATH = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
PROFILE_DIR = Path("./profiles/default")
URL = "https://brave.com"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

def main():
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            executable_path=BRAVE_PATH,
            headless=False #to see the browser launch
        )
        time.sleep(5) #wait to see the browser launch
        context.close()
    
if __name__ == "__main__":
    main()