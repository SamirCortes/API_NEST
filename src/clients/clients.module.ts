import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { RabbitmqModule } from '../rabbitmq/rabbitmq.module';
import { ClientsController } from './clients.controller';
import { ClientsService } from './clients.service';
import { Client } from './entities/client.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Client]), RabbitmqModule],
  controllers: [ClientsController],
  providers: [ClientsService],
})
export class ClientsModule {}
