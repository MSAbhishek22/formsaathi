# FormSaathi — फ़ॉर्म साथी

FormSaathi fills a form for a person who finds forms hard. The person adds photos of their documents, the app reads what it can, asks only for the few things it could not find, shows the full form for checking, and then stops. Nothing moves ahead until the person presses OK.

This build is a demo made for the Product Space Agentic AI Hackathon sprint (21 Nov 2026). The form is a mock Scholarship Application Form. All names, numbers and documents in it are fake sample data. Nothing is sent anywhere.

## How to run it

It is one file: `index.html`. No build step, no server code, no accounts.

- Open `index.html` in a browser, or
- serve the folder: `python3 -m http.server` in this folder, then open `http://localhost:8000`

It works on a phone-sized screen. That is on purpose — the people this is for mostly have a phone, not a computer.

## The flow, step by step

1. **Documents.** Three sample documents are built into the page: an Aadhaar-style card, a marksheet and a bank passbook, all stamped SAMPLE. You add each one with a button. You can also pick your own photo file — it is shown on the card, but see "what is real" below before you trust it.
2. **Reading.** The app reads the documents one by one and shows a table: every form field, the value it found, where it found it ("from Aadhaar card photo"), and a confidence mark — Sure, Not sure, or Not found.
3. **Questions.** Only the fields that were not found or not clear are asked, one at a time, in Hindi and English. In this demo that is exactly two: category (it is on none of the documents) and bank IFSC (it is half rubbed off on the sample passbook, so the app will not guess it). Answers can be typed, tapped from options, or spoken in Hindi if the browser supports voice input.
4. **Preview.** The filled form, field by field. Any field can be fixed with its Edit button. The form says DEMO on it.
5. **The stop.** A big STOP screen: "Check everything. Nothing is sent until you press OK." One button goes back to fix things. One button gives the OK. This stop is the main point of the app — the agent never sends anything on its own.
6. **Done.** A clean copy of the filled form, with a Print / PDF button (uses the browser's own print, "Save as PDF" works) and a start-again button.

## What is real and what is not

Real:

- The whole flow above, in the browser, with no server.
- A small text parser in the page (`parseAadhaar`, `parseMarksheet`, `parsePassbook` in the script) that reads the words printed on the sample documents and maps them to form fields, with a source and a confidence mark per field.
- The IFSC check is a real format check (4 letters, then 0, then 6 letters/digits). A wrong code is refused with a plain message.
- Voice answers use the browser's own speech recognition (Hindi), where the browser offers it.

Not real, and not claimed to be:

- **No photo reading.** The parser reads the printed words of the built-in sample documents. It does not read pixels, and it does not read your own uploaded photo — if you upload one, the fields still come from the sample text. A real version would read the photo with OCR. The reading code sits behind one function, `extractFromDocument(doc)`, so an OCR reader can replace the parser without touching the rest of the app.
- **No real submission.** The form is a mock. The OK button only makes the summary copy. Nothing leaves the page.
- **The data is fake.** The student, the school, the account number — all made up for the demo.

## Tests

In the project folder, one level up from this app folder:

- `node tests/parser.test.js` — 20 checks on the parser and the field mapping (which field comes from which document, what stays missing, what stays unclear).
- `python3 tests/clickthrough.py` — opens the app in headless Chromium and clicks through all 6 steps, including a wrong IFSC, an edit in the preview, and going back from the STOP screen once before approving.
