<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Today Sales</span>
            </div>
          </template>
          <div class="card-value">¥{{ stats.todaySales }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Today Orders</span>
            </div>
          </template>
          <div class="card-value">{{ stats.todayOrders }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Top Product</span>
            </div>
          </template>
          <div class="card-value">{{ stats.topProduct?.name || 'N/A' }}</div>
          <div class="card-sub-value" v-if="stats.topProduct">
            Sales: {{ stats.topProduct.sales }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Top 5 Products</span>
            </div>
          </template>
          <el-table :data="stats.topProducts" style="width: 100%">
            <el-table-column prop="name" label="Product Name" />
            <el-table-column prop="sales" label="Sales" width="100" />
            <el-table-column label="Popularity" width="200">
              <template #default="scope">
                <el-progress :percentage="calculatePercentage(scope.row.sales)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Refund Requests</span>
              <el-button link type="primary" @click="$router.push('/orders?status=refund_requested')">View All</el-button>
            </div>
          </template>
          <el-table :data="refundRequests" style="width: 100%" v-loading="loadingRefunds">
            <el-table-column prop="id" label="Order ID" width="100" />
            <el-table-column prop="total_amount" label="Amount" width="100">
              <template #default="scope">¥{{ scope.row.total_amount }}</template>
            </el-table-column>
            <el-table-column prop="status" label="Status">
               <template #default="scope">
                 <el-tag type="warning">{{ scope.row.status }}</el-tag>
               </template>
            </el-table-column>
            <el-table-column label="Action" width="100">
              <template #default="scope">
                <el-button link type="primary" @click="$router.push(`/orders/${scope.row.id}`)">Detail</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '@/api/stats'
import { getOrders } from '@/api/order'

const stats = ref({
  todaySales: 0,
  todayOrders: 0,
  topProduct: null,
  topProducts: []
})

const refundRequests = ref([])
const loadingRefunds = ref(false)

const calculatePercentage = (sales) => {
  if (!stats.value.topProducts.length) return 0
  const maxSales = Math.max(...stats.value.topProducts.map(p => p.sales))
  return maxSales ? Math.round((sales / maxSales) * 100) : 0
}

const fetchStats = async () => {
  try {
    const res = await getDashboardStats()
    // Assuming API returns data in res.data or directly res if interceptor handles it
    // Adjust based on your request utility
    stats.value = res.data || res 
  } catch (error) {
    console.error('Failed to fetch dashboard stats', error)
    // Mock data for demonstration if API fails or not implemented
    stats.value = {
      todaySales: 12580,
      todayOrders: 45,
      topProduct: { name: 'Wireless Headphones', sales: 120 },
      topProducts: [
        { name: 'Wireless Headphones', sales: 120 },
        { name: 'Smart Watch', sales: 98 },
        { name: 'Bluetooth Speaker', sales: 85 },
        { name: 'Laptop Stand', sales: 60 },
        { name: 'USB-C Cable', sales: 45 }
      ]
    }
  }
}

const fetchRefundRequests = async () => {
  loadingRefunds.value = true
  try {
    const res = await getOrders({ status: 'refund_requested', limit: 5 })
    const data = res.data || res
    refundRequests.value = Array.isArray(data) ? data : (data.items || [])
  } catch (error) {
    console.error('Failed to fetch refund requests', error)
  } finally {
    loadingRefunds.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchRefundRequests()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}
.mt-20 {
  margin-top: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.card-sub-value {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
