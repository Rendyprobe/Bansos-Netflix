import json
import random
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "input.txt"
BAHAN_DIR = PROJECT_DIR / "Bahan"
EKSEKUSI_FILE = PROJECT_DIR / "eksekusi.py"
PLAYWRIGHT_BROWSERS_DIR = PROJECT_DIR / ".ms-playwright"
TARGET_URL = "https://netflixcookiesmap.vercel.app/"
COPY_WAIT_TIMEOUT_MS = 15000

DATE_LINE_LABEL_PATTERN = re.compile(
    r"^\s*[-\u2013\u2014]?\s*"
    r"(?:"
    r"aktif\s+sampai|"
    r"berakhir|"
    r"billing|"
    r"date|"
    r"expire\s+date|"
    r"expiration\s+date|"
    r"expired|"
    r"expires|"
    r"expiry|"
    r"masa\s+aktif|"
    r"next\s+billing|"
    r"tanggal"
    r")\s*:",
    flags=re.IGNORECASE,
)

MONTH_NAMES = {
    "jan": 1,
    "january": 1,
    "januari": 1,
    "feb": 2,
    "february": 2,
    "februari": 2,
    "mar": 3,
    "march": 3,
    "marzo": 3,
    "maret": 3,
    "apr": 4,
    "april": 4,
    "abril": 4,
    "may": 5,
    "mayo": 5,
    "maio": 5,
    "mai": 5,
    "maja": 5,
    "mayıs": 5,
    "mei": 5,
    "jun": 6,
    "june": 6,
    "junho": 6,
    "junio": 6,
    "juin": 6,
    "czerwca": 6,
    "haziran": 6,
    "juni": 6,
    "jul": 7,
    "july": 7,
    "julho": 7,
    "julio": 7,
    "juillet": 7,
    "lipca": 7,
    "temmuz": 7,
    "juli": 7,
    "aug": 8,
    "agustus": 8,
    "august": 8,
    "agu": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "okt": 10,
    "oktober": 10,
    "octubre": 10,
    "outubro": 10,
    "octobre": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
    "diciembre": 12,
    "dezembro": 12,
    "decembre": 12,
    "des": 12,
    "desember": 12,
}

DAY_MONTH_NAME_PATTERN = re.compile(
    r"\b(?P<day>\d{1,2})(?!\d)(?:st|nd|rd|th)?\s+"
    r"(?P<month>[A-Za-zÀ-ÿ]+)(?:\s*,?\s*(?P<year>\d{2,4}))?\b",
    flags=re.IGNORECASE,
)
MONTH_NAME_DAY_PATTERN = re.compile(
    r"\b(?P<month>[A-Za-zÀ-ÿ]+)\s+"
    r"(?P<day>\d{1,2})(?!\d)(?:st|nd|rd|th)?"
    r"(?:\s*,?\s*(?P<year>\d{2,4}))?\b",
    flags=re.IGNORECASE,
)
NUMERIC_DAY_MONTH_PATTERN = re.compile(
    r"(?<![\d-])(?P<day>\d{1,2})[/-](?P<month>\d{1,2})"
    r"(?:[/-](?P<year>\d{2,4}))?(?!\d)"
)
ISO_DATE_PATTERN = re.compile(
    r"(?<!\d)(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})(?!\d)"
)
PREMIUM_PATTERN = re.compile(r"\bPremium\b", flags=re.IGNORECASE)

SKIPPED_LABELS = {
    "ALL",
    "COPY",
    "DATE",
    "DESC",
    "DETAILED DOCUMENTATION",
    "DISMISS",
    "ENTERING",
    "EXPLORE ARCHIVES",
    "GREEN",
    "JOIN NOW",
    "OPEN COUNTRY SEARCH",
    "PURPLE",
    "RED",
    "RESET VIEW",
    "ZOOM IN",
    "ZOOM OUT",
}


@dataclass(frozen=True)
class ExtractedDate:
    display: str
    day: int
    month: int
    year: int | None

    def comparison_key(self, today: date) -> tuple[int, int, int]:
        return (self.year or today.year, self.month, self.day)


@dataclass(frozen=True)
class SavedBahanMatch:
    path: Path
    content: str
    matched_date: ExtractedDate


def choose_main_menu() -> str:
    print("Test Cookie Parser")
    print()
    print("1. Generate URL")
    print("2. Dapatkan Bahan")
    print("0. Keluar")
    print()

    while True:
        choice = input("Pilih menu: ").strip()
        if choice in {"0", "1", "2"}:
            return choice
        print("Pilihan tidak valid. Masukkan 1, 2, atau 0.")


def choose_bahan_source_menu() -> str:
    print("Dapatkan Bahan")
    print()
    print("1. Ambil dari web")
    print("2. Ambil dari file tersimpan")
    print("0. Kembali")
    print()

    while True:
        choice = input("Pilih sumber bahan: ").strip()
        if choice in {"0", "1", "2"}:
            return choice
        print("Pilihan tidak valid. Masukkan 1, 2, atau 0.")


