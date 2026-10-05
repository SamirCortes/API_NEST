import { BadRequestException, ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { json, NextFunction, Request, Response, urlencoded } from 'express';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';
import { messagesBodyParser } from './messages/messages-body.middleware';
import {
  RABBITMQ_DEFAULT_QUEUE,
  RABBITMQ_DEFAULT_URL,
} from './rabbitmq/rabbitmq.constants';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, { bodyParser: false });
  const configService = app.get(ConfigService);

  app.use((req: Request, res: Response, next: NextFunction) => {
    const path = req.path.replace(/\/+$/, '') || '/';
    if (req.method === 'POST' && path === '/messages') {
      messagesBodyParser(req, res, next);
      return;
    }
    json()(req, res, next);
  });
  app.use(urlencoded({ extended: true }));

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
      exceptionFactory: (errors) => {
        const fieldLabels: Record<string, string> = {
          names: 'nombres',
          surnames: 'apellidos',
          age: 'edad',
          status: 'estado',
        };

        const messages = errors.flatMap((error) => {
          const label = fieldLabels[error.property] ?? error.property;

          if (error.constraints) {
            return Object.values(error.constraints).map((msg) => {
              if (msg.includes('should not exist')) {
                return `la propiedad ${label} no está permitida`;
              }
              return msg;
            });
          }
          return [`${label} no es válido`];
        });
        return new BadRequestException(messages.join(', '));
      },
    }),
  );
  app.useGlobalFilters(new HttpExceptionFilter());

  const rabbitQueue = configService.get<string>(
    'RABBITMQ_QUEUE',
    RABBITMQ_DEFAULT_QUEUE,
  );
  const rabbitUrl = configService.get<string>(
    'RABBITMQ_URL',
    RABBITMQ_DEFAULT_URL,
  );

  const swaggerConfig = new DocumentBuilder()
    .setTitle('API Nest - Clients')
    .setDescription('REST API de clientes y productor de mensajes RabbitMQ')
    .setVersion('1.0')
    .addTag('clients')
    .addTag('messages')
    .build();

  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('api/docs', app, document);

  const port = configService.get<number>('PORT', 3000);
  await app.listen(port);
  console.log(`API: http://localhost:${port}`);
  console.log(`Swagger: http://localhost:${port}/api/docs`);
  console.log(`RabbitMQ: ${rabbitUrl}`);
  console.log(`Cola durable: ${rabbitQueue}`);
}
bootstrap();
