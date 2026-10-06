import { Injectable, Logger } from '@nestjs/common';
import { DataSource } from 'typeorm';
import { Pago } from './entities/pago.entity';
import { Procesamiento } from './entities/procesamiento.entity';

export const PAGO_REFERENCIA_FALLO = 'PAG-FALLA';

@Injectable()
export class PagosProcessor {
  private readonly logger = new Logger(PagosProcessor.name);

  constructor(private readonly dataSource: DataSource) {}

  async process(id: number) {
    const takenAt = new Date();
    this.logger.log(
      `Pago ${id} tomado de la cola | hora: ${takenAt.toISOString()}`,
    );

    await this.sleep(this.delayMs());

    await this.dataSource.transaction(async (manager) => {
      const pago = await manager.findOne(Pago, { where: { id } });
      if (!pago) {
        throw new Error(`Pago ${id} no existe en la base de datos`);
      }
      if (pago.estado === 'PROCESADO') {
        this.logger.log(`Pago ${id} ya estaba PROCESADO`);
        return;
      }
      if (pago.referencia === PAGO_REFERENCIA_FALLO) {
        throw new Error(
          `Fallo simulado al procesar el pago ${id}. Sigue en REGISTRADO`,
        );
      }

      pago.estado = 'PROCESADO';
      await manager.save(pago);
      await manager.save(
        manager.create(Procesamiento, {
          pagoId: pago.id,
          resultado: `Comprobante ${pago.referencia} por ${pago.valor} via ${pago.medio}`,
        }),
      );
    });

    const finishedAt = new Date();
    this.logger.log(
      `Pago ${id} procesamiento finalizado | hora: ${finishedAt.toISOString()}`,
    );
  }

  private delayMs() {
    const value = Number(process.env.PROCESS_DELAY_MS ?? 4000);
    if (!Number.isFinite(value) || value < 0) {
      return 4000;
    }
    return value;
  }

  private sleep(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
