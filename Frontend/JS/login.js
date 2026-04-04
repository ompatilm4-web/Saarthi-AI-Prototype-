// =========================================================
//  login.js — Saarthi AI · Real API Integration
//  Replaces all simulated setTimeout() calls with live
//  calls to the FastAPI backend via api.js
// =========================================================

// ── Tab Switching ──────────────────────────────────────────
const tabButtons = document.querySelectorAll(".tab-button");
const formSections = document.querySelectorAll(".form-section");

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const tabName = button.getAttribute("data-tab");
    tabButtons.forEach((btn) => btn.classList.remove("active"));
    formSections.forEach((section) => section.classList.remove("active"));
    button.classList.add("active");
    document.getElementById(`${tabName}-form`).classList.add("active");
    resetAllForms();
  });
});

// ── Aadhaar input formatter ────────────────────────────────
const aadhaarInput = document.getElementById("aadhaarNumber");
aadhaarInput.addEventListener("input", (e) => {
  let value = e.target.value.replace(/\D/g, "");
  if (value.length > 12) value = value.slice(0, 12);
  let formatted = "";
  for (let i = 0; i < value.length; i++) {
    if (i > 0 && i % 4 === 0) formatted += "-";
    formatted += value[i];
  }
  e.target.value = formatted;
});

// ── Mobile input formatter ─────────────────────────────────
const mobileInput = document.getElementById("mobileNumber");
mobileInput.addEventListener("input", (e) => {
  e.target.value = e.target.value.replace(/\D/g, "").slice(0, 10);
});

// ── Shared state ───────────────────────────────────────────
let currentPhone = ""; // stores the phone number used for OTP

// ── Helper: set button loading state ──────────────────────
function setButtonLoading(btn, loading, originalText) {
  if (loading) {
    btn.innerHTML = `${originalText}... <span class="loading"></span>`;
    btn.disabled = true;
  } else {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

// ── Helper: show inline error ──────────────────────────────
function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) {
    el.textContent = message || el.dataset.defaultMsg || "";
    el.classList.add("show");
  }
}

function hideError(elementId) {
  const el = document.getElementById(elementId);
  if (el) el.classList.remove("show");
}

// ── Aadhaar: Send OTP ──────────────────────────────────────
// NOTE: Aadhaar OTP is handled via the mobile linked to Aadhaar.
// The backend /send-otp expects a phone number, so we use the
// Aadhaar number as a proxy identifier here — adapt if your
// backend handles Aadhaar differently.
document.getElementById("aadhaarLoginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const aadhaarNumber = aadhaarInput.value.replace(/-/g, "");

  if (aadhaarNumber.length !== 12) {
    showError("aadhaarError", "Please enter a valid 12-digit Aadhaar number.");
    aadhaarInput.classList.add("error");
    return;
  }

  hideError("aadhaarError");
  aadhaarInput.classList.remove("error");

  const button = document.getElementById("aadhaarSendOtp");
  const originalText = "Send OTP";
  setButtonLoading(button, true, originalText);

  try {
    // Backend expects a phone number; for Aadhaar flow pass the Aadhaar number
    // (update this if your backend has a dedicated Aadhaar endpoint)
    currentPhone = aadhaarNumber;
    await sendOtp(aadhaarNumber);

    const maskedMobile = `******${aadhaarNumber.slice(-4)}`;
    document.getElementById("aadhaarMaskedMobile").textContent = maskedMobile;

    document.getElementById("aadhaarLoginForm").style.display = "none";
    document.getElementById("aadhaarOtpContainer").classList.add("show");
    document.querySelector("#aadhaar-form .otp-input").focus();
    startTimer("aadhaar");
  } catch (err) {
    showError("aadhaarError", err.message || "Failed to send OTP. Please try again.");
    aadhaarInput.classList.add("error");
  } finally {
    setButtonLoading(button, false, originalText);
  }
});

