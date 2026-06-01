// main.js
// This file adds small interactive features to the page.
// It runs in the browser (client-side), not on the server.

"use strict";

// ── Auto-dismiss flash messages after 5 seconds ──────────────────────────
// Flash messages are the coloured notification bars (e.g. "Account created").
// This code fades them out and removes them automatically.

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert").forEach(el => {
    setTimeout(() => {
      el.style.transition = "opacity 0.4s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });
});

// ── Password strength indicator ──────────────────────────────────────────
// Changes the border colour of the password field as the user types:
//   Green = meets the requirements (8+ chars, uppercase, digit)
//   Amber = doesn't meet them yet

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
