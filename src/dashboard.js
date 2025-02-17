const fs = require('fs');

function createDashboard(rooms) {
  // Retrieve the list of recordings from the recordings directory
  const recordings = fs.readdirSync('./recordings');

  // Separate recordings with and without timestamps
  const recordingsWithTimestamp = recordings.filter(recording => /\d{13}\.log$/.test(recording));
  const recordingsWithoutTimestamp = recordings.filter(recording => !/\d{13}\.log$/.test(recording));

  // Sort recordings with timestamps
  const sortedRecordingsWithTimestamp = recordingsWithTimestamp.sort((a, b) => {
    const timestampA = parseInt(a.match(/(\d{13})\.log$/)[1], 10);
    const timestampB = parseInt(b.match(/(\d{13})\.log$/)[1], 10);
    return timestampA - timestampB;
  });

  // Concatenate sorted recordings with timestamps and recordings without timestamps
  const sortedRecordings = sortedRecordingsWithTimestamp.concat(recordingsWithoutTimestamp);

  // Generate HTML for displaying recordings in the dashboard
  let html = '<h1>Recordings</h1>';
  html += '<ul>';
  sortedRecordings.forEach((recording) => {
    html += `<li><a href="/replayer/${recording}">${recording}</a></li>`;
  });
  html += '</ul>';

  return html;
}

module.exports = { createDashboard };
