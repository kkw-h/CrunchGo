<template>
  <view class="order-detail-page" v-if="order">
    <view class="status-card">
      <text class="status-text" :class="order.status.toLowerCase()">{{ order.status }}</text>
      <view v-if="order.pickupCode && ['PAID', 'PREPARING', 'COMPLETED'].includes(order.status) && order.type === 'PICKUP'" class="pickup-section" style="text-align: center; margin: 20px 0;">
        <text class="pickup-label" style="display: block; font-size: 14px; color: #666;">Pickup Code</text>
        <text class="pickup-code" style="font-size: 48px; font-weight: bold; color: #ff9900; display: block;">{{ order.pickupCode }}</text>
      </view>
    </view>

    <view class="detail-card">
      <text class="card-title">Order Items</text>
      <view class="item-row" v-for="(item, index) in order.items" :key="index">
        <view style="flex: 1">
          <text class="item-name">{{ item.name }}</text>
        </view>
        <text class="item-qty">x{{ item.quantity }}</text>
        <text class="item-price">¥{{ item.price }}</text>
      </view>
      <view class="total-row">
        <text>Total</text>
        <text>¥{{ order.totalAmount }}</text>
      </view>
    </view>

    <view class="detail-card">
      <text class="card-title">Order Info</text>
      <view class="item-row">
        <text style="color: #999">Order ID</text>
        <text>{{ order.id }}</text>
      </view>
      <view class="item-row">
        <text style="color: #999">Created Time</text>
        <text>{{ formatDate(order.createdAt) }}</text>
      </view>
    </view>

    <view class="action-bar" v-if="order.status === 'Pending'">
      <view class="btn cancel-btn" @tap="handleCancel">Cancel</view>
      <view class="btn pay-btn" @tap="handlePay">Pay Now</view>
    </view>
    <view class="action-bar" v-if="['PAID', 'PREPARING'].includes(order.status)">
      <view class="btn cancel-btn" @tap="handleRefund" style="width: 100%; text-align: center; background-color: #f5f5f5; color: #333;">Request Refund</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Taro, { useLoad } from '@tarojs/taro';
import { getOrderDetail, payOrder, cancelOrder, refundOrder } from '../../api';
import './detail.scss';

const order = ref<any>(null);
const orderId = ref('');

const fetchOrderDetail = async (id: string) => {
  try {
    Taro.showLoading({ title: 'Loading...' });
    const res: any = await getOrderDetail(id);
    order.value = res;
    Taro.hideLoading();
  } catch (error) {
    Taro.hideLoading();
    console.error(error);
    Taro.showToast({ title: 'Failed to load order', icon: 'none' });
  }
};

const handlePay = async () => {
  try {
    Taro.showLoading({ title: 'Processing...' });
    await payOrder(orderId.value);
    Taro.hideLoading();
    Taro.showToast({ title: 'Payment Successful', icon: 'success' });
    fetchOrderDetail(orderId.value); // Refresh
  } catch (error) {
    Taro.hideLoading();
    console.error(error);
    Taro.showToast({ title: 'Payment Failed', icon: 'none' });
  }
};

const handleCancel = async () => {
  try {
    const res = await Taro.showModal({
      title: 'Cancel Order',
      content: 'Are you sure you want to cancel this order?',
    });
    
    if (res.confirm) {
      Taro.showLoading({ title: 'Cancelling...' });
      await cancelOrder(orderId.value);
      Taro.hideLoading();
      Taro.showToast({ title: 'Order Cancelled', icon: 'none' });
      fetchOrderDetail(orderId.value); // Refresh
    }
  } catch (error) {
    Taro.hideLoading();
    console.error(error);
    Taro.showToast({ title: 'Failed to cancel', icon: 'none' });
  }
};

const handleRefund = async () => {
  try {
    const res = await Taro.showModal({
      title: 'Request Refund',
      content: 'Are you sure you want to request a refund?',
    });
    
    if (res.confirm) {
      Taro.showLoading({ title: 'Processing...' });
      await refundOrder(orderId.value);
      Taro.hideLoading();
      Taro.showToast({ title: 'Refund Requested', icon: 'success' });
      fetchOrderDetail(orderId.value); // Refresh
    }
  } catch (error) {
    Taro.hideLoading();
    console.error(error);
    Taro.showToast({ title: 'Failed to request refund', icon: 'none' });
  }
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleString();
};

useLoad((params) => {
  if (params.id) {
    orderId.value = params.id;
    fetchOrderDetail(params.id);
  }
});
</script>
