(function () {
  const podium = document.querySelector("#podium");
  const list = document.querySelector("#ranking-list");
  const logoutButton = document.querySelector("#logout-button");
  const shareButton = document.querySelector("#share-ranking-button");
  const shareFeedback = document.querySelector("#share-ranking-feedback");
  const shareCard = document.querySelector("#ranking-share-card");
  const shareTitle = document.querySelector("#ranking-share-title");
  const shareMatch = document.querySelector("#ranking-share-match");
  const shareList = document.querySelector("#ranking-share-list");
  const shareUpdated = document.querySelector("#ranking-share-updated");
  const pagination = document.querySelector("#ranking-pagination");
  const prevPageButton = document.querySelector("#ranking-prev-page");
  const nextPageButton = document.querySelector("#ranking-next-page");
  const pageStatus = document.querySelector("#ranking-page-status");
  const rankingTitle = document.querySelector("#ranking-title");
  const rankingSubtitle = document.querySelector("#ranking-subtitle");
  const tabGlobal = document.querySelector("#ranking-tab-global");
  const tabRound = document.querySelector("#ranking-tab-round");
  const globalView = document.querySelector("#global-ranking-view");
  const roundView = document.querySelector("#round-ranking-view");
  const swipeArea = document.querySelector("#ranking-swipe-area");
  const roundMatchCard = document.querySelector("#round-match-card");
  const roundEmptyState = document.querySelector("#round-empty-state");
  const roundPodium = document.querySelector("#round-podium");
  const roundRankingBoard = document.querySelector("#round-ranking-board");
  const roundRankingList = document.querySelector("#round-ranking-list");
  const pageSize = 12;

  let currentView = "global";
  let currentRanking = [];
  let currentRoundRanking = [];
  let currentRoundMatch = null;
  let currentPage = 1;
  let roundLoaded = false;
  let roundLoading = false;
  let isSharing = false;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));

  const formatUpdatedAt = () => new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date());

  const formatMatchDate = (value) => {
    if (!value) {
      return "";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "";
    }

    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(date);
  };

  const setShareFeedback = (message, type = "") => {
    shareFeedback.textContent = message;
    shareFeedback.classList.toggle("is-error", type === "error");
    shareFeedback.classList.toggle("is-success", type === "success");
  };

  const activeRanking = () => (
    currentView === "round" ? currentRoundRanking : currentRanking
  );

  const updateShareButtonState = () => {
    shareButton.disabled = isSharing || roundLoading || !activeRanking().length;
  };

  const renderFlag = (src, name, className) => {
    if (src) {
      return `<img class="${className}" src="${escapeHtml(src)}" alt="${escapeHtml(name)}">`;
    }

    return `<span class="${className} round-team-flag-fallback" aria-hidden="true">?</span>`;
  };

  const renderShareMatch = () => {
    if (currentView !== "round" || !currentRoundMatch) {
      shareMatch.hidden = true;
      shareMatch.innerHTML = "";
      return;
    }

    shareMatch.hidden = false;
    shareMatch.innerHTML = `
      <div class="share-round-teams">
        <span>${renderFlag(currentRoundMatch.home_flag_url, currentRoundMatch.home_team, "share-round-flag")}</span>
        <strong>${escapeHtml(currentRoundMatch.display_score)}</strong>
        <span>${renderFlag(currentRoundMatch.away_flag_url, currentRoundMatch.away_team, "share-round-flag")}</span>
      </div>
      <p>${escapeHtml(currentRoundMatch.phase_label || "")}</p>
    `;
  };

  const renderShareCard = () => {
    const ranking = activeRanking();
    const updatedAt = `Atualizado em ${formatUpdatedAt()}`;
    shareUpdated.textContent = updatedAt;
    shareTitle.textContent = currentView === "round" ? "Ranking da Rodada" : "Ranking Global";
    renderShareMatch();

    const rankingToShare = ranking.slice(0, pageSize);
    if (!rankingToShare.length) {
      shareList.innerHTML = `<div class="share-ranking-empty">${
        currentView === "round"
          ? "Ranking da rodada ainda nao possui participantes."
          : "Ranking ainda nao possui participantes."
      }</div>`;
      return;
    }

    shareList.innerHTML = rankingToShare.map((item, index) => {
      const position = index + 1;
      const name = currentView === "round" ? item.name : item.participant.name;
      const points = item.points;
      const detail = currentView === "round"
        ? `${item.exact ? "Placar exato" : "Palpite"} - ${item.predicted_score}`
        : `${position}o lugar`;

      return `
        <article class="share-ranking-row ${position <= 3 ? "is-top-three" : ""}">
          <span class="share-ranking-position">${position}</span>
          <div class="share-ranking-player">
            <strong>${escapeHtml(name)}</strong>
            <span>${escapeHtml(detail)}</span>
          </div>
          <strong class="share-ranking-points">${points} pts</strong>
        </article>
      `;
    }).join("");
  };

  const renderGlobalEmpty = (message) => {
    currentRanking = [];
    currentPage = 1;
    podium.innerHTML = "";
    list.innerHTML = `<article class="users-empty">${escapeHtml(message)}</article>`;
    pagination.hidden = true;
    if (currentView === "global") {
      setShareFeedback("Ranking ainda nao possui participantes.");
      renderShareCard();
      updateShareButtonState();
    }
  };

  const renderLeaderboardPage = () => {
    const totalPages = Math.max(1, Math.ceil(currentRanking.length / pageSize));
    currentPage = Math.min(Math.max(currentPage, 1), totalPages);

    const start = (currentPage - 1) * pageSize;
    const pageItems = currentRanking.slice(start, start + pageSize);

    list.innerHTML = pageItems.map((item, index) => {
      const position = start + index + 1;
      return `
        <div class="leaderboard-row">
          <span>${position}o</span>
          <span class="player-name">${escapeHtml(item.participant.name)}</span>
          <span>${item.exact_scores}</span>
          <strong class="points">${item.points}</strong>
        </div>
      `;
    }).join("");

    pagination.hidden = currentRanking.length <= pageSize;
    prevPageButton.disabled = currentPage === 1;
    nextPageButton.disabled = currentPage === totalPages;
    pageStatus.textContent = `Pagina ${currentPage} de ${totalPages}`;
  };

  const renderGlobalRanking = (ranking) => {
    if (!ranking.length) {
      renderGlobalEmpty("Nenhum participante no ranking ainda.");
      return;
    }

    currentRanking = ranking;
    currentPage = 1;

    podium.innerHTML = ranking.slice(0, 3).map((item, index) => `
      <article class="podium-card">
        <p>${index + 1} lugar</p>
        <h3>${escapeHtml(item.participant.name)}</h3>
        <strong>${item.points}</strong>
        <span>pts</span>
      </article>
    `).join("");

    renderLeaderboardPage();
    if (currentView === "global") {
      setShareFeedback("");
      renderShareCard();
      updateShareButtonState();
    }
  };

  const renderRoundMatch = (match) => {
    const dateText = formatMatchDate(match.starts_at);
    roundMatchCard.innerHTML = `
      <div class="round-match-teams">
        <div class="round-team">
          ${renderFlag(match.home_flag_url, match.home_team, "round-team-flag")}
          <strong>${escapeHtml(match.home_team)}</strong>
        </div>
        <div class="round-score" aria-label="Placar oficial">
          <strong>${escapeHtml(match.home_score)} x ${escapeHtml(match.away_score)}</strong>
        </div>
        <div class="round-team">
          ${renderFlag(match.away_flag_url, match.away_team, "round-team-flag")}
          <strong>${escapeHtml(match.away_team)}</strong>
        </div>
      </div>
      <div class="round-match-meta">
        <span>${escapeHtml(match.phase_label || "Partida")}</span>
        ${dateText ? `<time datetime="${escapeHtml(match.starts_at)}">${escapeHtml(dateText)}</time>` : ""}
      </div>
    `;
  };

  const renderRoundEmpty = (message) => {
    currentRoundMatch = null;
    currentRoundRanking = [];
    roundMatchCard.innerHTML = "";
    roundEmptyState.textContent = message;
    roundEmptyState.hidden = false;
    roundPodium.innerHTML = "";
    roundRankingBoard.hidden = true;
    roundRankingList.innerHTML = "";
    if (currentView === "round") {
      setShareFeedback("Ranking da rodada ainda nao possui participantes.");
      renderShareCard();
      updateShareButtonState();
    }
  };

  const renderRoundRanking = (data) => {
    currentRoundMatch = data.match || null;
    currentRoundRanking = data.ranking || [];
    roundLoaded = true;

    if (!currentRoundMatch) {
      renderRoundEmpty(data.message || "Nenhuma rodada finalizada ainda.");
      return;
    }

    roundEmptyState.hidden = true;
    renderRoundMatch(currentRoundMatch);

    roundPodium.innerHTML = currentRoundRanking.slice(0, 3).map((item) => `
      <article class="podium-card">
        <p>${item.position} lugar</p>
        <h3>${escapeHtml(item.name)}</h3>
        <strong>${item.points}</strong>
        <span>pts</span>
      </article>
    `).join("");

    if (!currentRoundRanking.length) {
      roundEmptyState.textContent = "Nenhum palpite encontrado para esta partida.";
      roundEmptyState.hidden = false;
      roundRankingBoard.hidden = true;
      roundRankingList.innerHTML = "";
    } else {
      roundRankingBoard.hidden = false;
      roundRankingList.innerHTML = currentRoundRanking.map((item) => `
        <div class="leaderboard-row round-ranking-row">
          <span>${item.position}o</span>
          <span class="player-name">${escapeHtml(item.name)}</span>
          <span class="round-predicted-score">${escapeHtml(item.predicted_score)}</span>
          <span class="round-exact ${item.exact ? "is-exact" : ""}">${item.exact ? "Sim" : "Nao"}</span>
          <strong class="points">${item.points}</strong>
        </div>
      `).join("");
    }

    if (currentView === "round") {
      setShareFeedback("");
      renderShareCard();
      updateShareButtonState();
    }
  };

  const loadRoundRanking = async () => {
    if (roundLoaded || roundLoading) {
      return;
    }

    roundLoading = true;
    roundEmptyState.textContent = "Carregando ranking da rodada...";
    roundEmptyState.hidden = false;
    updateShareButtonState();

    try {
      const data = await window.BolaoApi.roundRanking();
      renderRoundRanking(data);
    } catch (error) {
      roundLoaded = true;
      renderRoundEmpty(error.message || "Nao foi possivel carregar o ranking da rodada.");
      setShareFeedback(error.message || "Nao foi possivel carregar o ranking da rodada.", "error");
    } finally {
      roundLoading = false;
      updateShareButtonState();
    }
  };

  const setView = (view) => {
    if (view !== "global" && view !== "round") {
      return;
    }

    currentView = view;
    const isRound = view === "round";
    tabGlobal.classList.toggle("active", !isRound);
    tabRound.classList.toggle("active", isRound);
    tabGlobal.setAttribute("aria-selected", String(!isRound));
    tabRound.setAttribute("aria-selected", String(isRound));
    globalView.classList.toggle("active", !isRound);
    roundView.classList.toggle("active", isRound);
    globalView.hidden = isRound;
    roundView.hidden = !isRound;
    rankingTitle.textContent = isRound ? "Ranking da Rodada" : "Ranking Global";
    rankingSubtitle.textContent = isRound
      ? "Pontuacao da ultima partida finalizada."
      : "Veja quem esta liderando as apostas.";
    setShareFeedback("");

    if (isRound) {
      loadRoundRanking();
    } else {
      renderShareCard();
      updateShareButtonState();
    }
  };

  logoutButton?.addEventListener("click", async () => {
    try {
      await fetch("/api/participants/logout", { method: "POST" });
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
  });

  const canvasToBlob = (canvas) => new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob);
        return;
      }

      reject(new Error("Nao foi possivel gerar a imagem."));
    }, "image/png", 1);
  });

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  const shareRanking = async () => {
    if (!activeRanking().length) {
      setShareFeedback(
        currentView === "round"
          ? "Ranking da rodada ainda nao possui participantes."
          : "Ranking ainda nao possui participantes.",
        "error",
      );
      return;
    }

    if (!window.html2canvas) {
      setShareFeedback("Nao foi possivel carregar o gerador de imagem.", "error");
      return;
    }

    isSharing = true;
    updateShareButtonState();
    setShareFeedback("Gerando imagem do ranking...");
    renderShareCard();

    const filename = currentView === "round" ? "ranking-rodada-bolao.png" : "ranking-bolao.png";
    const shareText = currentView === "round" ? "Ranking da rodada" : "Ranking global";

    try {
      const canvas = await window.html2canvas(shareCard, {
        backgroundColor: "#f7fafb",
        scale: 2,
        useCORS: true,
        windowWidth: 1080,
        windowHeight: 1920,
      });
      const blob = await canvasToBlob(canvas);
      const file = new File([blob], filename, { type: "image/png" });

      if (navigator.canShare?.({ files: [file] })) {
        try {
          await navigator.share({
            files: [file],
            title: "Bolao Bonassi",
            text: shareText,
          });
          setShareFeedback("Ranking compartilhado.", "success");
        } catch (error) {
          if (error.name === "AbortError") {
            setShareFeedback("");
            return;
          }

          downloadBlob(blob, filename);
          setShareFeedback(`Imagem baixada como ${filename}.`, "success");
        }
      } else {
        downloadBlob(blob, filename);
        setShareFeedback(`Imagem baixada como ${filename}.`, "success");
      }
    } catch (error) {
      setShareFeedback(error.message || "Nao foi possivel compartilhar o ranking.", "error");
    } finally {
      isSharing = false;
      updateShareButtonState();
    }
  };

  shareButton?.addEventListener("click", shareRanking);
  tabGlobal?.addEventListener("click", () => setView("global"));
  tabRound?.addEventListener("click", () => setView("round"));

  prevPageButton?.addEventListener("click", () => {
    currentPage -= 1;
    renderLeaderboardPage();
  });

  nextPageButton?.addEventListener("click", () => {
    currentPage += 1;
    renderLeaderboardPage();
  });

  let touchStartX = 0;
  let touchStartY = 0;

  swipeArea?.addEventListener("touchstart", (event) => {
    if (event.touches.length !== 1) {
      return;
    }

    touchStartX = event.touches[0].clientX;
    touchStartY = event.touches[0].clientY;
  }, { passive: true });

  swipeArea?.addEventListener("touchend", (event) => {
    const touch = event.changedTouches[0];
    if (!touch) {
      return;
    }

    const deltaX = touch.clientX - touchStartX;
    const deltaY = touch.clientY - touchStartY;
    if (Math.abs(deltaX) < 64 || Math.abs(deltaX) < Math.abs(deltaY) * 1.5) {
      return;
    }

    setView(deltaX < 0 ? "round" : "global");
  }, { passive: true });

  window.BolaoApi.ranking()
    .then((data) => renderGlobalRanking(data.items || []))
    .catch((error) => renderGlobalEmpty(error.message || "Ranking ainda nao possui participantes."));
})();
