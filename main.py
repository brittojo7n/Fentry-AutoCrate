import os
import sys
import datetime
from playwright.sync_api import sync_playwright, TimeoutError

SESSION_COOKIE_VALUE = os.environ.get("FENTRY_SESSION_COOKIE")
COOKIE_NAME = "connect.sid"
LOOTBOX_URL = "https://www.fentry.org/dashboard/lootboxes"
CRATE_BUTTON_SELECTOR = 'button:has-text("Open Regular Crate")'
LOG_FILE = "log.txt"

def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    
    print(log_message)
    
    if 'logger_started' not in write_log.__dict__:
        write_log.logger_started = True
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"=== Crate Claimer Log ===\n")
            f.write(f"Started: {timestamp}\n")
            f.write("=" * 40 + "\n\n")
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def run_claimer(playwright):
    if not SESSION_COOKIE_VALUE:
        write_log("ERROR: The FENTRY_SESSION_COOKIE secret was not found.")
        sys.exit(1)

    write_log("Starting the crate claimer script...")
    
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    try:
        write_log("Injecting session cookie for authentication...")
        cookie = {
            "name": COOKIE_NAME,
            "value": SESSION_COOKIE_VALUE,
            "domain": ".fentry.org",
            "path": "/",
        }
        context.add_cookies([cookie])
        
        page = context.new_page()
        write_log(f" navigating to {LOOTBOX_URL}...")
        page.goto(LOOTBOX_URL)
        page.wait_for_timeout(5000)

        if "dashboard" not in page.url:
            raise Exception(f"Login failed! Redirected to {page.url}. Please refresh your cookie.")
        
        write_log("Successfully authenticated and on the dashboard page.")

        write_log(f"Looking for the '{CRATE_BUTTON_SELECTOR}' button...")
        button_locator = page.locator(CRATE_BUTTON_SELECTOR)
        
        if button_locator.is_visible():
            if button_locator.is_enabled():
                write_log("Button is enabled! Clicking to claim crate...")
                button_locator.click()
                write_log("Success! Crate claimed. Waiting a bit to let the action complete.")
                page.wait_for_timeout(5000)
            else:
                write_log("Button found, but it is disabled (on cooldown). No action taken.")
        else:
            write_log("Crate button not found on the page. The page layout might have changed or login failed.")

    except Exception as e:
        write_log(f"{e}")
        page.screenshot(path="error_screenshot.png")

    finally:
        write_log(" shutting down.")
        browser.close()
        write_log("Script execution completed.")

with sync_playwright() as playwright:
    run_claimer(playwright)

write_log("=" * 40)
write_log(f"Script ended at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
