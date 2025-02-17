const generateRecorderHtml = () => `<!DOCTYPE html>

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Fusion Analytics Test Website" />
    <title>RRWEB recorder</title>

    <script src="https://cdn.socket.io/4.4.1/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/rrweb@latest/dist/rrweb-all.min.js"></script>

  </head>
  <body>
    <style> 
      * {
        background-color: aquamarine;
      }
    </style>
    <div id="root">
      <button id="start-recording">Start Recording</button>
      <button id="stop-recording">Stop Recording</button>
      <h1>Video Recorder</h1>

      <form action="/action_page.php">
        <label for="fname">First name:</label>
        <input type="text" id="fname" name="fname" /><br /><br />
        <label for="lname">Last name:</label>
        <input type="text" id="lname" name="lname" /><br /><br />
        <input type="submit" value="Submit" />
      </form>
    </div>
    <script>
      const socket = io("http://localhost:3000");
      let room = null;
      let stopFunction = null;
      document.addEventListener("DOMContentLoaded", () => {
        socket.on("connect", () => {
          document.getElementById('start-recording').addEventListener('click', () => {
            if(!room) {
              //use user id, timestamp or both instead for the filenames
              room = crypto.randomUUID();
              socket.emit("recorder-connect", room);
              stopFunction = rrweb.record({
                emit(event) {
                  socket.emit("recorder-event", { event });
                },
              });
              window.setInterval(() => {
                rrweb.record.addCustomEvent('eye-movement', {
                  name: 'eye-movement',
                  x: Math.random() * 500,
                  y: Math.random() * 500 
                })
              }, 1000);
            } 
          });
          document.getElementById('stop-recording').addEventListener('click', () => {
            if(room) {
              stopFunction();
              room = null;
              socket.emit("recorder-disconnect");
            }
          });
        });
        socket.on("disconnect", () => {
          if(room) {
            stopFunction();
            room = null;
          }
        });
      });
    </script>
  </body>
</html>`

module.exports = { generateRecorderHtml }