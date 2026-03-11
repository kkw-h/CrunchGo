import { createContext } from 'react';
import { Product } from '../types/product';

export interface CartItem {
  product: Product;
  quantity: number;
  options?: any;
}

export interface CartContextType {
  items: CartItem[];
  totalAmount: number;
  totalQuantity: number;
  addToCart: (product: Product, quantity?: number, options?: any) => void;
  removeFromCart: (productId: number) => void;
  updateQuantity: (productId: number, quantity: number) => void;
  clearCart: () => void;
}

export const CartContext = createContext<CartContextType>({
  items: [],
  totalAmount: 0,
  totalQuantity: 0,
  addToCart: () => {},
  removeFromCart: () => {},
  updateQuantity: () => {},
  clearCart: () => {},
});
