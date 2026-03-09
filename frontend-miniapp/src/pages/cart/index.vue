<template>
  <view class="cart-page">
    <view v-if="cartStore.items.length > 0">
      <view class="cart-item" v-for="item in cartStore.items" :key="item.id">
        <image class="item-image" :src="item.image || 'https://via.placeholder.com/80'" mode="aspectFill" />
        <view class="item-info">
          <text class="item-name">{{ item.name }}</text>
          <view class="item-bottom">
             <text class="item-price">¥{{ item.price }}</text>
          </view>
        </view>
        <view class="item-controls">
          <view class="btn minus" @tap="decreaseQuantity(item)">-</view>
          <text class="quantity">{{ item.quantity }}</text>
          <view class="btn plus" @tap="increaseQuantity(item)">+</view>
        </view>
      </view>

      <view class="cart-footer">
        <view class="total-info">
          <text class="total-label">Total:</text>
          <text class="total-price">¥{{ cartStore.totalPrice.toFixed(2) }}</text>
        </view>
        <view class="checkout-btn" @tap="handleCheckout">Checkout</view>
      </view>
    </view>
    
    <view v-else class="empty-cart">
      <text>Your cart is empty.</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { useCartStore } from '../../stores/cart';
import { createOrder } from '../../api';
import Taro from '@tarojs/taro';
import './index.scss';

const cartStore = useCartStore();

const increaseQuantity = (item: any) => {
  cartStore.addItem({ ...item });
};

const decreaseQuantity = (item: any) => {
  cartStore.removeItem(item.id);
};

const handleCheckout = async () => {
  if (cartStore.items.length === 0) return;

  try {
    Taro.showLoading({ title: 'Processing...' });
    
    // Create order payload
    const orderData = {
      items: cartStore.items.map(item => ({
        productId: item.id,
        quantity: item.quantity,
        price: item.price,
        name: item.name
      })),
      totalAmount: cartStore.totalPrice
    };

    const res: any = await createOrder(orderData);
    
    Taro.hideLoading();
    
    // Assuming res is the order object or contains the id
    const orderId = res.id || res.order?.id;

    if (orderId) {
      cartStore.clearCart();
      Taro.navigateTo({
        url: `/pages/order/detail?id=${orderId}`
      });
    } else {
      Taro.showToast({ title: 'Failed to create order', icon: 'none' });
    }
  } catch (error) {
    Taro.hideLoading();
    console.error(error);
    Taro.showToast({ title: 'Error creating order', icon: 'none' });
  }
};
</script>
