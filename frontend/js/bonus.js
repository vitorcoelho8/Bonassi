(function () {
  const params = new URLSearchParams(window.location.search);
  const participantId = params.get("participant_id");
  const heading = document.querySelector("#bonus-participant-heading");
  const participantCard = document.querySelector("#bonus-participant-card");
  const form = document.querySelector("#bonus-form");
  const feedback = document.querySelector("#bonus-feedback");
  const bonusTypes = Array.from(document.querySelectorAll("input[name='bonus_type']"));
  const referralFields = document.querySelector("#referral-fields");
  const backProfileButton = document.querySelector("#back-profile-button");
  const bonusNavLink = document.querySelector("#bonus-nav-link");
  const finishButton = document.querySelector("#finish-button");
  const participantBonusPanel = document.querySelector("#participant-bonus-panel");
  const participantBonusList = document.querySelector("#participant-bonus-list");
  const adminBonusPanel = document.querySelector("#admin-bonus-panel");
  const adminBonusList = document.querySelector("#admin-bonus-list");
  const adminBonusFeedback = document.querySelector("#admin-bonus-feedback");

  let participant = null;

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const setFeedback = (element, message, type) => {
    element.textContent = message;
    element.classList.toggle("is-error", type === "error");
    element.classList.toggle("is-success", type === "success");
  };

  const formatDate = (value) => {
    if (!value) {
      return "Data nao informada";
    }

    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(value));
  };

  const selectedBonusType = () => bonusTypes.find((input) => input.checked)?.value || "";

  const toggleReferralFields = () => {
    const isReferral = selectedBonusType() === "REFERRAL";
    referralFields.classList.toggle("hidden", !isReferral);
    referralFields.querySelectorAll("input").forEach((input) => {
      input.required = isReferral;
      if (!isReferral) {
        input.value = "";
      }
    });
  };

  const renderBonusList = (target, items, emptyMessage, includeParticipant = false) => {
    if (!items.length) {
      target.innerHTML = `<article class="users-empty">${escapeHtml(emptyMessage)}</article>`;
      return;
    }

    target.innerHTML = items.map((item) => `
      <article class="data-item bonus-request-card">
        ${includeParticipant ? `
          <div>
            <strong>${escapeHtml(item.participant?.name)}</strong>
            <span>${escapeHtml(item.participant?.phone)}</span>
          </div>
        ` : ""}
        <div>
          <strong>${escapeHtml(item.description || item.bonus_type)} (${escapeHtml(item.points)} pts)</strong>
          <span>Status: ${escapeHtml(item.status)}</span>
        </div>
        <p>${escapeHtml(item.evidence_text)}</p>
        ${item.referral_name || item.referral_phone ? `
          <p>Indicado: ${escapeHtml(item.referral_name)} - ${escapeHtml(item.referral_phone)}</p>
        ` : ""}
        <time>${escapeHtml(formatDate(item.created_at))}</time>
        ${includeParticipant ? `
          <div class="bonus-actions">
            <button class="primary-button" type="button" data-approve-bonus="${escapeHtml(item.id)}">Aprovar</button>
            <button class="secondary-button" type="button" data-reject-bonus="${escapeHtml(item.id)}">Recusar</button>
          </div>
        ` : ""}
      </article>
    `).join("");
  };

  const loadParticipantBonus = async () => {
    const data = await window.BolaoApi.participantBonus(participantId);
    const items = Array.isArray(data) ? data : data.items || [];
    renderBonusList(participantBonusList, items, "Nenhum bonus solicitado ainda.");
    participantBonusPanel.classList.remove("hidden");
  };

  const loadPendingBonus = async () => {
    try {
      const data = await window.BolaoApi.pendingBonus();
      const items = Array.isArray(data) ? data : data.items || [];
      renderBonusList(adminBonusList, items, "Nenhuma solicitacao pendente.", true);
    } catch (error) {
      renderBonusList(adminBonusList, [], "Nao foi possivel carregar os bonus pendentes.");
      setFeedback(adminBonusFeedback, error.message || "Nao foi possivel carregar os bonus pendentes.", "error");
    }
  };

  const showAdminMode = async () => {
    heading.textContent = "Aba de aprovacao de bonus";
    form.classList.add("hidden");
    participantCard.classList.add("hidden");
    participantBonusPanel.classList.add("hidden");
    adminBonusPanel.classList.remove("hidden");
    await loadPendingBonus();
  };

  const showParticipantMode = async () => {
    adminBonusPanel.classList.add("hidden");
    form.classList.remove("hidden");

    backProfileButton.addEventListener("click", () => {
      window.location.href = `palpites.html?participant_id=${encodeURIComponent(participantId)}`;
    });

    if (bonusNavLink) {
      bonusNavLink.href = `bonus.html?participant_id=${encodeURIComponent(participantId)}`;
    }

    const data = await window.BolaoApi.participant(participantId);
    participant = data.item;
    heading.textContent = `Perfil de: ${participant.name}`;
    participantCard.innerHTML = `
      <p><strong>Participante:</strong> ${escapeHtml(participant.name)}</p>
      <p><strong>Telefone:</strong> ${escapeHtml(participant.phone)}</p>
    `;
    participantCard.classList.remove("hidden");
    await loadParticipantBonus();
  };

  finishButton.addEventListener("click", () => {
    window.location.href = "admin.html";
  });

  bonusTypes.forEach((input) => {
    input.addEventListener("change", toggleReferralFields);
  });
  toggleReferralFields();

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity() || !participant) {
      return;
    }

    const formData = new FormData(form);
    setFeedback(feedback, "Enviando solicitacao...", "");

    try {
      await window.BolaoApi.saveBonus({
        participant_id: participant.id,
        bonus_type: formData.get("bonus_type"),
        evidence_text: formData.get("evidence_text"),
        referral_name: formData.get("referral_name") || null,
        referral_phone: formData.get("referral_phone") || null,
      });
      setFeedback(feedback, "Solicitacao enviada para aprovacao do admin.", "success");
      form.reset();
      toggleReferralFields();
      await loadParticipantBonus();
    } catch (error) {
      setFeedback(feedback, error.message || "Nao foi possivel salvar.", "error");
    }
  });

  adminBonusList?.addEventListener("click", async (event) => {
    const approveButton = event.target.closest("[data-approve-bonus]");
    const rejectButton = event.target.closest("[data-reject-bonus]");
    const bonusId = approveButton?.dataset.approveBonus || rejectButton?.dataset.rejectBonus;

    if (!bonusId) {
      return;
    }

    try {
      setFeedback(adminBonusFeedback, "Atualizando solicitacao...", "");
      const response = approveButton
        ? await window.BolaoApi.approveBonus(bonusId)
        : await window.BolaoApi.rejectBonus(bonusId);
      setFeedback(adminBonusFeedback, response.message || "Solicitacao atualizada.", "success");
      await loadPendingBonus();
    } catch (error) {
      setFeedback(adminBonusFeedback, error.message || "Nao foi possivel atualizar.", "error");
    }
  });

  (participantId ? showParticipantMode() : showAdminMode()).catch((error) => {
    heading.textContent = error.message || "Nao foi possivel carregar bonus.";
    form.classList.add("hidden");
    participantBonusPanel.classList.add("hidden");
    adminBonusPanel.classList.add("hidden");
  });
})();
