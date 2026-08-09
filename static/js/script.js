const sidebarLinks = document.querySelectorAll(".sidebar-link");

const setActiveLink = () => {
  const sections = ["home", "courses", "contact"]
    .map((id) => document.getElementById(id))
    .filter(Boolean);

  let current = "home";
  const offset = 120;

  sections.forEach((section) => {
    if (window.scrollY >= section.offsetTop - offset) {
      current = section.id;
    }
  });

  sidebarLinks.forEach((link) => {
    const href = link.getAttribute("href") || "";
    link.classList.toggle("active", href === `#${current}`);
  });
};

setActiveLink();
window.addEventListener("scroll", setActiveLink, { passive: true });

if (window.location.hash === "#contact") {
  const contact = document.querySelector("#contact");
  if (contact) {
    contact.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}
