import Taro from '@tarojs/taro';

const API_BASE_URL = 'http://localhost:3000'; // Should be configured in env

export interface CreateOrderItemDto {
  productId: number;
  quantity: number;
  options?: any;
}

export interface CreateOrderDto {
  items: CreateOrderItemDto[];
}

export interface Order {
  id: string;
  orderNumber: string;
  totalAmount: number;
  status: string;
  createdAt: string;
  items?: {
    productName: string;
    quantity: number;
    options: any;
  }[];
}

export const orderService = {
  async createOrder(data: CreateOrderDto): Promise<Order> {
    try {
      const response = await Taro.request({
        url: `${API_BASE_URL}/orders`,
        method: 'POST',
        data,
      });
      if (response.statusCode >= 400) {
        throw new Error(response.data.message || 'Create order failed');
      }
      return response.data;
    } catch (error) {
      console.error('Failed to create order:', error);
      throw error;
    }
  },

  async getOrders(): Promise<Order[]> {
    try {
      const response = await Taro.request({
        url: `${API_BASE_URL}/orders`,
        method: 'GET',
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      throw error;
    }
  },

  async updateOrderStatus(id: string, status: string): Promise<Order> {
    try {
      const response = await Taro.request({
        url: `${API_BASE_URL}/orders/${id}/status`,
        method: 'PATCH',
        data: { status },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update order status:', error);
      throw error;
    }
  },
};
