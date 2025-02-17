const generateReplayerHtml = (room,events,live) => { 
  const html = `<!DOCTYPE html>

  <html id="${room}" data-live="${live}" lang="en">
    <head>
      <script id="events-json" type="application/json">
        ${JSON.stringify(events)}
      </script>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta name="theme-color" content="#000000" />
      <meta name="description" content="Fusion Analytics Test Website" />
      <title>RRWEB replayer</title>

      <script src="https://cdn.socket.io/4.4.1/socket.io.min.js"></script>
    <link rel="stylesheet"href="https://cdn.jsdelivr.net/npm/rrweb@latest/dist/rrweb.min.css"/>
    <script src="https://cdn.jsdelivr.net/npm/rrweb@latest/dist/rrweb-all.min.js"></script>
    </head>
    <body>

      <script>
      const protocol = window.location.protocol === 'https:' ? 'https' : 'http';
      const socketUrl = protocol + '://' + window.location.hostname + ':8000';
      const socket = io(socketUrl);
      let room = document.querySelector("html").id;
      const eventStrings = JSON.parse(document.querySelector("#events-json").innerHTML);
      const events = eventStrings.map((eventString) => JSON.parse(eventString));
      const live = document.querySelector("html").dataset.live === "true";
      const replayer = new rrweb.Replayer(events, {
        liveMode: live,
        speed : 1,
        unpackFn: (data) => {
          if (data.type === 'custom' && data.data.type === 'system') {
            console.log(data.data.message);
          }
          return data;
        },
      });
      if(live) {
        replayer.startLive();
      } else {
        replayer.play();
      }
      
        socket.on("connect", () => {

          socket.emit("replayer-connect", room);
      
          socket.on("replayer-event", (data) => {
            replayer.addEvent(data);
          });
      });
      </script>
    </body
  </html>`
  return html;
}

module.exports = { generateReplayerHtml }
