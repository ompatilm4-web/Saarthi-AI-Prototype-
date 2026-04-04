// =========================================================
//  main.js — Saarthi AI
// =========================================================

// ── Conversation History Manager ──────────────────────────
class ConversationManager {
    constructor() {
        this.sessionId = null;
        this.history = [];
        this.maxHistoryLength = 50;
        // Do NOT load here — user not in localStorage at parse time.
        // Call initForCurrentUser() after login/page-load auth check.
    }

    // Returns Supabase user id or mobile — matches auth.py response
    getUserId() {
        try {
            const user = JSON.parse(localStorage.getItem('saarthi_user') || '{}');
            return user.mobile || user.id || null;
        } catch { return null; }
    }

    getHistoryKey() {
        const uid = this.getUserId();
        return uid ? `saarthi_history_${uid}` : null;
    }

    getSessionKey() {
        const uid = this.getUserId();
        return uid ? `saarthi_session_id_${uid}` : null;
    }

    // Call once after saarthi_user is written to localStorage.
    // Loads from Supabase first, falls back to localStorage cache.
    async initForCurrentUser() {
        this.sessionId = null;
        this.history = [];

        // Try Supabase first
        if (typeof fetchChatHistory === 'function') {
            try {
                const rows = await fetchChatHistory();
                if (rows && rows.length > 0) {
                    // Map DB rows { role, message, lang, created_at } → history format
                    this.history = rows.map(r => ({
                        role: r.role,
                        content: r.message,
                        timestamp: r.created_at
                    }));
                    // Update localStorage cache for this user
                    this.saveToStorage();
                    console.log(`[History] Loaded ${this.history.length} messages from Supabase`);
                    return;
                }
            } catch (e) {
                console.warn('[History] Supabase fetch failed, falling back to localStorage', e);
            }
        }

        // Fallback: localStorage cache
        this.loadFromStorage();
    }

    // Generate or retrieve session ID
    getSessionId() {
        const key = this.getSessionKey();
        if (!key) return 'session_guest';
        if (!this.sessionId) {
            this.sessionId = localStorage.getItem(key);
            if (!this.sessionId) {
                this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem(key, this.sessionId);
            }
        }
        return this.sessionId;
    }

    // Add message to history
    addMessage(role, content) {
        this.history.push({
            role: role,
            content: content,
            timestamp: new Date().toISOString()
        });

        // Trim history if too long
        if (this.history.length > this.maxHistoryLength) {
            this.history = this.history.slice(-this.maxHistoryLength);
        }

        // Save to localStorage for persistence
        this.saveToStorage();
    }

    // Add user message
    addUserMessage(content) {
        this.addMessage('user', content);
    }

    // Add assistant message
    addAssistantMessage(content) {
        this.addMessage('assistant', content);
    }

    // Get full history
    getHistory() {
        return this.history;
    }

    // Get last N messages for context
    getLastMessages(count = 10) {
        return this.history.slice(-count);
    }

    // Clear history
    clearHistory() {
        if (confirm('Clear all conversation history? This cannot be undone.')) {
            this.history = [];
            this.sessionId = null;
            const hKey = this.getHistoryKey();
            const sKey = this.getSessionKey();
            if (hKey) localStorage.removeItem(hKey);
            if (sKey) localStorage.removeItem(sKey);
            
            // Clear chat display except welcome message
            this.resetChatDisplay();
        }
    }

    // Reset chat display to welcome message
    resetChatDisplay() {
        if (chatDisplay) {
            while (chatDisplay.firstChild) chatDisplay.removeChild(chatDisplay.firstChild);
            const welcomeDiv = document.createElement("div");
            welcomeDiv.className = "message assistant-message";
            welcomeDiv.setAttribute('data-text', '👋 Namaste! How can I help you with government services today?');
            welcomeDiv.setAttribute('data-lang', getSelectedLang());
            welcomeDiv.innerHTML = '<p class="msg-text">👋 Namaste! How can I help you with government services today?</p>';
            
            // Add action buttons
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'msg-actions';
            actionsDiv.innerHTML = `
                <button class="msg-repeat-btn" onclick="saarthiMsgRepeat(this)">🔁 Repeat</button>
                <button class="msg-stop-btn" onclick="saarthiMsgStop()">⏹ Stop</button>
            `;
            welcomeDiv.appendChild(actionsDiv);
            chatDisplay.appendChild(welcomeDiv);
        }
    }

    // Save to localStorage (per-user cache)
    saveToStorage() {
        try {
            const key = this.getHistoryKey();
            if (key) localStorage.setItem(key, JSON.stringify(this.history));
        } catch (e) {
            console.warn('Failed to save history to localStorage', e);
        }
    }

    // Load from localStorage cache (fallback when offline)
    loadFromStorage() {
        try {
            const hKey = this.getHistoryKey();
            const sKey = this.getSessionKey();
            if (!hKey) return;
            const saved = localStorage.getItem(hKey);
            if (saved) {
                this.history = JSON.parse(saved);
                this.restoreChatDisplay();
            }
            this.sessionId = sKey ? localStorage.getItem(sKey) : null;
        } catch (e) {
            console.warn('Failed to load history from localStorage', e);
            this.history = [];
        }
    }

    // Restore chat messages to display
    restoreChatDisplay() {
        if (!chatDisplay || this.history.length === 0) return;

        // Clear existing messages
        while (chatDisplay.firstChild) chatDisplay.removeChild(chatDisplay.firstChild);

        // Add all history messages
        this.history.forEach(msg => {
            this.displayMessage(msg.role, msg.content);
        });
    }

