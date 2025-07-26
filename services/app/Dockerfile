FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . ./
RUN npm run build

FROM busybox:1.36.1-uclibc AS app-dist

WORKDIR /app

COPY --from=build /app/dist ./dist
