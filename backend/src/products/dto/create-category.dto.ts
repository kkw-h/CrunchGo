import { IsString, IsInt, IsOptional, IsBoolean } from 'class-validator';

export class CreateCategoryDto {
  @IsString()
  name: string;

  @IsInt()
  @IsOptional()
  sort?: number;

  @IsBoolean()
  @IsOptional()
  isActive?: boolean;
}
