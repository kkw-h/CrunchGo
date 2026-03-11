import { View, Text, Image } from '@tarojs/components'
import { useLoad } from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { productService } from '../../services/product.service'
import { Product, Category } from '../../types/product'
import './index.scss'

export default function Index () {
  const [categories, setCategories] = useState<Category[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

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
                  <View className='add-btn'><Text>+</Text></View>
                </View>
              </View>
            </View>
          ))
        )}
      </View>
    </View>
  )
}
