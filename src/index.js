const express = require('express');
const fs = require('fs');
const path = require('path');
const  socketIo = require('socket.io');
const { recorderConnect, recorderEvent, recorderDisconnect } = require('./recorder-events');
const { createDashboard } = require("./dashboard");
//const { generateRecorderHtml } = require('./recorder/recorderHtml');
const { generateReplayerHtml } = require("./replayer/replayerHtml");
const { replayerConnect } = require('./replayer-events');
const http = require('http');
const https = require('https');
const dotenv = require('dotenv');
const bodyParser = require('body-parser');

dotenv.config();

const PORT = 8000;
const app = express();
app.use(bodyParser.json());
let server;
let protocol;

const options = {
  key: fs.readFileSync('/app/certs/server.key'),
  cert: fs.readFileSync('/app/certs/server.crt')
};

const sockets = {}; // keep track of sockets via socketId


if (process.env.ENVIRONMENT == 'tunnel') { // if environment is set to tunnel, use http
  server = http.createServer(app);
  protocol = 'http://';
} else {
  server = https.createServer(options,app)
  protocol = 'https://';
}

// Enable CORS
const io = socketIo(server,{
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const rooms = {};
// hidden
const authToken = `XXXXXXXXXXXXXXXXXX`;


app.get('/', async(req, res) => {
  const filePath = path.join(__dirname, 'public', 'index.html');
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      return res.status(500).send("Error reading this file.");
    }
    //read and replace the url string depending on the .env environment set
    const fullUrl = `${protocol}${process.env.URL}`;
    const updatedData = data.replace('server-dummy-placeholder', fullUrl);
    res.send(updatedData);
  })
});


app.get('/mp3', async(req, res) => {
  const filePath = path.join(__dirname, 'public', 'audio.html');
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      return res.status(500).send("Error reading this file.");
    }
    //read and replace the url string depending on the .env environment set
    const fullUrl = `${protocol}${process.env.URL}`;
    const updatedData = data.replace('server-dummy-placeholder', fullUrl);
    res.send(updatedData);
  })
});


app.get('/replayer/:id', (req, res) => {
  const recordingId = req.params.id;
  const events = fs.readFileSync(`./recordings/${recordingId}`, 'utf-8').split('\n').filter((event) => event !== '');
  const live = req.query.live === 'true';
  const html = generateReplayerHtml(recordingId, events, live);
  res.send(html);
});

app.get('/dashboard', async(req, res) => {
  res.send(createDashboard(rooms));
});

app.post('/client-disconnect', (req, res) => {  // executed on unload (i.e when refreshing or closing website)
  const { socketId, room } = req.body; // Access the socketId and room from request body
  const socket = sockets[socketId];
  if (!socket) {
    console.log("socket not found");
    return res.sendStatus(404);
  }

  const socketObj = {
    socket,
    isRecorder: true,
    room: room,
  };
  recorderDisconnect(socketObj, rooms);
  socket.disconnect();
  res.sendStatus(200);
});



app.use(express.static(path.join(__dirname, 'public')));

// Handle WebSocket connections
io.use(function(socket, next) {
  if (socket.handshake.query && socket.handshake.query.token) {
    if (socket.handshake.query.token == authToken) {
      next();
    } else {
      return next(new Error('Authentication error'));
    }
  }
}).on('connection', (socket) => {
  sockets[socket.id] = socket;
  // Event handlers for recorder events
  const socketObj = {
    socket,
    isRecorder: false,
    room: null,
  };

  socket.on("recorder-connect", (room) => recorderConnect(room,socketObj, rooms));
  socket.on("recorder-event",(data) => recorderEvent(data,socketObj,rooms,io));
  socket.on("replayer-connect", (room) => replayerConnect(room, socketObj));
  socket.on("disconnect", () => { 
    // currently only do a disconnect if the page unloads
  });

});

server.listen(PORT, '0.0.0.0', () => console.log('Running on', `${protocol}${process.env.URL}:${PORT}`));


