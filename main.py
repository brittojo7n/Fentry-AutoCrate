import os
import sys
import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SESSION_COOKIE = os.environ.get("FENTRY_SESSION_COOKIE")
COOKIE_NAME = "connect.sid"
LOOTBOX_URL = "https://www.fentry.org/dashboard/lootboxes"
LOG_FILE = "log.txt"
BUTTON_SELECTOR = 'button:has-text("Open Regular Crate")'


def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)

    if not getattr(write_log, "logger_started", False):
        write_log.logger_started = True
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("=== Crate Claimer Log ===\n")
            f.write(f"Started: {timestamp}\n")
            f.write("=" * 40 + "\n\n")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")


def run_claimer(playwright):
    if not SESSION_COOKIE:
        write_log("ERROR: The FENTRY_SESSION_COOKIE environment variable was not found.")
        sys.exit(1)

    write_log("Starting the crate claimer script...")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    try:
        write_log("Injecting session cookie for authentication...")
        context.add_cookies([{
            "name": COOKIE_NAME,
            "value": SESSION_COOKIE,
            "domain": ".fentry.org",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax",
        }])

        write_log(f"Navigating to {LOOTBOX_URL}...")
        page.goto(LOOTBOX_URL, wait_until="domcontentloaded", timeout=30000)

        write_log("Waiting for page to fully render (networkidle)...")
        page.wait_for_load_state("networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        write_log(f"Current URL: {page.url}")
        if "dashboard" not in page.url:
            raise Exception(f"Authentication failed — redirected to: {page.url}. Please refresh your FENTRY_SESSION_COOKIE secret.")

        write_log("Authentication confirmed. On the lootbox page.")
        write_log(f"Looking for crate button: {BUTTON_SELECTOR!r}")

        button = page.locator(BUTTON_SELECTOR).first
        button.wait_for(state="visible", timeout=10000)

        if button.is_enabled():
            write_log("Button is ENABLED — clicking to claim crate...")
            button.click()
            write_log("Crate claimed! Waiting for animation to complete...")
            page.wait_for_timeout(6000)
            write_log("Done.")
            page.screenshot(path="success_screenshot.png")
        else:
            write_log("Button found but DISABLED — crate is on cooldown. No action taken.")
            page.screenshot(path="cooldown_screenshot.png")

    except PlaywrightTimeoutError as e:
        write_log("TIMEOUT: Could not find the crate button in time. The page layout may have changed.")
        write_log(f"Detail: {e}")
        try:
            buttons = page.locator("button").all()
            write_log(f"DEBUG — {len(buttons)} buttons found on page:")
            for i, btn in enumerate(buttons):
                try:
                    write_log(f"  [{i}] '{btn.inner_text().strip()[:80]}' enabled={btn.is_enabled()}")
                except Exception:
                    pass
        except Exception:
            pass
        page.screenshot(path="error_screenshot.png")
        write_log("Screenshot saved to error_screenshot.png")
    except Exception as e:
        write_log(f"ERROR: {e}")
        try:
            page.screenshot(path="error_screenshot.png")
            write_log("Error screenshot saved.")
        except Exception:
            pass
    finally:
        write_log("Shutting down browser.")
        browser.close()
        write_log("Script execution completed.")


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run_claimer(playwright)

    write_log("=" * 40)
    write_log(f"Script ended at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
