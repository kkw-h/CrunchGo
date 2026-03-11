import { View, Text, Button, ScrollView } from '@tarojs/components'
import { useLoad, showToast } from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { orderService, Order } from '../../services/order.service'
import './index.scss'

export default function MerchantIndex () {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)

  const fetchOrders = async () => {
    try {
      const data = await orderService.getOrders()
      setOrders(data)
    } catch (error) {
      console.error('Failed to load orders', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrders()
    // Simple polling for new orders every 10 seconds
    const interval = setInterval(fetchOrders, 10000)
    return () => clearInterval(interval)
  }, [])

  const handleUpdateStatus = async (id: string, newStatus: string) => {
    try {
      await orderService.updateOrderStatus(id, newStatus)
      showToast({ title: '状态已更新', icon: 'success' })
      fetchOrders()
    } catch (error) {
      showToast({ title: '更新失败', icon: 'none' })
    }
  }

  const getNextStatus = (currentStatus: string) => {
    switch (currentStatus) {
      case 'PAID': return 'PREPARING';
      case 'PREPARING': return 'READY';
      case 'READY': return 'COMPLETED';
      default: return null;
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'PENDING': return '待支付';
      case 'PAID': return '待制作';
      case 'PREPARING': return '制作中';
      case 'READY': return '请取餐';
      case 'COMPLETED': return '已完成';
      case 'CANCELLED': return '已取消';
      default: return status;
    }
  }

  return (
    <View className='merchant-index'>
      <View className='header'>
        <Text className='title'>商家接单看板</Text>
        <Button size='mini' onClick={fetchOrders}>刷新</Button>
      </View>

      <ScrollView scrollY className='order-list'>
        {orders.map(order => (
          <View key={order.id} className={`order-card ${order.status.toLowerCase()}`}>
            <View className='card-header'>
              <Text className='order-number'>{order.orderNumber}</Text>
              <Text className='order-time'>{new Date(order.createdAt).toLocaleTimeString()}</Text>
            </View>
            
            <View className='card-body'>
              {order.items?.map((item, idx) => (
                <View key={idx} className='order-item'>
                  <Text className='item-name'>{item.productName} x{item.quantity}</Text>
                  {item.options && (
                    <Text className='item-options'>
                      {Object.values(item.options).join(', ')}
                    </Text>
                  )}
                </View>
              ))}
            </View>

            <View className='card-footer'>
              <Text className='order-status'>{getStatusText(order.status)}</Text>
              {getNextStatus(order.status) && (
                <Button 
                  className='action-btn' 
                  onClick={() => handleUpdateStatus(order.id, getNextStatus(order.status)!)}
                >
                  {getStatusText(getNextStatus(order.status)!)}
                </Button>
              )}
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  )
}
