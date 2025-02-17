FROM node:20.11.0
WORKDIR /app
COPY ./package.json ./
RUN npm install
EXPOSE 8000
CMD node --watch ./src/index.js