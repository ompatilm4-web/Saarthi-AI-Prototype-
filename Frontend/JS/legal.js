async function analyzeLegalIssue(userQuery, lang) {
  // If backend is running, it would call:
  // const response = await fetch("/api/ai/legal", { ... });
  // return response.json();
  
  // Return mocked data to show the UI
  return {
    analysis: `You mentioned: "${userQuery}". This falls under civil property dispute law.`,
    explanation: "Under the Transfer of Property Act, you have the right to peaceful possession of your property. If someone is claiming ownership, they must produce valid legal documents.",
    solution: "1. Do not sign any documents.\n2. Collect your sale deed and property tax receipts.\n3. File an injunction suite in the local civil court."
  };
}

document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyzeLegalBtn");
    const legalQuery = document.getElementById("legalQuery");
    const resultsArea = document.getElementById("legalResults");
    
    if (analyzeBtn && legalQuery) {
        analyzeBtn.addEventListener("click", async () => {
            const query = legalQuery.value.trim();
            if (!query) return alert("Please describe your problem first.");
            
            analyzeBtn.innerText = "Analyzing...";
            resultsArea.style.display = "none";
            
            // Mock API delay
            setTimeout(async () => {
                const data = await analyzeLegalIssue(query, "en-IN");
                
                document.getElementById("legalIssueText").innerText = data.analysis;
                document.getElementById("legalExplanationText").innerText = data.explanation;
                document.getElementById("legalSolutionText").innerText = data.solution;
                
                resultsArea.style.display = "block";
                analyzeBtn.innerText = "Analyze My Problem →";
            }, 1000);
        });
    }
});
