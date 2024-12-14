// index.js
const express = require('express');
const path = require('path');
const WebSocket = require('ws');
var WebSocketServer = require('ws').Server;
var wss = new WebSocketServer({ port: 3001 });

wss.on('connection', function(ws) {
    ws.on('message', function(message) {
         // 如果是 Buffer，转换为字符串
         const buffer = Buffer.from(message);
         const decodedMessage = buffer.toString('utf-8'); // 或者使用其他编码
         console.log('接收到的 Buffer 消息:', decodedMessage);
        console.log(`ws client lenth=${wss.clients.size}`)
         // 广播消息给所有连接的客户端
         wss.clients.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                client.send(decodedMessage);
            }
        });
    });
});
const app = express();
const PORT = 3000;

// 提供静态文件
app.use(express.static(path.join(__dirname)));

// 启动服务器
app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});