def run_eksekusi_script() -> None:
    if not EKSEKUSI_FILE.exists():
        print(f"{EKSEKUSI_FILE.name} tidak ditemukan.")
        return

    print(f"Running {EKSEKUSI_FILE.name}...", flush=True)
    completed = subprocess.run(
        [sys.executable, str(EKSEKUSI_FILE)],
        check=False,
        cwd=str(PROJECT_DIR),
    )
    if completed.returncode != 0:
        print(f"{EKSEKUSI_FILE.name} exited with code {completed.returncode}.")
        return

    print(f"Finished running {EKSEKUSI_FILE.name}.")


def validate_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Target URL harus diawali http:// atau https://")
    return url.strip()


def normalize_year(raw_year: str | None) -> int | None:
    if not raw_year:
        return None

    year = int(raw_year)
    if len(raw_year) == 2:
        return 2000 + year if year < 70 else 1900 + year
    return year


def build_extracted_date(
    display: str,
    day: str,
    month: str | int,
    year: str | None,
) -> ExtractedDate | None:
    month_number = (
        int(month)
        if isinstance(month, int) or str(month).isdigit()
        else MONTH_NAMES.get(str(month).lower())
    )
    if month_number is None or not 1 <= month_number <= 12:
        return None

    day_number = int(day)
    year_number = normalize_year(year)

    try:
        date(year_number or 2000, month_number, day_number)
    except ValueError:
        return None

    return ExtractedDate(
        display=display.strip(),
        day=day_number,
        month=month_number,
        year=year_number,
    )


def extract_dates_from_segment(segment: str) -> list[ExtractedDate]:
    dates = []

    for match in ISO_DATE_PATTERN.finditer(segment):
        extracted = build_extracted_date(
            match.group(0),
            match.group("day"),
            match.group("month"),
            match.group("year"),
        )
        if extracted:
            dates.append(extracted)

    for match in DAY_MONTH_NAME_PATTERN.finditer(segment):
        extracted = build_extracted_date(
            match.group(0),
            match.group("day"),
            match.group("month"),
            match.group("year"),
        )
        if extracted:
            dates.append(extracted)

    for match in MONTH_NAME_DAY_PATTERN.finditer(segment):
        extracted = build_extracted_date(
            match.group(0),
            match.group("day"),
            match.group("month"),
            match.group("year"),
        )
        if extracted:
            dates.append(extracted)

    for match in NUMERIC_DAY_MONTH_PATTERN.finditer(segment):
        extracted = build_extracted_date(
            match.group(0),
            match.group("day"),
            match.group("month"),
            match.group("year"),
        )
        if extracted:
            dates.append(extracted)

    return dates


def extract_candidate_dates(content: str) -> list[ExtractedDate]:
    candidate_dates = []

    for line in content.splitlines():
        if not DATE_LINE_LABEL_PATTERN.search(line):
            continue

        candidate_dates.extend(extract_dates_from_segment(line))

    return candidate_dates


def has_premium_marker(content: str) -> bool:
    return PREMIUM_PATTERN.search(content) is not None


def is_after_runtime(extracted: ExtractedDate, today: date) -> bool:
    return extracted.comparison_key(today) > (today.year, today.month, today.day)


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def find_saved_bahan_file(today: date) -> SavedBahanMatch | None:
    if not BAHAN_DIR.exists():
        print(f"Folder {BAHAN_DIR.name} tidak ditemukan.")
        return None

    files = sorted(
        (
            path
            for path in BAHAN_DIR.iterdir()
            if path.is_file() and path.suffix.lower() == ".txt"
        ),
        key=lambda path: path.name.lower(),
    )
    if not files:
        print(f"Tidak ada file .txt di folder {BAHAN_DIR.name}.")
        return None

    matches = []
    for path in files:
        content = read_text_file(path).strip()
        if not content:
            continue
        if not has_premium_marker(content):
            continue

        future_dates = [
            extracted
            for extracted in extract_candidate_dates(content)
            if is_after_runtime(extracted, today)
        ]
        if not future_dates:
            continue

        matched_date = min(
            future_dates,
            key=lambda extracted: extracted.comparison_key(today),
        )
        matches.append(
            SavedBahanMatch(path=path, content=content, matched_date=matched_date)
        )

    if not matches:
        print(
            f"Tidak ada file .txt di folder {BAHAN_DIR.name} "
            "yang berisi Premium dan tanggalnya setelah hari ini."
        )
        return None

    return random.choice(matches)


