import { create } from "zustand";
import { persist } from "zustand/middleware";

type Tokens = { accessToken: string; refreshToken: string };
type AuthUser = { id: string; email: string; roles: string[] };

type AuthState = {
  user: AuthUser | null;
  tokens: Tokens | null;
  setSession: (user: AuthUser, tokens: Tokens) => void;
  clear: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      setSession: (user, tokens) => set({ user, tokens }),
      clear: () => set({ user: null, tokens: null }),
    }),
    { name: "foodstore.auth" }
  )
);
