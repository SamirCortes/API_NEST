import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RabbitmqModule } from '../rabbitmq/rabbitmq.module';
import { Pago } from './entities/pago.entity';
import { PagosController } from './pagos.controller';
import { PagosService } from './pagos.service';

@Module({
  imports: [TypeOrmModule.forFeature([Pago]), RabbitmqModule],
  controllers: [PagosController],
  providers: [PagosService],
})
export class PagosModule {}