// ── Mobile: Send OTP ───────────────────────────────────────
document.getElementById("mobileLoginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const mobileNumber = mobileInput.value;

  if (mobileNumber.length !== 10) {
    showError("mobileError", "Please enter a valid 10-digit mobile number.");
    mobileInput.classList.add("error");
    return;
  }

  hideError("mobileError");
  mobileInput.classList.remove("error");

  const button = document.getElementById("mobileSendOtp");
  const originalText = "Send OTP";
  setButtonLoading(button, true, originalText);

  try {
    currentPhone = mobileNumber;
    await sendOtp(mobileNumber);

    const maskedNumber = `******${mobileNumber.slice(-4)}`;
    document.getElementById("mobileMaskedNumber").textContent = maskedNumber;

    document.getElementById("mobileLoginForm").style.display = "none";
    document.getElementById("mobileOtpContainer").classList.add("show");
    document.querySelector("#mobile-form .otp-input").focus();
    startTimer("mobile");
  } catch (err) {
    showError("mobileError", err.message || "Failed to send OTP. Please try again.");
    mobileInput.classList.add("error");
  } finally {
    setButtonLoading(button, false, originalText);
  }
});

// ── OTP Input auto-advance ─────────────────────────────────
document.querySelectorAll(".otp-input").forEach((input, index, inputs) => {
  input.addEventListener("input", (e) => {
    e.target.value = e.target.value.replace(/\D/g, "");
    if (e.target.value.length === 1 && index < inputs.length - 1) {
      inputs[index + 1].focus();
    }
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Backspace" && !e.target.value && index > 0) {
      inputs[index - 1].focus();
    }
  });
});

// ── Timer ──────────────────────────────────────────────────
function startTimer(type) {
  let timeLeft = 30;
  const timerElement = document.getElementById(`${type}Timer`);
  const resendLink = document.getElementById(`${type}Resend`);
  resendLink.classList.add("disabled");

  const countdown = setInterval(() => {
    timeLeft--;
    timerElement.innerHTML = `Resend OTP in <strong>${timeLeft}</strong> seconds`;
    if (timeLeft <= 0) {
      clearInterval(countdown);
      timerElement.style.display = "none";
      resendLink.classList.remove("disabled");
    }
  }, 1000);
}

// ── Resend OTP ─────────────────────────────────────────────
document.getElementById("aadhaarResend").addEventListener("click", async (e) => {
  e.preventDefault();
  if (!e.target.classList.contains("disabled")) {
    try {
      await sendOtp(currentPhone);
      document.getElementById("aadhaarTimer").style.display = "inline";
      startTimer("aadhaar");
      document.querySelectorAll("#aadhaar-form .otp-input").forEach((i) => (i.value = ""));
    } catch (err) {
      alert("Failed to resend OTP: " + err.message);
    }
  }
});

document.getElementById("mobileResend").addEventListener("click", async (e) => {
  e.preventDefault();
  if (!e.target.classList.contains("disabled")) {
    try {
      await sendOtp(currentPhone);
      document.getElementById("mobileTimer").style.display = "inline";
      startTimer("mobile");
      document.querySelectorAll("#mobile-form .otp-input").forEach((i) => (i.value = ""));
    } catch (err) {
      alert("Failed to resend OTP: " + err.message);
    }
  }
});

// ── Verify OTP — Aadhaar ───────────────────────────────────
document.getElementById("aadhaarVerifyOtp").addEventListener("click", async () => {
  const otp = Array.from(document.querySelectorAll("#aadhaar-form .otp-input"))
    .map((i) => i.value)
    .join("");

  if (otp.length !== 6) {
    alert("Please enter the complete 6-digit OTP.");
    return;
  }

  const button = document.getElementById("aadhaarVerifyOtp");
  const originalText = "Verify & Login";
  setButtonLoading(button, true, originalText);

  try {
    const result = await verifyOtp(currentPhone, otp);
    if (result && result.access_token) {
      // Merge DB user with locally-saved registration data
      const existing = JSON.parse(localStorage.getItem('saarthi_user') || '{}');
      const merged = { ...existing, ...(result.user || {}) };
      if (!merged.full_name && merged.name)      merged.full_name = merged.name;
      if (!merged.name      && merged.full_name) merged.name      = merged.full_name;
      localStorage.setItem('saarthi_user', JSON.stringify(merged));
      saveToken(result.access_token);
      // Push any registration data that was saved locally back to DB
      await syncProfileAfterLogin(currentPhone, result.access_token);
      showSuccessAndRedirect();
    }
  } catch (err) {
    alert("OTP verification failed: " + (err.message || "Invalid OTP"));
  } finally {
    setButtonLoading(button, false, originalText);
  }
});

