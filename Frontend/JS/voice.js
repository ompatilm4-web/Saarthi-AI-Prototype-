class SaarthiVoice {
  constructor(langCode) {
    this.langCode = langCode;
    this.recognition = null;
  }

  startListening(onResult, onError) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      onError("Voice input not supported in this browser. Please try Chrome or Edge.");
      return;
    }
    this.recognition = new SpeechRecognition();
    this.recognition.lang = this.langCode;
    this.recognition.interimResults = true;
    this.recognition.continuous = false;
    this.recognition.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
      onResult(transcript, e.results[e.results.length-1].isFinal);
    };
    this.recognition.onerror = onError;
    this.recognition.start();
  }

  stopListening() {
    this.recognition?.stop();
  }
}
