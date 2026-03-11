import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';
import * as crypto from 'crypto';
import { RedisService } from '../redis/redis.service';
import { Order } from '../orders/entities/order.entity';

@Injectable()
export class PrinterService {
  private readonly logger = new Logger(PrinterService.name);
  private readonly apiUrl = 'https://open-api.10ss.net'; // Yilianyun API V2
  
  constructor(
    private readonly configService: ConfigService,
    private readonly redisService: RedisService,
  ) {}

  /**
   * Print an order receipt
   */
  async printOrder(order: Order): Promise<void> {
    const machineCode = this.configService.get<string>('YILIANYUN_MACHINE_CODE');
    if (!machineCode) {
      this.logger.warn('YILIANYUN_MACHINE_CODE not configured, skipping print.');
      return;
    }

    try {
      const accessToken = await this.getAccessToken();
      const content = this.formatReceipt(order);
      
      const response = await axios.post(`${this.apiUrl}/print/index`, {
        client_id: this.configService.get<string>('YILIANYUN_CLIENT_ID'),
        access_token: accessToken,
        machine_code: machineCode,
        content: content,
        origin_id: order.orderNumber,
        sign: this.generateSign(Math.floor(Date.now() / 1000)),
        id: this.generateUuid(),
        timestamp: Math.floor(Date.now() / 1000),
      }, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' } // Yilianyun usually expects form-data or urlencoded
      });

      if (response.data && response.data.error === '0') {
        this.logger.log(`Print command sent successfully for order ${order.orderNumber}`);
      } else {
        this.logger.error(`Failed to print order ${order.orderNumber}: ${JSON.stringify(response.data)}`);
      }
    } catch (error) {
      this.logger.error(`Error printing order ${order.orderNumber}`, error);
    }
  }

  /**
   * Format receipt content for Yilianyun printer
   * Specific tags: <BR> newline, <CB> center bold, <L> left, <R> right, <B> bold, <QR> qr code
   */
  private formatReceipt(order: Order): string {
    let content = '';
    
    content += '<CB>CrunchGo 街边点餐</CB><BR>';
    content += '<BR>';
    content += `<CB>取餐号: ${order.orderNumber}</CB><BR>`;
    content += '<BR>';
    content += '--------------------------------<BR>';
    content += `订单时间: ${new Date(order.createdAt).toLocaleString()}<BR>`;
    content += '--------------------------------<BR>';
    content += '<B>商品列表</B><BR>';
    
    order.items.forEach(item => {
      content += `<B>${item.productName}</B> <R>x${item.quantity}</R><BR>`;
      if (item.options) {
        const optionsStr = Object.values(item.options).join(', ');
        content += `${optionsStr}<BR>`;
      }
      content += '--------------------------------<BR>';
    });
    
    content += `<R>合计: ${order.totalAmount}元</R><BR>`;
    content += '--------------------------------<BR>';
    content += '<CB>请留意叫号取餐</CB><BR>';
    content += '<CB>谢谢惠顾!</CB><BR>';
    
    return content;
  }

  /**
   * Get Access Token (cached in Redis)
   */
  private async getAccessToken(): Promise<string> {
    const redis = this.redisService.getClient();
    const cacheKey = 'yilianyun:access_token';
    
    const cachedToken = await redis.get(cacheKey);
    if (cachedToken) {
      return cachedToken;
    }

    const clientId = this.configService.get<string>('YILIANYUN_CLIENT_ID');
    const clientSecret = this.configService.get<string>('YILIANYUN_CLIENT_SECRET');
    const timestamp = Math.floor(Date.now() / 1000);
    const sign = this.generateSign(timestamp);

    try {
      const response = await axios.post(`${this.apiUrl}/oauth/oauth`, {
        client_id: clientId,
        grant_type: 'client_credentials',
        sign: sign,
        scope: 'all',
        timestamp: timestamp,
        id: this.generateUuid(),
      }, {
         headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      if (response.data && response.data.error === '0') {
        const token = response.data.body.access_token;
        const expiresIn = response.data.body.expires_in;
        // Cache token slightly less than expiry time
        await redis.set(cacheKey, token, 'EX', expiresIn - 60);
        return token;
      } else {
        throw new Error(`Failed to get access token: ${JSON.stringify(response.data)}`);
      }
    } catch (error) {
      this.logger.error('Error fetching access token', error);
      throw error;
    }
  }

  /**
   * Generate MD5 signature
   * sign = MD5(client_id + timestamp + client_secret)
   */
  private generateSign(timestamp: number): string {
    const clientId = this.configService.get<string>('YILIANYUN_CLIENT_ID');
    const clientSecret = this.configService.get<string>('YILIANYUN_CLIENT_SECRET');
    const str = clientId + timestamp + clientSecret;
    return crypto.createHash('md5').update(str).digest('hex');
  }

  private generateUuid(): string {
    return crypto.randomUUID();
  }
}
