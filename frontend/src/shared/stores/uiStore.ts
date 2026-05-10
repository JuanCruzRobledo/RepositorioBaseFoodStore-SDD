import { create } from "zustand";
import { persist } from "zustand/middleware";

type UiState = {
  theme: "light" | "dark";
  modalOpen: string | null;
  setTheme: (theme: "light" | "dark") => void;
  openModal: (id: string) => void;
  closeModal: () => void;
};

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      theme: "light",
      modalOpen: null,
      setTheme: (theme) => set({ theme }),
      openModal: (modalOpen) => set({ modalOpen }),
      closeModal: () => set({ modalOpen: null }),
    }),
    { name: "foodstore.ui" }
  )
);
