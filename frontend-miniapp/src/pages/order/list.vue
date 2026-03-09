<template>
  <view class="order-list-page">
    <view class="tabs">
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'All' }" 
        @tap="switchTab('All')"
      >All</view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'Pending' }" 
        @tap="switchTab('Pending')"
      >Pending</view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'Paid' }" 
        @tap="switchTab('Paid')"
      >Paid</view>
      <view 
        class="tab-item" 
        :class="{ active: currentTab === 'Completed' }" 
        @tap="switchTab('Completed')"
      >Completed</view>
    </view>

    <view class="order-list" v-if="orders.length > 0">
      <view class="order-card" v-for="order in orders" :key="order.id" @tap="goToDetail(order.id)">
        <view class="card-header">
          <text class="order-id">Order #{{ order.id.slice(-6) }}</text>
          <text class="order-status" :class="order.status.toLowerCase()">{{ order.status }}</text>
        </view>
        <view class="card-body">
          <view class="order-item" v-for="(item, index) in order.items.slice(0, 2)" :key="index">
            <text>{{ item.name }} x{{ item.quantity }}</text>
          </view>
          <view v-if="order.items.length > 2" style="font-size: 12px; color: #999;">...</view>
        </view>
        <view class="card-footer">
          <text class="total-amount">Total: ¥{{ order.totalAmount }}</text>
        </view>
      </view>
    </view>
    
    <view v-else class="empty-state">
      <text>No orders found.</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { getOrders } from '../../api';
import Taro, { useDidShow } from '@tarojs/taro';
import './list.scss';

const currentTab = ref('All');
const orders = ref<any[]>([]);

const fetchOrders = async () => {
  try {
    Taro.showLoading({ title: 'Loading...' });
    const status = currentTab.value === 'All' ? undefined : currentTab.value;
    const res: any = await getOrders(status);
    // Adjust based on backend response format
    orders.value = Array.isArray(res) ? res : (res.orders || []);
    Taro.hideLoading();
  } catch (error) {
    Taro.hideLoading();
    console.error(error);
    // Don't show error toast on initial load to avoid noise if just empty
    if (orders.value.length > 0) {
        Taro.showToast({ title: 'Failed to update orders', icon: 'none' });
    }
  }
};

const switchTab = (tab: string) => {
  currentTab.value = tab;
  fetchOrders();
};

const goToDetail = (id: string) => {
  Taro.navigateTo({
    url: `/pages/order/detail?id=${id}`
  });
};

useDidShow(() => {
  fetchOrders();
});
</script>
