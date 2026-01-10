"""
Gemini API 中继路由
用于飞书 Aily 助手调用 Gemini API
"""
import logging
import requests
from flask import Blueprint, request, jsonify
from functools import wraps

# 创建蓝图
gemini_bp = Blueprint('gemini', __name__, url_prefix='/api/gemini')

logger = logging.getLogger(__name__)

# Gemini API 配置
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_API_KEY = None  # 从环境变量读取


def init_gemini_config(app):
    """初始化 Gemini 配置"""
    global GEMINI_API_KEY
    GEMINI_API_KEY = app.config.get('GEMINI_API_KEY')
    if GEMINI_API_KEY:
        logger.info(f"✅ Gemini API 已配置: {GEMINI_API_KEY[:7]}...")
    else:
        logger.warning("⚠️  Gemini API Key 未配置")

    # 检查代理配置
    http_proxy = app.config.get('HTTP_PROXY') or app.config.get('HTTPS_PROXY')
    if http_proxy:
        logger.info(f"✅ 已配置代理: {http_proxy}")
    else:
        logger.info("ℹ️  未配置代理，直接连接 Gemini API")


def handle_errors(f):
    """错误处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Gemini API 错误: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    return decorated_function


@gemini_bp.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "Gemini Relay API",
        "hasApiKey": bool(GEMINI_API_KEY),
        "apiKeyPrefix": GEMINI_API_KEY[:7] + "..." if GEMINI_API_KEY else "not-set"
    })


@gemini_bp.route('/models', methods=['GET'])
def list_models():
    """获取可用模型列表"""
    models = [
        {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "description": "快速响应，适合简单任务"
        },
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "description": "高质量输出，适合复杂任务"
        },
        {
            "id": "gemini-pro",
            "name": "Gemini Pro",
            "description": "通用模型"
        }
    ]
    return jsonify({
        "success": True,
        "models": models
    })


@gemini_bp.route('/generate', methods=['POST'])
@handle_errors
def generate():
    """完整的 Gemini 生成接口"""
    if not GEMINI_API_KEY:
        return jsonify({
            "success": False,
            "error": "服务器配置错误：缺少 Gemini API Key"
        }), 500

    data = request.get_json()
    model = data.get('model', 'gemini-1.5-flash')
    contents = data.get('contents')
    generation_config = data.get('generationConfig', {})
    safety_settings = data.get('safetySettings', [])

    # 验证参数
    if not contents or not isinstance(contents, list) or len(contents) == 0:
        return jsonify({
            "success": False,
            "error": "参数错误：缺少 contents 字段"
        }), 400

    # 构建请求
    api_url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={GEMINI_API_KEY}"

    # 正确构建请求体
    request_body = {"contents": contents}
    if generation_config:
        request_body["generationConfig"] = generation_config
    if safety_settings:
        request_body["safetySettings"] = safety_settings

    logger.info(f"[Gemini] 请求: 模型={model}, 内容长度={len(str(contents))}")

    # 调用 Gemini API
    try:
        # 配置代理
        proxies = None
        http_proxy = app.config.get('HTTP_PROXY') or app.config.get('HTTPS_PROXY') if hasattr(app, 'config') else None
        if http_proxy:
            proxies = {
                'http': http_proxy,
                'https': http_proxy
            }
            logger.info(f"[Gemini] 使用代理: {http_proxy}")

        response = requests.post(
            api_url,
            json=request_body,
            headers={'Content-Type': 'application/json'},
            timeout=60,
            proxies=proxies
        )
        response.raise_for_status()

        result = response.json()
        logger.info(f"[Gemini] 成功: 状态码={response.status_code}")

        return jsonify({
            "success": True,
            "data": result,
            "meta": {
                "model": model,
                "timestamp": requests.utils.iso8601_to_datetime(response.headers.get('Date', ''))
            }
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"[Gemini] API 调用失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Gemini API 调用失败: {str(e)}"
        }), 502


@gemini_bp.route('/aily', methods=['POST'])
@handle_errors
def aily():
    """飞书 Aily 简化接口"""
    if not GEMINI_API_KEY:
        return jsonify({
            "success": False,
            "error": "服务器配置错误：缺少 Gemini API Key"
        }), 500

    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model', 'gemini-1.5-flash')

    if not prompt:
        return jsonify({
            "success": False,
            "error": "缺少 prompt 参数"
        }), 400

    # 构建请求
    api_url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={GEMINI_API_KEY}"
    request_body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    logger.info(f"[Gemini/Aily] 请求: 模型={model}, prompt长度={len(prompt)}")

    try:
        response = requests.post(
            api_url,
            json=request_body,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        response.raise_for_status()

        result = response.json()

        # 提取文本
        text = ""
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0].get('content', {})
            parts = content.get('parts', [])
            if parts and len(parts) > 0:
                text = parts[0].get('text', '')

        logger.info(f"[Gemini/Aily] 成功: 生成文本长度={len(text)}")

        return jsonify({
            "success": True,
            "text": text,
            "fullResponse": result
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"[Gemini/Aily] API 调用失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Gemini API 调用失败: {str(e)}"
        }), 502
