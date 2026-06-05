(() => {
  const navToggle = document.querySelector(".nav-toggle");
  const siteNav = document.querySelector(".site-nav");

  if (navToggle && siteNav) {
    navToggle.addEventListener("click", () => {
      const isOpen = siteNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });
  }

  const contactEmail = "tater@tatertottersonai.com";
  const contactOpenButtons = Array.from(document.querySelectorAll("[data-contact-open]"));
  let contactModal = null;
  let contactForm = null;

  if (contactOpenButtons.length) {
    contactModal = document.createElement("div");
    contactModal.className = "contact-modal";
    contactModal.hidden = true;
    contactModal.setAttribute("data-contact-modal", "");
    contactModal.setAttribute("role", "dialog");
    contactModal.setAttribute("aria-modal", "true");
    contactModal.setAttribute("aria-labelledby", "contact-title");
    contactModal.innerHTML = `
      <button class="contact-backdrop" type="button" data-contact-close aria-label="Close contact form"></button>
      <section class="contact-dialog" role="document">
        <button class="contact-close" type="button" data-contact-close aria-label="Close contact form">Close</button>
        <span class="eyebrow">Contact</span>
        <h2 id="contact-title">Contact Tater</h2>
        <p>Send questions, install notes, or integration ideas to <a href="mailto:${contactEmail}">${contactEmail}</a>.</p>
        <form class="contact-form" data-contact-form>
          <label>
            <span>Name</span>
            <input name="name" autocomplete="name">
          </label>
          <label>
            <span>Email</span>
            <input name="email" type="email" autocomplete="email">
          </label>
          <label>
            <span>Subject</span>
            <input name="subject" autocomplete="off">
          </label>
          <label>
            <span>Message</span>
            <textarea name="message" rows="5" required></textarea>
          </label>
          <div class="action-row">
            <button class="button" type="submit">Open email</button>
            <a class="button button-ghost" href="mailto:${contactEmail}">Email directly</a>
          </div>
        </form>
      </section>
    `;
    document.body.appendChild(contactModal);
    contactForm = contactModal.querySelector("[data-contact-form]");
  }

  const contactCloseButtons = Array.from(contactModal?.querySelectorAll("[data-contact-close]") || []);

  const closeContact = () => {
    if (!contactModal) {
      return;
    }
    contactModal.hidden = true;
    document.body.classList.remove("modal-open");
  };

  const openContact = () => {
    if (!contactModal) {
      return;
    }
    contactModal.hidden = false;
    document.body.classList.add("modal-open");
    const firstField = contactModal.querySelector(".contact-form input, .contact-form textarea, .contact-close");
    firstField?.focus();
  };

  contactOpenButtons.forEach((button) => {
    button.addEventListener("click", openContact);
  });

  contactCloseButtons.forEach((button) => {
    button.addEventListener("click", closeContact);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && contactModal && !contactModal.hidden) {
      closeContact();
    }
  });

  if (contactForm) {
    contactForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const formData = new FormData(contactForm);
      const name = String(formData.get("name") || "").trim();
      const email = String(formData.get("email") || "").trim();
      const subject = String(formData.get("subject") || "Tater Assistant contact").trim();
      const message = String(formData.get("message") || "").trim();
      const body = [
        name ? `Name: ${name}` : "",
        email ? `Email: ${email}` : "",
        "",
        message,
      ].filter((line, index) => line || index === 2).join("\n");

      window.location.href = `mailto:${contactEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
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
