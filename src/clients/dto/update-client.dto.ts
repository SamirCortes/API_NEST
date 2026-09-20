import { ApiPropertyOptional } from '@nestjs/swagger';
import {
  IsBoolean,
  IsInt,
  IsOptional,
  IsString,
  MaxLength,
  Min,
} from 'class-validator';

export class UpdateClientDto {
  @ApiPropertyOptional({ example: 'Ana', maxLength: 100 })
  @IsOptional()
  @IsString({ message: 'nombres debe ser una cadena de texto' })
  @MaxLength(100, {
    message: 'nombres debe tener máximo 100 caracteres',
  })
  names?: string;

  @ApiPropertyOptional({ example: 'Lopez', maxLength: 100 })
  @IsOptional()
  @IsString({ message: 'apellidos debe ser una cadena de texto' })
  @MaxLength(100, {
    message: 'apellidos debe tener máximo 100 caracteres',
  })
  surnames?: string;

  @ApiPropertyOptional({ example: 28, minimum: 0, nullable: true })
  @IsOptional()
  @IsInt({ message: 'edad debe ser un número entero' })
  @Min(0, { message: 'edad debe ser mayor o igual a 0' })
  age?: number | null;

  @ApiPropertyOptional({ example: true })
  @IsOptional()
  @IsBoolean({ message: 'estado debe ser un valor booleano' })
  status?: boolean;
}
