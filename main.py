import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError

SESSION_COOKIE_VALUE = os.environ.get("FENTRY_SESSION_COOKIE")

COOKIE_NAME = "connect.sid"
LOOTBOX_URL = "https://www.fentry.org/dashboard/lootboxes"
CRATE_BUTTON_SELECTOR = 'button:has-text("Open Regular Crate")'

def run_claimer(playwright):
    if not SESSION_COOKIE_VALUE:
        print("🛑 ERROR: The FENTRY_SESSION_COOKIE secret was not found.")
        sys.exit(1)

    print("🚀 Starting the crate claimer script...")
    
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    try:
        print("🔑 Injecting session cookie for authentication...")
        cookie = {
            "name": COOKIE_NAME,
            "value": SESSION_COOKIE_VALUE,
            "domain": ".fentry.org",
            "path": "/",
        }
        context.add_cookies([cookie])
        
        page = context.new_page()
        print(f" navigating to {LOOTBOX_URL}...")
        page.goto(LOOTBOX_URL)
        page.wait_for_timeout(5000)

        if "dashboard" not in page.url:
            raise Exception(f"❌ Login failed! Redirected to {page.url}. Please refresh your cookie.")
        
        print("✅ Successfully authenticated and on the dashboard page.")

        print(f"🔎 Looking for the '{CRATE_BUTTON_SELECTOR}' button...")
        button_locator = page.locator(CRATE_BUTTON_SELECTOR)
        
        if button_locator.is_visible():
            if button_locator.is_enabled():
                print("✅ Button is enabled! Clicking to claim crate...")
                button_locator.click()
                print("🎉 Success! Crate claimed. Waiting a bit to let the action complete.")
                page.wait_for_timeout(5000)
            else:
                print("⏳ Button found, but it is disabled (on cooldown). No action taken.")
        else:
            print("❌ Crate button not found on the page. The page layout might have changed or login failed.")

    except Exception as e:
        print(f"{e}")
        page.screenshot(path="error_screenshot.png")

    finally:
        print(" shutting down.")
        browser.close()

with sync_playwright() as playwright:
    run_claimer(playwright)