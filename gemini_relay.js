import express from 'express';
import axios from 'axios';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import morgan from 'morgan';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// 信任 Zeabur 的反向代理
app.set('trust proxy', true);

// Gemini API 配置
const GEMINI_API_BASE = 'https://generativelanguage.googleapis.com/v1beta';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

// 安全中间件
app.use(helmet());
app.use(cors({
  origin: '*', // 生产环境建议限制为飞书域名
  methods: ['POST', 'GET'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// 速率限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100, // 限制每个 IP 15 分钟内最多 100 次请求
  message: {
    error: '请求过于频繁，请稍后再试'
  }
});
app.use('/api/', limiter);

// 日志
app.use(morgan('combined'));

// 解析请求体
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 健康检查
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'Gemini Relay API',
    config: {
      hasApiKey: !!GEMINI_API_KEY,
      apiKeyPrefix: GEMINI_API_KEY ? GEMINI_API_KEY.substring(0, 7) + '...' : 'not-set',
      port: PORT
    }
  });
});

// 根路径
app.get('/', (req, res) => {
  res.json({
    service: 'Gemini Relay API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      generate: '/api/generate',
      aily: '/api/aily',
      image: '/api/image',
      models: '/api/models'
    },
    docs: 'https://github.com/your-repo/gemini-relay-api'
  });
});

// 获取可用模型列表
app.get('/api/models', async (req, res) => {
  try {
    const models = [
      {
        id: 'gemini-2.5-pro',
        name: 'Gemini 2.5 Pro',
        description: '最强大的推理模型，最高答案准确率',
        type: 'text'
      },
      {
        id: 'gemini-3-pro-preview',
        name: 'Gemini 3 Pro Preview',
        description: '最新推理优先模型，支持复杂代理工作流',
        type: 'text',
        default: true
      },
      {
        id: 'gemini-2.5-flash',
        name: 'Gemini 2.5 Flash',
        description: '快速响应，平衡性能与速度',
        type: 'text'
      },
      {
        id: 'gemini-2.0-flash-exp',
        name: 'Gemini 2.0 Flash Experimental',
        description: '实验性快速模型',
        type: 'text'
      },
      {
        id: 'gemini-1.5-pro',
        name: 'Gemini 1.5 Pro',
        description: '高质量输出，适合复杂任务',
        type: 'text'
      },
      {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        description: '快速响应，适合简单任务',
        type: 'text'
      },
      {
        id: 'gemini-3-pro-image-preview',
        name: 'Gemini 3 Pro Image Preview',
        description: '图像生成模型',
        type: 'image',
        default: true
      }
    ];

    res.json({
      success: true,
      models
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: '获取模型列表失败'
    });
  }
});

// 核心中继接口
app.post('/api/generate', async (req, res) => {
  const startTime = Date.now();

  try {
    const {
      model = 'gemini-3-pro-preview',
      contents,
      generationConfig = {},
      safetySettings = []
    } = req.body;

    // 验证必要参数
    if (!GEMINI_API_KEY) {
      return res.status(500).json({
        success: false,
        error: '服务器配置错误：缺少 Gemini API Key'
      });
    }

    if (!contents || !Array.isArray(contents) || contents.length === 0) {
      return res.status(400).json({
        success: false,
        error: '参数错误：缺少 contents 字段'
      });
    }

    // 构建请求 URL
    const apiUrl = `${GEMINI_API_BASE}/models/${model}:generateContent?key=${GEMINI_API_KEY}`;

    // 构建请求体
    const requestBody = {
      contents,
      ...(generationConfig && { generationConfig }),
      ...(safetySettings.length > 0 && { safetySettings })
    };

    console.log(`[请求] 模型: ${model}, 内容长度: ${JSON.stringify(contents).length}`);
    console.log(`[请求] API URL: ${apiUrl.replace(GEMINI_API_KEY, '***')}`);

    // 调用 Gemini API
    const axiosConfig = {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 60000 // 60 秒超时
    };

    // 如果配置了代理，使用代理
    if (process.env.HTTP_PROXY || process.env.HTTPS_PROXY) {
      axiosConfig.proxy = {
        host: process.env.HTTP_PROXY?.split('://')[1]?.split(':')[0] || process.env.HTTPS_PROXY?.split('://')[1]?.split(':')[0],
        port: parseInt(process.env.HTTP_PROXY?.split(':')[2] || process.env.HTTPS_PROXY?.split(':')[2] || '8080')
      };
      console.log(`[代理] 使用代理: ${axiosConfig.proxy.host}:${axiosConfig.proxy.port}`);
    }

    const response = await axios.post(apiUrl, requestBody, axiosConfig);

    const duration = Date.now() - startTime;
    console.log(`[成功] 耗时: ${duration}ms`);

    // 返回标准化响应
    res.json({
      success: true,
      data: response.data,
      meta: {
        model,
        duration: `${duration}ms`,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`[错误] 耗时: ${duration}ms`);
    console.error(`[错误] 类型: ${error.code || 'UNKNOWN'}`);
    console.error(`[错误] 消息: ${error.message}`);
    if (error.response) {
      console.error(`[错误] 状态码: ${error.response.status}`);
      console.error(`[错误] 响应:`, JSON.stringify(error.response.data));
    }

    // 处理不同类型的错误
    if (error.response) {
      // API 返回了错误响应
      return res.status(error.response.status).json({
        success: false,
        error: error.response.data?.error?.message || 'Gemini API 错误',
        details: error.response.data
      });
    } else if (error.request) {
      // 请求发送但没有收到响应
      return res.status(503).json({
        success: false,
        error: '无法连接到 Gemini API，请检查网络',
        details: error.message
      });
    } else {
      // 其他错误
      return res.status(500).json({
        success: false,
        error: '服务器内部错误',
        details: error.message
      });
    }
  }
});

// 飞书 Aily 专用接口（简化版）
app.post('/api/aily', async (req, res) => {
  const startTime = Date.now();

  try {
    const { prompt, model = 'gemini-3-pro-preview' } = req.body;

    if (!prompt) {
      return res.status(400).json({
        success: false,
        error: '缺少 prompt 参数'
      });
    }

    // 验证 API Key
    if (!GEMINI_API_KEY) {
      return res.status(500).json({
        success: false,
        error: '服务器配置错误：缺少 Gemini API Key'
      });
    }

    // 直接调用 Gemini API（不通过 localhost 转发）
    const apiUrl = `${GEMINI_API_BASE}/models/${model}:generateContent?key=${GEMINI_API_KEY}`;
    const requestBody = {
      contents: [
        {
          parts: [
            { text: prompt }
          ]
        }
      ]
    };

    console.log(`[Aily] 请求: 模型=${model}, prompt长度=${prompt.length}`);

    const axiosConfig = {
      headers: { 'Content-Type': 'application/json' },
      timeout: 60000
    };

    const response = await axios.post(apiUrl, requestBody, axiosConfig);

    const duration = Date.now() - startTime;
    console.log(`[Aily] 成功: 耗时=${duration}ms`);

    // 提取文本内容
    const text = response.data.candidates?.[0]?.content?.parts?.[0]?.text || '';

    res.json({
      success: true,
      text,
      fullResponse: response.data
    });

  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`[Aily] 错误: ${duration}ms`, error.message);

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        error: error.response.data?.error?.message || 'Gemini API 错误',
        details: error.response.data
      });
    }

    res.status(500).json({
      success: false,
      error: error.message || '服务器内部错误'
    });
  }
});

