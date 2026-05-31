(function () {
  const form = document.querySelector("#bonus-form");
  const feedback = document.querySelector("#bonus-feedback");

  const setFeedback = (message, type) => {
    feedback.textContent = message;
    feedback.classList.toggle("is-error", type === "error");
    feedback.classList.toggle("is-success", type === "success");
  };

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
      return;
    }

    const formData = new FormData(form);
    setFeedback("Salvando...", "");

    try {
      await window.BolaoApi.saveBonus({
        question_key: "champion",
        answer: formData.get("answer"),
      });
      setFeedback("Bonus salvo.", "success");
    } catch (error) {
      setFeedback(error.message || "Nao foi possivel salvar.", "error");
    }
  });
})();
