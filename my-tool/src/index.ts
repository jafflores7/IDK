import 'dotenv/config';
import { createTool, stringField } from '@ai-spine/tools';

interface ProxyInput {
  face_image: string; // base64 face image
  user_id: string;    // user identifier
}

interface ProxyConfig {
  python_url?: string; // URL of the Python face service
}

const faceProxyTool = createTool<ProxyInput, ProxyConfig>({
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
      face_image: stringField({
        required: true,
        description: 'Base64 encoded face image',
      }),
      user_id: stringField({
        required: true,
        description: 'User ID for matching',
      }),
    },
    config: {
      python_url: {
        type: 'string',
        required: false,
        description: 'Base URL of the Python service',
        default: 'http://127.0.0.1:3000',
      },
    },
  },

  async execute(input, config, context) {
    const url = `${config.python_url}/execute`;

    try {
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

      // 🔥 Print Python response for debugging/logging
      console.log("🔎 Face verification result:", JSON.stringify(result, null, 2));

      return {
        status: 'success',
        data: result, // keep the Python response in your tool output
      };
    } catch (err) {
      console.error("Python service call failed:", err);
      return {
        status: 'error',
        message: `Failed to call Python face agent: ${(err as Error).message}`,
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

export default faceProxyTool;