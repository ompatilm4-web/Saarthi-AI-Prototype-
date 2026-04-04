const scholarships = [
  {
    name: "National Scholarship Portal (NSP)",
    provider: "Central Government",
    categories: ["Pre-Matric", "Post-Matric", "Merit-cum-Means"],
    eligibility: { income_max: 250000, type: "student" },
    amount: "₹500–₹20,000/year",
    deadline: "October 31",
    apply_url: "https://scholarships.gov.in",
    documents: ["Aadhaar", "Bank Account", "Income Certificate", "Marksheet", "Caste Certificate"]
  },
  {
    name: "PM Yasasvi Scholarship",
    provider: "Central Government",
    categories: ["OBC", "EBC", "DNT students"],
    eligibility: { income_max: 250000, class: ["9", "11"] },
    amount: "₹75,000–₹1,25,000/year",
    apply_url: "https://yet.nta.ac.in"
  },
  {
    name: "Begum Hazrat Mahal National Scholarship",
    provider: "Maulana Azad Education Foundation",
    categories: ["Minority Girls"],
    eligibility: { gender: "female", minority: true, class: ["9", "10", "11", "12"] },
    amount: "₹5,000–₹6,000/year"
  },
  {
    name: "Inspire Scholarship",
    provider: "DST, Central Government",
    categories: ["Science Students"],
    amount: "₹80,000/year",
    apply_url: "https://online-inspire.gov.in"
  }
];

// When user asks "Which scholarships am I eligible for?"
async function findMatchingScholarships(userProfile) {
  const systemPrompt = `
    Match the user to relevant Indian scholarships based on their profile.
    Return the top 5 most relevant scholarships with eligibility match score.
    Respond in ${userProfile.lang} language.
    User profile: ${JSON.stringify(userProfile)}
    Available scholarships: ${JSON.stringify(scholarships)}
  `;
  const response = await fetch("/api/ai/scholarships", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem("saarthi_token")}`
    },
    body: JSON.stringify({ profile: userProfile })
  });
  return (await response.json()).matches;
}
