import axios, { AxiosError } from "axios";
import { useAuthStore } from "@shared/stores/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const status = error.response?.status ?? 0;
    const detail = error.response?.data?.detail ?? error.message;

    if (status === 401) {
      useAuthStore.getState().clear();
      if (location.pathname !== "/login") {
        location.href = "/login";
      }
      return Promise.reject(error);
    }

    if (status >= 500) {
      window.dispatchEvent(
        new CustomEvent("toast", {
          detail: { type: "error", message: "Error del servidor. Intentá de nuevo en unos minutos." },
        })
      );
      return Promise.reject(error);
    }

    if (status >= 400) {
      window.dispatchEvent(
        new CustomEvent("toast", { detail: { type: "warning", message: detail } })
      );
    }

    return Promise.reject(error);
  }
);
