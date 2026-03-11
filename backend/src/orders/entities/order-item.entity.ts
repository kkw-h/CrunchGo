import { Entity, PrimaryGeneratedColumn, Column, ManyToOne, JoinColumn } from 'typeorm';
import { Order } from './order.entity';
import { Product } from '../../products/entities/product.entity';

@Entity('order_items')
export class OrderItem {
  @PrimaryGeneratedColumn()
  id: number;

  @ManyToOne(() => Order, (order) => order.items, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'orderId' })
  order: Order;

  @Column()
  orderId: string;

  @ManyToOne(() => Product)
  @JoinColumn({ name: 'productId' })
  product: Product;

  @Column()
  productId: number;

  @Column()
  productName: string; // Snapshot of product name

  @Column('decimal', { precision: 10, scale: 2 })
  price: number; // Snapshot of price at purchase time

  @Column('int')
  quantity: number;

  @Column('jsonb', { nullable: true })
  options: any; // e.g., { "temperature": "Hot", "sugar": "Half" }
}
