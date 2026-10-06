import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Pago } from './pagos/entities/pago.entity';
import { Procesamiento } from './pagos/entities/procesamiento.entity';
import { PagosConsumer } from './pagos/pagos.consumer';
import { PagosProcessor } from './pagos/pagos.processor';
import { RabbitmqConsumer } from './rabbitmq/rabbitmq.consumer';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        type: 'mysql',
        host: configService.get<string>('DB_HOST', 'localhost'),
        port: configService.get<number>('DB_PORT', 3306),
        username: configService.get<string>('DB_USERNAME', 'nest'),
        password: configService.get<string>('DB_PASSWORD', 'nest'),
        database: configService.get<string>('DB_DATABASE', 'api_nest'),
        entities: [Pago, Procesamiento],
        synchronize: false,
        retryAttempts: 20,
        retryDelay: 3000,
        extra: {
          allowPublicKeyRetrieval: true,
        },
      }),
    }),
    TypeOrmModule.forFeature([Pago, Procesamiento]),
  ],
  controllers: [RabbitmqConsumer, PagosConsumer],
  providers: [PagosProcessor],
})
export class ConsumerModule {}
