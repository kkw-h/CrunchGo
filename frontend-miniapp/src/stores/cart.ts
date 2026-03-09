import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  image?: string;
  options?: Record<string, any>;
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([]);

  const totalQuantity = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0);
  });

  const totalPrice = computed(() => {
    return items.value.reduce((total, item) => total + item.price * item.quantity, 0);
  });

  const addItem = (product: Omit<CartItem, 'quantity'>) => {
    const existingItem = items.value.find(item => item.id === product.id);
    if (existingItem) {
      existingItem.quantity++;
    } else {
      items.value.push({ ...product, quantity: 1 });
    }
  };

  const removeItem = (productId: string) => {
    const index = items.value.findIndex(item => item.id === productId);
    if (index !== -1) {
      const item = items.value[index];
      if (item.quantity > 1) {
        item.quantity--;
      } else {
        items.value.splice(index, 1);
      }
    }
  };

  const clearCart = () => {
    items.value = [];
  };

  return {
    items,
    totalQuantity,
    totalPrice,
    addItem,
    removeItem,
    clearCart,
  };
});
