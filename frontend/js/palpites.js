(function () {
  const params = new URLSearchParams(window.location.search);
  const participantId = params.get("participant_id");
  const heading = document.querySelector("#participant-heading");
  const profilePanel = document.querySelector("#profile-panel");
  const predictionPanel = document.querySelector("#prediction-panel");
  const nextMatch = document.querySelector("#next-match");
  const predictionForm = document.querySelector("#prediction-form");
  const feedback = document.querySelector("#prediction-feedback");
  const matchIdInput = document.querySelector("#match-id");
  const bonusButton = document.querySelector("#bonus-button");
  const finishButton = document.querySelector("#finish-button");

  let participant = null;
  let match = null;

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

  const showError = (message) => {
    heading.textContent = message;
    profilePanel.classList.add("hidden");
    predictionPanel.classList.add("hidden");
    bonusButton.classList.add("hidden");
  };

  const formatDate = (value) => {
    if (!value) {
      return "Horario nao definido";
    }

    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(value));
  };

  if (!participantId) {
    showError("Participante nao informado. Volte ao painel e selecione um perfil.");
    return;
  }

  bonusButton.addEventListener("click", () => {
    window.location.href = `bonus.html?participant_id=${encodeURIComponent(participantId)}`;
  });

  finishButton.addEventListener("click", () => {
    window.location.href = "admin.html";
  });

  predictionForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!predictionForm.reportValidity() || !participant || !match) {
      return;
    }

    const formData = new FormData(predictionForm);
    setFeedback("Salvando palpite...", "");

    try {
      await window.BolaoApi.savePrediction({
        participant_id: participant.id,
        match_id: match.id,
        predicted_home_score: formData.get("predicted_home_score"),
        predicted_away_score: formData.get("predicted_away_score"),
      });
      setFeedback("Palpite salvo com sucesso.", "success");
      predictionForm.reset();
    } catch (error) {
      setFeedback(error.message || "Nao foi possivel salvar o palpite.", "error");
    }
  });

  const load = async () => {
    try {
      const participantData = await window.BolaoApi.participant(participantId);
      participant = participantData.item;
      heading.textContent = `Perfil de: ${participant.name}`;
      profilePanel.innerHTML = `
        <h2>Participante</h2>
        <p><strong>Perfil de:</strong> ${escapeHtml(participant.name)}</p>
        <p><strong>Telefone:</strong> ${escapeHtml(participant.phone)}</p>
      `;
      profilePanel.classList.remove("hidden");
    } catch (error) {
      showError(error.message || "Participante nao encontrado.");
      return;
    }

    try {
      const matchData = await window.BolaoApi.nextMatch();
      match = matchData.item;
      matchIdInput.value = match.id;
      nextMatch.innerHTML = `
        <strong>${escapeHtml(match.home_team)} x ${escapeHtml(match.away_team)}</strong>
        <span>${escapeHtml(formatDate(match.match_date || match.starts_at))}</span>
      `;
      predictionPanel.classList.remove("hidden");
    } catch (error) {
      predictionPanel.classList.remove("hidden");
      nextMatch.innerHTML = '<p>Nenhum proximo jogo disponivel para palpite.</p>';
      predictionForm.classList.add("hidden");
    }
  };

  load();
})();
