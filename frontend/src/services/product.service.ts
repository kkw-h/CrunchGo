import Taro from '@tarojs/taro';
import { Product, Category } from '../types/product';

const API_BASE_URL = 'http://localhost:3000'; // Should be configured in env

export const productService = {
  async getProducts(): Promise<Product[]> {
    try {
      const response = await Taro.request({
        url: `${API_BASE_URL}/products`,
        method: 'GET',
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch products:', error);
      throw error;
    }
  },

  async getCategories(): Promise<Category[]> {
    try {
      const response = await Taro.request({
        url: `${API_BASE_URL}/categories`,
        method: 'GET',
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  },
};
