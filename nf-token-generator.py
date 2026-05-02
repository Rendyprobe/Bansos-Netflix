import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "input.txt"
EKSEKUSI_FILE = PROJECT_DIR / "eksekusi.py"
PLAYWRIGHT_BROWSERS_DIR = PROJECT_DIR / ".ms-playwright"
TARGET_URL = "https://netflixcookiesmap.vercel.app/"
COPY_WAIT_TIMEOUT_MS = 15000

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
            run_interactive_copy()

        print()


if __name__ == "__main__":
    main()
