import { PropsWithChildren } from 'react'
import { useLaunch } from '@tarojs/taro'
import { ConfigProvider } from '@nutui/nutui-react-taro'
import '@nutui/nutui-react-taro/dist/style.css'

import './app.scss'

const theme = {
  nutuiColorPrimary: '#FF6B00',
  nutuiColorPrimaryStop: '#FF6B00',
}

function App({ children }: PropsWithChildren<any>) {
  useLaunch(() => {
    console.log('App launched.')
  })

  // children 是将要会渲染的页面
  return (
    <ConfigProvider theme={theme}>
      {children}
    </ConfigProvider>
  )
}

export default App
