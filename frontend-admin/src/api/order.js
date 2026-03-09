import request from '@/utils/request'

export function getOrders(params) {
  return request({
    url: '/orders',
    method: 'get',
    params
  })
}

export function getOrder(id) {
  return request({
    url: `/orders/${id}`,
    method: 'get'
  })
}

export function refundOrder(id) {
  return request({
    url: `/orders/${id}/refund`,
    method: 'post'
  })
}
