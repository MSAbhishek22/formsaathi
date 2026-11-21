/* FormSaathi — parser / field-mapping unit checks.
   Loads the real <script> out of app/index.html and tests the parser
   exactly as the page uses it. Run: node tests/parser.test.js */
"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const html = fs.readFileSync(path.join(__dirname, "..", "app", "index.html"), "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("FAIL: no <script> block found in index.html"); process.exit(1); }

const sandbox = { window: {}, console };
vm.createContext(sandbox);
vm.runInContext(m[1], sandbox);
const FS = sandbox.window.FormSaathi;
if (!FS) { console.error("FAIL: window.FormSaathi was not exposed"); process.exit(1); }

let pass = 0, fail = 0;
function check(name, cond, extra) {
  if (cond) { pass++; console.log("  PASS  " + name); }
  else { fail++; console.log("  FAIL  " + name + (extra ? "  -> " + extra : "")); }
}
function eq(a, b) { return a === b; }

console.log("— Aadhaar parser —");
const a = FS.parseAadhaar(FS.SAMPLE_DOCS.aadhaar.lines);
check("name", eq(a.name && a.name.value, "Aarav Kumar Sharma"), JSON.stringify(a.name));
check("fatherName", eq(a.fatherName && a.fatherName.value, "Ramesh Kumar Sharma"));
check("dob", eq(a.dob && a.dob.value, "14/03/2011"));
check("address has street + PIN", !!a.address && a.address.value.includes("MG Road") && a.address.value.includes("800001"), a.address && a.address.value);
check("aadhaarLast4 = 9012", eq(a.aadhaarLast4 && a.aadhaarLast4.value, "9012"), a.aadhaarLast4 && a.aadhaarLast4.value);
check("all aadhaar fields high confidence", ["name","fatherName","dob","address","aadhaarLast4"].every(k => a[k] && a[k].confidence === "high" && a[k].status === "found"));

console.log("— Marksheet parser —");
const mk = FS.parseMarksheet(FS.SAMPLE_DOCS.marksheet.lines);
check("school", eq(mk.school && mk.school.value, "Govt. Higher Secondary School, Patna"));
check("classLevel = 'Class 8'", eq(mk.classLevel && mk.classLevel.value, "Class 8"), mk.classLevel && mk.classLevel.value);

console.log("— Passbook parser —");
const pb = FS.parsePassbook(FS.SAMPLE_DOCS.passbook.lines);
check("bankAccount", eq(pb.bankAccount && pb.bankAccount.value, "50100234567890"));
check("bankIfsc is UNCLEAR (smudged in the sample)", !!pb.bankIfsc && pb.bankIfsc.status === "unclear" && pb.bankIfsc.confidence === "low", JSON.stringify(pb.bankIfsc));

console.log("— Full extraction / field mapping —");
const all = FS.extractAll(["aadhaar", "marksheet", "passbook"]);
check("10 form fields", all.length === 10, "got " + all.length);
const byKey = {}; all.forEach(f => byKey[f.key] = f);
check("category is MISSING (on no document)", byKey.category.status === "missing");
check("bankIfsc is UNCLEAR", byKey.bankIfsc.status === "unclear");
const toAsk = all.filter(f => f.status !== "found");
check("exactly 2 fields left to ask (category + IFSC)", toAsk.length === 2 && toAsk.every(f => ["category", "bankIfsc"].includes(f.key)), toAsk.map(f => f.key).join(","));
check("8 fields found", all.filter(f => f.status === "found").length === 8);
check("every found field carries a source label", all.filter(f => f.status === "found").every(f => f.sourceEn && f.sourceEn.startsWith("from ")), JSON.stringify(all.filter(f => f.status === "found" && !f.sourceEn).map(f => f.key)));
check("name source is the Aadhaar card", byKey.name.sourceEn === "from Aadhaar card photo", byKey.name.sourceEn);
check("school source is the marksheet", byKey.school.sourceEn === "from Marksheet photo", byKey.school.sourceEn);
check("account source is the passbook", byKey.bankAccount.sourceEn === "from Passbook photo", byKey.bankAccount.sourceEn);

console.log("— extractFromDocument interface —");
const one = FS.extractFromDocument(FS.SAMPLE_DOCS.passbook);
check("returns passbook fields with source attached", !!one.bankAccount && one.bankAccount.sourceEn === "from Passbook photo");

console.log("\n" + pass + " passed, " + fail + " failed");
process.exit(fail ? 1 : 0);
