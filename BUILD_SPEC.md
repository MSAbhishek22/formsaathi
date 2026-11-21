# FormSaathi — build spec for the Product Space Agentic AI sprint (21 Nov)

## The idea in one line
A person photographs their documents; the agent fills the government form for them, asks only for the 2-3 fields it cannot find, and stops for a human OK before anything is submitted.

## Demo form
A realistic mock "Scholarship Application Form" (name, father's name, DOB, address, category, school, class, bank account, Aadhaar last 4) — clearly labelled DEMO, no real submission anywhere.

## Flow (what the demo must show, in order)
1. Upload photos of 2-3 sample documents (Aadhaar-style card, marksheet, bank passbook — all SAMPLE/fake data, generated locally).
2. Agent extracts fields with OCR/vision, shows each field with its source ("from Aadhaar card photo") and a confidence mark.
3. Missing/unclear fields (say: category, bank IFSC) are asked one by one in plain Hindi+English — only those, nothing else.
4. Filled form preview, field by field, with edit option.
5. Big STOP point: "Check everything. Nothing is sent until you press OK." — human approval gate is the headline feature.
6. On OK: a filled PDF-style summary is generated (demo only).

## Build notes
- Single-page app, static hosting (GitHub Pages), same pattern as JalRaksha.
- Extraction can be simulated with a small local parser over the sample docs for reliability in the demo; if a vision API key is available at build time, wire it behind the same interface. Never claim real OCR if it is simulated — the write-up must say which parts are real.
- Voice input for the missing-field answers (Hindi) is a plus if time allows.
- Tests: field-mapping unit checks + a full click-through of the 6 steps.

## Submission pack checklist
- [ ] Live link
- [ ] Repo
- [ ] Demo video: screen recording of the LIVE site, one full run of the flow
- [ ] Write-up in plain words: who it helps (people who fear forms / low literacy / elderly), the human-OK gate as the safety story