def run_saved_bahan_copy() -> None:
    selected = find_saved_bahan_file(date.today())
    if selected is None:
        return

    INPUT_FILE.write_text(selected.content + "\n", encoding="utf-8")
    relative_path = selected.path.relative_to(PROJECT_DIR)
    print(
        f"Saved {relative_path} to {INPUT_FILE.name} "
        f"(tanggal terbaca: {selected.matched_date.display})."
    )


def run_get_bahan_menu() -> None:
    source = choose_bahan_source_menu()
    if source == "0":
        return
    if source == "1":
        run_interactive_copy()
        return
    run_saved_bahan_copy()


def configure_playwright_browser_path() -> None:
    import os

    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS_DIR))


def install_playwright_chromium() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if completed.returncode != 0:
        details = (completed.stderr or completed.stdout).strip()
        print("Gagal menginstall Chromium Playwright otomatis.")
        print(f"Jalankan manual: {sys.executable} -m playwright install chromium")
        if details:
            print(details)
        raise RuntimeError("Chromium Playwright belum siap.")


def launch_chromium(playwright, playwright_error_type):
    try:
        return playwright.chromium.launch(headless=True)
    except playwright_error_type as exc:
        if "Executable doesn't exist" not in str(exc):
            raise RuntimeError(f"Playwright gagal membuka Chromium: {exc}") from exc

    install_playwright_chromium()
    try:
        return playwright.chromium.launch(headless=True)
    except playwright_error_type as exc:
        raise RuntimeError(f"Chromium sudah diinstall tetapi masih gagal dibuka: {exc}") from exc


def text_selector(label: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9 _.-]+", label):
        return "text=" + label
    return "text=" + json.dumps(label)


