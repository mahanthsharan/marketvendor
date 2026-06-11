import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartState {
  items: any[];
  addToCart: (product: any) => void;
  removeFromCart: (index: number) => void;
  clearCart: () => void;
}

const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      addToCart: (product: any) =>
        set((state) => ({
          items: [...state.items, product],
        })),
      removeFromCart: (index: number) =>
        set((state) => ({
          items: state.items.filter((_, i) => i !== index),
        })),
      clearCart: () =>
        set({
          items: [],
        }),
    }),
    {
      name: 'cart-storage',
    }
  )
);

export default useCartStore;
