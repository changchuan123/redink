"""
Gemini API 中继路由
用于飞书 Aily 助手调用 Gemini API
使用 Google GenAI Python SDK
"""
import logging
from flask import Blueprint, request, jsonify, current_app
from google import genai
from functools import wraps

# 创建蓝图
gemini_bp = Blueprint('gemini', __name__, url_prefix='/api/gemini')

logger = logging.getLogger(__name__)


def init_gemini_config(app):
    """初始化 Gemini 配置"""
    api_key = app.config.get('GEMINI_API_KEY')
    if api_key:
        logger.info(f"✅ Gemini API 已配置: {api_key[:7]}...")
    else:
        logger.warning("⚠️  Gemini API Key 未配置")


def get_genai_client():
    """获取 Gemini 客户端"""
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return None
    return genai.Client(api_key=api_key, vertexai=False)


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
    api_key = current_app.config.get('GEMINI_API_KEY')
    return jsonify({
        "status": "ok",
        "service": "Gemini Relay API",
        "hasApiKey": bool(api_key),
        "apiKeyPrefix": api_key[:7] + "..." if api_key else "not-set"
    })


@gemini_bp.route('/models', methods=['GET'])
def list_models():
    """获取可用模型列表"""
    models = [
        {
            "id": "gemini-3-pro-preview",
            "name": "Gemini 3 Pro Preview",
            "description": "最新 Gemini 3 模型，高质量输出"
        },
        {
            "id": "gemini-2.5-flash-preview",
            "name": "Gemini 2.5 Flash Preview",
            "description": "快速响应，适合简单任务"
        },
        {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "description": "高质量输出，适合复杂任务"
        },
        {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "description": "快速响应模型"
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
    client = get_genai_client()
    if not client:
        return jsonify({
            "success": False,
            "error": "服务器配置错误：缺少 Gemini API Key"
        }), 500

    data = request.get_json()
    model = data.get('model', 'gemini-3-pro-preview')
    contents = data.get('contents')

    # 验证参数
    if not contents or not isinstance(contents, list) or len(contents) == 0:
        return jsonify({
            "success": False,
            "error": "参数错误：缺少 contents 字段"
        }), 400

    logger.info(f"[Gemini] 请求: 模型={model}, 内容长度={len(str(contents))}")

    try:
        # 使用 Google GenAI SDK 调用
        response = client.models.generate_content(
            model=model,
            contents=contents
        )

        logger.info(f"[Gemini] 成功: 状态=完成")

        # 构建响应
        result = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": response.text}],
                        "role": response.candidates[0].content.role if response.candidates else "model"
                    },
                    "finishReason": response.candidates[0].finish_reason.name if response.candidates else "STOP"
                }
            ]
        }

        return jsonify({
            "success": True,
            "data": result,
            "meta": {
                "model": model,
                "text": response.text
            }
        })

    except Exception as e:
        logger.error(f"[Gemini] API 调用失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Gemini API 调用失败: {str(e)}"
        }), 502


@gemini_bp.route('/aily', methods=['POST'])
@handle_errors
def aily():
    """飞书 Aily 简化接口"""
    client = get_genai_client()
    if not client:
        return jsonify({
            "success": False,
            "error": "服务器配置错误：缺少 Gemini API Key"
        }), 500

    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model', 'gemini-3-pro-preview')

    if not prompt:
        return jsonify({
            "success": False,
            "error": "缺少 prompt 参数"
        }), 400

    logger.info(f"[Gemini/Aily] 请求: 模型={model}, prompt长度={len(prompt)}")

    try:
        # 使用 Google GenAI SDK 调用
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        text = response.text if response else ""
        logger.info(f"[Gemini/Aily] 成功: 生成文本长度={len(text)}")

        return jsonify({
            "success": True,
            "text": text,
            "model": model
        })

    except Exception as e:
        logger.error(f"[Gemini/Aily] API 调用失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Gemini API 调用失败: {str(e)}"
        }), 502
