"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("dotenv/config");
const tools_1 = require("@ai-spine/tools");
const faceProxyTool = (0, tools_1.createTool)({
    metadata: {
        name: 'face-proxy-tool',
        version: '1.0.0',
        description: 'Proxy tool that connects to Python Face Recognition Agent',
        capabilities: ['face-recognition'],
        author: 'Your Name',
        license: 'MIT',
    },
    schema: {
        input: {
            face_image: (0, tools_1.stringField)({
                required: true,
                description: 'Base64 encoded face image',
            }),
            user_id: (0, tools_1.stringField)({
                required: true,
                description: 'User ID for matching',
            }),
        },
        config: {
            python_url: {
                type: 'string',
                required: false,
                description: 'Base URL of the Python service',
                default: 'http://localhost:3000',
            },
        },
    },
    async execute(input, config, context) {
        const url = `${config.python_url}/execute`;
        try {
            // Enviar solo los campos que FastAPI espera
            const payload = {
                face_image: input.face_image,
                user_id: input.user_id,
            };
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                throw new Error(`Python service error: ${response.statusText}`);
            }
            const result = await response.json();
            return {
                status: 'success',
                data: result,
            };
        }
        catch (err) {
            console.error("Python service call failed:", err);
            return {
                status: 'error',
                message: `Failed to call Python face agent: ${err.message}`,
            };
        }
    },
});
// Start the tool server
if (require.main === module) {
    faceProxyTool.start({
        port: process.env.PORT ? parseInt(process.env.PORT) : 4000,
        host: process.env.HOST || '0.0.0.0',
    });
}
exports.default = faceProxyTool;
//# sourceMappingURL=index.js.map