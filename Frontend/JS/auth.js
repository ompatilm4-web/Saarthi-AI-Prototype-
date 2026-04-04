const AUTH_API = "/api/auth";

async function sendOTP(mobile) {
  const res = await fetch(`${AUTH_API}/send-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mobile })
  });
  return res.json();
}

async function verifyOTP(mobile, otp) {
  const res = await fetch(`${AUTH_API}/verify-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mobile, otp })
  });
  const data = await res.json();
  if (data.token) {
    localStorage.setItem("saarthi_token", data.token);
    localStorage.setItem("saarthi_user", JSON.stringify(data.user));
    window.location.href = "dashboard.html";
  }
  return data;
}

function logout() {
  // Clear this user's scoped chat history and session before removing user data
  try {
    const user = JSON.parse(localStorage.getItem('saarthi_user') || '{}');
    const uid = user.id || user.mobile || user.phone || user.user_id || null;
    if (uid) {
      localStorage.removeItem(`saarthi_history_user_${uid}`);
      localStorage.removeItem(`saarthi_session_id_user_${uid}`);
    }
  } catch (e) {}

  localStorage.removeItem("saarthi_token");
  localStorage.removeItem("saarthi_user");
  window.location.href = "login.html";
}

function isLoggedIn() {
  return !!localStorage.getItem("saarthi_token");
}

function getUser() {
  return JSON.parse(localStorage.getItem("saarthi_user") || "{}");
}