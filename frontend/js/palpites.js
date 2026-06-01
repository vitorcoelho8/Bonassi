(function () {
  const params = new URLSearchParams(window.location.search);
  const participantId = params.get("participant_id");
  const heading = document.querySelector("#participant-heading");
  const profilePanel = document.querySelector("#profile-panel");
  const predictionPanel = document.querySelector("#prediction-panel");
  const nextMatch = document.querySelector("#next-match");
  const savedPredictionPanel = document.querySelector("#saved-prediction");
  const predictionForm = document.querySelector("#prediction-form");
  const feedback = document.querySelector("#prediction-feedback");
  const matchIdInput = document.querySelector("#match-id");
  const brazilScoreInput = document.querySelector("#brazil-score");
  const opponentScoreInput = document.querySelector("#opponent-score");
  const bonusButton = document.querySelector("#bonus-button");
  const bonusNavLink = document.querySelector("#bonus-nav-link");

  let participant = null;
  let match = null;
  let matchContext = null;
  let savedPrediction = null;

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

  const getBrazilMatchContext = (currentMatch) => {
    const homeTeam = String(currentMatch?.home_team || "").trim();
    const awayTeam = String(currentMatch?.away_team || "").trim();

    if (homeTeam.toLowerCase() === "brasil") {
      return {
        opponentTeam: awayTeam,
        brazilIsHome: true,
      };
    }

    if (awayTeam.toLowerCase() === "brasil") {
      return {
        opponentTeam: homeTeam,
        brazilIsHome: false,
      };
    }

    throw new Error("Este jogo nao e uma partida do Brasil.");
  };

  const getPredictionBrazilScore = (prediction, context) => {
    if (prediction.brazil_score !== undefined && prediction.brazil_score !== null) {
      return prediction.brazil_score;
    }

    return context.brazilIsHome ? prediction.predicted_home_score : prediction.predicted_away_score;
  };

  const getPredictionOpponentScore = (prediction, context) => {
    if (prediction.opponent_score !== undefined && prediction.opponent_score !== null) {
      return prediction.opponent_score;
    }

    return context.brazilIsHome ? prediction.predicted_away_score : prediction.predicted_home_score;
  };

  const renderSavedPrediction = () => {
    if (!savedPrediction || !matchContext) {
      savedPredictionPanel.classList.add("hidden");
      savedPredictionPanel.innerHTML = "";
      return;
    }

    const brazilScore = getPredictionBrazilScore(savedPrediction, matchContext);
    const opponentScore = getPredictionOpponentScore(savedPrediction, matchContext);
    savedPredictionPanel.innerHTML = `
      <strong>Palpite atual</strong>
      <span>Brasil ${escapeHtml(brazilScore)} x ${escapeHtml(opponentScore)} ${escapeHtml(matchContext.opponentTeam)}</span>
    `;
    savedPredictionPanel.classList.remove("hidden");
  };

  const loadSavedPrediction = async () => {
    savedPrediction = null;
    savedPredictionPanel.classList.add("hidden");
    savedPredictionPanel.innerHTML = "";

    const predictionsData = await window.BolaoApi.participantPredictions(participant.id);
    const predictions = predictionsData.items || [];
    savedPrediction = predictions.find((prediction) => prediction.match_id === match.id) || null;
    if (!savedPrediction) {
      return;
    }

    brazilScoreInput.value = getPredictionBrazilScore(savedPrediction, matchContext);
    opponentScoreInput.value = getPredictionOpponentScore(savedPrediction, matchContext);
    renderSavedPrediction();
  };

  const readScore = (input, emptyMessage) => {
    const rawValue = input.value.trim();
    if (!rawValue) {
      setFeedback(emptyMessage, "error");
      input.focus();
      return null;
    }

    const score = Number(rawValue);
    if (!Number.isInteger(score)) {
      setFeedback("O placar deve ser um numero inteiro.", "error");
      input.focus();
      return null;
    }

    if (score < 0) {
      setFeedback("O placar nao pode ser negativo.", "error");
      input.focus();
      return null;
    }

    return score;
  };

  if (!participantId) {
    showError("Participante nao informado. Volte ao painel e selecione um perfil.");
    return;
  }

  bonusButton.addEventListener("click", () => {
    window.location.href = `bonus.html?participant_id=${encodeURIComponent(participantId)}`;
  });

  if (bonusNavLink) {
    bonusNavLink.href = `bonus.html?participant_id=${encodeURIComponent(participantId)}`;
  }

  predictionForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!participant || !match || !matchContext) {
      return;
    }

    const brazilScore = readScore(brazilScoreInput, "Informe o placar do Brasil.");
    if (brazilScore === null) {
      return;
    }

    const opponentScore = readScore(opponentScoreInput, "Informe o placar do adversario.");
    if (opponentScore === null) {
      return;
    }

    setFeedback("Salvando palpite...", "");

    try {
      const payload = {
        participant_id: participant.id,
        match_id: match.id,
        brazil_score: brazilScore,
        opponent_score: opponentScore,
      };
      const data = savedPrediction
        ? await window.BolaoApi.updatePrediction(savedPrediction.id, payload)
        : await window.BolaoApi.savePrediction(payload);
      savedPrediction = data.item;
      renderSavedPrediction();
      setFeedback("Palpite salvo com sucesso.", "success");
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
      matchContext = getBrazilMatchContext(match);
      matchIdInput.value = match.id;
      nextMatch.innerHTML = `
        <strong>Brasil x ${escapeHtml(matchContext.opponentTeam)}</strong>
        <span>${escapeHtml(formatDate(match.match_date || match.starts_at))}</span>
      `;
      await loadSavedPrediction();
      predictionPanel.classList.remove("hidden");
    } catch (error) {
      predictionPanel.classList.remove("hidden");
      nextMatch.innerHTML = `<p>${escapeHtml(error.message || "Nenhum proximo jogo disponivel para palpite.")}</p>`;
      predictionForm.classList.add("hidden");
    }
  };

  load();
})();
