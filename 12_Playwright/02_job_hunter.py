from playwright.sync_api import sync_playwright


SEARCH_URL = "https://justjoin.it/job-offers/poland-remote/testing"


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=500
    )

    page = browser.new_page(
        viewport={"width": 1400, "height": 900}
    )

    print("Otwieram oferty pracy...")

    page.goto(
        SEARCH_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    print("Strona została otwarta.")

    # Czekamy chwilę, aż oferty zostaną wyświetlone
    page.wait_for_timeout(5000)

    # Pobieramy tekst widoczny na stronie
    page_text = page.locator("body").inner_text()

    # Słowa, których szukamy w ofertach
    keywords = [
        "automation",
        "automatyz",
        "playwright",
        "selenium",
        "cypress",
        "qa engineer",
        "test engineer"
    ]

    print("\nSZUKANE TECHNOLOGIE I STANOWISKA:\n")

    for keyword in keywords:
        if keyword.lower() in page_text.lower():
            print(f"[ZNALEZIONO] {keyword}")
        else:
            print(f"[BRAK] {keyword}")

    # Zapisujemy screenshot całej strony
    page.screenshot(
        path="job_hunter_results.png",
        full_page=True
    )

    print("\nScreenshot zapisano jako job_hunter_results.png")
    print("Przeglądarka zamknie się za 15 sekund.")

    page.wait_for_timeout(15000)

    browser.close()