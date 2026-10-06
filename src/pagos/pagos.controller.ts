import {
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  ParseIntPipe,
  Post,
} from '@nestjs/common';
import {
  ApiBody,
  ApiConsumes,
  ApiOkResponse,
  ApiOperation,
  ApiTags,
} from '@nestjs/swagger';
import { PagosService } from './pagos.service';

@ApiTags('pagos')
@Controller('pagos')
export class PagosController {
  constructor(private readonly pagosService: PagosService) {}

  @Post()
  @HttpCode(HttpStatus.OK)
  @ApiConsumes('application/json')
  @ApiOperation({ summary: 'Registrar un pago' })
  @ApiBody({
    schema: {
      type: 'object',
      required: ['referencia', 'valor', 'medio'],
      properties: {
        referencia: { type: 'string', example: 'PAG-0001' },
        valor: { type: 'number', example: 125000 },
        medio: { type: 'string', example: 'transferencia' },
      },
    },
  })
  @ApiOkResponse({
    schema: {
      example: {
        status: true,
        message: 'Pago registrado',
        data: { id: 1, estado: 'REGISTRADO' },
      },
    },
  })
  register(@Body() body: unknown) {
    return this.pagosService.register(body);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Consultar un pago por id' })
  @ApiOkResponse({ description: 'Pago consultado' })
  findOne(@Param('id', ParseIntPipe) id: number) {
    return this.pagosService.findOne(id);
  }
}
