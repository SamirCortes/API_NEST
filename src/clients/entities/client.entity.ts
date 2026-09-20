import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import {
  Column,
  CreateDateColumn,
  Entity,
  PrimaryGeneratedColumn,
} from 'typeorm';

@Entity('clients')
export class Client {
  @ApiProperty({ example: 1 })
  @PrimaryGeneratedColumn()
  id: number;

  @ApiProperty({ example: 'Ana' })
  @Column({ type: 'varchar', length: 100 })
  names: string;

  @ApiProperty({ example: 'Lopez' })
  @Column({ type: 'varchar', length: 100 })
  surnames: string;

  @ApiPropertyOptional({ example: 28, nullable: true })
  @Column({ type: 'int', nullable: true })
  age: number | null;

  @ApiProperty({ example: '2026-03-20T16:00:00.000Z' })
  @CreateDateColumn({ name: 'created_at', type: 'timestamp' })
  createdAt: Date;

  @ApiProperty({ example: true })
  @Column({ type: 'boolean', default: true })
  status: boolean;
}
