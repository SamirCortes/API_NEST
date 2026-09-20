import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import {
  IsBoolean,
  IsInt,
  IsNotEmpty,
  IsOptional,
  IsString,
  MaxLength,
  Min,
} from 'class-validator';

export class CreateClientDto {
  @ApiProperty({ example: 'Ana', maxLength: 100 })
  @IsString({ message: 'nombres debe ser una cadena de texto' })
  @IsNotEmpty({ message: 'nombres no debe estar vacío' })
  @MaxLength(100, {
    message: 'nombres debe tener máximo 100 caracteres',
  })
  names: string;

  @ApiProperty({ example: 'Lopez', maxLength: 100 })
  @IsString({ message: 'apellidos debe ser una cadena de texto' })
  @IsNotEmpty({ message: 'apellidos no debe estar vacío' })
  @MaxLength(100, {
    message: 'apellidos debe tener máximo 100 caracteres',
  })
  surnames: string;

  @ApiPropertyOptional({ example: 28, minimum: 0 })
  @IsOptional()
  @IsInt({ message: 'edad debe ser un número entero' })
  @Min(0, { message: 'edad debe ser mayor o igual a 0' })
  age?: number;

  @ApiPropertyOptional({ example: true, default: true })
  @IsOptional()
  @IsBoolean({ message: 'estado debe ser un valor booleano' })
  status?: boolean;
}
