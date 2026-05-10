import { create } from "zustand";
import { persist } from "zustand/middleware";

type Profile = { name: string; phone: string | null };

type UserState = {
  profile: Profile | null;
  setProfile: (profile: Profile) => void;
  clear: () => void;
};

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      profile: null,
      setProfile: (profile) => set({ profile }),
      clear: () => set({ profile: null }),
    }),
    { name: "foodstore.user" }
  )
);
