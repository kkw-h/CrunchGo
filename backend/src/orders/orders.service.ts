import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, DataSource } from 'typeorm';
import { Order, OrderStatus } from './entities/order.entity';
import { OrderItem } from './entities/order-item.entity';
import { Product } from '../products/entities/product.entity';
import { CreateOrderDto, CreateOrderItemDto } from './dto/create-order.dto';
import { RedisService } from '../redis/redis.service';

@Injectable()
export class OrdersService {
  constructor(
    @InjectRepository(Order)
    private readonly orderRepository: Repository<Order>,
    @InjectRepository(Product)
    private readonly productRepository: Repository<Product>,
    private readonly redisService: RedisService,
    private readonly dataSource: DataSource,
  ) {}

  async create(createOrderDto: CreateOrderDto): Promise<Order> {
    const { items } = createOrderDto;

    // 1. Validate items and calculate total
    const productIds = items.map((item) => item.productId);
    const products = await this.productRepository.findByIds(productIds);
    const productMap = new Map(products.map((p) => [p.id, p]));

    let totalAmount = 0;
    const orderItems: OrderItem[] = [];

    for (const itemDto of items) {
      const product = productMap.get(itemDto.productId);
      if (!product) {
        throw new NotFoundException(`Product #${itemDto.productId} not found`);
      }
      if (!product.isAvailable) {
        throw new BadRequestException(`Product ${product.name} is not available`);
      }
      if (product.stock < itemDto.quantity) {
        throw new BadRequestException(`Insufficient stock for ${product.name}`);
      }

      const orderItem = new OrderItem();
      orderItem.product = product;
      orderItem.productName = product.name;
      orderItem.price = product.price;
      orderItem.quantity = itemDto.quantity;
      orderItem.options = itemDto.options;

      totalAmount += Number(product.price) * itemDto.quantity;
      orderItems.push(orderItem);
    }

    // 2. Generate Order Number (e.g., A101) using Redis
    const orderNumber = await this.generateOrderNumber();

    // 3. Create Order in Transaction
    const queryRunner = this.dataSource.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      // Deduct stock
      for (const item of orderItems) {
        await queryRunner.manager.decrement(
          Product,
          { id: item.product.id },
          'stock',
          item.quantity,
        );
      }

      // Save Order
      const order = new Order();
      order.orderNumber = orderNumber;
      order.totalAmount = totalAmount;
      order.status = OrderStatus.PENDING;
      order.items = orderItems;

      const savedOrder = await queryRunner.manager.save(Order, order);

      await queryRunner.commitTransaction();
      return savedOrder;
    } catch (err) {
      await queryRunner.rollbackTransaction();
      throw err;
    } finally {
      await queryRunner.release();
    }
  }

  async findAll(): Promise<Order[]> {
    return this.orderRepository.find({
      relations: ['items'],
      order: { createdAt: 'DESC' },
    });
  }

  async findOne(id: string): Promise<Order> {
    const order = await this.orderRepository.findOne({
      where: { id },
      relations: ['items'],
    });
    if (!order) {
      throw new NotFoundException(`Order #${id} not found`);
    }
    return order;
  }

  private async generateOrderNumber(): Promise<string> {
    const redis = this.redisService.getClient();
    const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    const key = `order_seq:${today}`;
    
    // Increment sequence number
    const seq = await redis.incr(key);
    
    // Set expiry for 24 hours if it's new
    if (seq === 1) {
      await redis.expire(key, 86400);
    }

    // Format: A + 3 digits (e.g., A001, A002)
    // For simplicity, just using A prefix. Could be expanded to multiple windows.
    return `A${seq.toString().padStart(3, '0')}`;
  }
}
