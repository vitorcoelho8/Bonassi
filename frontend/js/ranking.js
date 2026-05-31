(function () {
  const fallbackRanking = [
    { participant: { name: "Joao P." }, exact_scores: 8, points: 210 },
    { participant: { name: "Mariana C." }, exact_scores: 7, points: 185 },
    { participant: { name: "Carlos Silva" }, exact_scores: 6, points: 170 },
    { participant: { name: "Ana Beatriz" }, exact_scores: 5, points: 165 },
  ];

  const podium = document.querySelector("#podium");
  const list = document.querySelector("#ranking-list");
  const score = document.querySelector("#user-score");

  const render = (items) => {
    const ranking = items.length ? items : fallbackRanking;

    podium.innerHTML = ranking.slice(0, 3).map((item, index) => `
      <article class="podium-card">
        <p>${index + 1} lugar</p>
        <h3>${item.participant.name}</h3>
        <strong>${item.points}</strong>
        <span>pts</span>
      </article>
    `).join("");

    list.innerHTML = ranking.map((item, index) => `
      <div class="leaderboard-row">
        <span>${index + 1}o</span>
        <span class="player-name">${item.participant.name}</span>
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
    .catch(() => render(fallbackRanking));
})();
