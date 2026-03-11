import { View, Text, Image } from '@tarojs/components'
import { useLoad, showToast, showLoading, hideLoading } from '@tarojs/taro'
import { useState, useEffect, useContext } from 'react'
import { productService } from '../../services/product.service'
import { orderService } from '../../services/order.service'
import { Product, Category } from '../../types/product'
import { CartContext } from '../../context/CartContext'
import './index.scss'

export default function Index () {
  const [categories, setCategories] = useState<Category[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const { items, addToCart, totalAmount, totalQuantity, clearCart } = useContext(CartContext)

  useLoad(() => {
    console.log('Page loaded.')
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cats, prods] = await Promise.all([
          productService.getCategories(),
          productService.getProducts()
        ])
        setCategories(cats)
        setProducts(prods)
      } catch (error) {
        console.error('Failed to load data', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleAddToCart = (product: Product) => {
    addToCart(product)
    showToast({ title: '已加入购物车', icon: 'success', duration: 1000 })
  }

  const handleCheckout = async () => {
    if (items.length === 0) return

    showLoading({ title: '正在下单...' })
    try {
      // Simulate payment delay
      await new Promise(resolve => setTimeout(resolve, 1000))

      const orderData = {
        items: items.map(item => ({
          productId: item.product.id,
          quantity: item.quantity,
          options: item.options
        }))
      }
      
      const order = await orderService.createOrder(orderData)
      
      hideLoading()
      showToast({ title: `支付成功! 取餐号: ${order.orderNumber}`, icon: 'success', duration: 3000 })
      clearCart()
      
      // TODO: Navigate to Order Detail or Success Page
      
    } catch (error: any) {
      hideLoading()
      showToast({ title: error.message || '下单失败', icon: 'none' })
    }
  }

  if (loading) {
    return <View className='loading'><Text>Loading...</Text></View>
  }

  return (
    <View className='index'>
      <View className='header'>
        <Text className='title'>CrunchGo Menu</Text>
      </View>
      
      <View className='categories'>
        {categories.map(cat => (
          <View key={cat.id} className='category-tag'>
            <Text>{cat.name}</Text>
          </View>
        ))}
      </View>

      <View className='product-list'>
        {products.length === 0 ? (
          <Text className='empty-text'>暂无商品</Text>
        ) : (
          products.map(prod => (
            <View key={prod.id} className='product-card'>
              {prod.image && <Image src={prod.image} className='product-image' />}
              <View className='product-info'>
                <Text className='product-name'>{prod.name}</Text>
                <Text className='product-desc'>{prod.description}</Text>
                <View className='product-bottom'>
                  <Text className='product-price'>¥{prod.price}</Text>
                  <View className='add-btn' onClick={() => handleAddToCart(prod)}><Text>+</Text></View>
                </View>
              </View>
            </View>
          ))
        )}
      </View>

      {/* Cart Summary Bar */}
      {totalQuantity > 0 && (
        <View className='cart-bar'>
          <View className='cart-info'>
            <View className='cart-badge'>
              <Text>{totalQuantity}</Text>
            </View>
            <Text className='cart-total'>¥{totalAmount.toFixed(2)}</Text>
          </View>
          <View className='checkout-btn' onClick={handleCheckout}>
            <Text>去结算</Text>
          </View>
        </View>
      )}
    </View>
  )
}

