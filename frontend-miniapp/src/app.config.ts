export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/menu/index',
    'pages/cart/index',
    'pages/order/list',
    'pages/order/detail',
    'pages/user/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: 'CrunchGo',
    navigationBarTextStyle: 'black'
  },
  tabBar: {
    color: '#999',
    selectedColor: '#ff9900',
    backgroundColor: '#fff',
    list: [
      {
        pagePath: 'pages/index/index',
        text: 'Home',
        iconPath: './assets/home.png',
        selectedIconPath: './assets/home-active.png'
      },
      {
        pagePath: 'pages/menu/index',
        text: 'Menu',
        iconPath: './assets/menu.png',
        selectedIconPath: './assets/menu-active.png'
      },
      {
        pagePath: 'pages/cart/index',
        text: 'Cart',
        iconPath: './assets/cart.png',
        selectedIconPath: './assets/cart-active.png'
      },
      {
        pagePath: 'pages/order/list',
        text: 'Orders',
        iconPath: './assets/order.png',
        selectedIconPath: './assets/order-active.png'
      },
      {
        pagePath: 'pages/user/index',
        text: 'Me',
        iconPath: './assets/user.png',
        selectedIconPath: './assets/user-active.png'
      }
    ]
  }
})
