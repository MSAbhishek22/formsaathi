"""FormSaathi — full click-through of the 6 steps in headless Chromium.
Serves app/ on a local port and drives the whole flow:
docs -> reading -> 2 questions -> preview (+ one edit) -> STOP gate
(backs out once, then approves) -> demo summary.
Run: python3 tests/clickthrough.py
"""
import subprocess, sys, time, urllib.request

from playwright.sync_api import sync_playwright

PORT = 8791
BASE = f"http://127.0.0.1:{PORT}"

results = []
def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(("  PASS  " if cond else "  FAIL  ") + name + ("" if cond else f"  -> {extra}"))

server = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
    cwd="app", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
try:
    for _ in range(50):
        try:
            urllib.request.urlopen(BASE + "/index.html", timeout=1)
            break
        except Exception:
            time.sleep(0.2)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE + "/index.html")
        page.wait_for_selector("#screen-docs.on")

        print("— Step 1: documents —")
        check("proceed disabled before docs are added", page.is_disabled("#btn-to-reading"))
        for doc in ["aadhaar", "marksheet", "passbook"]:
            page.click(f"[data-add-sample='{doc}']")
        check("count shows 3 / 3", "3 / 3" in page.inner_text("#docs-count"))
        check("proceed enabled after 3 docs", page.is_enabled("#btn-to-reading"))
        page.click("#btn-to-reading")

        print("— Step 2: reading + extraction results —")
        page.wait_for_selector("#extract-results", state="visible", timeout=15000)
        body = page.inner_text("#extract-body")
        check("name extracted", "Aarav Kumar Sharma" in body)
        check("source label shown (Aadhaar)", "from Aadhaar card photo" in body)
        check("school extracted", "Govt. Higher Secondary School, Patna" in body)
        check("account number extracted", "50100234567890" in body)
        check("category marked not found", "Nahi mila" in body)
        check("IFSC marked not sure", "Pakka nahi" in body)
        page.click("#btn-to-questions")

        print("— Step 3: only the missing fields are asked —")
        page.wait_for_selector("#screen-questions.on")
        check("Q1 is the category question", "category" in page.inner_text("#q-title-hi").lower())
        check("progress says 1 of 2", "1 / 2" in page.inner_text("#q-progress") or "1 of 2" in page.inner_text("#q-progress"))
        page.click("#btn-q-next")  # empty answer must be rejected
        check("empty category answer rejected", page.is_visible("#q-error.on") if page.query_selector("#q-error.on") else False)
        page.click(".chip[data-value='OBC']")
        page.click("#btn-q-next")
        check("Q2 is the IFSC question", "IFSC" in page.inner_text("#q-title-hi"))
        page.fill("#q-input", "12345")
        page.click("#btn-q-next")
        check("bad IFSC rejected with a plain error", page.query_selector("#q-error.on") is not None)
        page.fill("#q-input", "bank0123456")  # lowercase on purpose: app must normalise
        page.click("#btn-q-next")

        print("— Step 4: preview + edit —")
        page.wait_for_selector("#screen-preview.on")
        prev = page.inner_text("#preview-form")
        check("preview shows answered category OBC", "OBC" in prev)
        check("preview shows normalised IFSC BANK0123456", "BANK0123456" in prev)
        check("preview shows 'You told us' source", "You told us" in prev)
        page.click("[data-edit='classLevel']")
        page.fill("#edit-input", "Class 9")
        page.click("[data-save='classLevel']")
        prev = page.inner_text("#preview-form")
        check("edit applied (Class 9)", "Class 9" in prev)
        check("edit marked as user-edited", "You edited this" in prev)
        page.click("#btn-to-gate")

        print("— Step 5: STOP gate —")
        page.wait_for_selector("#screen-gate.on")
        gate = page.inner_text("#screen-gate")
        check("gate says nothing is sent until OK", "Nothing is sent until you press OK" in gate)
        page.click("#btn-back-fix")
        check("'go back and fix' returns to preview", page.is_visible("#screen-preview.on"))
        page.click("#btn-to-gate")
        page.click("#btn-approve")

        print("— Step 6: demo summary —")
        page.wait_for_selector("#screen-done.on")
        summ = page.inner_text("#summary-doc")
        check("summary has the name", "Aarav Kumar Sharma" in summ)
        check("summary has edited class", "Class 9" in summ)
        check("summary has OBC + IFSC", "OBC" in summ and "BANK0123456" in summ)
        check("summary states nothing was really sent", "Nothing was really sent anywhere" in summ)
        check("no JS page errors during the whole run", len(errors) == 0, "; ".join(errors))
        browser.close()
finally:
    server.terminate()

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
