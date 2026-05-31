// static/js/main.js — CSA Session 43 Lab
//
// BEHAVIOUR LAYER (JavaScript — Slide 3)
// This file is intentionally minimal.
//
// LAB ANNOTATION:
//   This file is served from /static/js/main.js.
//   Open it in the browser (DevTools → Sources) to see client-side code.
//   In a real pentest, reading JS source reveals:
//     - API endpoint paths
//     - Client-side validation logic (that can be bypassed)
//     - Hidden feature flags
//     - Hardcoded tokens or API keys (a common misconfiguration)
//
// ATTACK SURFACE NOTE:
//   Client-side validation (e.g., maxlength checks below) is a UX aid only.
//   All validation must be repeated server-side. Burp can bypass any JS check
//   by intercepting the request after it leaves the browser.

"use strict";

// ── Auto-dismiss flash messages after 5 seconds ───────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert").forEach(el => {
    setTimeout(() => {
      el.style.transition = "opacity 0.4s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });
});

// ── Lab: highlight dangerous Jinja2 patterns in source hints ──────────────
// This runs in the browser console — it doesn't affect the DOM.
// Students can paste this into DevTools console to find | safe filters.
//
// document.querySelectorAll('*').forEach(el => {
//   if (el.innerHTML.includes('| safe')) console.warn('unsafe:', el);
// });

// ── Client-side password strength indicator (UX only, not security) ───────
const pwInput = document.querySelector('input[name="password"]');
if (pwInput) {
  pwInput.addEventListener("input", () => {
    const val = pwInput.value;
    const strong = val.length >= 8
      && /[A-Z]/.test(val)
      && /[0-9]/.test(val);
    pwInput.style.borderColor = val.length === 0
      ? ""
      : strong ? "var(--mint)" : "var(--amber)";
  });
}
