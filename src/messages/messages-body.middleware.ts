import { NextFunction, Request, Response } from 'express';

const INVALID_MESSAGE = {
  status: false,
  message: 'Formato de mensaje inválido',
};

export function messagesBodyParser(
  req: Request,
  res: Response,
  next: NextFunction,
) {
  const chunks: Buffer[] = [];

  req.on('data', (chunk: Buffer) => {
    chunks.push(chunk);
  });
  req.on('error', next);
  req.on('end', () => {
    try {
      req.body = JSON.parse(Buffer.concat(chunks).toString('utf8')) as unknown;
      next();
    } catch {
      res.status(400).json(INVALID_MESSAGE);
    }
  });
}
