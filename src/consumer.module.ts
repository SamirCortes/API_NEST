import { Module } from '@nestjs/common';
import { RabbitmqConsumer } from './rabbitmq/rabbitmq.consumer';

@Module({
  controllers: [RabbitmqConsumer],
})
export class ConsumerModule {}
