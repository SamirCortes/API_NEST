import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ClientsModule } from './clients/clients.module';
import { Client } from './clients/entities/client.entity';
import { MessagesModule } from './messages/messages.module';
import { Pago } from './pagos/entities/pago.entity';
import { Procesamiento } from './pagos/entities/procesamiento.entity';
import { PagosModule } from './pagos/pagos.module';
import { RabbitmqModule } from './rabbitmq/rabbitmq.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
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
        entities: [Client, Pago, Procesamiento],
        synchronize: false,
        migrationsRun: true,
        retryAttempts: 20,
        retryDelay: 3000,
        migrations: [__dirname + '/database/migrations/*{.ts,.js}'],
        extra: {
          allowPublicKeyRetrieval: true,
        },
      }),
    }),
    RabbitmqModule,
    ClientsModule,
    MessagesModule,
    PagosModule,
  ],
})
export class AppModule {}
