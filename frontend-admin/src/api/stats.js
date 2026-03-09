import request from '@/utils/request'

export function getDashboardStats() {
  return request({
    url: '/stats/dashboard',
    method: 'get'
  })
}
