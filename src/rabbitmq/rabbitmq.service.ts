import { Inject, Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { ClientProxy } from '@nestjs/microservices';
import { firstValueFrom, timeout } from 'rxjs';
import { RABBITMQ_SERVICE } from './rabbitmq.constants';

@Injectable()
export class RabbitmqService implements OnModuleInit {
  private readonly logger = new Logger(RabbitmqService.name);

  constructor(
    @Inject(RABBITMQ_SERVICE)
    private readonly client: ClientProxy,
  ) {}

  async onModuleInit() {
    let attempt = 0;

    while (true) {
      attempt += 1;
      try {
        await this.client.connect();
        this.logger.log('Conectado a RabbitMQ');
        return;
      } catch (error) {
        this.logger.warn(
          `Intento ${attempt} de conexión a RabbitMQ falló. Reintentando en 3s.`,
        );
        this.logger.debug(error);
        await this.client.close().catch(() => undefined);
        await this.delay(3000);
      }
    }
  }

  async emit(pattern: string, data: unknown) {
    await firstValueFrom(this.client.emit(pattern, data));
    this.logger.log(`Evento publicado: ${pattern}`);
  }

  async send<TResult = unknown>(
    pattern: string,
    data: unknown,
  ): Promise<TResult> {
    return firstValueFrom(
      this.client.send<TResult>(pattern, data).pipe(timeout(5000)),
    );
  }

  private delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
