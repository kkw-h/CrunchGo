import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './app.scss'

const App = createApp({
  onShow () {},
  // 入口组件不需要实现 render 方法，即使在构建 h5 时也不需要
})

App.use(createPinia())

export default App
