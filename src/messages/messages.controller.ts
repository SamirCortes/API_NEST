import {
  BadRequestException,
  Body,
  Controller,
  HttpCode,
  HttpStatus,
  Post,
} from '@nestjs/common';
import {
  ApiBody,
  ApiConsumes,
  ApiOkResponse,
  ApiOperation,
  ApiTags,
} from '@nestjs/swagger';
import { ApiResponseDto } from '../common/dto/api-response.dto';
import { MessagesService } from './messages.service';

@ApiTags('messages')
@Controller('messages')
export class MessagesController {
  constructor(private readonly messagesService: MessagesService) {}

  @Post()
  @HttpCode(HttpStatus.OK)
  @ApiConsumes('application/json')
  @ApiOperation({ summary: 'Publicar un mensaje en la cola' })
  @ApiBody({
    description: 'Cuerpo JSON del mensaje. El contenido es libre.',
    schema: {
      type: 'object',
      additionalProperties: true,
      example: {
        sensor: 'OD-01',
        valor: 4.2,
        unidad: 'mg/L',
      },
    },
  })
  @ApiOkResponse({
    description: 'Mensaje encolado',
    schema: {
      example: { status: true, message: 'Mensaje encolado' },
    },
  })
  async publish(@Body() body: unknown) {
    if (body === undefined || body === null) {
      throw new BadRequestException('Formato de mensaje inválido');
    }

    await this.messagesService.publish(body);
    return ApiResponseDto.success('Mensaje encolado');
  }
}
