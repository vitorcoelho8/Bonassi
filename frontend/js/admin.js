(function () {
  const list = document.querySelector("#participants-list");

  const render = (participants) => {
    if (!participants.length) {
      list.innerHTML = '<article class="data-item">Nenhum participante encontrado.</article>';
      return;
    }

    list.innerHTML = participants.map((participant) => `
      <article class="data-item">
        <strong>${participant.name}</strong>
        <span>${participant.email}</span>
      </article>
    `).join("");
  };

  window.BolaoApi.adminParticipants()
    .then((data) => render(data.items || []))
    .catch(() => render([]));
})();
