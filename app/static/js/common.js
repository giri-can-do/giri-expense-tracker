const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");

if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
        const isOpen = navLinks.classList.toggle("show");

        menuToggle.textContent = isOpen ? "✕" : "☰";
        menuToggle.setAttribute("aria-expanded", String(isOpen));
    });

    navLinks.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            navLinks.classList.remove("show");
            menuToggle.textContent = "☰";
            menuToggle.setAttribute("aria-expanded", "false");
        });
    });
}