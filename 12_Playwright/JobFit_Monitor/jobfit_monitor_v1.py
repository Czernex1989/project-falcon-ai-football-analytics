import csv
import re
from pathlib import Path
from urllib.parse import quote, urljoin

from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


# ============================================================
# KONFIGURACJA BOTA
# ============================================================

SEARCH_PHRASE = "junior tester"
MAX_OFFERS = 10

# False = widzisz działającą przeglądarkę
# True = bot działa bez wyświetlania okna
HEADLESS = False

# True = przeglądarka zostanie otwarta do naciśnięcia Enter
KEEP_BROWSER_OPEN = True

BASE_URL = "https://www.pracuj.pl"

# Pliki zostaną zapisane w tym samym folderze co skrypt.
SCRIPT_FOLDER = Path(__file__).resolve().parent
CSV_FILE = SCRIPT_FOLDER / "job_results.csv"
SCREENSHOT_FILE = SCRIPT_FOLDER / "jobfit_monitor_results.png"


# ============================================================
# FUNKCJE POMOCNICZE
# ============================================================

def clean_text(text: str | None) -> str:
    """
    Usuwa nadmiarowe spacje i znaki nowej linii.
    """
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def accept_cookies(page: Page) -> None:
    """
    Próbuje zaakceptować komunikat dotyczący plików cookies.
    Jeżeli komunikatu nie ma, bot przechodzi dalej.
    """
    cookie_patterns = [
        r"akceptuj wszystkie",
        r"zaakceptuj wszystkie",
        r"akceptuję",
        r"zgadzam się",
        r"accept all",
    ]

    for pattern in cookie_patterns:
        try:
            button = page.get_by_role(
                "button",
                name=re.compile(pattern, re.IGNORECASE),
            )

            if button.count() > 0:
                button.first.click(timeout=3_000)
                print("[OK] Zaakceptowano pliki cookies.")
                return

        except PlaywrightTimeoutError:
            continue

    print("[INFO] Nie znaleziono komunikatu cookies.")


def find_offer_card(offer_link: Locator) -> Locator:
    """
    Szuka najbliższego większego elementu zawierającego całą ofertę.

    Zaczynamy od linku z nazwą stanowiska i przechodzimy
    coraz wyżej po strukturze strony.
    """
    parent = offer_link.locator("xpath=..")
    fallback = parent

    for _ in range(8):
        try:
            text = clean_text(parent.inner_text(timeout=1_000))

            has_location = parent.locator("h4").count() > 0
            has_company = (
                parent.locator(
                    "a[href*='pracodawcy.pracuj.pl']"
                ).count()
                > 0
            )

            if 50 < len(text) < 2_000:
                fallback = parent

            if has_location or has_company:
                return parent

        except PlaywrightTimeoutError:
            pass

        parent = parent.locator("xpath=..")

    return fallback


def get_company(card: Locator) -> str:
    """
    Pobiera nazwę firmy z karty oferty.
    """
    try:
        company_link = card.locator(
            "a[href*='pracodawcy.pracuj.pl']"
        ).first

        if company_link.count() > 0:
            company = clean_text(
                company_link.inner_text(timeout=1_000)
            )

            if company:
                return company

    except PlaywrightTimeoutError:
        pass

    return "Brak danych"


def get_location(card: Locator) -> str:
    """
    Pobiera lokalizację z nagłówka h4 znajdującego się
    na karcie oferty.
    """
    try:
        location_element = card.locator("h4").first

        if location_element.count() > 0:
            location = clean_text(
                location_element.inner_text(timeout=1_000)
            )

            if location:
                return location

    except PlaywrightTimeoutError:
        pass

    return "Brak danych"


