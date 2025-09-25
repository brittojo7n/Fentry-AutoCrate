# claim_crate.py

import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError

# Get the session cookie from the GitHub Secret
SESSION_COOKIE_VALUE = os.environ.get("FENTRY_SESSION_COOKIE")

# --- Configuration ---
FENTRY_DOMAIN = "www.fentry.org"
LOOTBOX_URL = f"https://{FENTRY_DOMAIN}/dashboard/lootboxes"
# This is the name of the cookie we found in the browser
COOKIE_NAME = "connect.sid"
# This is the selector for the specific button to click
CRATE_BUTTON_SELECTOR = 'button:has-text("Open Regular Crate")'

def run_claimer(playwright):
    """
    Launches a browser, injects the auth cookie, and attempts to claim a crate.
    """
    if not SESSION_COOKIE_VALUE:
        print("🛑 ERROR: The FENTRY_SESSION_COOKIE secret was not found.")
        sys.exit(1)

    print("🚀 Starting the crate claimer script...")
    
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )

    try:
        # Step 1: Inject the authentication cookie to bypass login
        print("🔑 Injecting session cookie for authentication...")
        cookie = {
            "name": COOKIE_NAME,
            "value": SESSION_COOKIE_VALUE,
            "domain": FENTRY_DOMAIN,
            "path": "/",
        }
        context.add_cookies([cookie])
        print("✅ Cookie set successfully.")

        # Step 2: Navigate directly to the lootboxes page
        page = context.new_page()
        print(f" navigating to {LOOTBOX_URL}...")
        page.goto(LOOTBOX_URL)

        # Step 3: Check for and click the crate button
        print(f"🔎 Looking for the '{CRATE_BUTTON_SELECTOR}' button...")
        
        try:
            # Try to click the button. If it's not available (due to the timer),
            # this will time out after 10 seconds and trigger the 'except' block.
            page.locator(CRATE_BUTTON_SELECTOR).click(timeout=10000)
            
            print("🎉 Success! The crate button was clicked and the prize was claimed.")
            
        except TimeoutError:
            print("⏳ The crate is not available yet (on cooldown). No action taken.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        page.screenshot(path="error_screenshot.png") # Takes a screenshot on failure

    finally:
        print(" shutting down.")
        browser.close()

# Main execution block
with sync_playwright() as playwright:
    run_claimer(playwright)