import { Logger } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { MicroserviceOptions, Transport } from '@nestjs/microservices';
import { config as loadEnv } from 'dotenv';
import { ConsumerModule } from './consumer.module';
import {
  RABBITMQ_DEFAULT_QUEUE,
  RABBITMQ_DEFAULT_URL,
} from './rabbitmq/rabbitmq.constants';

loadEnv({ quiet: true });

async function bootstrap() {
  const logger = new Logger('ConsumerBootstrap');
  const rabbitUrl = process.env.RABBITMQ_URL ?? RABBITMQ_DEFAULT_URL;
  const rabbitQueue = process.env.RABBITMQ_QUEUE ?? RABBITMQ_DEFAULT_QUEUE;

  logger.log(
    `Esperando a RabbitMQ para consumir la cola ${rabbitQueue}. La conexión se reintenta sola.`,
  );

  const app = await NestFactory.createMicroservice<MicroserviceOptions>(
    ConsumerModule,
    {
      transport: Transport.RMQ,
      options: {
        urls: [rabbitUrl],
        queue: rabbitQueue,
        noAck: false,
        prefetchCount: 1,
        persistent: true,
        queueOptions: {
          durable: true,
        },
        socketOptions: {
          reconnectTimeInSeconds: 5,
        },
      },
    },
  );

  await app.listen();
  logger.log(`Consumidor escuchando la cola durable ${rabbitQueue}`);
}

void bootstrap();
