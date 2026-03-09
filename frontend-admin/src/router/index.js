import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/layout/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: 'Dashboard' }
      },
      {
        path: 'products',
        name: 'ProductList',
        component: () => import('@/views/product/List.vue'),
        meta: { title: 'Products' }
      },
      {
        path: 'products/create',
        name: 'ProductCreate',
        component: () => import('@/views/product/Form.vue'),
        meta: { title: 'Create Product' }
      },
      {
        path: 'products/:id/edit',
        name: 'ProductEdit',
        component: () => import('@/views/product/Form.vue'),
        meta: { title: 'Edit Product' }
      },
      {
        path: 'orders',
        name: 'OrderList',
        component: () => import('@/views/order/List.vue'),
        meta: { title: 'Orders' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
