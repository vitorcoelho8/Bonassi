(function () {
  const form = document.querySelector("#login-form");
  const feedback = document.querySelector("#login-feedback");
  const submitButton = form?.querySelector("button[type='submit']");

  if (!form || !feedback || !submitButton) {
    return;
  }

  const setFeedback = (message, type) => {
    feedback.textContent = message;
    feedback.classList.toggle("is-error", type === "error");
    feedback.classList.toggle("is-success", type === "success");
  };

  const normalizeError = (message) => {
    const messages = {
      "Invalid credentials.": "Email ou senha inv\u00e1lidos.",
      "Inactive user.": "Usu\u00e1rio inativo.",
    };

    return messages[message] || message || "N\u00e3o foi poss\u00edvel entrar.";
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
      return;
    }

    const formData = new FormData(form);
    const payload = {
      email: String(formData.get("email") || "").trim(),
      password: String(formData.get("password") || ""),
    };

    submitButton.disabled = true;
    setFeedback("Entrando...", "");

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const responseBody = await response.text();
      let data = {};

      try {
        data = responseBody ? JSON.parse(responseBody) : {};
      } catch {
        data = {};
      }

      if (!response.ok) {
        throw new Error(normalizeError(data.error || `Erro ${response.status} ao entrar.`));
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      setFeedback("Login realizado com sucesso.", "success");
      window.location.href = "/home";
    } catch (error) {
      setFeedback(normalizeError(error.message || "Erro ao entrar."), "error");
    } finally {
      submitButton.disabled = false;
    }
  });
})();
