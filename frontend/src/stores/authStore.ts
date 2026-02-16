/**
 * Zustand store for authentication state
 */
import { create } from 'zustand';
import { User, AuthState } from '../types';

interface AuthStore extends AuthState {
  setUser: (user: User | null) => void;
  setAccessToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  accessToken: null,
  loading: true,
  error: null,

  setUser: (user) => set({ user }),
  setAccessToken: (token) => set({ accessToken: token }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, accessToken: null, error: null });
  },
}));
