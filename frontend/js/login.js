(function () {
  const form = document.querySelector("#login-form");
  const feedback = document.querySelector("#login-feedback");

  const setFeedback = (message, type) => {
    feedback.textContent = message;
    feedback.classList.toggle("is-error", type === "error");
    feedback.classList.toggle("is-success", type === "success");
  };

  const toPayload = (targetForm) => Object.fromEntries(new FormData(targetForm).entries());

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
      return;
    }

    setFeedback("Entrando...", "");

    try {
      const data = await window.BolaoApi.login(toPayload(form));
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "ranking.html";
    } catch (error) {
      setFeedback(error.message || "Nao foi possivel entrar.", "error");
    }
  });
})();
