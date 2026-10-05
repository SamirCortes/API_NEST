import { Module } from '@nestjs/common';
import { RabbitmqModule } from '../rabbitmq/rabbitmq.module';
import { MessagesController } from './messages.controller';
import { MessagesService } from './messages.service';

@Module({
  imports: [RabbitmqModule],
  controllers: [MessagesController],
  providers: [MessagesService],
})
export class MessagesModule {}
