<template>
  <div class="product-form">
    <h2>{{ isEdit ? 'Edit Product' : 'Create Product' }}</h2>
    <el-form :model="form" label-width="120px" ref="formRef" :rules="rules">
      <el-form-item label="Name" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="Description" prop="description">
        <el-input type="textarea" v-model="form.description" />
      </el-form-item>
      <el-form-item label="Price" prop="price">
        <el-input-number v-model="form.price" :min="0" />
      </el-form-item>
      <el-form-item label="Stock" prop="stock">
        <el-input-number v-model="form.stock" :min="0" />
      </el-form-item>
      <el-form-item label="Category" prop="category">
        <el-input v-model="form.category" />
      </el-form-item>
      
      <h3>SKUs</h3>
      <div v-for="(sku, index) in form.skus" :key="index" class="sku-item">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input v-model="sku.spec" placeholder="Spec (e.g., Color: Red)" />
          </el-col>
          <el-col :span="6">
            <el-input-number v-model="sku.price" :min="0" placeholder="Price" />
          </el-col>
          <el-col :span="6">
            <el-input-number v-model="sku.stock" :min="0" placeholder="Stock" />
          </el-col>
          <el-col :span="4">
            <el-button type="danger" @click="removeSku(index)">Remove</el-button>
          </el-col>
        </el-row>
      </div>
      <el-button type="primary" plain @click="addSku" style="margin-top: 10px;">Add SKU</el-button>

      <div class="actions" style="margin-top: 20px;">
        <el-button type="primary" @click="onSubmit">Save</el-button>
        <el-button @click="$router.back()">Cancel</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createProduct, getProduct, updateProduct } from '@/api/product'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  description: '',
  price: 0,
  stock: 0,
  category: '',
  skus: []
})

const rules = {
  name: [{ required: true, message: 'Please input product name', trigger: 'blur' }],
  price: [{ required: true, message: 'Please input price', trigger: 'blur' }],
  stock: [{ required: true, message: 'Please input stock', trigger: 'blur' }]
}

const addSku = () => {
  form.skus.push({ spec: '', price: 0, stock: 0 })
}

const removeSku = (index) => {
  form.skus.splice(index, 1)
}

const fetchData = async (id) => {
  try {
    const res = await getProduct(id)
    Object.assign(form, res.data || res)
  } catch (error) {
    console.error(error)
  }
}

const onSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await updateProduct(route.params.id, form)
          ElMessage.success('Product updated successfully')
        } else {
          await createProduct(form)
          ElMessage.success('Product created successfully')
        }
        router.push('/products')
      } catch (error) {
        console.error(error)
      }
    }
  })
}

onMounted(() => {
  if (isEdit.value) {
    fetchData(route.params.id)
  }
})
</script>

<style scoped>
.sku-item {
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
</style>