def clean_label(label: str) -> str:
    cleaned = re.sub(
        r"\s+[-\u2013\u2014]\s+click to view cookies\s*$",
        "",
        label,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+click to view cookies\s*$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def discover_selectable_items(page) -> list[dict]:
    items = page.evaluate(
        """() => {
            const nodes = Array.from(document.querySelectorAll(
                'button, a, [role="button"], [data-country], [data-code], [data-iso], [aria-label], [title]'
            ));

            const isVisible = (el) => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 &&
                    style.visibility !== 'hidden' &&
                    style.display !== 'none' &&
                    style.opacity !== '0';
            };

            const cssEscape = (value) => {
                if (window.CSS && window.CSS.escape) return window.CSS.escape(value);
                return value.replace(/["\\\\]/g, '\\\\$&');
            };

            const attrSelector = (attr, value) => `[${attr}="${value.replace(/["\\\\]/g, '\\\\$&')}"]`;

            const selectorFor = (el) => {
                if (el.id) return '#' + cssEscape(el.id);
                for (const attr of ['data-country', 'data-code', 'data-iso', 'data-testid', 'aria-label', 'title']) {
                    const value = el.getAttribute(attr);
                    if (value) return attrSelector(attr, value);
                }
                return null;
            };

            return nodes
                .filter(isVisible)
                .map((el) => {
                    const data = el.dataset || {};
                    const label = String(
                        data.country ||
                        data.code ||
                        data.iso ||
                        el.getAttribute('aria-label') ||
                        el.getAttribute('title') ||
                        el.innerText ||
                        el.textContent ||
                        ''
                    ).replace(/\\s+/g, ' ').trim();
                    const rect = el.getBoundingClientRect();
                    return {
                        label,
                        selector: selectorFor(el),
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2,
                    };
                })
                .filter((item) => item.label && item.label.length <= 80);
        }"""
    )

    seen = set()
    filtered = []
    for item in items:
        raw_label = str(item.get("label", "")).strip()
        label = clean_label(raw_label)
        selector = item.get("selector") or text_selector(label)
        normalized = label.upper()

        if not label or normalized in SKIPPED_LABELS:
            continue
        if (normalized, selector) in seen:
            continue

        seen.add((normalized, selector))
        filtered.append(
            {
                "label": label,
                "selector": selector,
                "x": item.get("x"),
                "y": item.get("y"),
            }
        )

    return filtered


def choose_item(items: list[dict]) -> dict:
    print("Selectable items:")
    for index, item in enumerate(items, start=1):
        print(f"{index}. {item['label']}")

    while True:
        selected = input("Choose country/item: ").strip()
        if selected.isdigit():
            index = int(selected)
            if 1 <= index <= len(items):
                return items[index - 1]

        for item in items:
            if item["label"].lower() == selected.lower():
                return item

        print("Invalid choice. Enter menu number or exact label.")


def click_selector(page, selector: str, timeout_ms: int = 15000) -> None:
    locator = page.locator(selector).first
    locator.wait_for(state="visible", timeout=timeout_ms)
    locator.click(timeout=timeout_ms)


def click_item(page, item: dict) -> None:
    selector = item.get("selector")
    if selector:
        try:
            click_selector(page, selector)
            return
        except Exception:
            pass

    x = item.get("x")
    y = item.get("y")
    if x is None or y is None:
        raise RuntimeError(f"Tidak bisa klik item: {item.get('label', 'unknown')}")

    page.mouse.click(float(x), float(y))


def discover_copy_buttons(page) -> list[dict]:
    buttons = page.evaluate(
        """() => {
            const nodes = Array.from(document.querySelectorAll(
                'button, a, [role="button"], [data-copy], [data-testid], [aria-label], [title]'
            ));

            const isVisible = (el) => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 &&
                    style.visibility !== 'hidden' &&
                    style.display !== 'none' &&
                    style.opacity !== '0';
            };

            const cssEscape = (value) => {
                if (window.CSS && window.CSS.escape) return window.CSS.escape(value);
                return value.replace(/["\\\\]/g, '\\\\$&');
            };

            const attrSelector = (attr, value) => `[${attr}="${value.replace(/["\\\\]/g, '\\\\$&')}"]`;

            const selectorFor = (el) => {
                if (el.id) return '#' + cssEscape(el.id);
                for (const attr of ['data-copy', 'data-testid', 'aria-label', 'title']) {
                    const value = el.getAttribute(attr);
                    if (value) return attrSelector(attr, value);
                }
                return null;
            };

            return nodes
                .filter(isVisible)
                .map((el) => {
                    const data = el.dataset || {};
                    const label = String(
                        data.copy ||
                        el.getAttribute('aria-label') ||
                        el.getAttribute('title') ||
                        el.innerText ||
                        el.textContent ||
                        'copy button'
                    ).replace(/\\s+/g, ' ').trim();
                    const searchable = [
                        label,
                        data.copy || '',
                        el.getAttribute('data-testid') || '',
                        el.getAttribute('aria-label') || '',
                        el.getAttribute('title') || '',
                    ].join(' ').toLowerCase();
                    const rect = el.getBoundingClientRect();
                    return {
                        label,
                        searchable,
                        selector: selectorFor(el),
                        x: rect.left + rect.width / 2,
                        y: rect.top + rect.height / 2,
                    };
                })
                .filter((item) => item.searchable.includes('copy') || item.searchable.includes('salin'));
        }"""
    )

    seen = set()
    filtered = []
    for button in buttons:
        label = str(button.get("label", "copy button")).strip() or "copy button"
        selector = button.get("selector") or text_selector(label)
        key = (label.upper(), selector)
        if key in seen:
            continue

        seen.add(key)
        filtered.append(
            {
                "label": label,
                "selector": selector,
                "x": button.get("x"),
                "y": button.get("y"),
            }
        )

    return filtered


def wait_for_copy_buttons(page) -> list[dict]:
    deadline = time.monotonic() + (COPY_WAIT_TIMEOUT_MS / 1000)
    while time.monotonic() < deadline:
        buttons = discover_copy_buttons(page)
        if buttons:
            return buttons
        page.wait_for_timeout(500)
    return []


def click_copy(page) -> None:
    for selector in ("text=COPY", "text=Copy", "text=SALIN", "text=Salin"):
        try:
            click_selector(page, selector, timeout_ms=1500)
            return
        except Exception:
            pass

    buttons = wait_for_copy_buttons(page)
    if not buttons:
        raise RuntimeError("No COPY/SALIN button appeared.")

    click_item(page, buttons[0])


def run_interactive_copy() -> None:
    configure_playwright_browser_path()

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright belum terinstall.")
        print("Jalankan: myenv/bin/python -m pip install playwright")
        return

    try:
        target_url = validate_url(TARGET_URL)
    except ValueError as exc:
        print(exc)
        return

    with sync_playwright() as playwright:
        browser = None
        try:
            browser = launch_chromium(playwright, PlaywrightError)
            context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
            page = context.new_page()
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_load_state("load", timeout=15000)

            items = discover_selectable_items(page)
            if not items:
                print("Tidak ada negara/item yang bisa dipilih.")
                return

            while True:
                item = choose_item(items)
                click_item(page, item)
                page.wait_for_timeout(750)

                try:
                    click_copy(page)
                except RuntimeError:
                    print(f"No COPY button appeared for {item['label']}. Choose another item.")
                    continue

                copied_text = page.evaluate("navigator.clipboard.readText()")
                INPUT_FILE.write_text(copied_text.strip() + "\n", encoding="utf-8")
                print(f"Saved copied text to {INPUT_FILE.name}.")
                return
        except PlaywrightError as exc:
            print(f"Playwright error: {exc}")
        except RuntimeError as exc:
            print(exc)
        finally:
            if browser is not None:
                browser.close()


def main() -> None:
    while True:
        choice = choose_main_menu()
        if choice == "0":
            print("Selesai.")
            return

        if choice == "1":
            run_eksekusi_script()
        else:
            run_get_bahan_menu()

        print()


if __name__ == "__main__":
    main()
