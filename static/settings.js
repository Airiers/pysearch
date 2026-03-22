// Charger les paramètres au démarrage
function loadSettings() {
  try {
    const settings = JSON.parse(localStorage.getItem("settings")) || {
      theme: "light",
      linkTarget: "_blank",
    };

    // Appliquer le thème
    document.body.setAttribute("data-theme", settings.theme);
    document.querySelector("#theme").textContent =
      settings.theme === "dark" ? "Thème sombre" : "Thème clair";

    // Appliquer le comportement des liens
    const articles = document.querySelectorAll("article");
    for (const article of articles) {
      const links = article.querySelectorAll("a");
      for (const link of links) {
        if (settings.linkTarget === "_blank") {
          link.target = "_blank";
        } else {
          link.removeAttribute("target");
        }
      }
    }
    document.querySelector("#linkto").textContent =
      settings.linkTarget === "_blank" ? "Nouvel onglet" : "Remplacer l'onglet";
  } catch (error) {
    console.error("Erreur lors du chargement des paramètres:", error);
  }
}

// Sauvegarder les paramètres
function saveSettings() {
  const currentTheme = document.body.getAttribute("data-theme") || "light";
  const currentLinkTarget = document.querySelector("article a")?.target || "";

  const settings = {
    theme: currentTheme,
    linkTarget: currentLinkTarget,
  };

  localStorage.setItem("settings", JSON.stringify(settings));
}

// Charger au démarrage
loadSettings();

const settingsBtn = document.querySelector(".settings");
const modal = document.getElementById("settingsModal");
const closeBtn = document.querySelector(".close");

settingsBtn.addEventListener("click", () => {
  modal.style.display = "block";
});

closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.style.display = "none";
  }
});

const themeBtn = document.querySelector(".theme");

themeBtn.addEventListener("click", () => {
  const currentTheme = document.body.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  document.querySelector("#theme").textContent =
    newTheme === "dark" ? "Thème sombre" : "Thème clair";
  document.body.setAttribute("data-theme", newTheme);
  saveSettings();
});

const articles = document.querySelectorAll("article");
const linktoBtn = document.querySelector(".linkto");

linktoBtn.addEventListener("click", () => {
  for (const article of articles) {
    console.log(article);
    const links = article.querySelectorAll("a");
    for (const link of links) {
      if (link.target === "_blank") {
        link.removeAttribute("target");
        document.querySelector("#linkto").textContent = "Remplacer l'onglet";
      } else {
        link.target = "_blank";
        document.querySelector("#linkto").textContent = "Nouvel onglet";
      }
    }
  }
  saveSettings();
});