    // Display a message in the chat
    displayMessage(role, content) {
        if (!chatDisplay) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        messageDiv.setAttribute('data-text', content);
        messageDiv.setAttribute('data-lang', getSelectedLang());

        // Format content
        const textPara = document.createElement('p');
        textPara.className = 'msg-text';
        textPara.innerHTML = this.formatMessage(content);
        messageDiv.appendChild(textPara);

        // Add action buttons for assistant messages
        if (role === 'assistant') {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'msg-actions';

            // Detect if this message mentions any scheme
            const schemeDetectKw = [
                "scheme", "yojana", "योजना", "benefit", "लाभ", "apply", "आवेदन",
                "eligib", "पात्र", "pm-kisan", "pmkisan", "ayushman", "mudra",
                "scholarship", "pension", "awas", "nrega", "mgnrega", "fasal bima",
                "subsidy", "सब्सिडी", "ration", "राशन", "सरकारी", "pradhan mantri",
                "प्रधानमंत्री", "bima", "बीमा", "sukanya", "ujjwala", "vishwakarma"
            ];
            const isSchemeMsg = schemeDetectKw.some(kw => content.toLowerCase().includes(kw));

            actionsDiv.innerHTML = `
                <button class="msg-repeat-btn" onclick="saarthiMsgRepeat(this)">🔁 Repeat</button>
                <button class="msg-stop-btn" onclick="saarthiMsgStop()">⏹ Stop</button>
                ${isSchemeMsg ? `<button class="msg-eligibility-btn" onclick="window.location.href='apply-scheme.html#eligSection'">✅ Check Eligibility</button>` : ''}
            `;
            messageDiv.appendChild(actionsDiv);
        }

        chatDisplay.appendChild(messageDiv);
        
        // Scroll to bottom
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    // Format message with markdown-like syntax
    formatMessage(text) {
        return text
            .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.+?)\*/g, "<em>$1</em>")
            .replace(/^###\s+(.+)$/gm, "<strong>$1</strong>")
            .replace(/^##\s+(.+)$/gm, "<strong>$1</strong>")
            .replace(/^#\s+(.+)$/gm, "<strong>$1</strong>")
            .replace(/^[\-\*]\s+(.+)$/gm, "• $1")
            .replace(/\n/g, "<br>");
    }
}

// ── DOM References ─────────────────────────────────────────
const heroSection = document.getElementById("heroSection");
const chatOnlyView = document.getElementById("chatOnlyView");
const featuresSection = document.getElementById("features");
const languagesSection = document.getElementById("languages");
const footerSection = document.getElementById("footerSection");
const navLinks = document.querySelectorAll(".nav-link");

const textInputSimple = document.getElementById("textInputSimple");
const micButtonLarge = document.getElementById("micButtonLarge");
const statusTextSimple = document.getElementById("statusTextSimple");

const micButton = document.getElementById("micButton");
const sendButton = document.getElementById("sendButton");
const textInput = document.getElementById("textInput");
const chatDisplay = document.getElementById("chatDisplay");
const statusText = document.getElementById("statusText");
const languageSelect = document.getElementById("language");
const backButton = document.getElementById("backButton");

// ── App state ──────────────────────────────────────────────
let isChatActive = false;
let isListening = false;
let currentSessionId = null;

// ── Initialize Conversation Manager ────────────────────────
const conversationManager = new ConversationManager();

// ── Tracks the last detected language from speech ──────────
let lastDetectedLang = null;

// ── Audio management ───────────────────────────────────────
let currentAudio = null;

function stopCurrentAudio() {
  if (currentAudio) {
    try { currentAudio.pause(); currentAudio.src = ""; } catch(e) {}
    currentAudio = null;
  }
  if (window.speechSynthesis) window.speechSynthesis.cancel();
}

// ── Message Button Helpers ─────────────────────────────────
function saarthiMsgRepeat(btn) {
  const msgDiv = btn.closest('[data-text]');
  if (!msgDiv) return;
  const text = msgDiv.dataset.text || '';
  const lang = msgDiv.dataset.lang || getSelectedLang() || 'hi-IN';
  // Stop anything currently playing first
  stopCurrentAudio();
  // saarthiTTS is defined in tts.js and attached to window
  if (window.saarthiTTS && typeof window.saarthiTTS.speak === 'function') {
    window.saarthiTTS.speak(text, lang);
  } else {
    speakWithBrowserTTS(text, lang.split('-')[0]);
  }
}

function saarthiMsgStop() {
  stopCurrentAudio();
  // Also call saarthiTTS.stop() which cancels speechSynthesis via tts.js
  if (window.saarthiTTS && typeof window.saarthiTTS.stop === 'function') {
    window.saarthiTTS.stop();
  }
}

function playAudioBase64(base64Data) {
  stopCurrentAudio();
  currentAudio = new Audio("data:audio/mp3;base64," + base64Data);
  currentAudio.play().catch(err => console.warn("TTS play failed:", err));
}

function speakWithBrowserTTS(text, langCode) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();

  const localeMap = {
    hi: "hi-IN", en: "en-IN", bn: "bn-IN", ta: "ta-IN",
    te: "te-IN", mr: "mr-IN", gu: "gu-IN", kn: "kn-IN",
    ml: "ml-IN", pa: "pa-IN", or: "or-IN", as: "as-IN",
    ur: "ur-IN", ne: "ne-IN", sd: "sd-IN"
  };
  const locale = localeMap[langCode] || "hi-IN";

  // Clean text for speech — keep all content, just remove formatting symbols
  const cleanText = text
    .replace(/<[^>]*>/g, " ")           // remove HTML tags
    .replace(/\*\*(.+?)\*\*/g, "$1")    // remove bold markers, keep text
    .replace(/\*(.+?)\*/g, "$1")        // remove italic markers, keep text
    .replace(/#{1,3}\s+/g, "")          // remove heading markers
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")  // markdown links → just text
    .replace(/https?:\/\/\S+/g, "")     // remove bare URLs
    .replace(/[•\-]\s+/g, ", ")         // bullet points → comma pause
    .replace(/(\d+)\.\s+/g, "$1. ")     // keep numbered steps
    .replace(/\n+/g, " ")               // newlines to space
    .replace(/\s+/g, " ")               // normalize spaces
    .trim();

  if (!cleanText) return;

  // Split into chunks of exactly 120 chars at word boundaries
  function chunkText(t) {
    const chunks = [];
    let remaining = t;
    while (remaining.length > 0) {
      if (remaining.length <= 120) {
        chunks.push(remaining.trim());
        break;
      }
      // Find last space before 120 chars
      let cutAt = 120;
      while (cutAt > 80 && remaining[cutAt] !== ' ') cutAt--;
      if (cutAt <= 80) cutAt = 120; // no space found, hard cut
      chunks.push(remaining.slice(0, cutAt).trim());
      remaining = remaining.slice(cutAt).trim();
    }
    return chunks.filter(c => c.length > 0);
  }

  const chunks = chunkText(cleanText);
  console.log("🔊 TTS chunks:", chunks.length, "| lang:", locale);

  // Pick best voice for the language
  function getVoice(voices) {
    return (
      voices.find(v => v.lang === locale) ||
      voices.find(v => v.name.toLowerCase().includes("heera")) ||
      voices.find(v => v.name.toLowerCase().includes("raveena")) ||
      voices.find(v => v.lang === "en-IN") ||
      voices.find(v => v.lang.startsWith("en")) ||
      voices[0] || null
    );
  }

  function doSpeak(voice) {
    let i = 0;
    const ka = setInterval(() => {
      if (window.speechSynthesis.speaking) window.speechSynthesis.resume();
      else clearInterval(ka);
    }, 3000);

    function next() {
      if (i >= chunks.length) { clearInterval(ka); return; }
      const u = new SpeechSynthesisUtterance(chunks[i]);
      u.lang = voice ? voice.lang : locale;
      u.rate = 0.82;
      u.pitch = 1.05;
      u.volume = 1.0;
      if (voice) u.voice = voice;
      u.onend = () => { i++; setTimeout(next, 50); };
      u.onerror = () => { i++; next(); };
      window.speechSynthesis.speak(u);
    }
    next();
  }

  setTimeout(() => {
    const voices = window.speechSynthesis.getVoices();
    if (voices.length === 0) {
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.onvoiceschanged = null;
        doSpeak(getVoice(window.speechSynthesis.getVoices()));
      };
    } else {
      const voice = getVoice(voices);
      console.log("🔊 Voice:", voice ? voice.name : "default");
      doSpeak(voice);
    }
  }, 150);
}

// ── CHANGE 1: Improved detectLangFromTranscript ────────────
// Uses character scoring instead of first-match to find
// the dominant script across the whole transcript
function detectLangFromTranscript(text) {
  if (!text || !text.trim()) return null;

  const scores = {
    bn: 0, ta: 0, te: 0, kn: 0,
    ml: 0, gu: 0, pa: 0, hi: 0, en: 0
  };

  for (const ch of text) {
    const cp = ch.codePointAt(0);
    if      (cp >= 0x0980 && cp <= 0x09FF) scores.bn++;  // Bengali
    else if (cp >= 0x0B80 && cp <= 0x0BFF) scores.ta++;  // Tamil
    else if (cp >= 0x0C00 && cp <= 0x0C7F) scores.te++;  // Telugu
    else if (cp >= 0x0C80 && cp <= 0x0CFF) scores.kn++;  // Kannada
    else if (cp >= 0x0D00 && cp <= 0x0D7F) scores.ml++;  // Malayalam
    else if (cp >= 0x0A80 && cp <= 0x0AFF) scores.gu++;  // Gujarati
    else if (cp >= 0x0A00 && cp <= 0x0A7F) scores.pa++;  // Punjabi
    else if (cp >= 0x0900 && cp <= 0x097F) scores.hi++;  // Devanagari
    else if ((cp >= 0x41 && cp <= 0x5A) || (cp >= 0x61 && cp <= 0x7A)) scores.en++;
  }

  const dominant = Object.entries(scores).reduce((a, b) => b[1] > a[1] ? b : a);
  if (dominant[1] === 0) return null;

  // Devanagari — distinguish Marathi from Hindi
  if (dominant[0] === "hi") {
    const marathiMarkers = [
      "आहे","नाही","मला","तुम्ही","आम्ही","कसे","येथे","तेथे",
      "सांगा","करा","द्या","घ्या","माझे","तुमचे","अर्ज",
      "माहिती","मदत","शेती","आरोग्य","पैसे","काय","मी","हे","ते",
      "होते","होता","होती","केले","करतो","करते","आणि","किंवा",
      "म्हणजे","म्हणून","त्यांना","त्याला","तिला","आपण"
    ];
    return marathiMarkers.some(w => text.includes(w)) ? "mr" : "hi";
  }

  return dominant[0];
}

// ── Get effective TTS language ─────────────────────────────
function getEffectiveTTSLang() {
  // Always prioritize UI language selector first
  if (languageSelect && languageSelect.value) {
    return languageSelect.value.split("-")[0];
  }
  const saved = localStorage.getItem("saarthi_lang");
  if (saved) return saved.split("-")[0];
  if (lastDetectedLang) return lastDetectedLang;
  return "hi";
}

// ── Speech Recognition ─────────────────────────────────────
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognitionSupported = !!SpeechRecognition;

// ── Init ───────────────────────────────────────────────────
if (chatOnlyView) {
  chatOnlyView.style.display = "none";
  chatOnlyView.classList.remove("active");
}

const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get("openChat") === "true") {
  window.addEventListener("DOMContentLoaded", () => showChatOnly(""));
  if (document.readyState !== "loading") showChatOnly("");
}

