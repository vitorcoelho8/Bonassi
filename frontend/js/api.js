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
    createParticipant: (payload) => request("/api/participants", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    participants: () => request("/api/participants"),
    participant: (id) => request(`/api/participants/${encodeURIComponent(id)}`),
    searchParticipants: (term) => request(`/api/participants/search?term=${encodeURIComponent(term)}`),
    ranking: () => request("/api/ranking/"),
    matches: () => request("/api/matches/"),
    nextMatch: () => request("/api/matches/next"),
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
    adminParticipants: () => request("/api/participants"),
  };
})();
