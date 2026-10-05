import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import {
  ClientsModule as MicroserviceClientsModule,
  Transport,
} from '@nestjs/microservices';
import {
  RABBITMQ_DEFAULT_QUEUE,
  RABBITMQ_DEFAULT_URL,
  RABBITMQ_SERVICE,
} from './rabbitmq.constants';
import { RabbitmqService } from './rabbitmq.service';

@Module({
  imports: [
    MicroserviceClientsModule.registerAsync([
      {
        name: RABBITMQ_SERVICE,
        imports: [ConfigModule],
        inject: [ConfigService],
        useFactory: (configService: ConfigService) => ({
          transport: Transport.RMQ,
          options: {
            urls: [
              configService.get<string>('RABBITMQ_URL', RABBITMQ_DEFAULT_URL),
            ],
            queue: configService.get<string>(
              'RABBITMQ_QUEUE',
              RABBITMQ_DEFAULT_QUEUE,
            ),
            persistent: true,
            queueOptions: {
              durable: true,
            },
            socketOptions: {
              reconnectTimeInSeconds: 5,
            },
          },
        }),
      },
    ]),
  ],
  providers: [RabbitmqService],
  exports: [RabbitmqService],
})
export class RabbitmqModule {}
