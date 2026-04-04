document.getElementById("hamburger")?.addEventListener("click", () => {
  document.querySelector(".nav-links")?.classList.toggle("open");
});

// Close menu on link click
document.querySelectorAll(".nav-links a").forEach(link => {
  link.addEventListener("click", () => {
    document.querySelector(".nav-links")?.classList.remove("open");
  });
});
