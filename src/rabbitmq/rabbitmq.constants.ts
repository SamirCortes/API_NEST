export const RABBITMQ_SERVICE = 'RABBITMQ_SERVICE';

export const RABBITMQ_DEFAULT_URL = 'amqp://nest:nest@localhost:5672';
export const RABBITMQ_DEFAULT_QUEUE = 'messages_queue';

export const RABBITMQ_EVENTS = {
  CLIENT_CREATED: 'client.created',
  CLIENT_UPDATED: 'client.updated',
  CLIENT_DELETED: 'client.deleted',
  MESSAGE_PUBLISHED: 'message.published',
} as const;
