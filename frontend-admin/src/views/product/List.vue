<template>
  <div class="product-list">
    <div class="header">
      <h2>Products</h2>
      <el-button type="primary" @click="$router.push('/products/create')">
        Add Product
      </el-button>
    </div>

    <el-table :data="products" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="Name" />
      <el-table-column prop="price" label="Price" width="120">
        <template #default="scope">
          ¥{{ scope.row.price }}
        </template>
      </el-table-column>
      <el-table-column prop="stock" label="Stock" width="120" />
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">Edit</el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(scope.row)"
          >
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, deleteProduct } from '@/api/product'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const products = ref([])
const loading = ref(false)

const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await getProducts()
    products.value = res.data || res // Adjust based on API response
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleEdit = (row) => {
  router.push(`/products/${row.id}/edit`)
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    'Are you sure to delete this product?',
    'Warning',
    {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(async () => {
      await deleteProduct(row.id)
      ElMessage({
        type: 'success',
        message: 'Delete completed',
      })
      fetchProducts()
    })
    .catch(() => {})
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
