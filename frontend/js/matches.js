(function () {
  const matchesList = document.querySelector("#matches-list");
  const pageFeedback = document.querySelector("#matches-feedback");
  const createMatchButton = document.querySelector("#create-brazil-match-button");
  const phaseFilters = document.querySelector("#phase-filters");

  const resultModal = document.querySelector("#result-modal");
  const resultForm = document.querySelector("#result-form");
  const resultFeedback = document.querySelector("#result-feedback");
  const homeTeamLabel = document.querySelector("#result-home-team");
  const awayTeamLabel = document.querySelector("#result-away-team");
  const homeScoreInput = document.querySelector("#result-home-score");
  const awayScoreInput = document.querySelector("#result-away-score");

  const reopenMatchModal = document.querySelector("#reopen-match-modal");
  const reopenMatchForm = document.querySelector("#reopen-match-form");
  const reopenMatchFeedback = document.querySelector("#reopen-match-feedback");
  const reopenMatchTitle = document.querySelector("#reopen-match-title");

  const nextMatchModal = document.querySelector("#next-match-modal");
  const nextMatchForm = document.querySelector("#next-match-form");
  const nextMatchPhase = document.querySelector("#next-match-phase");
  const nextMatchOpponent = document.querySelector("#next-match-opponent");
  const nextMatchDate = document.querySelector("#next-match-date");
  const nextMatchTime = document.querySelector("#next-match-time");
  const nextMatchPreview = document.querySelector("#next-match-preview");
  const nextMatchFeedback = document.querySelector("#next-match-feedback");

  const PHASES = [
    { value: "GROUP_STAGE", label: "Fase de grupos", round_order: 1 },
    { value: "ROUND_OF_32", label: "Segunda fase", round_order: 2 },
    { value: "ROUND_OF_16", label: "Oitavas de final", round_order: 3 },
    { value: "QUARTER_FINAL", label: "Quartas de final", round_order: 4 },
    { value: "SEMI_FINAL", label: "Semifinal", round_order: 5 },
    { value: "FINAL", label: "Final", round_order: 6 },
  ];

  let currentMatch = null;
  let currentReopenMatch = null;
  let phaseOptions = [];
  let allMatches = [];
  let selectedPhase = "GROUP_STAGE";

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const isBrazilMatch = (match) => {
    if (typeof match.is_brazil_match === "boolean") {
      return match.is_brazil_match;
    }

    const homeTeam = String(match.home_team || "").toLowerCase();
    const awayTeam = String(match.away_team || "").toLowerCase();
    return homeTeam === "brasil" || awayTeam === "brasil";
  };

  const formatDate = (value) => {
    if (!value) {
      return { date: "Horario nao definido", time: "" };
    }

    const date = new Date(value);
    return {
      date: new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        timeZone: "America/Sao_Paulo",
      }).format(date),
      time: new Intl.DateTimeFormat("pt-BR", {
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "America/Sao_Paulo",
      }).format(date),
    };
  };

  const formatStatus = (status) => {
    const normalizedStatus = String(status || "").toUpperCase();
    const labels = {
      SCHEDULED: "AGENDADO",
      LIVE: "AO VIVO",
      FINISHED: "FINALIZADO",
      CANCELLED: "CANCELADO",
      TO_BE_DEFINED: "A DEFINIR",
    };

    return labels[normalizedStatus] || normalizedStatus || "INDEFINIDO";
  };

  const hasResult = (match) => match.home_score !== null
    && match.home_score !== undefined
    && match.away_score !== null
    && match.away_score !== undefined;

  const isFinished = (match) => String(match.status || "").toUpperCase() === "FINISHED";

  const formatMatchTitle = (match) => {
    if (!isFinished(match) || !hasResult(match)) {
      return `${match.home_team} x ${match.away_team}`;
    }

    return `${match.home_team} ${match.home_score} x ${match.away_score} ${match.away_team}`;
  };

  const compareMatches = (a, b) => {
    const aRoundOrder = a.round_order || 0;
    const bRoundOrder = b.round_order || 0;
    if (aRoundOrder !== bRoundOrder) {
      return aRoundOrder - bRoundOrder;
    }

    const aStartsAt = new Date(a.starts_at || a.match_date || 0).getTime();
    const bStartsAt = new Date(b.starts_at || b.match_date || 0).getTime();
    return (Number.isNaN(aStartsAt) ? 0 : aStartsAt) - (Number.isNaN(bStartsAt) ? 0 : bStartsAt);
  };

  const getAvailablePhases = () => {
    const phasesByValue = new Map(PHASES.map((phase) => [phase.value, phase]));

    allMatches.forEach((match) => {
      if (!match.phase || phasesByValue.has(match.phase)) {
        return;
      }

      phasesByValue.set(match.phase, {
        value: match.phase,
        label: match.phase_label || match.phase,
        round_order: match.round_order || 99,
      });
    });

    return Array.from(phasesByValue.values()).sort((a, b) => {
      return (a.round_order || 0) - (b.round_order || 0);
    });
  };

  const getFilteredMatches = () => allMatches.filter((match) => match.phase === selectedPhase);

  const renderPhaseButtons = () => {
    if (!phaseFilters) {
      return;
    }

    phaseFilters.innerHTML = getAvailablePhases().map((phase) => `
      <button
        class="phase-filter-button${phase.value === selectedPhase ? " active" : ""}"
        type="button"
        data-phase="${escapeHtml(phase.value)}"
        aria-pressed="${phase.value === selectedPhase ? "true" : "false"}"
      >
        ${escapeHtml(phase.label)}
      </button>
    `).join("");

    phaseFilters.querySelectorAll("[data-phase]").forEach((button) => {
      button.addEventListener("click", () => {
        selectedPhase = button.dataset.phase || "GROUP_STAGE";
        renderPhaseButtons();
        renderMatches();
      });
    });
  };

  const setResultFeedback = (message, type = "") => {
    resultFeedback.textContent = message;
    resultFeedback.classList.toggle("is-error", type === "error");
    resultFeedback.classList.toggle("is-success", type === "success");
  };

  const setReopenMatchFeedback = (message, type = "") => {
    reopenMatchFeedback.textContent = message;
    reopenMatchFeedback.classList.toggle("is-error", type === "error");
    reopenMatchFeedback.classList.toggle("is-success", type === "success");
  };

  const setNextMatchFeedback = (message, type = "") => {
    nextMatchFeedback.textContent = message;
    nextMatchFeedback.classList.toggle("is-error", type === "error");
    nextMatchFeedback.classList.toggle("is-success", type === "success");
  };

  const setPageFeedback = (message, type = "") => {
    pageFeedback.textContent = message;
    pageFeedback.classList.toggle("is-error", type === "error");
    pageFeedback.classList.toggle("is-success", type === "success");
  };

  const openResultModal = (match) => {
    currentMatch = match;
    homeTeamLabel.textContent = match.home_team;
    awayTeamLabel.textContent = match.away_team;
    homeScoreInput.value = hasResult(match) ? match.home_score : "";
    awayScoreInput.value = hasResult(match) ? match.away_score : "";
    setResultFeedback("");
    resultModal.showModal();
    homeScoreInput.focus();
  };

  const closeResultModal = () => {
    resultModal.close();
    currentMatch = null;
    resultForm.reset();
    setResultFeedback("");
  };

  const openReopenMatchModal = (match) => {
    currentReopenMatch = match;
    reopenMatchTitle.textContent = formatMatchTitle(match);
    setReopenMatchFeedback("");
    reopenMatchModal.showModal();
  };

  const closeReopenMatchModal = () => {
    reopenMatchModal.close();
    currentReopenMatch = null;
    reopenMatchForm.reset();
    setReopenMatchFeedback("");
  };

  const renderMatches = () => {
    const matches = getFilteredMatches();
    if (!matches.length) {
      matchesList.innerHTML = '<p class="users-empty">Nenhuma partida cadastrada para esta fase.</p>';
      return;
    }

    matchesList.innerHTML = matches.map((match) => {
      const dateParts = formatDate(match.match_date || match.starts_at);
      const matchTitle = formatMatchTitle(match);
      const phaseLabel = match.phase_label || match.phase || "Fase nao informada";
      const reopenButton = isFinished(match)
        ? `
          <button class="danger-button result-button reopen-match-button" type="button" data-reopen-match-id="${escapeHtml(match.id)}">
            <span class="material-symbols-outlined" aria-hidden="true">restart_alt</span>
            <span>Reabrir</span>
          </button>
        `
        : "";

      return `
        <article class="match-row">
          <div class="match-teams">
            <strong>${escapeHtml(matchTitle)}</strong>
          </div>
          <span class="match-phase">${escapeHtml(phaseLabel)}</span>
          <time datetime="${escapeHtml(match.starts_at || "")}">
            <span>${escapeHtml(dateParts.date)}</span>
            ${dateParts.time ? `<span>${escapeHtml(dateParts.time)}</span>` : ""}
          </time>
          <span class="status-chip">${escapeHtml(formatStatus(match.status))}</span>
          <div class="match-actions">
            <button class="secondary-button result-button" type="button" data-match-id="${escapeHtml(match.id)}">
              <span class="material-symbols-outlined" aria-hidden="true">scoreboard</span>
              <span>Resultado</span>
            </button>
            ${reopenButton}
          </div>
        </article>
      `;
    }).join("");

    matchesList.querySelectorAll("[data-match-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const match = matches.find((item) => item.id === button.dataset.matchId);
        if (match) {
          openResultModal(match);
        }
      });
    });

    matchesList.querySelectorAll("[data-reopen-match-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const match = matches.find((item) => item.id === button.dataset.reopenMatchId);
        if (match) {
          openReopenMatchModal(match);
        }
      });
    });
  };

  const loadMatches = async () => {
    try {
      const data = await window.BolaoApi.matches();
      allMatches = (data.items || []).filter(isBrazilMatch).sort(compareMatches);
      renderPhaseButtons();
      renderMatches();
    } catch (error) {
      setPageFeedback("");
      matchesList.innerHTML = `<p class="users-empty">${escapeHtml(error.message || "Nao foi possivel carregar os jogos.")}</p>`;
    }
  };

  const loadPhases = async () => {
    if (phaseOptions.length) {
      return;
    }

    const phases = await window.BolaoApi.matchPhases();
    phaseOptions = Array.isArray(phases) ? phases : phases.items || [];
    nextMatchPhase.innerHTML = `
      <option value="">Selecione a fase</option>
      ${phaseOptions.map((phase) => `
        <option value="${escapeHtml(phase.value)}">${escapeHtml(phase.label)}</option>
      `).join("")}
    `;
  };

  const buildStartsAt = () => {
    if (!nextMatchDate.value || !nextMatchTime.value) {
      return "";
    }

    return `${nextMatchDate.value}T${nextMatchTime.value}:00-03:00`;
  };

  const updateNextMatchPreview = () => {
    const selectedPhase = phaseOptions.find((phase) => phase.value === nextMatchPhase.value);
    const phaseLabel = selectedPhase?.label || "Fase nao selecionada";
    const opponent = nextMatchOpponent.value.trim() || "Adversario";
    const title = `Brasil x ${opponent}`;
    const startsAt = buildStartsAt();
    const dateParts = startsAt ? formatDate(startsAt) : { date: "Data nao informada", time: "" };

    nextMatchPreview.innerHTML = `
      <strong>Proxima fase: ${escapeHtml(phaseLabel)}</strong>
      <span>Partida: ${escapeHtml(title)}</span>
      <span>Data: ${escapeHtml(dateParts.date)}${dateParts.time ? ` as ${escapeHtml(dateParts.time)}` : ""}</span>
    `;
  };

  const openNextMatchModal = async () => {
    setNextMatchFeedback("");
    try {
      await loadPhases();
    } catch (error) {
      setNextMatchFeedback(error.message || "Nao foi possivel carregar as fases.", "error");
    }

    updateNextMatchPreview();
    nextMatchModal.showModal();
    nextMatchPhase.focus();
  };

  const closeNextMatchModal = () => {
    nextMatchModal.close();
    nextMatchForm.reset();
    setNextMatchFeedback("");
    updateNextMatchPreview();
  };

  const validateNextMatchForm = () => {
    if (!nextMatchForm.reportValidity()) {
      return null;
    }

    const opponentTeam = nextMatchOpponent.value.trim();
    if (opponentTeam.toLowerCase() === "brasil") {
      setNextMatchFeedback("O adversario nao pode ser Brasil.", "error");
      nextMatchOpponent.focus();
      return null;
    }

    const startsAt = buildStartsAt();
    if (!startsAt || new Date(startsAt) <= new Date()) {
      setNextMatchFeedback("Data e horario devem ser futuros.", "error");
      nextMatchDate.focus();
      return null;
    }

    return {
      phase: nextMatchPhase.value,
      opponent_team: opponentTeam,
      starts_at: startsAt,
    };
  };

  resultForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!currentMatch || !resultForm.reportValidity()) {
      return;
    }

    const homeScore = Number(homeScoreInput.value);
    const awayScore = Number(awayScoreInput.value);
    if (!Number.isInteger(homeScore) || !Number.isInteger(awayScore) || homeScore < 0 || awayScore < 0) {
      setResultFeedback("Informe placares inteiros e maiores ou iguais a zero.", "error");
      return;
    }

    setResultFeedback("Salvando resultado...");

    try {
      const data = await window.BolaoApi.saveMatchResult(currentMatch.id, {
        home_score: homeScore,
        away_score: awayScore,
      });
      closeResultModal();
      setPageFeedback(data.message || "Resultado salvo com sucesso.", "success");
      await loadMatches();
    } catch (error) {
      setResultFeedback(error.message || "Nao foi possivel salvar o resultado.", "error");
    }
  });

  reopenMatchForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!currentReopenMatch) {
      return;
    }

    setReopenMatchFeedback("Reabrindo partida...");

    try {
      const data = await window.BolaoApi.reopenMatch(currentReopenMatch.id);
      closeReopenMatchModal();
      setPageFeedback(data.message || "Partida reaberta com sucesso.", "success");
      await loadMatches();
    } catch (error) {
      setReopenMatchFeedback(error.message || "Nao foi possivel reabrir a partida.", "error");
    }
  });

  nextMatchForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = validateNextMatchForm();
    if (!payload) {
      return;
    }

    setNextMatchFeedback("Criando partida...");

    try {
      const data = await window.BolaoApi.createNextBrazilMatch(payload);
      closeNextMatchModal();
      selectedPhase = payload.phase;
      setPageFeedback(data.message || "Proxima partida do Brasil criada com sucesso.", "success");
      await loadMatches();
    } catch (error) {
      setNextMatchFeedback(error.message || "Nao foi possivel criar a partida.", "error");
    }
  });

  resultModal?.addEventListener("cancel", () => {
    currentMatch = null;
    resultForm.reset();
    setResultFeedback("");
  });

  reopenMatchModal?.addEventListener("cancel", () => {
    currentReopenMatch = null;
    reopenMatchForm.reset();
    setReopenMatchFeedback("");
  });

  nextMatchModal?.addEventListener("cancel", () => {
    nextMatchForm.reset();
    setNextMatchFeedback("");
    updateNextMatchPreview();
  });

  document.querySelectorAll("[data-close-result]").forEach((button) => {
    button.addEventListener("click", closeResultModal);
  });

  document.querySelectorAll("[data-close-reopen-match]").forEach((button) => {
    button.addEventListener("click", closeReopenMatchModal);
  });

  document.querySelectorAll("[data-close-next-match]").forEach((button) => {
    button.addEventListener("click", closeNextMatchModal);
  });

  createMatchButton?.addEventListener("click", openNextMatchModal);
  [nextMatchPhase, nextMatchOpponent, nextMatchDate, nextMatchTime].forEach((element) => {
    element?.addEventListener("input", updateNextMatchPreview);
    element?.addEventListener("change", updateNextMatchPreview);
  });

  loadMatches();
})();
