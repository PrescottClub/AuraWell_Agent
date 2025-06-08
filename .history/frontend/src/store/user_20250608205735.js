import { defineStore } from 'pinia';
import { login, getUserInfo } from '@/api/user';

export const useUserStore = defineStore('user', {
    state: () => ({
        token: localStorage.getItem('token') || '',
        userInfo: null,
        permissions: []
    }),
    
    getters: {
        isLoggedIn: (state) => !!state.token,
        hasPermission: (state) => (permission) => state.permissions.includes(permission)
    },
    
    actions: {
        async login(username, password) {
            try {
                const res = await login({ username, password });
                this.token = res.data.token;
                this.userInfo = res.data.userInfo;
                localStorage.setItem('token', res.data.token);
                return res;
            } catch (error) {
                throw error;
            }
        },
        
        async getUserInfo() {
            try {
                const res = await getUserInfo();
                this.userInfo = res.data;
                this.permissions = res.data.permissions;
                return res;
            } catch (error) {
                throw error;
            }
        },
        
        logout() {
            this.token = '';
            this.userInfo = null;
            this.permissions = [];
            localStorage.removeItem('token');
        }
    }
}); 