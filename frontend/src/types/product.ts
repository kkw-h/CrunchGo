export interface Category {
  id: number;
  name: string;
  sort: number;
  isActive: boolean;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  price: number;
  stock: number;
  image?: string;
  specs?: any;
  isAvailable: boolean;
  categoryId?: number;
  category?: Category;
}
