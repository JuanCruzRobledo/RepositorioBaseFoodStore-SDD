import { create } from "zustand";
import { persist } from "zustand/middleware";

export type CartItem = {
  productId: string;
  name: string;
  unitPrice: number;
  quantity: number;
  excludedIngredientIds: string[];
};

type CartState = {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  setQuantity: (productId: string, qty: number) => void;
  remove: (productId: string) => void;
  clear: () => void;
  total: () => number;
};

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      addItem: (item) =>
        set((s) => {
          const existing = s.items.find((i) => i.productId === item.productId);
          if (existing) {
            return {
              items: s.items.map((i) =>
                i.productId === item.productId
                  ? { ...i, quantity: i.quantity + item.quantity }
                  : i
              ),
            };
          }
          return { items: [...s.items, item] };
        }),
      setQuantity: (productId, qty) =>
        set((s) => ({
          items: qty <= 0
            ? s.items.filter((i) => i.productId !== productId)
            : s.items.map((i) => (i.productId === productId ? { ...i, quantity: qty } : i)),
        })),
      remove: (productId) =>
        set((s) => ({ items: s.items.filter((i) => i.productId !== productId) })),
      clear: () => set({ items: [] }),
      total: () => get().items.reduce((acc, i) => acc + i.unitPrice * i.quantity, 0),
    }),
    { name: "foodstore.cart" }
  )
);
