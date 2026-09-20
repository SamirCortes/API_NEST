import { MigrationInterface, QueryRunner } from 'typeorm';

export class CreateClientsTable1740000000000 implements MigrationInterface {
  name = 'CreateClientsTable1740000000000';

  public async up(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`
      CREATE TABLE \`clients\` (
        \`id\` int NOT NULL AUTO_INCREMENT,
        \`names\` varchar(100) NOT NULL,
        \`surnames\` varchar(100) NOT NULL,
        \`age\` int NULL,
        \`created_at\` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        \`status\` tinyint NOT NULL DEFAULT 1,
        PRIMARY KEY (\`id\`)
      ) ENGINE=InnoDB
    `);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    await queryRunner.query(`DROP TABLE \`clients\``);
  }
}
