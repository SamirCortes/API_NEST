import { config as loadEnv } from 'dotenv';
import { DataSource } from 'typeorm';
import { Client } from '../clients/entities/client.entity';

loadEnv();

export default new DataSource({
  type: 'mysql',
  host: process.env.DB_HOST ?? 'localhost',
  port: Number(process.env.DB_PORT ?? 3306),
  username: process.env.DB_USERNAME ?? 'nest',
  password: process.env.DB_PASSWORD ?? 'nest',
  database: process.env.DB_DATABASE ?? 'api_nest',
  entities: [Client],
  migrations: ['src/database/migrations/*.ts'],
  synchronize: false,
  extra: {
    allowPublicKeyRetrieval: true,
  },
});
