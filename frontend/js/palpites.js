(function () {
  const list = document.querySelector("#matches-list");

  const render = (matches) => {
    if (!matches.length) {
      list.innerHTML = '<article class="data-item">Nenhuma partida cadastrada ainda.</article>';
      return;
    }

    list.innerHTML = matches.map((match) => `
      <article class="data-item">
        <strong>${match.home_team} x ${match.away_team}</strong>
        <span>${match.status}</span>
      </article>
    `).join("");
  };

  window.BolaoApi.matches()
    .then((data) => render(data.items || []))
    .catch(() => render([]));
})();
