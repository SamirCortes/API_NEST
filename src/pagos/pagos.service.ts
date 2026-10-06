import { BadRequestException, Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ApiResponseDto } from '../common/dto/api-response.dto';
import { RABBITMQ_EVENTS } from '../rabbitmq/rabbitmq.constants';
import { RabbitmqService } from '../rabbitmq/rabbitmq.service';
import { Pago } from './entities/pago.entity';

type PagoInput = {
  referencia: string;
  valor: number;
  medio: string;
};

@Injectable()
export class PagosService {
  constructor(
    @InjectRepository(Pago)
    private readonly pagosRepository: Repository<Pago>,
    private readonly rabbitmqService: RabbitmqService,
  ) {}

  async register(body: unknown) {
    const input = this.parse(body);
    if (!input) {
      throw new BadRequestException('Datos del pago inválidos');
    }

    const saved = await this.pagosRepository.save(
      this.pagosRepository.create({
        referencia: input.referencia,
        valor: input.valor,
        medio: input.medio,
        estado: 'REGISTRADO',
      }),
    );

    await this.rabbitmqService.emit(RABBITMQ_EVENTS.PAYMENT_REGISTERED, {
      id: saved.id,
    });

    return ApiResponseDto.success('Pago registrado', {
      id: saved.id,
      estado: saved.estado,
    });
  }

  async findOne(id: number) {
    const pago = await this.pagosRepository.findOne({ where: { id } });
    if (!pago) {
      throw new NotFoundException('Pago no encontrado');
    }

    return ApiResponseDto.success('Pago consultado', {
      id: pago.id,
      referencia: pago.referencia,
      valor: Number(pago.valor),
      medio: pago.medio,
      fechaRegistro: pago.fechaRegistro,
      estado: pago.estado,
    });
  }

  private parse(body: unknown): PagoInput | null {
    if (!body || typeof body !== 'object' || Array.isArray(body)) {
      return null;
    }

    const record = body as Record<string, unknown>;
    const referencia =
      typeof record.referencia === 'string' ? record.referencia.trim() : '';
    const medio = typeof record.medio === 'string' ? record.medio.trim() : '';
    const valor = record.valor;

    if (!referencia || !medio) {
      return null;
    }
    if (typeof valor !== 'number' || !Number.isFinite(valor) || valor <= 0) {
      return null;
    }

    return { referencia, valor, medio };
  }
}
