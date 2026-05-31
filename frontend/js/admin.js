(function () {
  const form = document.querySelector("#participant-form");
  const feedback = document.querySelector("#participant-feedback");
  const searchForm = document.querySelector("#search-form");
  const searchTerm = document.querySelector("#search-term");
  const list = document.querySelector("#participants-list");

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

  const visitProfile = (participantId) => {
    window.location.href = `palpites.html?participant_id=${encodeURIComponent(participantId)}`;
  };

  const render = (participants) => {
    if (!participants.length) {
      list.innerHTML = '<article class="data-item">Nenhum participante encontrado.</article>';
      return;
    }

    list.innerHTML = participants.map((participant) => `
      <article class="data-item">
        <strong>${escapeHtml(participant.name)}</strong>
        <span>${escapeHtml(participant.phone)}</span>
        <button class="secondary-button" type="button" data-visit-id="${escapeHtml(participant.id)}">Visitar perfil</button>
      </article>
    `).join("");
  };

  const loadParticipants = async (term = "") => {
    const data = term
      ? await window.BolaoApi.searchParticipants(term)
      : await window.BolaoApi.adminParticipants();
    render(data.items || []);
  };

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
      return;
    }

    const payload = Object.fromEntries(new FormData(form).entries());
    setFeedback("Salvando participante...", "");

    try {
      const data = await window.BolaoApi.createParticipant(payload);
      const participant = data.item;
      setFeedback("Participante cadastrado com sucesso.", "success");
      form.reset();
      render([participant]);
    } catch (error) {
      setFeedback(error.message || "Nao foi possivel cadastrar.", "error");
    }
  });

  searchForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
      await loadParticipants(searchTerm.value.trim());
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

  loadParticipants().catch(() => render([]));
})();
