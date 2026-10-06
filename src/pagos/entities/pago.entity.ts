import { ApiProperty } from '@nestjs/swagger';
import {
  Column,
  CreateDateColumn,
  Entity,
  PrimaryGeneratedColumn,
} from 'typeorm';

export type PagoEstado = 'REGISTRADO' | 'PROCESADO';

@Entity('pagos')
export class Pago {
  @ApiProperty({ example: 1 })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({ example: 'PAG-0001' })
  @Column({ type: 'varchar', length: 100 })
  referencia: string;

  @ApiProperty({ example: 125000 })
  @Column({
    type: 'decimal',
    precision: 12,
    scale: 2,
    transformer: {
      to: (value: number) => value,
      from: (value: string) => Number(value),
    },
  })
  valor: number;

  @ApiProperty({ example: 'transferencia' })
  @Column({ name: 'medio_pago', type: 'varchar', length: 50 })
  medio: string;

  @ApiProperty({ example: '2026-10-06T22:00:00.000Z' })
  @CreateDateColumn({ name: 'fecha_registro', type: 'timestamp' })
  fechaRegistro: Date;

  @ApiProperty({ example: 'REGISTRADO', enum: ['REGISTRADO', 'PROCESADO'] })
  @Column({ type: 'varchar', length: 20, default: 'REGISTRADO' })
  estado: PagoEstado;
}