// 图像生成接口
app.post('/api/image', async (req, res) => {
  const startTime = Date.now();

  try {
    const { prompt, model = 'gemini-3-pro-image-preview' } = req.body;

    if (!prompt) {
      return res.status(400).json({
        success: false,
        error: '缺少 prompt 参数'
      });
    }

    // 验证 API Key
    if (!GEMINI_API_KEY) {
      return res.status(500).json({
        success: false,
        error: '服务器配置错误：缺少 Gemini API Key'
      });
    }

    // 使用 Gemini 图像生成 API (generateContent)
    const apiUrl = `${GEMINI_API_BASE}/models/${model}:generateContent?key=${GEMINI_API_KEY}`;

    const requestBody = {
      contents: [
        {
          parts: [
            { text: prompt }
          ]
        }
      ],
      generationConfig: {
        responseMimeType: "image/png",
        responseModalities: ["IMAGE", "TEXT"]
      }
    };

    console.log(`[Image] 请求: 模型=${model}, prompt长度=${prompt.length}`);

    const axiosConfig = {
      headers: { 'Content-Type': 'application/json' },
      timeout: 120000 // 图像生成超时时间设置为 2 分钟
    };

    const response = await axios.post(apiUrl, requestBody, axiosConfig);

    const duration = Date.now() - startTime;
    console.log(`[Image] 成功: 耗时=${duration}ms`);

    // 提取图像数据（base64 格式）
    let imageData = '';
    const parts = response.data.candidates?.[0]?.content?.parts || [];

    for (const part of parts) {
      if (part.inlineData) {
        imageData = part.inlineData.data;
        break;
      }
    }

    if (!imageData) {
      throw new Error('无法从响应中提取图像数据');
    }

    res.json({
      success: true,
      image: imageData,
      mimeType: 'image/png',
      dataUrl: `data:image/png;base64,${imageData}`,
      fullResponse: response.data
    });

  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`[Image] 错误: ${duration}ms`, error.message);

    if (error.response) {
      return res.status(error.response.status).json({
        success: false,
        error: error.response.data?.error?.message || 'Gemini API 错误',
        details: error.response.data
      });
    }

    res.status(500).json({
      success: false,
      error: error.message || '服务器内部错误'
    });
  }
});

// 404 处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: '接口不存在',
    path: req.path
  });
});

// 全局错误处理
app.use((err, req, res, next) => {
  console.error('未捕获的错误:', err);
  res.status(500).json({
    success: false,
    error: '服务器内部错误',
    message: err.message
  });
});

// 启动服务器
app.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔════════════════════════════════════════╗
║   Gemini Relay API 服务已启动          ║
╚════════════════════════════════════════╝

🚀 服务地址: http://0.0.0.0:${PORT}
📖 API 文档: http://0.0.0.0:${PORT}/
💊 健康检查: http://0.0.0.0:${PORT}/health

📝 可用接口:
  - POST /api/generate  (完整功能)
  - POST /api/aily      (飞书 Aily 简化版)
  - POST /api/image     (图像生成)
  - GET  /api/models    (模型列表)

⏰ 启动时间: ${new Date().toLocaleString('zh-CN')}
  `);
});
