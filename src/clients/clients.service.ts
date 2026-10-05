import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ApiResponseDto } from '../common/dto/api-response.dto';
import { RABBITMQ_EVENTS } from '../rabbitmq/rabbitmq.constants';
import { RabbitmqService } from '../rabbitmq/rabbitmq.service';
import { CreateClientDto } from './dto/create-client.dto';
import { UpdateClientDto } from './dto/update-client.dto';
import { Client } from './entities/client.entity';

@Injectable()
export class ClientsService {
  constructor(
    @InjectRepository(Client)
    private readonly clientsRepository: Repository<Client>,
    private readonly rabbitmqService: RabbitmqService,
  ) {}

  async create(createClientDto: CreateClientDto) {
    const client = this.clientsRepository.create({
      ...createClientDto,
      status: createClientDto.status ?? true,
    });
    const saved = await this.clientsRepository.save(client);

    await this.rabbitmqService.emit(RABBITMQ_EVENTS.CLIENT_CREATED, saved);

    return ApiResponseDto.success('Registro creado', saved);
  }

  async findAll() {
    const clients = await this.clientsRepository.find({
      order: { id: 'ASC' },
    });
    return ApiResponseDto.success('Registros listados', clients);
  }

  async findOne(id: number) {
    const client = await this.clientsRepository.findOne({ where: { id } });
    if (!client) {
      throw new NotFoundException('Registro no encontrado');
    }
    return ApiResponseDto.success('Registro consultado', client);
  }

  async update(id: number, updateClientDto: UpdateClientDto) {
    const client = await this.clientsRepository.findOne({ where: { id } });
    if (!client) {
      throw new NotFoundException('Registro no encontrado');
    }

    Object.assign(client, updateClientDto);
    const updated = await this.clientsRepository.save(client);

    await this.rabbitmqService.emit(RABBITMQ_EVENTS.CLIENT_UPDATED, updated);

    return ApiResponseDto.success('Registro actualizado', updated);
  }

  async remove(id: number) {
    const client = await this.clientsRepository.findOne({ where: { id } });
    if (!client) {
      throw new NotFoundException('Registro no encontrado');
    }

    const payload = { id: client.id };
    await this.clientsRepository.remove(client);

    await this.rabbitmqService.emit(RABBITMQ_EVENTS.CLIENT_DELETED, payload);

    return ApiResponseDto.success('Registro eliminado');
  }
}
