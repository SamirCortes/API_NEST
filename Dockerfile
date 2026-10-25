# syntax=docker/dockerfile:1

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22-alpine AS production
WORKDIR /app
ENV NODE_ENV=production \
    OTEL_SERVICE_NAME=api-nest \
    OTEL_TRACES_EXPORTER=otlp \
    OTEL_METRICS_EXPORTER=otlp \
    OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf \
    OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318 \
    OTEL_NODE_RESOURCE_DETECTORS=env,host,os \
    OTEL_NODE_DISABLED_INSTRUMENTATIONS=fs,dns,net,grpc \
    OTEL_LOGS_EXPORTER=none
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json
EXPOSE 3000
CMD ["node", "--require", "@opentelemetry/auto-instrumentations-node/register", "dist/main.js"]
