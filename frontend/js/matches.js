(function () {
  const matchesList = document.querySelector("#matches-list");
  const pageFeedback = document.querySelector("#matches-feedback");
  const modal = document.querySelector("#result-modal");
  const form = document.querySelector("#result-form");
  const feedback = document.querySelector("#result-feedback");
  const homeTeamLabel = document.querySelector("#result-home-team");
  const awayTeamLabel = document.querySelector("#result-away-team");
  const homeScoreInput = document.querySelector("#result-home-score");
  const awayScoreInput = document.querySelector("#result-away-score");
  let currentMatch = null;

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const isBrazilMatch = (match) => {
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
    };

    return labels[normalizedStatus] || normalizedStatus || "INDEFINIDO";
  };

  const hasResult = (match) => match.home_score !== null
    && match.home_score !== undefined
    && match.away_score !== null
    && match.away_score !== undefined;

  const formatMatchTitle = (match) => {
    if (!hasResult(match)) {
      return `${match.home_team} x ${match.away_team}`;
    }

    return `${match.home_team} ${match.home_score} x ${match.away_score} ${match.away_team}`;
  };

  const setFeedback = (message, type = "") => {
    feedback.textContent = message;
    feedback.classList.toggle("is-error", type === "error");
    feedback.classList.toggle("is-success", type === "success");
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
    setFeedback("");
    modal.showModal();
    homeScoreInput.focus();
  };

  const closeResultModal = () => {
    modal.close();
    currentMatch = null;
    form.reset();
    setFeedback("");
  };

  const renderMatches = (matches) => {
    if (!matches.length) {
      matchesList.innerHTML = '<p class="users-empty">Nenhum jogo do Brasil cadastrado.</p>';
      return;
    }

    matchesList.innerHTML = matches.map((match) => {
      const dateParts = formatDate(match.match_date || match.starts_at);
      const matchTitle = formatMatchTitle(match);

      return `
        <article class="match-row">
          <div class="match-teams">
            <strong>${escapeHtml(matchTitle)}</strong>
            <span>Primeira fase</span>
          </div>
          <time datetime="${escapeHtml(match.starts_at || "")}">
            <span>${escapeHtml(dateParts.date)}</span>
            ${dateParts.time ? `<span>${escapeHtml(dateParts.time)}</span>` : ""}
          </time>
          <span class="status-chip">${escapeHtml(formatStatus(match.status))}</span>
          <button class="secondary-button result-button" type="button" data-match-id="${escapeHtml(match.id)}">
            <span class="material-symbols-outlined" aria-hidden="true">scoreboard</span>
            <span>Resultado</span>
          </button>
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
  };

  const loadMatches = async () => {
    try {
      const data = await window.BolaoApi.matches();
      const brazilMatches = (data.items || []).filter(isBrazilMatch);
      renderMatches(brazilMatches);
    } catch (error) {
      setPageFeedback("");
      matchesList.innerHTML = `<p class="users-empty">${escapeHtml(error.message || "Nao foi possivel carregar os jogos.")}</p>`;
    }
  };

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!currentMatch || !form.reportValidity()) {
      return;
    }

    const homeScore = Number(homeScoreInput.value);
    const awayScore = Number(awayScoreInput.value);
    if (!Number.isInteger(homeScore) || !Number.isInteger(awayScore) || homeScore < 0 || awayScore < 0) {
      setFeedback("Informe placares inteiros e maiores ou iguais a zero.", "error");
      return;
    }

    setFeedback("Salvando resultado...");

    try {
      const data = await window.BolaoApi.saveMatchResult(currentMatch.id, {
        home_score: homeScore,
        away_score: awayScore,
      });
      closeResultModal();
      setPageFeedback(data.message || "Resultado salvo com sucesso.", "success");
      await loadMatches();
    } catch (error) {
      setFeedback(error.message || "Nao foi possivel salvar o resultado.", "error");
    }
  });

  modal?.addEventListener("cancel", () => {
    currentMatch = null;
    form.reset();
    setFeedback("");
  });

  document.querySelectorAll("[data-close-result]").forEach((button) => {
    button.addEventListener("click", closeResultModal);
  });

  loadMatches();
})();
