import { Injectable } from '@nestjs/common';
import { RABBITMQ_EVENTS } from '../rabbitmq/rabbitmq.constants';
import { RabbitmqService } from '../rabbitmq/rabbitmq.service';

@Injectable()
export class MessagesService {
  constructor(private readonly rabbitmqService: RabbitmqService) {}

  publish(message: unknown) {
    return this.rabbitmqService.emit(
      RABBITMQ_EVENTS.MESSAGE_PUBLISHED,
      message,
    );
  }
}
