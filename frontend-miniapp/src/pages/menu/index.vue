<template>
  <view class="menu-container">
    <!-- Left Sidebar: Categories -->
    <scroll-view class="left-sidebar" scroll-y>
      <view
        v-for="category in categories"
        :key="category.id"
        class="category-item"
        :class="{ active: currentCategoryId === category.id }"
        @tap="handleCategoryClick(category.id)"
      >
        {{ category.name }}
      </view>
    </scroll-view>

    <!-- Right Content: Products -->
    <scroll-view class="right-content" scroll-y>
      <view class="category-title" v-if="currentCategoryName">
        {{ currentCategoryName }}
      </view>
      <view class="product-list">
        <view
          v-for="product in products"
          :key="product.id"
          class="product-item"
          @tap="openSkuModal(product)"
        >
          <image class="product-image" :src="product.image || 'https://via.placeholder.com/80'" mode="aspectFill" />
          <view class="product-info">
            <text class="product-name">{{ product.name }}</text>
            <text class="product-desc">{{ product.description }}</text>
            <view class="product-bottom">
              <text class="product-price">¥{{ product.price }}</text>
              <view class="add-btn">Select</view>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- SKU Selection Modal -->
    <view v-if="showModal" class="sku-modal" @tap="closeModal">
      <view class="modal-content" @tap.stop>
        <view class="close-btn" @tap="closeModal">×</view>
        <view class="modal-title">{{ selectedProduct?.name }}</view>
        
        <view class="sku-options" v-if="selectedProduct?.options">
           <!-- Simple implementation for options -->
           <view v-for="(values, key) in selectedProduct.options" :key="key" class="option-group">
             <text class="option-title">{{ key }}</text>
             <view class="option-values">
               <text 
                 v-for="val in values" 
                 :key="val" 
                 class="option-value"
                 :class="{ selected: selectedOptions[key] === val }"
                 @tap="selectOption(key, val)"
               >
                 {{ val }}
               </text>
             </view>
           </view>
        </view>

        <view class="modal-footer">
          <text class="price">¥{{ selectedProduct?.price }}</text>
          <view class="confirm-btn" @tap="addToCart">Add to Cart</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCartStore } from '../../stores/cart'
import { getCategories, getProducts } from '../../api'
import './index.scss'

// Types
interface Category {
  id: string
  name: string
}

interface Product {
  id: string
  categoryId: string
  name: string
  description: string
  price: number
  image?: string
  options?: Record<string, string[]>
}

// State
const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const currentCategoryId = ref<string>('')
const showModal = ref(false)
const selectedProduct = ref<Product | null>(null)
const selectedOptions = ref<Record<string, string>>({})

const cartStore = useCartStore()

// Computed
const currentCategoryName = computed(() => {
  const category = categories.value.find(c => c.id === currentCategoryId.value)
  return category ? category.name : ''
})

// Methods
const fetchCategories = async () => {
  try {
    const res: any = await getCategories()
    // Handle different response structures
    const data = res.data || res
    if (Array.isArray(data)) {
      categories.value = data
      if (categories.value.length > 0) {
        currentCategoryId.value = categories.value[0].id
        fetchProducts(currentCategoryId.value)
      }
    }
  } catch (error) {
    console.error('Failed to fetch categories', error)
    // Fallback data for demo purposes if API fails
    categories.value = [
      { id: '1', name: 'Burgers' },
      { id: '2', name: 'Drinks' },
      { id: '3', name: 'Sides' }
    ]
    currentCategoryId.value = '1'
    fetchProducts('1')
  }
}

const fetchProducts = async (categoryId: string) => {
  try {
    const res: any = await getProducts(categoryId)
    const data = res.data || res
    if (Array.isArray(data)) {
      products.value = data
    } else {
        // Fallback
        products.value = getMockProducts(categoryId)
    }
  } catch (error) {
    console.error('Failed to fetch products', error)
    products.value = getMockProducts(categoryId)
  }
}

const getMockProducts = (categoryId: string): Product[] => {
    if (categoryId === '1') {
        return [
            { id: '101', categoryId: '1', name: 'Classic Burger', description: 'Beef patty, lettuce, tomato, cheese', price: 12.99, image: '', options: { Size: ['Regular', 'Large'], Spiciness: ['Mild', 'Hot'] } },
            { id: '102', categoryId: '1', name: 'Cheese Burger', description: 'Double cheese, beef patty, pickles', price: 14.99, image: '' }
        ]
    } else if (categoryId === '2') {
        return [
            { id: '201', categoryId: '2', name: 'Cola', description: 'Ice cold cola', price: 2.99, image: '' },
            { id: '202', categoryId: '2', name: 'Lemonade', description: 'Freshly squeezed', price: 3.50, image: '' }
        ]
    }
    return []
}

const handleCategoryClick = (id: string) => {
  currentCategoryId.value = id
  fetchProducts(id)
}

const openSkuModal = (product: Product) => {
  selectedProduct.value = product
  selectedOptions.value = {}
  // Default select first options
  if (product.options) {
      Object.keys(product.options).forEach(key => {
          if (product.options && product.options[key].length > 0) {
              selectedOptions.value[key] = product.options[key][0]
          }
      })
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedProduct.value = null
}

const selectOption = (key: string, value: string) => {
    selectedOptions.value[key] = value
}

const addToCart = () => {
  if (selectedProduct.value) {
    cartStore.addItem({
      id: selectedProduct.value.id,
      name: selectedProduct.value.name,
      price: selectedProduct.value.price,
      image: selectedProduct.value.image,
      options: { ...selectedOptions.value }
    })
    
    // Show feedback
    // In Taro/uni-app we might use showToast, here we assume it's available or just console log
    console.log('Added to cart:', selectedProduct.value.name)
    closeModal()
  }
}

// Lifecycle
onMounted(() => {
  fetchCategories()
})
</script>
