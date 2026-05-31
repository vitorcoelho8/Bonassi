(function () {
  const matchesList = document.querySelector("#matches-list");

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
      return "Horario nao definido";
    }

    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
      timeZone: "America/Sao_Paulo",
    }).format(new Date(value));
  };

  const formatStatus = (status) => {
    const normalizedStatus = String(status || "").toUpperCase();
    const labels = {
      SCHEDULED: "Agendado",
      LIVE: "Ao vivo",
      FINISHED: "Finalizado",
      CANCELLED: "Cancelado",
    };

    return labels[normalizedStatus] || normalizedStatus || "Indefinido";
  };

  const renderMatches = (matches) => {
    if (!matches.length) {
      matchesList.innerHTML = '<p class="users-empty">Nenhum jogo do Brasil cadastrado.</p>';
      return;
    }

    matchesList.innerHTML = matches.map((match) => `
      <article class="match-row">
        <div class="match-teams">
          <strong>${escapeHtml(match.home_team)} x ${escapeHtml(match.away_team)}</strong>
          <span>Primeira fase</span>
        </div>
        <time datetime="${escapeHtml(match.starts_at || "")}">${escapeHtml(formatDate(match.match_date || match.starts_at))}</time>
        <span class="status-chip">${escapeHtml(formatStatus(match.status))}</span>
      </article>
    `).join("");
  };

  const loadMatches = async () => {
    try {
      const data = await window.BolaoApi.matches();
      const brazilMatches = (data.items || []).filter(isBrazilMatch);
      renderMatches(brazilMatches);
    } catch (error) {
      matchesList.innerHTML = `<p class="users-empty">${escapeHtml(error.message || "Nao foi possivel carregar os jogos.")}</p>`;
    }
  };

  loadMatches();
})();