// ── Verify OTP — Mobile ────────────────────────────────────
document.getElementById("mobileVerifyOtp").addEventListener("click", async () => {
  const otp = Array.from(document.querySelectorAll("#mobile-form .otp-input"))
    .map((i) => i.value)
    .join("");

  if (otp.length !== 6) {
    alert("Please enter the complete 6-digit OTP.");
    return;
  }

  const button = document.getElementById("mobileVerifyOtp");
  const originalText = "Verify & Login";
  setButtonLoading(button, true, originalText);

  try {
    const result = await verifyOtp(currentPhone, otp);
    if (result && result.access_token) {
      // Merge DB user with locally-saved registration data
      const existing = JSON.parse(localStorage.getItem('saarthi_user') || '{}');
      const merged = { ...existing, ...(result.user || {}) };
      if (!merged.full_name && merged.name)      merged.full_name = merged.name;
      if (!merged.name      && merged.full_name) merged.name      = merged.full_name;
      localStorage.setItem('saarthi_user', JSON.stringify(merged));
      saveToken(result.access_token);
      // Push any registration data that was saved locally back to DB
      await syncProfileAfterLogin(currentPhone, result.access_token);
      showSuccessAndRedirect();
    }
  } catch (err) {
    alert("OTP verification failed: " + (err.message || "Invalid OTP"));
  } finally {
    setButtonLoading(button, false, originalText);
  }
});

// ── Back buttons ───────────────────────────────────────────
document.getElementById("aadhaarBack").addEventListener("click", () => {
  document.getElementById("aadhaarLoginForm").style.display = "block";
  document.getElementById("aadhaarOtpContainer").classList.remove("show");
  document.querySelectorAll("#aadhaar-form .otp-input").forEach((i) => (i.value = ""));
});

document.getElementById("mobileBack").addEventListener("click", () => {
  document.getElementById("mobileLoginForm").style.display = "block";
  document.getElementById("mobileOtpContainer").classList.remove("show");
  document.querySelectorAll("#mobile-form .otp-input").forEach((i) => (i.value = ""));
});

// ── Success & Redirect ─────────────────────────────────────
function showSuccessAndRedirect() {
  document.getElementById("successMessage").classList.add("show");
  setTimeout(() => {
    window.location.href = "index.html";
  }, 2000);
}

// ── Reset forms ────────────────────────────────────────────
function resetAllForms() {
  document.getElementById("aadhaarLoginForm").reset();
  document.getElementById("aadhaarLoginForm").style.display = "block";
  document.getElementById("aadhaarOtpContainer").classList.remove("show");
  hideError("aadhaarError");
  aadhaarInput.classList.remove("error");

  document.getElementById("mobileLoginForm").reset();
  document.getElementById("mobileLoginForm").style.display = "block";
  document.getElementById("mobileOtpContainer").classList.remove("show");
  hideError("mobileError");
  mobileInput.classList.remove("error");

  document.querySelectorAll(".otp-input").forEach((i) => (i.value = ""));
}

// ── Post-login profile sync ────────────────────────────────
// After OTP verify, the DB row is returned but may have nulls if
// the user just registered. We merge DB data with any locally-saved
// registration data and push it back to the DB in one PUT call.
async function syncProfileAfterLogin(mobile, token) {
  try {
    const local = JSON.parse(localStorage.getItem('saarthi_user') || '{}');

    // Build payload from local data — only fields that have real values
    const payload = {};
    if (local.full_name || local.name) {
      payload.full_name = local.full_name || local.name;
      payload.name      = payload.full_name;
    }
    if (local.age)        payload.age        = local.age;
    if (local.gender)     payload.gender     = local.gender;
    if (local.state)      payload.state      = local.state;
    if (local.occupation) payload.occupation = local.occupation;
    if (local.income)     payload.income     = local.income;
    if (local.category)   payload.category   = local.category;
    if (local.email)      payload.email      = local.email;
    if (local.aadhaar)    payload.aadhaar    = local.aadhaar;

    // Nothing useful to sync
    if (Object.keys(payload).length === 0) return;

    const res = await fetch(
      `http://localhost:8080/profile?mobile=${encodeURIComponent(mobile)}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      }
    );

    if (res.ok) {
      const data = await res.json();
      if (data.user) {
        // Final merge: DB response wins for DB fields, local fills gaps
        const synced = { ...local, ...data.user };
        if (!synced.full_name && synced.name) synced.full_name = synced.name;
        if (!synced.name && synced.full_name) synced.name = synced.full_name;
        localStorage.setItem('saarthi_user', JSON.stringify(synced));
      }
    }
  } catch (e) {
    console.warn('[syncProfileAfterLogin] failed:', e);
  }
}