window.testShowChat = function () { showChatOnly("Test message"); };

function getSelectedLang() {
  if (languageSelect && languageSelect.value) return languageSelect.value;
  const saved = localStorage.getItem("saarthi_lang");
  if (saved) return saved.includes("-") ? saved : saved + "-IN";
  return "hi-IN";
}

// =========================================================
//  MOCK AI RESPONSE (fallback only)
// =========================================================
function getMockResponse(userMessage) {
  const msg = userMessage.toLowerCase();

  if (msg.includes("pension") || msg.includes("पेंशन"))
    return "To check your pension status, visit the NSAP portal or call helpline <strong>1800-123-456</strong>. Would you like step-by-step guidance?";

  if (msg.includes("pm kisan") || msg.includes("farmer") || msg.includes("किसान"))
    return "PM-KISAN provides <strong>₹6,000 per year</strong> to farmer families in 3 instalments. The next instalment is due in March 2026. Want me to help you check your status?";

  if (msg.includes("certificate") || msg.includes("birth") || msg.includes("income") || msg.includes("caste"))
    return "You can apply for certificates through your state portal. Which do you need?<br><br>• 📄 Birth Certificate<br>• 📄 Caste Certificate<br>• 📄 Income Certificate<br>• 📄 Residence Certificate";

  if (msg.includes("ration") || msg.includes("राशन"))
    return "For ration card services I can help you check status, add members, or apply for a new card. Please share your ration card number or Aadhaar to proceed.";

  if (msg.includes("ayushman") || msg.includes("health") || msg.includes("hospital"))
    return "Ayushman Bharat PM-JAY provides <strong>₹5 lakh health cover</strong> per family per year. To check eligibility visit pmjay.gov.in or call <strong>14555</strong>.";

  if (msg.includes("mudra") || msg.includes("loan") || msg.includes("business"))
    return "PM Mudra Yojana provides loans from <strong>₹50,000 to ₹10 lakh</strong> for small businesses at low interest. Want me to guide you through the application?";

  if (msg.includes("scholarship") || msg.includes("education") || msg.includes("student"))
    return "Several scholarships are available on <strong>scholarships.gov.in</strong>. You can filter by category (SC/ST/OBC/Minority) and education level. Want me to find the best match for you?";

  if (msg.includes("hello") || msg.includes("hi") || msg.includes("नमस्ते") || msg.includes("namaste"))
    return "Namaste! 🙏 I'm Saarthi, your AI assistant for government services. Ask me about:<br><br>🌾 Farmer schemes &nbsp;|&nbsp; 💰 Pensions<br>📄 Certificates &nbsp;|&nbsp; 🏥 Healthcare<br>🎓 Education &nbsp;|&nbsp; 🏦 Banking";

  return "I'm here to help! You can ask me about:<br><br>🌾 <strong>Farmer schemes</strong> (PM-KISAN, Fasal Bima)<br>💰 <strong>Pensions & benefits</strong><br>📄 <strong>Certificates</strong> (Birth, Caste, Income)<br>🏥 <strong>Healthcare</strong> (Ayushman Bharat)<br>🎓 <strong>Education & scholarships</strong><br>🏦 <strong>Banking</strong> (Jan Dhan, Mudra)";
}

