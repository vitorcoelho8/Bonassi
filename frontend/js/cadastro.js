(function () {
  const setFeedback = (element, message, type) => {
    if (!element) {
      return;
    }

    element.textContent = message;
    element.classList.toggle("is-error", type === "error");
    element.classList.toggle("is-success", type === "success");
  };

  const toPayload = (form) => Object.fromEntries(new FormData(form).entries());

  const loginForm = document.querySelector("#login-form");
  const loginFeedback = document.querySelector("#login-feedback");

  loginForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!loginForm.reportValidity()) {
      return;
    }

    setFeedback(loginFeedback, "Entrando...", "");

    try {
      const data = await window.BolaoApi.login(toPayload(loginForm));
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "ranking.html";
    } catch (error) {
      setFeedback(loginFeedback, error.message || "Nao foi possivel entrar.", "error");
    }
  });

  const registerForm = document.querySelector("#register-form");
  const registerFeedback = document.querySelector("#register-feedback");

  registerForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!registerForm.reportValidity()) {
      return;
    }

    setFeedback(registerFeedback, "Salvando cadastro...", "");

    try {
      await window.BolaoApi.register(toPayload(registerForm));
      setFeedback(registerFeedback, "Cadastro realizado com sucesso.", "success");
      registerForm.reset();
    } catch (error) {
      setFeedback(registerFeedback, error.message || "Nao foi possivel cadastrar.", "error");
    }
  });
})();
