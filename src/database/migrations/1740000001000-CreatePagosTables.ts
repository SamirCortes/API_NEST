import { MigrationInterface, QueryRunner } from 'typeorm';

export class CreatePagosTables1740000001000 implements MigrationInterface {
  name = 'CreatePagosTables1740000001000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      CREATE TABLE \`pagos\` (
        \`id\` int NOT NULL AUTO_INCREMENT,
        \`referencia\` varchar(100) NOT NULL,
        \`valor\` decimal(12,2) NOT NULL,
        \`medio_pago\` varchar(50) NOT NULL,
        \`fecha_registro\` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        \`estado\` varchar(20) NOT NULL DEFAULT 'REGISTRADO',
        PRIMARY KEY (\`id\`)
      ) ENGINE=InnoDB
    `);

    await queryRunner.query(`
      CREATE TABLE \`procesamientos\` (
        \`id\` int NOT NULL AUTO_INCREMENT,
        \`pago_id\` int NOT NULL,
        \`fecha_procesamiento\` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        \`resultado\` varchar(255) NOT NULL,
        PRIMARY KEY (\`id\`),
        KEY \`IDX_procesamientos_pago_id\` (\`pago_id\`),
        CONSTRAINT \`FK_procesamientos_pago\` FOREIGN KEY (\`pago_id\`) REFERENCES \`pagos\` (\`id\`)
      ) ENGINE=InnoDB
    `);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`DROP TABLE \`procesamientos\``);
    await queryRunner.query(`DROP TABLE \`pagos\``);
  }
}
