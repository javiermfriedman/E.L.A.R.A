FROM node:20-alpine

WORKDIR /frontend

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npx", "vite", "--host"]
