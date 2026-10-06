import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { ApiResponseDto } from '../dto/api-response.dto';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    if (this.isInvalidJson(exception)) {
      const path = this.pathOf(request);
      if (path === '/messages') {
        response
          .status(HttpStatus.BAD_REQUEST)
          .json(ApiResponseDto.fail('Formato de mensaje inválido'));
        return;
      }
      if (request.method === 'POST' && path === '/pagos') {
        response
          .status(HttpStatus.BAD_REQUEST)
          .json(ApiResponseDto.fail('Datos del pago inválidos'));
        return;
      }
    }

    let statusCode = HttpStatus.INTERNAL_SERVER_ERROR;
    let message = 'Error interno del servidor';

    if (exception instanceof HttpException) {
      statusCode = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === 'string') {
        message = exceptionResponse;
      } else if (
        typeof exceptionResponse === 'object' &&
        exceptionResponse !== null
      ) {
        const body = exceptionResponse as {
          message?: string | string[];
        };
        message = Array.isArray(body.message)
          ? body.message.join(', ')
          : (body.message ?? exception.message);
      }
    } else if (exception instanceof Error) {
      message = exception.message;
    }

    response.status(statusCode).json(ApiResponseDto.fail(message));
  }

  private pathOf(request: Request) {
    return (request.originalUrl ?? request.url ?? '')
      .split('?')[0]
      .replace(/\/+$/, '');
  }

  private isInvalidJson(exception: unknown) {
    if (!exception || typeof exception !== 'object') {
      return false;
    }

    const error = exception as { name?: string; type?: string };
    return error.type === 'entity.parse.failed' || error.name === 'SyntaxError';
  }
}
