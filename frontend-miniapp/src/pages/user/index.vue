<template>
  <view class="user-page">
    <view class="header">
      <image class="avatar" src="https://api.dicebear.com/9.x/avataaars/svg?seed=Felix" mode="aspectFill" />
      <view class="info">
        <text class="nickname">User</text>
      </view>
    </view>

    <view class="points-card">
      <text class="label">My Points</text>
      <text class="balance">{{ points }}</text>
    </view>

    <view class="history-list">
      <view class="list-header">Points History</view>
      <view class="history-item" v-for="(item, index) in history" :key="index">
        <view class="left">
          <text class="reason">{{ item.reason }}</text>
          <text class="time">{{ formatDate(item.createdAt) }}</text>
        </view>
        <text class="amount" :class="item.amount > 0 ? 'positive' : 'negative'">
          {{ item.amount > 0 ? '+' : '' }}{{ item.amount }}
        </text>
      </view>
      <view v-if="history.length === 0" style="padding: 20px; text-align: center; color: #999;">
        No history yet
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Taro, { useDidShow } from '@tarojs/taro';
import { getUserPoints } from '../../api';
import './index.scss';

const points = ref(0);
const history = ref<any[]>([]);

const fetchPoints = async () => {
  try {
    const res: any = await getUserPoints();
    // Assuming API returns { balance: number, history: array }
    // If it returns just points, adjust accordingly. 
    // Based on typical implementation:
    if (res) {
        points.value = res.balance || 0;
        history.value = res.history || [];
    }
  } catch (error) {
    console.error('Failed to fetch points', error);
  }
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

useDidShow(() => {
  fetchPoints();
});
</script>
