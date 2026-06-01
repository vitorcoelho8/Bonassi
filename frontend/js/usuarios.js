(function () {
  const form = document.querySelector("#user-form");
  const formPanel = document.querySelector("#user-form-panel");
  const addUserButton = document.querySelector("#add-user-button");
  const feedback = document.querySelector("#user-feedback");
  const searchForm = document.querySelector("#user-search-form");
  const searchTerm = document.querySelector("#user-search-term");
  const list = document.querySelector("#users-list");

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const setFeedback = (message, type) => {
    feedback.textContent = message;
    feedback.classList.toggle("is-error", type === "error");
    feedback.classList.toggle("is-success", type === "success");
  };

  const initials = (name) => String(name || "?")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  const visitProfile = (participantId) => {
    window.location.href = `palpites.html?participant_id=${encodeURIComponent(participantId)}`;
  };

  const render = (users) => {
    if (!users.length) {
      list.innerHTML = '<article class="users-empty">Nenhum usuario encontrado.</article>';
      return;
    }

    list.innerHTML = users.map((user) => `
      <article class="user-list-row">
        <div class="user-avatar" aria-hidden="true">${escapeHtml(initials(user.name))}</div>
        <div class="user-row-copy">
          <h3>${escapeHtml(user.name)}</h3>
          <p>${escapeHtml(user.phone)}</p>
        </div>
        <span class="status-chip">Ativo</span>
        <button class="secondary-button visit-profile-button" type="button" data-visit-id="${escapeHtml(user.id)}">
          Visitar perfil
        </button>
      </article>
    `).join("");
  };

  const loadUsers = async (term = "") => {
    const data = term
      ? await window.BolaoApi.searchUsers(term)
      : await window.BolaoApi.users();
    render(data.items || []);
  };

  addUserButton?.addEventListener("click", () => {
    formPanel.classList.toggle("hidden");
    if (!formPanel.classList.contains("hidden")) {
      formPanel.querySelector("input")?.focus();
    }
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
      return;
    }

    setFeedback("Salvando usuario...", "");

    try {
      const payload = Object.fromEntries(new FormData(form).entries());
      const data = await window.BolaoApi.createUser(payload);
      setFeedback("Usuario cadastrado com sucesso.", "success");
      form.reset();
      formPanel.classList.add("hidden");
      await loadUsers(searchTerm.value.trim());
    } catch (error) {
      setFeedback(error.message || "Nao foi possivel cadastrar.", "error");
    }
  });

  searchForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
      await loadUsers(searchTerm.value.trim());
    } catch (error) {
      render([]);
    }
  });

  list?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-visit-id]");
    if (button) {
      visitProfile(button.dataset.visitId);
    }
  });

  loadUsers().catch(() => render([]));
})();