// =========================================================
//  sendMessageToBackend
// =========================================================
// Global variable for pending document upload
window.pendingDocFile = null;

async function sendMessageToBackend(message) {
  addTypingIndicator();

  const ttsLang = getEffectiveTTSLang();
  const queryLang = ttsLang;
  console.log("📨 Query lang:", queryLang, "| 🔊 TTS lang:", ttsLang);

  try {
    const userProfile = JSON.parse(localStorage.getItem("saarthi_user") || "{}");

    // ── Document upload flow ──────────────────────────────
    if (window.pendingDocFile) {
      const file = window.pendingDocFile;
      window.pendingDocFile = null;
      // Clear preview bar if present
      const bar = document.getElementById("filePreviewBar");
      if (bar) bar.style.display = "none";
      const fileInput = document.getElementById("docFileInput");
      if (fileInput) fileInput.value = "";

      // ── Read file once as dataURL — used for preview AND base64 ──
      const isPdf   = file.type === "application/pdf";
      const isImage = file.type.startsWith("image/");
      const ext     = file.name.split('.').pop().toUpperCase();

      const fileDataUrl = await new Promise((resolve, reject) => {
        const r = new FileReader();
        r.onload  = () => resolve(r.result);
        r.onerror = reject;
        r.readAsDataURL(file);
      });
      const base64 = fileDataUrl.split(",")[1];

      // ── Show doc bubble ABOVE the user text message ───────
      // Pull out the last user text bubble so we can reinsert it after preview
      const allUserMsgs = chatDisplay
        ? [...chatDisplay.querySelectorAll('.user-message:not(.doc-preview-bubble)')]
        : [];
      const lastUserMsg = allUserMsgs.length ? allUserMsgs[allUserMsgs.length - 1] : null;
      if (lastUserMsg) chatDisplay.removeChild(lastUserMsg);

      const previewDiv = document.createElement("div");
      previewDiv.className = "message user-message doc-preview-bubble";

      if (isImage) {
        previewDiv.innerHTML = `
          <div class="doc-bubble-wrap">
            <img src="${fileDataUrl}" alt="${file.name}"
              style="max-width:220px;max-height:180px;border-radius:10px;display:block;cursor:pointer;"
              title="Click to expand"
              onclick="this.style.maxWidth=this.style.maxWidth==='100%'?'220px':'100%'">
            <div class="doc-bubble-name">\u{1F5BC}\uFE0F ${file.name}</div>
            <div class="doc-bubble-size">${(file.size/1024).toFixed(0)} KB</div>
          </div>`;
      } else {
        // PDF / other — blob URL lets user open it in a new tab
        const blobUrl = URL.createObjectURL(file);
        previewDiv.innerHTML = `
          <div class="doc-bubble-wrap" style="cursor:pointer;"
               onclick="window.open('${blobUrl}','_blank')" title="Click to open ${file.name}">
            <div class="doc-bubble-icon">\u{1F4C4}</div>
            <div class="doc-bubble-name">${file.name}</div>
            <div class="doc-bubble-meta">${ext} \u00B7 ${(file.size/1024).toFixed(0)} KB</div>
            <div class="doc-bubble-meta" style="color:#2563eb;font-weight:600;margin-top:2px;">\u{1F50D} Click to view</div>
          </div>`;
      }

      // Append preview first, then re-add user text below it
      if (chatDisplay) {
        chatDisplay.appendChild(previewDiv);
        if (lastUserMsg) chatDisplay.appendChild(lastUserMsg);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
      }

      const docResponse = await fetch("http://localhost:8080/chat-with-doc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message || "Please analyze this document and provide legal advice.",
          lang: queryLang,
          profile: userProfile,
          document: base64,
          document_name: file.name,
          is_pdf: isPdf,
          history: conversationManager.getLastMessages(5),
          session_id: conversationManager.getSessionId()
        })
      });
      if (!docResponse.ok) throw new Error(`Server error: ${docResponse.status}`);
      const docResult = await docResponse.json();
      removeTypingIndicator();
      const docReply = docResult?.reply || docResult?.response || "Could not analyze the document.";
      const docTtsAudio = docResult?.tts_audio || "";
      
      // Store in conversation history
      conversationManager.addAssistantMessage(docReply);
      
      // Display message
      conversationManager.displayMessage('assistant', docReply);
      
      if (docTtsAudio) { playAudioBase64(docTtsAudio); }
      else { speakWithBrowserTTS(docReply, ttsLang); }

      return;
    }

    // ── Normal chat flow ──────────────────────────────────
    const response = await fetch("http://localhost:8080/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        message: message, 
        lang: queryLang, 
        profile: userProfile,
        history: conversationManager.getLastMessages(10),
        session_id: conversationManager.getSessionId()
      }),
    });
    if (!response.ok) throw new Error(`Server error: ${response.status}`);
    const result = await response.json();
    removeTypingIndicator();

    let replyText = result?.reply || result?.schemes_summarized ||
      result?.response || result?.answer || result?.text || null;

    // If raw JSON accidentally returned as reply, parse it
    if (replyText && replyText.trim().startsWith("{")) {
      try { const p = JSON.parse(replyText); replyText = p.reply || replyText; } catch(e) {}
    }

    const ttsAudio = result?.tts_audio || "";

    if (replyText) {
      // Store in conversation history
      conversationManager.addAssistantMessage(replyText);
      
      // Display message
      conversationManager.displayMessage('assistant', replyText);
      
      if (ttsAudio) {
        playAudioBase64(ttsAudio);
      } else {
        speakWithBrowserTTS(replyText, queryLang);
      }
    } else {
      console.warn("Unexpected API response shape:", result);
      const fallbackMsg = "I couldn't find a clear answer for that. Could you try rephrasing?";
      conversationManager.addAssistantMessage(fallbackMsg);
      conversationManager.displayMessage('assistant', fallbackMsg);
    }
  } catch (err) {
    console.error("API Error:", err);
    removeTypingIndicator();
    const errorMsg = "Something went wrong while talking to Saarthi. Please try again.";
    conversationManager.addAssistantMessage(errorMsg);
    conversationManager.displayMessage('assistant', errorMsg);
  }
}

