<template>
  <div class="order-list">
    <h2>Orders</h2>
    <div class="filter-container">
      <el-select v-model="statusFilter" placeholder="Filter by Status" clearable @change="fetchOrders">
        <el-option label="Pending" value="pending" />
        <el-option label="Paid" value="paid" />
        <el-option label="Shipped" value="shipped" />
        <el-option label="Completed" value="completed" />
        <el-option label="Refunded" value="refunded" />
        <el-option label="Cancelled" value="cancelled" />
      </el-select>
      <el-button type="primary" @click="fetchOrders">Search</el-button>
    </div>

    <el-table :data="orders" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user_id" label="User ID" width="100" />
      <el-table-column prop="total_amount" label="Amount" width="120">
        <template #default="scope">
          ¥{{ scope.row.total_amount }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="Status" width="120">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="Created At" width="180" />
      <el-table-column label="Actions" width="150">
        <template #default="scope">
          <el-button
            v-if="scope.row.status === 'paid' || scope.row.status === 'shipped'"
            size="small"
            type="warning"
            @click="handleRefund(scope.row)"
          >
            Refund
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOrders, refundOrder } from '@/api/order'
import { ElMessage, ElMessageBox } from 'element-plus'

const orders = ref([])
const loading = ref(false)
const statusFilter = ref('')

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const res = await getOrders(params)
    orders.value = res.data || res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    paid: 'success',
    shipped: 'primary',
    completed: 'success',
    refunded: 'warning',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const handleRefund = (row) => {
  ElMessageBox.confirm(
    'Are you sure to refund this order?',
    'Warning',
    {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(async () => {
      await refundOrder(row.id)
      ElMessage({
        type: 'success',
        message: 'Refund initiated',
      })
      fetchOrders()
    })
    .catch(() => {})
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.filter-container {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
</style>
