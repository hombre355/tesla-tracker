import { create } from 'zustand'

interface AuthState {
  authenticated: boolean
  vehicleCount: number
  setAuth: (authenticated: boolean, vehicleCount: number) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  authenticated: false,
  vehicleCount: 0,
  setAuth: (authenticated, vehicleCount) => set({ authenticated, vehicleCount }),
}))
