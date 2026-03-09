import { defineStore } from 'pinia';
import Taro from '@tarojs/taro';
import { ref } from 'vue';
import { login as apiLogin } from '../api';

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(Taro.getStorageSync('token') || null);
  const userInfo = ref<any>(Taro.getStorageSync('userInfo') || null);

  const login = async () => {
    try {
      const { code } = await Taro.login();
      if (code) {
        const res = await apiLogin(code);
        // 假设后端返回的数据结构包含 token 和 user 信息
        // 根据实际后端接口调整
        const { token: newToken, user } = res;
        
        if (newToken) {
          token.value = newToken;
          Taro.setStorageSync('token', newToken);
        }
        
        if (user) {
          userInfo.value = user;
          Taro.setStorageSync('userInfo', user);
        }
        
        return res;
      } else {
        throw new Error('Taro login failed: code is missing');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    token.value = null;
    userInfo.value = null;
    Taro.removeStorageSync('token');
    Taro.removeStorageSync('userInfo');
    // 可以根据需要跳转到登录页
    Taro.reLaunch({ url: '/pages/index/index' });
  };

  const setUserInfo = (info: any) => {
    userInfo.value = info;
    Taro.setStorageSync('userInfo', info);
  };

  return {
    token,
    userInfo,
    login,
    logout,
    setUserInfo,
  };
});
