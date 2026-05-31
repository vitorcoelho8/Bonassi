(function () {
  const getToken = () => localStorage.getItem("access_token") || "";

  const request = async (path, options = {}) => {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    const token = getToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(path, {
      ...options,
      headers,
    });
    const body = await response.text();
    const data = body ? JSON.parse(body) : {};

    if (!response.ok) {
      throw new Error(data.error || `Erro ${response.status}`);
    }

    return data;
  };

  window.BolaoApi = {
    login: (payload) => request("/api/participants/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    register: (payload) => request("/api/participants/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    ranking: () => request("/api/ranking/"),
    matches: () => request("/api/matches/"),
    predictions: () => request("/api/predictions/"),
    savePrediction: (payload) => request("/api/predictions/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    saveBonus: (payload) => request("/api/bonus/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    adminParticipants: () => request("/api/admin/participants"),
  };
})();
