import { useCallback } from 'react';
import { useAuth as useAuthContext } from '../contexts/AuthContext';
import { validateLoginForm, validateRegisterForm } from '../utils/validators';
import { LoginData, RegisterData } from '../types/userTypes';

export const useAuth = () => {
  const authContext = useAuthContext();

  const login = useCallback((data: LoginData) => {
    const validation = validateLoginForm(data.username, data.password);
    if (!validation.isValid) {
      authContext.setError(validation.errors[0]);
      return;
    }
    authContext.login(data);
  }, [authContext]);

  const register = useCallback((data: RegisterData) => {
    const validation = validateRegisterForm(
      data.username, 
      data.email, 
      data.password, 
      data.password // Using password as confirmPassword for simplicity
    );
    if (!validation.isValid) {
      authContext.setError(validation.errors[0]);
      return;
    }
    authContext.register(data);
  }, [authContext]);

  const logout = useCallback(() => {
    authContext.logout();
  }, [authContext]);

  const clearError = useCallback(() => {
    authContext.clearError();
  }, [authContext]);

  return {
    ...authContext,
    login,
    register,
    logout,
    clearError
  };
}; 