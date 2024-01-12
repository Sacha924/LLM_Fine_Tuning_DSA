// Import the required libraries
const WebSocket = require('ws');
const http = require('http');
const axios = require('axios');
require("dotenv").config()
const {API_KEY} = process.env
const OpenAI = require("openai")
const openai = new OpenAI({ apiKey: API_KEY });


const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('WebSocket server is running');
});

const openAIRequestMYModel = async (message) => {
    try {
        const api_url = "https://api.openai.com/v1/completions";
        const headers = {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${API_KEY}`
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

const openAIRequestGPT4 = async (message) => {
    const completion = await openai.chat.completions.create({
        messages: [
            { "role": "user", "content": `Write an optimized Python function to solve the following problem: ${message}` },],
        model: "gpt-4-1106-preview",
        "max_tokens": 300
    });
    console.log(completion.choices[0])
    console.log(completion.choices[0].message.content);
    return completion.choices[0].message.content
}

const wss = new WebSocket.Server({ server });

wss.on('connection', (ws) => {
    console.log('New client connected!');
    ws.send('Welcome to the chat!');

    ws.on('message', async(message) => {
        console.log(`Received message from client: ${message}`);
        const response = await openAIRequestGPT4(message);
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
