import {
  Column,
  CreateDateColumn,
  Entity,
  PrimaryGeneratedColumn,
} from 'typeorm';

@Entity('procesamientos')
export class Procesamiento {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'pago_id', type: 'int' })
  pagoId: number;

  @CreateDateColumn({ name: 'fecha_procesamiento', type: 'timestamp' })
  fechaProcesamiento: Date;

  @Column({ type: 'varchar', length: 255 })
  resultado: string;
}
