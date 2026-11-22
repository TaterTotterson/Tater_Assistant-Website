(() => {
  const navToggle = document.querySelector('.nav-toggle');
  const siteNav = document.querySelector('.site-nav');
  const closeNav = (restoreFocus = false) => {
    siteNav?.classList.remove('is-open');
    navToggle?.setAttribute('aria-expanded', 'false');
    if (restoreFocus) navToggle?.focus();
  };
  navToggle?.addEventListener('click', () => {
    const open = siteNav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(open));
  });
  siteNav?.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeNav();
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.site-header')) closeNav();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && siteNav?.classList.contains('is-open')) closeNav(true);
  });
  window.matchMedia('(min-width: 761px)').addEventListener('change', () => closeNav());

  // Panels stay readable without JavaScript. Enhance each independent tab group.
  document.querySelectorAll('[data-tabs]').forEach((group) => {
    const tabs = Array.from(group.querySelectorAll('[role="tab"]'));
    const panels = tabs.map((tab) => document.getElementById(tab.getAttribute('aria-controls')));
    const select = (index, focus = false) => {
      tabs.forEach((tab, i) => {
        tab.setAttribute('aria-selected', String(i === index));
        tab.tabIndex = i === index ? 0 : -1;
        panels[i].hidden = i !== index;
      });
      if (focus) {
        tabs[index].focus();
        tabs[index].scrollIntoView({ block: 'nearest', inline: 'nearest' });
      }
    };
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', (event) => {
        event.preventDefault();
        select(index);
      });
      tab.addEventListener('keydown', (event) => {
        let next = index;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = tabs.length - 1;
        else if (event.key === ' ' || event.key === 'Enter') next = index;
        else return;
        event.preventDefault();
        select(next, true);
      });
    });
    const selectedFromHash = panels.findIndex((panel) => `#${panel.id}` === window.location.hash);
    select(selectedFromHash >= 0 ? selectedFromHash : 0);
    group.classList.add('tabs-ready');
  });

  const guideSearch = document.querySelector('[data-guide-search]');
  const guideGroups = Array.from(document.querySelectorAll('[data-guide-group]'));
  const guideCount = document.querySelector('[data-guide-count]');
  const guideEmpty = document.querySelector('[data-guide-empty]');
  guideSearch?.addEventListener('input', () => {
    const words = guideSearch.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let total = 0;
    guideGroups.forEach((group) => {
      let visible = 0;
      group.querySelectorAll('[data-guide]').forEach((guide) => {
        const text = `${guide.textContent} ${guide.dataset.guideKeywords || ''}`.toLowerCase();
        guide.hidden = !words.every((word) => text.includes(word));
        if (!guide.hidden) visible++;
      });
      group.hidden = visible === 0;
      total += visible;
    });
    guideCount.textContent = `${total} ${total === 1 ? 'guide' : 'guides'}${words.length ? ' found.' : ' to help you get growing.'}`;
    guideEmpty.hidden = total !== 0;
  });

  // Preserve the technical directories' search and platform filters.
  const searchInput = document.querySelector('[data-plugin-search]');
  const filterButtons = Array.from(document.querySelectorAll('[data-platform-filter]'));
  const cards = Array.from(document.querySelectorAll('[data-plugin-card]'));
  const emptyState = document.querySelector('[data-plugin-empty]');
  const resultsCount = document.querySelector('[data-results-count]');
  let activePlatform = 'all';
  const applyFilters = () => {
    const query = String(searchInput?.value || '').trim().toLowerCase();
    let visibleCount = 0;
    cards.forEach((card) => {
      const text = `${card.dataset.name || ''} ${card.dataset.description || ''}`.toLowerCase();
      const platforms = (card.dataset.platforms || '').split(/\s+/);
      const visible = (!query || text.includes(query)) && (activePlatform === 'all' || platforms.includes(activePlatform));
      card.hidden = !visible;
      if (visible) visibleCount++;
    });
    if (resultsCount) resultsCount.textContent = String(visibleCount);
    if (emptyState) emptyState.hidden = visibleCount !== 0;
  };
  filterButtons.forEach((button) => {
    button.setAttribute('aria-pressed', String(button.classList.contains('is-active')));
    button.addEventListener('click', () => {
      activePlatform = button.dataset.platformFilter || 'all';
      filterButtons.forEach((item) => {
        item.classList.toggle('is-active', item === button);
        item.setAttribute('aria-pressed', String(item === button));
      });
      applyFilters();
    });
  });
  searchInput?.addEventListener('input', applyFilters);
  if (cards.length) applyFilters();
})();
