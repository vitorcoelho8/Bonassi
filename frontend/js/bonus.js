(function () {
  const params = new URLSearchParams(window.location.search);
  const participantId = params.get("participant_id");
  const heading = document.querySelector("#bonus-participant-heading");
  const form = document.querySelector("#bonus-form");
  const feedback = document.querySelector("#bonus-feedback");
  const bonusType = document.querySelector("#bonus-type");
  const referralFields = document.querySelector("#referral-fields");
  const backProfileButton = document.querySelector("#back-profile-button");
  const finishButton = document.querySelector("#finish-button");

  let participant = null;

  const setFeedback = (message, type) => {
    feedback.textContent = message;
    feedback.classList.toggle("is-error", type === "error");
    feedback.classList.toggle("is-success", type === "success");
  };

  const toggleReferralFields = () => {
    const isReferral = bonusType.value === "REFERRAL";
    referralFields.classList.toggle("hidden", !isReferral);
    referralFields.querySelectorAll("input").forEach((input) => {
      input.required = isReferral;
    });
  };

  const showError = (message) => {
    heading.textContent = message;
    form.classList.add("hidden");
  };

  if (!participantId) {
    showError("Participante nao informado. Volte ao painel e selecione um perfil.");
    return;
  }

  backProfileButton.addEventListener("click", () => {
    window.location.href = `palpites.html?participant_id=${encodeURIComponent(participantId)}`;
  });

  finishButton.addEventListener("click", () => {
    window.location.href = "admin.html";
  });

  bonusType.addEventListener("change", toggleReferralFields);
  toggleReferralFields();

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity() || !participant) {
      return;
    }

    const formData = new FormData(form);
    setFeedback("Enviando solicitacao...", "");

    try {
      await window.BolaoApi.saveBonus({
        participant_id: participant.id,
        bonus_type: formData.get("bonus_type"),
        evidence_text: formData.get("evidence_text"),
        referral_name: formData.get("referral_name") || null,
        referral_phone: formData.get("referral_phone") || null,
      });
      setFeedback("Solicitacao enviada para aprovacao do admin.", "success");
      form.reset();
      toggleReferralFields();
    } catch (error) {
      setFeedback(error.message || "Nao foi possivel salvar.", "error");
    }
  });

  const load = async () => {
    try {
      const data = await window.BolaoApi.participant(participantId);
      participant = data.item;
      heading.textContent = `Perfil de: ${participant.name}`;
    } catch (error) {
      showError(error.message || "Participante nao encontrado.");
    }
  };

  load();
})();
