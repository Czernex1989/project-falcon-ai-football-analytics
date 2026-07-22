from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto("https://playwright.dev")

    page.get_by_role("link", name="Get started").click()

    page.wait_for_timeout(5000)

    browser.close()