def save_to_csv(offers: list[dict[str, str]]) -> None:
    """
    Zapisuje znalezione oferty do pliku CSV.

    utf-8-sig sprawia, że polskie znaki powinny być
    poprawnie wyświetlane również w Excelu.
    """
    fieldnames = [
        "lp",
        "stanowisko",
        "firma",
        "lokalizacja",
        "link",
    ]

    with CSV_FILE.open(
        mode="w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(offers)


# ============================================================
# GŁÓWNA FUNKCJA
# ============================================================

def main() -> None:
    encoded_phrase = quote(SEARCH_PHRASE)

    search_url = (
        f"{BASE_URL}/praca/"
        f"{encoded_phrase}%3Bkw"
    )

    print("=" * 60)
    print("JOBFIT MONITOR v1.0")
    print("=" * 60)
    print(f"Szukana fraza: {SEARCH_PHRASE}")
    print(f"Maksymalna liczba ofert: {MAX_OFFERS}")
    print(f"Adres wyszukiwania: {search_url}")
    print()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=HEADLESS,
        )

        context = browser.new_context(
            viewport={
                "width": 1440,
                "height": 900,
            },
            locale="pl-PL",
        )

        page = context.new_page()

        try:
            print("[START] Otwieranie Pracuj.pl...")

            page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            accept_cookies(page)

            # Czekamy, aż na stronie pojawią się linki.
            page.locator("a[href*='/praca/']").first.wait_for(
                state="visible",
                timeout=15_000,
            )

            all_links = page.locator("a[href*='/praca/']")

            print(
                f"[INFO] Znaleziono linków na stronie: "
                f"{all_links.count()}"
            )

            offers: list[dict[str, str]] = []
            seen_urls: set[str] = set()

            for index in range(all_links.count()):
                if len(offers) >= MAX_OFFERS:
                    break

                link = all_links.nth(index)

                try:
                    href = link.get_attribute("href")

                    if not href:
                        continue

                    href_lower = href.lower()

                    # Interesują nas wyłącznie linki do ofert.
                    is_offer_link = (
                        ",oferta," in href_lower
                        or "%2coferta%2c" in href_lower
                    )

                    if not is_offer_link:
                        continue

                    full_url = urljoin(BASE_URL, href)

                    # Usuwamy parametry śledzące z końca linku.
                    clean_url = full_url.split("?")[0]

                    if clean_url in seen_urls:
                        continue

                    title = clean_text(
                        link.inner_text(timeout=1_500)
                    )

                    if not title:
                        continue

                    card = find_offer_card(link)

                    company = get_company(card)
                    location = get_location(card)

                    offer = {
                        "lp": str(len(offers) + 1),
                        "stanowisko": title,
                        "firma": company,
                        "lokalizacja": location,
                        "link": clean_url,
                    }

                    offers.append(offer)
                    seen_urls.add(clean_url)

                    print()
                    print(
                        f"[OFERTA {offer['lp']}] "
                        f"{offer['stanowisko']}"
                    )
                    print(f"Firma: {offer['firma']}")
                    print(
                        f"Lokalizacja: "
                        f"{offer['lokalizacja']}"
                    )
                    print(f"Link: {offer['link']}")

                except PlaywrightTimeoutError:
                    print(
                        "[UWAGA] Pominięto element, "
                        "którego nie udało się odczytać."
                    )

                except Exception as error:
                    print(
                        f"[BŁĄD] Nie udało się pobrać "
                        f"jednej oferty: {error}"
                    )

            if not offers:
                print()
                print(
                    "[BŁĄD] Nie znaleziono żadnych ofert."
                )
                print(
                    "Strona mogła zmienić strukturę "
                    "albo nie załadowała wyników."
                )
                return

            save_to_csv(offers)

            page.screenshot(
                path=str(SCREENSHOT_FILE),
                full_page=True,
            )

            print()
            print("=" * 60)
            print(
                f"[SUKCES] Zapisano ofert: "
                f"{len(offers)}"
            )
            print(f"CSV: {CSV_FILE}")
            print(f"Screenshot: {SCREENSHOT_FILE}")
            print("=" * 60)

            if KEEP_BROWSER_OPEN:
                input(
                    "\nNaciśnij Enter, aby zamknąć "
                    "przeglądarkę..."
                )

        except PlaywrightTimeoutError:
            print()
            print(
                "[BŁĄD] Strona ładowała się zbyt długo "
                "lub nie znaleziono wyników."
            )

        except Exception as error:
            print()
            print(f"[BŁĄD KRYTYCZNY] {error}")

        finally:
            context.close()
            browser.close()


# ============================================================
# URUCHOMIENIE PROGRAMU
# ============================================================

if __name__ == "__main__":
    main()