// ── CHANGE 2: createRecognition with full auto-detection ───
function createRecognition() {
  if (!SpeechRecognition) return null;
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  // Use currently selected language for transcription
  recognition.lang = getSelectedLang();

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    console.log(`🎤 Transcript: "${transcript}"`);

    // Detect language from actual spoken transcript
    const detected = detectLangFromTranscript(transcript);
    console.log(`🔍 Detected lang: ${detected}`);

    if (detected && detected !== "en") {
      lastDetectedLang = detected;
      localStorage.setItem("saarthi_lang", detected);

      // Sync dropdown
      const langMap = {
        hi: "hi-IN", mr: "mr-IN", en: "en-IN", bn: "bn-IN",
        ta: "ta-IN", te: "te-IN", gu: "gu-IN", kn: "kn-IN",
        ml: "ml-IN", pa: "pa-IN"
      };
      if (languageSelect && langMap[detected]) {
        languageSelect.value = langMap[detected];
      }

      // Sync lang panel button label
      const langLabels = {
        hi: "हिंदी", mr: "मराठी", en: "English", bn: "বাংলা",
        ta: "தமிழ்", te: "తెలుగు", gu: "ગુજરાતી",
        kn: "ಕನ್ನಡ", ml: "മലയാളം", pa: "ਪੰਜਾਬੀ"
      };
      const labelEl = document.getElementById("langBtnLabel");
      if (labelEl && langLabels[detected]) {
        labelEl.textContent = langLabels[detected];
      }

      // Sync active state in lang panel
      const langMap2 = langMap; // same map
      document.querySelectorAll(".lang-opt").forEach(b => {
        b.classList.toggle("active", b.dataset.val === langMap2[detected]);
      });

      if (typeof setLanguage === "function") setLanguage(detected);
    }

    handleRecognitionResult(transcript);
  };

  recognition.onerror = (e) => handleRecognitionError(e.error);
  recognition.onend = () => {
    isListening = false;
    micButtonLarge?.classList.remove("listening");
    micButton?.classList.remove("listening");
    if (!isChatActive) statusTextSimple?.classList.remove("listening");
    else statusText?.classList.remove("listening");
  };
  return recognition;
}

function handleRecognitionResult(transcript) {
  if (!isChatActive) {
    if (statusTextSimple) statusTextSimple.textContent = "Processing...";
    setTimeout(() => {
      showChatOnly(transcript);
      if (statusTextSimple) { statusTextSimple.textContent = ""; statusTextSimple.classList.remove("listening"); }
      micButtonLarge?.classList.remove("listening");
      isListening = false;
    }, 400);
  } else {
    if (textInput) textInput.value = transcript;
    if (statusText) statusText.textContent = "Processing...";
    setTimeout(() => {
      sendMessage(transcript);
      if (statusText) { statusText.textContent = ""; statusText.classList.remove("listening"); }
      micButton?.classList.remove("listening");
      isListening = false;
    }, 400);
  }
}

function handleRecognitionError(error) {
  const msgs = {
    "not-allowed": "Microphone access denied. Please enable permissions.",
    "service-not-allowed": "Microphone access denied. Please enable permissions.",
    "no-speech": "No speech detected. Please try again.",
    "network": "Network error. Please check your connection.",
    "aborted": "",
  };
  const msg = msgs[error] ?? "Could not understand. Please try again.";
  if (!isChatActive) {
    if (statusTextSimple) statusTextSimple.textContent = msg;
    statusTextSimple?.classList.remove("listening");
    micButtonLarge?.classList.remove("listening");
  } else {
    if (statusText) statusText.textContent = msg;
    statusText?.classList.remove("listening");
    micButton?.classList.remove("listening");
  }
  isListening = false;
  if (msg) setTimeout(() => {
    if (statusTextSimple) statusTextSimple.textContent = "";
    if (statusText) statusText.textContent = "";
  }, 4000);
}

