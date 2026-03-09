<template>
  <view class="landing-page">
    <view class="logo">CrunchGo</view>
    <view class="slogan">Delicious Food, Delivered Fast!</view>
    <view class="start-btn" @tap="goToMenu">
      Start Ordering
    </view>
  </view>
</template>

<script setup lang="ts">
import Taro from '@tarojs/taro'
import './index.scss'

const goToMenu = () => {
  Taro.navigateTo({
    url: '/pages/menu/index'
  })
}
</script>
