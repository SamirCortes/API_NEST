import { BadRequestException, ValidationPipe } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

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

  const swaggerConfig = new DocumentBuilder()
    .setTitle('API Nest - Clients')
    .setDescription('REST API for clients management')
    .setVersion('1.0')
    .addTag('clients')
    .build();

  const document = SwaggerModule.createDocument(app, swaggerConfig);
  SwaggerModule.setup('api/docs', app, document);

  const port = process.env.PORT ?? 3000;
  await app.listen(port);
  console.log(`API: http://localhost:${port}`);
  console.log(`Swagger: http://localhost:${port}/api/docs`);
}
bootstrap();
