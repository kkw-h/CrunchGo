import { IsString, IsNumber, IsOptional, IsInt, IsBoolean, IsJSON } from 'class-validator';

export class CreateProductDto {
  @IsString()
  name: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsNumber()
  price: number;

  @IsInt()
  @IsOptional()
  stock?: number;

  @IsString()
  @IsOptional()
  image?: string;

  @IsOptional()
  specs?: any;

  @IsBoolean()
  @IsOptional()
  isAvailable?: boolean;

  @IsInt()
  @IsOptional()
  categoryId?: number;
}
