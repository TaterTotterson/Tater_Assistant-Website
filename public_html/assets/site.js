(() => {
  const navToggle = document.querySelector(".nav-toggle");
  const siteNav = document.querySelector(".site-nav");

  if (navToggle && siteNav) {
    navToggle.addEventListener("click", () => {
      const isOpen = siteNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });
  }

  const searchInput = document.querySelector("[data-plugin-search]");
  const filterButtons = Array.from(document.querySelectorAll("[data-platform-filter]"));
  const pluginCards = Array.from(document.querySelectorAll("[data-plugin-card]"));
  const emptyState = document.querySelector("[data-plugin-empty]");
  const resultsCount = document.querySelector("[data-results-count]");

  if (!pluginCards.length) {
    return;
  }

  let activePlatform = "all";

  const applyFilters = () => {
    const query = String(searchInput?.value || "").trim().toLowerCase();
    let visibleCount = 0;

    pluginCards.forEach((card) => {
      const name = card.getAttribute("data-name") || "";
      const description = card.getAttribute("data-description") || "";
      const platforms = (card.getAttribute("data-platforms") || "").split(/\s+/).filter(Boolean);
      const matchesQuery = !query || name.includes(query) || description.includes(query);
      const matchesPlatform = activePlatform === "all" || platforms.includes(activePlatform);
      const visible = matchesQuery && matchesPlatform;

      card.hidden = !visible;
      if (visible) {
        visibleCount += 1;
      }
    });

    if (resultsCount) {
      resultsCount.textContent = String(visibleCount);
    }
    if (emptyState) {
      emptyState.hidden = visibleCount !== 0;
    }
  };

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activePlatform = button.getAttribute("data-platform-filter") || "all";
      filterButtons.forEach((item) => item.classList.toggle("is-active", item === button));
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  applyFilters();
})();
