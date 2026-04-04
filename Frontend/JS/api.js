const API_BASE = "http://localhost:8080";

// ── User helpers ───────────────────────────────────────────
function getUser() {
    try { return JSON.parse(localStorage.getItem("saarthi_user") || "{}"); }
    catch { return {}; }
}
function saveToken(token) { localStorage.setItem("saarthi_token", token); }
function saveUser(user)  { localStorage.setItem("saarthi_user", JSON.stringify(user)); }
function getToken()      { return localStorage.getItem("saarthi_token"); }

function logout() {
    // Scoped chat history cleanup
    try {
        const user = getUser();
        const uid = user.id || user.mobile || null;
        if (uid) {
            localStorage.removeItem(`saarthi_history_${uid}`);
            localStorage.removeItem(`saarthi_session_id_${uid}`);
        }
    } catch (e) {}
    localStorage.removeItem("saarthi_token");
    localStorage.removeItem("saarthi_user");
    window.location.href = "login.html";
}

function isLoggedIn() { return !!getToken(); }

// ── OTP flow ───────────────────────────────────────────────
// Single source of truth — always hits http://localhost:8080
async function sendOtp(mobile) {
    const res = await fetch(`${API_BASE}/send-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to send OTP");
    return data;
}

async function verifyOtp(mobile, otp) {
    const res = await fetch(`${API_BASE}/verify-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile, otp })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "OTP verification failed");

    // ── Save token ──
    if (data.token) saveToken(data.token);

    // ── Merge DB user with any existing localStorage data ──
    // Registration saves full_name/email/aadhaar locally before login.
    // DB row may not have those yet if profile PUT raced or failed,
    // so we merge: DB fields win, but locally-saved fields fill gaps.
    // Also normalise: DB uses 'name' column, frontend uses 'full_name'.
    if (data.user) {
        const existing = getUser();
        const dbUser = data.user;
        // Ensure full_name is always populated from whichever source has it
        if (!dbUser.full_name && dbUser.name)       dbUser.full_name = dbUser.name;
        if (!dbUser.name      && dbUser.full_name)  dbUser.name      = dbUser.full_name;
        const merged = { ...existing, ...dbUser };
        saveUser(merged);
    }

    return { access_token: data.token, user: data.user, ...data };
}

// ── Chat ───────────────────────────────────────────────────
async function askSaarthi(userMessage, lang, userProfile) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${getToken()}`
        },
        body: JSON.stringify({ message: userMessage, lang, profile: userProfile })
    });
    const data = await response.json();
    return data.reply;
}

// ── Schemes ────────────────────────────────────────────────
async function fetchAllSchemes() {
    const res = await fetch(`${API_BASE}/api/v1/schemes/`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

async function apiFetch(path, options = {}) {
    const res = await fetch(`${API_BASE}/api/v1${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

async function fetchRecommendations(userProfile) {
    return apiFetch("/recommendations/", {
        method: "POST",
        body: JSON.stringify({ user_profile: userProfile, top_n: 10, lang: "en" })
    });
}

async function fetchRecommendationExplanation(schemeId, userProfile, lang = "en") {
    return apiFetch("/recommendations/explain", {
        method: "POST",
        body: JSON.stringify({ scheme_id: schemeId, user_profile: userProfile, lang })
    });
}

// ── Chat history ───────────────────────────────────────────
async function fetchChatHistory() {
    try {
        const user = getUser();
        const mobile = user.mobile;
        if (!mobile) return [];
        const res = await fetch(
            `${API_BASE}/chat-history?mobile=${encodeURIComponent(mobile)}`,
            { headers: { "Authorization": `Bearer ${getToken()}` } }
        );
        if (!res.ok) return [];
        const data = await res.json();
        return data.history || [];
    } catch (e) {
        console.warn("fetchChatHistory failed:", e);
        return [];
    }
}

// ── Personalized recommendations ──────────────────────────
async function fetchUserRecommendations(userProfile, topN = 6) {
    try {
        return await apiFetch("/recommendations/for-user", {
            method: "POST",
            body: JSON.stringify({
                user_profile: userProfile,
                top_n: topN,
                lang: userProfile.preferred_lang || "en",
                use_llm_rerank: false
            })
        });
    } catch (e) {
        console.warn("fetchUserRecommendations failed:", e);
        return { recommendations: [] };
    }
}