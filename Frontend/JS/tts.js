class SaarthiTTS {
  constructor() {
    this.currentUtterance = null;
    this.lastText = "";
    this.lastLang = "";
    this.slowRate = 0.6;   // Slow voice rate
    this.normalRate = 1.0;
  }

  speak(text, langCode, slow = false) {
    this.lastText = text;
    this.lastLang = langCode;
    window.speechSynthesis.cancel(); // Stop any ongoing speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = slow ? this.slowRate : this.normalRate;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    // Pick best available voice for the language
    const voices = window.speechSynthesis.getVoices();
    const match = voices.find(v => v.lang.startsWith(langCode.split("-")[0]));
    if (match) utterance.voice = match;

    this.currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
    return utterance;
  }

  // Replay last spoken message
  replay() {
    if (this.lastText) this.speak(this.lastText, this.lastLang);
  }

  // Replay in slow mode
  replaySlow() {
    if (this.lastText) this.speak(this.lastText, this.lastLang, true);
  }

  stop() {
    window.speechSynthesis.cancel();
  }
}

// Global TTS instance
window.saarthiTTS = new SaarthiTTS();
