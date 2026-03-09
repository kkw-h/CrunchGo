import request from '../utils/request';

// Auth
export const login = (code: string) => {
  return request({
    url: '/auth/login',
    method: 'POST',
    data: { code },
  });
};

// Menu
export const getCategories = () => {
  return request({
    url: '/categories',
    method: 'GET',
  });
};

export const getProducts = (categoryId?: string) => {
  return request({
    url: '/products',
    method: 'GET',
    data: { categoryId },
  });
};

// Order
export const createOrder = (orderData: any) => {
  return request({
    url: '/orders',
    method: 'POST',
    data: orderData,
  });
};

export const getOrders = (status?: string) => {
  return request({
    url: '/orders',
    method: 'GET',
    data: { status },
  });
};

export const getOrderDetail = (id: string) => {
  return request({
    url: `/orders/${id}`,
    method: 'GET',
  });
};

export const payOrder = (id: string) => {
  return request({
    url: `/orders/${id}/pay`,
    method: 'POST',
  });
};

export const cancelOrder = (id: string) => {
  return request({
    url: `/orders/${id}/cancel`,
    method: 'POST',
  });
};

export const refundOrder = (id: string) => {
  return request({
    url: `/orders/${id}/refund`,
    method: 'POST',
  });
};

// User
export const getUserPoints = () => {
  return request({
    url: '/user/points',
    method: 'GET',
  });
};
