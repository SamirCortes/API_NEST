import { Controller, Logger } from '@nestjs/common';
import { Ctx, EventPattern, Payload, RmqContext } from '@nestjs/microservices';
import { RABBITMQ_EVENTS } from '../rabbitmq/rabbitmq.constants';
import { PagosProcessor } from './pagos.processor';

type PaymentMessage = {
  id?: number;
};

@Controller()
export class PagosConsumer {
  private readonly logger = new Logger(PagosConsumer.name);

  constructor(private readonly pagosProcessor: PagosProcessor) {}

  @EventPattern(RABBITMQ_EVENTS.PAYMENT_REGISTERED)
  async onPaymentRegistered(
    @Payload() data: PaymentMessage,
    @Ctx() context: RmqContext,
  ) {
    const channel = context.getChannelRef();
    const message = context.getMessage();
    const id = Number(data?.id);

    try {
      if (!Number.isInteger(id) || id <= 0) {
        throw new Error('El mensaje del pago no trae un id valido');
      }
      await this.pagosProcessor.process(id);
      channel.ack(message);
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      this.logger.error(
        `Pago ${id} no se procesó. Sigue en REGISTRADO y el mensaje vuelve a la cola. ${detail}`,
      );
      channel.nack(message, false, true);
    }
  }
}
