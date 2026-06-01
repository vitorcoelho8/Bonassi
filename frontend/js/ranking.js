(function () {
  const podium = document.querySelector("#podium");
  const list = document.querySelector("#ranking-list");
  const score = document.querySelector("#user-score");

  const escapeHtml = (value) => String(value || "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));

  const renderEmpty = (message) => {
    podium.innerHTML = "";
    list.innerHTML = `<article class="users-empty">${escapeHtml(message)}</article>`;
    score.textContent = "0 pts";
  };

  const render = (ranking) => {
    if (!ranking.length) {
      renderEmpty("Nenhum participante no ranking ainda.");
      return;
    }

    podium.innerHTML = ranking.slice(0, 3).map((item, index) => `
      <article class="podium-card">
        <p>${index + 1} lugar</p>
        <h3>${escapeHtml(item.participant.name)}</h3>
        <strong>${item.points}</strong>
        <span>pts</span>
      </article>
    `).join("");

    list.innerHTML = ranking.map((item, index) => `
      <div class="leaderboard-row">
        <span>${index + 1}o</span>
        <span class="player-name">${escapeHtml(item.participant.name)}</span>
        <span>${item.exact_scores}</span>
        <strong class="points">${item.points}</strong>
      </div>
    `).join("");

    const currentUser = JSON.parse(localStorage.getItem("user") || "null");
    const current = ranking.find((item) => item.participant.id === currentUser?.id);
    score.textContent = `${current?.points || 0} pts`;
  };

  window.BolaoApi.ranking()
    .then((data) => render(data.items || []))
    .catch((error) => renderEmpty(error.message || "Nao foi possivel carregar o ranking."));
})();