// ── Show Chat ──────────────────────────────────────────────
function showChatOnly(firstMessage = "") {
  if (isChatActive) return;

  heroSection?.style.setProperty("display", "none");
  featuresSection?.style.setProperty("display", "none");
  languagesSection?.style.setProperty("display", "none");
  footerSection?.style.setProperty("display", "none");
  document.getElementById("categories")?.style.setProperty("display", "none");
  document.querySelector(".featured-section")?.style.setProperty("display", "none");
  navLinks.forEach((l) => l?.style.setProperty("display", "none"));

  const headerEl = document.getElementById("header");
  const announcementBarEl = document.getElementById("announcementBar");
  if (headerEl) headerEl.style.transform = "translateY(-200%)";
  if (announcementBarEl) announcementBarEl.style.transform = "translateY(-200%)";

  if (chatOnlyView) {
    chatOnlyView.style.display = "block";
    chatOnlyView.classList.add("active", "fullscreen");
  }

  isChatActive = true;

  // Add clear history button if not exists
  addClearHistoryButton();

  // Load THIS user's history from Supabase (or localStorage cache),
  // restore the display, THEN send any first message.
  // Everything is inside .then() so the chat is ready before sending.
  conversationManager.initForCurrentUser().then(() => {
    if (conversationManager.getHistory().length === 0) {
      conversationManager.resetChatDisplay();
    } else {
      conversationManager.restoreChatDisplay();
    }

    const prefill = localStorage.getItem("saarthi_prefill_query");
    if (prefill) {
      localStorage.removeItem("saarthi_prefill_query");
      setTimeout(() => {
        conversationManager.addUserMessage(prefill);
        conversationManager.displayMessage('user', prefill);
        sendMessageToBackend(prefill);
      }, 300);
    } else if (firstMessage && firstMessage !== "Test message") {
      conversationManager.addUserMessage(firstMessage);
      conversationManager.displayMessage('user', firstMessage);
      sendMessageToBackend(firstMessage);
    }

    setTimeout(() => textInput?.focus(), 500);
  });

  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ── Add Clear History Button ───────────────────────────────
function addClearHistoryButton() {
  const chatTopBar = document.querySelector('.chat-top-bar');
  if (chatTopBar && !document.getElementById('clearHistoryBtn')) {
    const clearBtn = document.createElement('button');
    clearBtn.id = 'clearHistoryBtn';
    clearBtn.className = 'clear-history-btn';
    clearBtn.innerHTML = '🗑️ Clear Chat';
    clearBtn.onclick = () => conversationManager.clearHistory();
    clearBtn.style.cssText = `
      background: #f1f5f9;
      border: none;
      border-radius: 20px;
      padding: 6px 12px;
      font-size: 0.8rem;
      color: #475569;
      cursor: pointer;
      margin-left: 10px;
    `;
    chatTopBar.appendChild(clearBtn);
  }
}

// ── Go Back ────────────────────────────────────────────────
function goBackToHome() {
  if (!isChatActive) return;

  if (heroSection) { heroSection.style.display = "flex"; heroSection.classList.remove("hidden"); }
  if (featuresSection) featuresSection.style.display = "block";
  if (languagesSection) languagesSection.style.display = "block";
  if (footerSection) footerSection.style.display = "block";

  document.getElementById("categories")?.style.setProperty("display", "block");
  document.querySelector(".featured-section")?.style.setProperty("display", "block");
  navLinks.forEach((l) => { if (l) l.style.display = "block"; });

  const headerEl = document.getElementById("header");
  const announcementBarEl = document.getElementById("announcementBar");
  if (headerEl) headerEl.style.transform = "";
  if (announcementBarEl && !announcementBarEl.classList.contains("hidden")) announcementBarEl.style.transform = "";

  if (chatOnlyView) {
    chatOnlyView.style.display = "none";
    chatOnlyView.classList.remove("active", "fullscreen");
  }

  isChatActive = false;
  currentSessionId = null;
  lastDetectedLang = null;
  stopCurrentAudio();

  heroSection?.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Chat helpers ───────────────────────────────────────────
// Deprecated - use conversationManager.displayMessage instead
function addMessage(text, isUser = false, schemeData = null, ttsText = "", ttsAudio = "") {
  console.warn('addMessage is deprecated, use conversationManager.displayMessage');
  if (!chatDisplay) return;
  
  if (isUser) {
    conversationManager.addUserMessage(text);
  } else {
    conversationManager.addAssistantMessage(text);
  }
  conversationManager.displayMessage(isUser ? 'user' : 'assistant', text);
}

// Redirect to my-schemes.html — the dedicated eligibility & schemes page
function goToMySchemes() {
  window.location.href = "my-schemes.html";
}

function showEligibilityChecker(schemeData) {
  // Remove existing checker if open
  document.getElementById("eligibilityPanel")?.remove();

  const panel = document.createElement("div");
  panel.id = "eligibilityPanel";
  panel.className = "message assistant-message eligibility-panel";
  panel.innerHTML = `
    <b>🔍 Eligibility Checker</b><br><br>
    <label>Your Age: <input type="number" id="eli_age" placeholder="e.g. 35" min="1" max="100" style="width:80px;padding:4px;border-radius:6px;border:1px solid #ccc"></label><br><br>
    <label>Occupation:
      <select id="eli_occ" style="padding:4px;border-radius:6px;border:1px solid #ccc">
        <option value="farmer">Farmer / किसान</option>
        <option value="student">Student / विद्यार्थी</option>
        <option value="woman">Woman / महिला</option>
        <option value="business">Business / व्यापार</option>
        <option value="labourer">Labourer / मजदूर</option>
        <option value="other">Other / अन्य</option>
      </select>
    </label><br><br>
    <label>Annual Income (₹):
      <select id="eli_income" style="padding:4px;border-radius:6px;border:1px solid #ccc">
        <option value="below1">Below ₹1 Lakh</option>
        <option value="1to2">₹1–2 Lakh</option>
        <option value="2to5">₹2–5 Lakh</option>
        <option value="above5">Above ₹5 Lakh</option>
      </select>
    </label><br><br>
    <button onclick="checkEligibility()" style="background:#1a56db;color:white;border:none;padding:8px 18px;border-radius:8px;cursor:pointer;font-size:14px">✅ Check Now</button>
    <button onclick="document.getElementById('eligibilityPanel').remove()" style="background:#e5e7eb;color:#333;border:none;padding:8px 14px;border-radius:8px;cursor:pointer;font-size:14px;margin-left:8px">✖ Close</button>
    <div id="eligibilityResult" style="margin-top:12px"></div>
  `;
  chatDisplay.appendChild(panel);
  chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

function checkEligibility() {
  const age = parseInt(document.getElementById("eli_age")?.value) || 0;
  const occ = document.getElementById("eli_occ")?.value;
  const income = document.getElementById("eli_income")?.value;
  const result = document.getElementById("eligibilityResult");
  if (!result) return;

  // Simple eligibility logic based on common scheme patterns
  let eligible = true;
  let reasons = [];

  if (age < 18) { eligible = false; reasons.push("Age must be 18 or above for most schemes"); }
  if (income === "above5") { eligible = false; reasons.push("Income above ₹5 lakh may not qualify for most welfare schemes"); }

  if (eligible) {
    result.innerHTML = `<span style="color:#16a34a;font-weight:bold">✅ You appear eligible!</span><br>
    Based on your profile (Age: ${age}, ${occ}, ${income.replace("below1","Below ₹1L").replace("1to2","₹1-2L").replace("2to5","₹2-5L")}), 
    you likely qualify. Visit the official portal or nearest CSC centre to apply.`;
  } else {
    result.innerHTML = `<span style="color:#dc2626;font-weight:bold">❌ You may not be eligible</span><br>
    ${reasons.join("<br>")}`;
  }
}

function addTypingIndicator() {
  if (!chatDisplay) return;
  const div = document.createElement("div");
  div.className = "message assistant-message typing-indicator";
  div.id = "typingIndicator";
  div.innerHTML = "<span></span><span></span><span></span>";
  chatDisplay.appendChild(div);
  chatDisplay.scrollTop = chatDisplay.scrollHeight;
}

function removeTypingIndicator() {
  document.getElementById("typingIndicator")?.remove();
}

function sendMessage(text = null) {
  const message = text || textInput?.value.trim();
  if (!message) return;
  stopCurrentAudio();
  
  // Add user message to history and display
  conversationManager.addUserMessage(message);
  conversationManager.displayMessage('user', message);
  
  if (textInput) textInput.value = "";
  sendMessageToBackend(message);
}

// ── Event Listeners ────────────────────────────────────────
textInputSimple?.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && textInputSimple.value.trim()) {
    showChatOnly(textInputSimple.value.trim());
    textInputSimple.value = "";
  }
});

