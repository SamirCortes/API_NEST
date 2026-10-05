import { Controller, Logger } from '@nestjs/common';
import {
  Ctx,
  EventPattern,
  Payload,
  RmqContext,
} from '@nestjs/microservices';
import { RABBITMQ_EVENTS } from './rabbitmq.constants';

@Controller()
export class RabbitmqConsumer {
  private readonly logger = new Logger(RabbitmqConsumer.name);

  @EventPattern(RABBITMQ_EVENTS.MESSAGE_PUBLISHED)
  onMessagePublished(@Payload() data: unknown, @Ctx() context: RmqContext) {
    this.consume(data, context);
  }

  @EventPattern(RABBITMQ_EVENTS.CLIENT_CREATED)
  onClientCreated(@Payload() data: unknown, @Ctx() context: RmqContext) {
    this.consume(data, context);
  }

  @EventPattern(RABBITMQ_EVENTS.CLIENT_UPDATED)
  onClientUpdated(@Payload() data: unknown, @Ctx() context: RmqContext) {
    this.consume(data, context);
  }

  @EventPattern(RABBITMQ_EVENTS.CLIENT_DELETED)
  onClientDeleted(@Payload() data: unknown, @Ctx() context: RmqContext) {
    this.consume(data, context);
  }

  private consume(data: unknown, context: RmqContext) {
    const receivedAt = new Date().toISOString();
    this.logger.log(
      `Mensaje recibido | hora: ${receivedAt} | contenido: ${JSON.stringify(data)}`,
    );
    context.getChannelRef().ack(context.getMessage());
  }
}
