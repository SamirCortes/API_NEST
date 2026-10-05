import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ClientsModule } from './clients/clients.module';
import { Client } from './clients/entities/client.entity';
import { MessagesModule } from './messages/messages.module';
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
        entities: [Client],
        synchronize: false,
        migrationsRun: true,
        migrations: [__dirname + '/database/migrations/*{.ts,.js}'],
        extra: {
          allowPublicKeyRetrieval: true,
        },
      }),
    }),
    RabbitmqModule,
    ClientsModule,
    MessagesModule,
  ],
})
export class AppModule {}