sendButton?.addEventListener("click", () => sendMessage());
textInput?.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });

micButtonLarge?.addEventListener("click", () => {
  if (!recognitionSupported) {
    if (statusTextSimple) statusTextSimple.textContent = "Voice recognition not supported. Please type.";
    setTimeout(() => { if (statusTextSimple) statusTextSimple.textContent = ""; }, 3000);
    return;
  }
  if (!isListening) {
    const rec = createRecognition();
    if (rec) {
      try {
        stopCurrentAudio();
        rec.start(); isListening = true;
        micButtonLarge.classList.add("listening");
        if (statusTextSimple) { statusTextSimple.textContent = "Listening… Speak now"; statusTextSimple.classList.add("listening"); }
      } catch { isListening = false; }
    }
  } else {
    isListening = false;
    micButtonLarge.classList.remove("listening");
    if (statusTextSimple) { statusTextSimple.textContent = ""; statusTextSimple.classList.remove("listening"); }
  }
});

micButton?.addEventListener("click", () => {
  if (!recognitionSupported) {
    if (statusText) statusText.textContent = "Voice recognition not supported. Please type.";
    setTimeout(() => { if (statusText) statusText.textContent = ""; }, 3000);
    return;
  }
  if (!isListening) {
    const rec = createRecognition();
    if (rec) {
      try {
        stopCurrentAudio();
        rec.start(); isListening = true;
        micButton.classList.add("listening");
        if (statusText) { statusText.textContent = "Listening… Speak now"; statusText.classList.add("listening"); }
      } catch { isListening = false; }
    }
  } else {
    isListening = false;
    micButton.classList.remove("listening");
    if (statusText) { statusText.textContent = ""; statusText.classList.remove("listening"); }
  }
});

backButton?.addEventListener("click", goBackToHome);
document.addEventListener("keydown", (e) => { if (e.key === "Escape" && isChatActive) goBackToHome(); });
document.querySelector(".logo")?.addEventListener("click", () => { if (isChatActive) goBackToHome(); else window.location.reload(); });

// ── Scroll animation ───────────────────────────────────────
const observer = new IntersectionObserver(
  (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("animated"); }),
  { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
);
document.querySelectorAll(".animate-on-scroll, .animate-left, .animate-right, .animate-scale").forEach((el) => el && observer.observe(el));

window.addEventListener("scroll", () => {
  document.getElementById("header")?.classList.toggle("scrolled", window.scrollY > 50);
});

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    if (!isChatActive) {
      e.preventDefault();
      document.querySelector(this.getAttribute("href"))?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
});

document.getElementById("announcementClose")?.addEventListener("click", () => {
  document.getElementById("announcementBar")?.classList.add("hidden");
  const h = document.getElementById("header");
  const s = document.getElementById("heroSection");
  if (h) h.style.top = "0px";
  if (s) s.style.marginTop = "70px";
});

// ── Chat Language Panel ────────────────────────────────────
function toggleLangPanel() {
  const dropdown = document.getElementById('langDropdown');
  dropdown.classList.toggle('open');
}

function selectChatLang(btn) {
  const val = btn.dataset.val;
  const label = btn.dataset.label;
  const langCode = val.split('-')[0];

  const sel = document.getElementById('language');
  if (sel) sel.value = val;

  localStorage.setItem('saarthi_lang', langCode);
  lastDetectedLang = langCode;

  const labelEl = document.getElementById('langBtnLabel');
  if (labelEl) labelEl.textContent = label;

  document.querySelectorAll('.lang-opt').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('langDropdown').classList.remove('open');

  if (typeof setLanguage === 'function') setLanguage(langCode);
}

document.addEventListener('click', (e) => {
  const wrap = document.getElementById('langBtnWrap');
  if (wrap && !wrap.contains(e.target)) {
    document.getElementById('langDropdown')?.classList.remove('open');
  }
});

