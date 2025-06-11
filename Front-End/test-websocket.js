// Simple WebSocket test script
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8765');

ws.on('open', function open() {
  console.log('✅ WebSocket connection opened');
  
  // Send authentication message with correct format
  const authMessage = {
    type: 'auth',
    user_id: 'test-user-123',
    timestamp: new Date().toISOString()
  };
  
  console.log('📤 Sending auth message:', JSON.stringify(authMessage, null, 2));
  ws.send(JSON.stringify(authMessage));
});

ws.on('message', function message(data) {
  try {
    const parsed = JSON.parse(data.toString());
    console.log('📥 Received message:', JSON.stringify(parsed, null, 2));
  } catch (error) {
    console.log('📥 Received raw message:', data.toString());
  }
});

ws.on('error', function error(err) {
  console.error('❌ WebSocket error:', err.message);
});

ws.on('close', function close(code, reason) {
  console.log('🔌 WebSocket connection closed:', code, reason.toString());
});

// Send a ping after 2 seconds
setTimeout(() => {
  if (ws.readyState === WebSocket.OPEN) {
    const pingMessage = {
      type: 'ping',
      timestamp: new Date().toISOString()
    };
    console.log('📤 Sending ping message:', JSON.stringify(pingMessage, null, 2));
    ws.send(JSON.stringify(pingMessage));
  }
}, 2000);

// Close connection after 10 seconds
setTimeout(() => {
  console.log('🔚 Closing connection...');
  ws.close();
}, 10000);
