// Import the required libraries
const WebSocket = require('ws');
const http = require('http');
const axios = require('axios');

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('WebSocket server is running');
});

const openAIRequest = async (message) => {
    try {
        const api_url = "https://api.openai.com/v1/completions";
        const headers = {
            "Content-Type": "application/json",
            "Authorization": `Bearer OPEN API KEY`
        };

        // Ensure message is a string
        const promptMessage = typeof message === 'string' ? message : new TextDecoder().decode(message);

        const data = {
            "model": "ft:davinci-002:personal:sacha-dsa-v1:8cH2wbef",
            "prompt": promptMessage,
            "max_tokens": 100
        };

        const response = await axios.post(api_url, data, { headers });
        return response.data.choices[0].text;
    } catch (error) {
        console.error("Error with OpenAI API request:", error);
        return "An error occurred while processing your request.";
    }
};


const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    console.log('New client connected!');
    ws.send('Welcome to the chat!');

    ws.on('message', async(message) => {
        console.log(`Received message from client: ${message}`);
        const response = await openAIRequest(message);
        console.log("here" + response)
        ws.send(response);
    });

    ws.on('close', () => {
        console.log('Client has disconnected');
    });
});


server.listen(8080, () => {
    console.log('Server is listening on port 8080');
});
