const fs =  require('fs');

const recorderConnect = (room,socketObj,rooms) => {
    socketObj.isRecorder = true;
    socketObj.room = room;
    socketObj.socket.join(room);
    const stream = fs.createWriteStream(`./recordings/${room}.log`, { flags: 'a' });
    rooms[room] = stream; 
};

const recorderEvent = (data,socketObj,rooms,io) => {
    if(rooms[socketObj.room]) {
        rooms[socketObj.room].write(`${JSON.stringify(data.event)}\n`);
        io.to(socketObj.room).emit("replayer-event", data.event);
    }
};

const recorderDisconnect = (socketObj, rooms) => {
    if (!rooms[socketObj.room]) return;
    const endEvent = { //append ending message to logfile to verify proper recording disconnection
        type: 'custom',
        data: {
            type: 'system',
            message: 'Recording stopped successfully',
        },
        timestamp: Date.now(),
    };

    rooms[socketObj.room].write(`${JSON.stringify(endEvent)}\n`, () => {
        rooms[socketObj.room].end();
        delete rooms[socketObj.room];
    });
};
module.exports =  { recorderDisconnect, recorderEvent,recorderConnect }