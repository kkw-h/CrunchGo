import Taro from '@tarojs/taro';

const BASE_URL = process.env.TARO_APP_API_URL || 'http://localhost:3000/api';

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  header?: any;
}

const request = async <T = any>(options: RequestOptions): Promise<T> => {
  const { url, method = 'GET', data, header = {} } = options;

  // Get token from storage
  const token = Taro.getStorageSync('token');
  if (token) {
    header['Authorization'] = `Bearer ${token}`;
  }

  // Content-Type default
  if (!header['Content-Type']) {
    header['Content-Type'] = 'application/json';
  }

  try {
    const response = await Taro.request({
      url: url.startsWith('http') ? url : `${BASE_URL}${url}`,
      method,
      data,
      header,
    });

    // Handle response status
    if (response.statusCode >= 200 && response.statusCode < 300) {
      // Assuming backend returns data in { code: 0, data: ..., message: ... } format or similar
      // Adjust based on actual backend response structure
      return response.data as T;
    } else if (response.statusCode === 401) {
      // Token expired or unauthorized
      Taro.removeStorageSync('token');
      Taro.navigateTo({ url: '/pages/login/index' });
      throw new Error('Unauthorized');
    } else {
      const errorMessage = response.data?.message || `Request failed with status ${response.statusCode}`;
      Taro.showToast({
        title: errorMessage,
        icon: 'none',
      });
      throw new Error(errorMessage);
    }
  } catch (error: any) {
    console.error('Request Error:', error);
    Taro.showToast({
      title: error.message || 'Network Error',
      icon: 'none',
    });
    throw error;
  }
};

export default request;
