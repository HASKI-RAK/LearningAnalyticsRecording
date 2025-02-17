const replayerConnect = (room,socketObj) => {
    socketObj.socket.join(room);
}

module.exports = { replayerConnect }