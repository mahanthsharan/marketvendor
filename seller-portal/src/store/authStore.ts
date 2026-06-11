import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  seller: any | null;
  setAuth: (token: string, seller: any) => void;
  logout: () => void;
}

const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      token: null,
      seller: null,
      setAuth: (token: string, seller: any) =>
        set({
          token,
          seller,
          isAuthenticated: true,
        }),
      logout: () =>
        set({
          token: null,
          seller: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'auth-storage',
    }
  )
);

export default useAuthStore;
