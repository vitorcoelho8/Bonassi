(function () {
  const getToken = () => localStorage.getItem("access_token") || "";
  const clearAuth = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  };
  const isLoginPage = () => {
    const page = window.location.pathname.split("/").pop() || "index.html";
    return page === "index.html" || page === "login";
  };

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
      if (response.status === 401) {
        clearAuth();
        if (!isLoginPage()) {
          window.location.href = "/login";
        }
      }

      throw new Error(data.error || `Erro ${response.status}`);
    }

    return data;
  };

  window.BolaoApi = {
    login: (payload) => request("/api/participants/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    createUser: (payload) => request("/api/users", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    participants: () => request("/api/participants"),
    participant: (id) => request(`/api/participants/${encodeURIComponent(id)}`),
    searchParticipants: (term) => request(`/api/participants/search?term=${encodeURIComponent(term)}`),
    users: () => request("/api/users"),
    user: (id) => request(`/api/users/${encodeURIComponent(id)}`),
    searchUsers: (term) => request(`/api/users/search?term=${encodeURIComponent(term)}`),
    ranking: () => request("/api/ranking/"),
    matches: () => request("/api/matches/"),
    nextMatch: () => request("/api/matches/next"),
    matchPhases: () => request("/api/admin/matches/phases"),
    createNextBrazilMatch: (payload) => request("/api/admin/matches/next-brazil-match", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    saveMatchResult: (matchId, payload) => request(`/api/admin/matches/${encodeURIComponent(matchId)}/result`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
    predictions: () => request("/api/predictions/"),
    participantPredictions: (participantId) => request(`/api/predictions/participant/${encodeURIComponent(participantId)}`),
    savePrediction: (payload) => request("/api/predictions/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    updatePrediction: (predictionId, payload) => request(`/api/predictions/${encodeURIComponent(predictionId)}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
    saveBonus: (payload) => request("/api/bonus/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    participantBonus: (participantId) => request(`/api/bonus/participant/${encodeURIComponent(participantId)}`),
    pendingBonus: () => request("/api/admin/bonus/pending"),
    approveBonus: (bonusId) => request(`/api/admin/bonus/${encodeURIComponent(bonusId)}/approve`, {
      method: "PATCH",
    }),
    rejectBonus: (bonusId, payload = {}) => request(`/api/admin/bonus/${encodeURIComponent(bonusId)}/reject`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
    adminParticipants: () => request("/api/participants"),
    me: () => request("/api/participants/me"),
  };
})();