(function restoreLang() {
  const saved = localStorage.getItem('saarthi_lang');
  if (!saved) return;

  let btn = document.querySelector(`.lang-opt[data-val="${saved}-IN"]`);
  if (!btn) btn = document.querySelector(`.lang-opt[data-val="${saved}"]`);

  if (btn) {
    const sel = document.getElementById('language');
    if (sel) sel.value = btn.dataset.val;
    const labelEl = document.getElementById('langBtnLabel');
    if (labelEl) labelEl.textContent = btn.dataset.label;
    document.querySelectorAll('.lang-opt').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
})();

// ── Typing indicator CSS ───────────────────────────────────
const style = document.createElement("style");
style.textContent = `
  .typing-indicator { display:flex; align-items:center; gap:5px; padding:12px 16px !important; }
  .typing-indicator span { width:8px; height:8px; border-radius:50%; background:#1a56db; display:inline-block; animation:typingBounce 1.2s infinite ease-in-out; }
  .typing-indicator span:nth-child(2) { animation-delay:.2s; }
  .typing-indicator span:nth-child(3) { animation-delay:.4s; }
  @keyframes typingBounce { 0%,80%,100%{transform:scale(.7);opacity:.5} 40%{transform:scale(1);opacity:1} }
  .scheme-card { background:#f8faff; border-left:3px solid #1a56db; padding:10px 14px; margin:8px 0; border-radius:8px; }
  .scheme-card h3 { margin:0 0 6px 0; font-size:15px; color:#1a56db; }
  .scheme-card ol { margin:4px 0 4px 18px; padding:0; }
  .scheme-card li { margin-bottom:3px; }
  .eligibility-btn { margin-top:10px; background:#1a56db; color:white; border:none; padding:8px 16px; border-radius:8px; cursor:pointer; font-size:13px; display:block; }
  .eligibility-btn:hover { background:#1648b8; }
  .eligibility-panel { border:2px solid #1a56db; border-radius:12px; }
  hr { border:none; border-top:1px solid #e5e7eb; margin:10px 0; }
  .legal-card { background:#fff8f0; border-left:3px solid #dc2626; padding:10px 14px; margin:8px 0; border-radius:8px; }
  .legal-card h3 { margin:0 0 6px 0; font-size:15px; color:#dc2626; }
  .legal-card ol { margin:4px 0 4px 18px; padding:0; }
  .legal-card li { margin-bottom:3px; }
  
  /* Message actions styling */
  .msg-actions { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; align-items: center; }
  .msg-repeat-btn, .msg-stop-btn, .msg-eligibility-btn {
    border: none; border-radius: 20px; cursor: pointer;
    font-size: 0.75rem; font-weight: 600; padding: 4px 12px;
    transition: background 0.15s, transform 0.1s;
  }
  .msg-repeat-btn { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
  .msg-repeat-btn:hover { background: #dbeafe; transform: scale(1.04); }
  .msg-stop-btn { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
  .msg-stop-btn:hover { background: #fee2e2; transform: scale(1.04); }
  .msg-eligibility-btn { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
  .msg-eligibility-btn:hover { background: #dcfce7; transform: scale(1.04); }

  /* Document preview bubble */
  .doc-preview-bubble { background: transparent !important; padding: 4px 0 !important; }
  .doc-bubble-wrap {
    display: inline-flex; flex-direction: column; align-items: flex-end;
    background: #dbeafe; border: 1px solid #bfdbfe;
    border-radius: 14px 14px 4px 14px;
    padding: 10px 12px; max-width: 240px; gap: 4px;
  }
  .doc-bubble-icon { font-size: 2rem; line-height: 1; }
  .doc-bubble-name {
    font-size: 0.78rem; font-weight: 600; color: #1e40af;
    word-break: break-all; max-width: 200px;
  }
  .doc-bubble-meta, .doc-bubble-size {
    font-size: 0.7rem; color: #64748b;
  }
`;
document.head.appendChild(style);

console.log("Saarthi AI initialized ✅");
console.log("Speech recognition supported:", recognitionSupported);
// ── Personalized Recommendations ──────────────────────────
const CAT_ICONS = {
    agriculture: "🌾", health: "🏥", education: "🎓",
    women: "👩", housing: "🏠", business: "💼",
    social_welfare: "🤝", employment: "👷"
};

async function loadPersonalizedRecommendations() {
    const user = getUser ? getUser() : (JSON.parse(localStorage.getItem("saarthi_user") || "{}"));
    const token = localStorage.getItem("saarthi_token");
    if (!token || !user || !user.mobile) return; // not logged in

    const section = document.getElementById("recommendations");
    const grid = document.getElementById("recoGrid");
    const subtitle = document.getElementById("recoSubtitle");
    if (!section || !grid) return;

    // Build profile — check all possible locations where occupation might be stored
    const p = user.profile || {};
    const occupation = (user.occupation || p.occupation || user.job || p.job || "").toLowerCase().trim();
    const profile = {
        mobile: user.mobile,
        occupation: occupation,
        age: user.age || p.age || null,
        state: (user.state || p.state || "").toLowerCase(),
        annual_income: user.income || p.annual_income || p.income || null,
        gender: (user.gender || p.gender || "").toLowerCase(),
        caste_category: (user.caste || p.caste_category || p.caste || "").toLowerCase(),
        preferred_lang: localStorage.getItem("saarthi_lang") || "en",
    };

    // Show section with loading state
    section.style.display = "block";
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:#64748b;">
        <div style="font-size:1.5rem;margin-bottom:8px;">⏳</div>
        <div>Finding schemes for you...</div>
    </div>`;

    // Update subtitle based on occupation
    const occMap = {
        farmer: "🌾 Schemes for Farmers",
        student: "🎓 Schemes for Students",
        business: "💼 Schemes for Business Owners",
        homemaker: "👩 Schemes for Women",
        daily_wage: "👷 Schemes for Daily Wage Workers",
        salaried: "💼 Schemes for Salaried Employees",
        unemployed: "🤝 Welfare Schemes for You",
        artisan: "🎨 Schemes for Artisans",
        fisherman: "🐟 Schemes for Fishermen",
    };
    if (subtitle) {
        subtitle.textContent = occupation
            ? (occMap[occupation] || `Schemes matched to your profile`)
            : "Personalized schemes based on your profile";
    }

    try {
        const data = await fetchUserRecommendations(profile, 6);
        const recs = data?.recommendations || [];
        if (recs.length === 0) {
            grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:#64748b;">
                <div>No schemes found. <a href="my-schemes.html" style="color:#2563eb;">Browse all schemes →</a></div>
            </div>`;
            return;
        }

        // Show section
        section.style.display = "block";

        grid.innerHTML = recs.map(scheme => {
            const cat = (scheme.category || "").toLowerCase();
            const icon = CAT_ICONS[cat] || "📋";
            const score = Math.round((scheme.recommendation_score || 0) * 100);
            const reasons = (scheme.match_reasons || []).slice(0, 2).join(" • ");
            return `
            <div class="scheme-card" style="position:relative;">
                <div class="scheme-tag">${icon} ${scheme.category || "Scheme"}</div>
                ${score > 0 ? `<div style="position:absolute;top:12px;right:12px;background:#dcfce7;color:#16a34a;font-size:0.72rem;font-weight:700;padding:2px 8px;border-radius:20px;">${score}% match</div>` : ""}
                <h3 style="margin:8px 0 6px;">${scheme.name_en || scheme.scheme_id}</h3>
                <p class="scheme-desc">${(scheme.description || "").slice(0, 100)}...</p>
                ${reasons ? `<p style="font-size:0.75rem;color:#16a34a;margin:4px 0;">✓ ${reasons}</p>` : ""}
                <div class="eligibility-box">
                    <p class="eligibility-label">Benefits</p>
                    <p class="eligibility-value">${scheme.benefits?.amount ? "₹" + Number(scheme.benefits.amount).toLocaleString() : "Varies"}</p>
                </div>
                <div class="card-footer">
                    <a href="apply-scheme.html?scheme_id=${scheme.scheme_id}" class="details-link">📄 Details</a>
                    <button class="apply-btn" onclick="window.location.href='apply-scheme.html?scheme_id=${scheme.scheme_id}'">Apply Now</button>
                </div>
            </div>`;
        }).join("");

    } catch (e) {
        console.warn("Recommendations failed:", e);
    }
}

// Load recommendations when page is ready
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(loadPersonalizedRecommendations, 500);
});