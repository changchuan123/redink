"""API 路由"""
import json
import logging
import os
import time
import traceback
import zipfile
import io
from flask import Blueprint, request, jsonify, Response, send_file
from backend.services.outline import get_outline_service
from backend.services.image import get_image_service
from backend.services.history import get_history_service
from backend.services.sync_service import get_sync_service

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _log_request(endpoint: str, data: dict = None):
    """记录请求日志"""
    logger.info(f"📥 收到请求: {endpoint}")
    if data:
        # 过滤敏感信息和大数据
        safe_data = {k: v for k, v in data.items() if k not in ['images', 'user_images'] and not isinstance(v, bytes)}
        if 'images' in data:
            safe_data['images'] = f"[{len(data['images'])} 张图片]"
        if 'user_images' in data:
            safe_data['user_images'] = f"[{len(data['user_images'])} 张图片]"
        logger.debug(f"  请求数据: {safe_data}")


def _log_error(endpoint: str, error: Exception):
    """记录错误日志"""
    logger.error(f"❌ 请求失败: {endpoint}")
    logger.error(f"  错误类型: {type(error).__name__}")
    logger.error(f"  错误信息: {str(error)}")
    logger.debug(f"  堆栈跟踪:\n{traceback.format_exc()}")


@api_bp.route('/outline', methods=['POST'])
def generate_outline():
    """生成大纲（支持图片上传）"""
    start_time = time.time()
    try:
        # 检查是否是 multipart/form-data（带图片）
        if request.content_type and 'multipart/form-data' in request.content_type:
            topic = request.form.get('topic')
            # 获取上传的图片
            images = []
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file and file.filename:
                        image_data = file.read()
                        images.append(image_data)
            _log_request('/outline', {'topic': topic, 'images': images})
        else:
            # JSON 请求（无图片或 base64 图片）
            data = request.get_json()
            topic = data.get('topic')
            # 支持 base64 格式的图片
            images_base64 = data.get('images', [])
            images = []
            if images_base64:
                import base64
                for img_b64 in images_base64:
                    # 移除可能的 data URL 前缀
                    if ',' in img_b64:
                        img_b64 = img_b64.split(',')[1]
                    images.append(base64.b64decode(img_b64))
            _log_request('/outline', {'topic': topic, 'images': images})

        if not topic:
            logger.warning("大纲生成请求缺少 topic 参数")
            return jsonify({
                "success": False,
                "error": "参数错误：topic 不能为空。\n请提供要生成图文的主题内容。"
            }), 400

        # 调用大纲生成服务
        logger.info(f"🔄 开始生成大纲，主题: {topic[:50]}...")
        outline_service = get_outline_service()
        result = outline_service.generate_outline(topic, images if images else None)

        elapsed = time.time() - start_time
        if result["success"]:
            logger.info(f"✅ 大纲生成成功，耗时 {elapsed:.2f}s，共 {len(result.get('pages', []))} 页")
            return jsonify(result), 200
        else:
            logger.error(f"❌ 大纲生成失败: {result.get('error', '未知错误')}")
            return jsonify(result), 500

    except Exception as e:
        _log_error('/outline', e)
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"大纲生成异常。\n错误详情: {error_msg}\n建议：检查后端日志获取更多信息"
        }), 500


@api_bp.route('/generate', methods=['POST'])
def generate_images():
    """生成图片（SSE 流式返回，支持用户上传参考图片）"""
    try:
        # JSON 请求
        data = request.get_json()
        pages = data.get('pages')
        task_id = data.get('task_id')
        full_outline = data.get('full_outline', '')
        user_topic = data.get('user_topic', '')  # 用户原始输入
        # 支持 base64 格式的用户参考图片
        user_images_base64 = data.get('user_images', [])
        user_images = []
        if user_images_base64:
            import base64
            for img_b64 in user_images_base64:
                if ',' in img_b64:
                    img_b64 = img_b64.split(',')[1]
                user_images.append(base64.b64decode(img_b64))

        _log_request('/generate', {
            'pages_count': len(pages) if pages else 0,
            'task_id': task_id,
            'user_topic': user_topic[:50] if user_topic else None,
            'user_images': user_images
        })

        if not pages:
            logger.warning("图片生成请求缺少 pages 参数")
            return jsonify({
                "success": False,
                "error": "参数错误：pages 不能为空。\n请提供要生成的页面列表数据。"
            }), 400

        # 获取图片生成服务
        logger.info(f"🖼️  开始图片生成任务: {task_id}, 共 {len(pages)} 页")
        image_service = get_image_service()

        def generate():
            """SSE 生成器"""
            for event in image_service.generate_images(
                pages, task_id, full_outline,
                user_images=user_images if user_images else None,
                user_topic=user_topic
            ):
                event_type = event["event"]
                event_data = event["data"]

                # 格式化为 SSE 格式
                yield f"event: {event_type}\n"
                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )

    except Exception as e:
        _log_error('/generate', e)
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"图片生成异常。\n错误详情: {error_msg}\n建议：检查图片生成服务配置和后端日志"
        }), 500


@api_bp.route('/images/<task_id>/<filename>', methods=['GET'])
def get_image(task_id, filename):
    """获取图片（支持缩略图）"""
    try:
        logger.debug(f"获取图片: {task_id}/{filename}")
        # 检查是否请求缩略图
        thumbnail = request.args.get('thumbnail', 'true').lower() == 'true'

        # 直接构建路径，不需要初始化 ImageService
        history_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "history"
        )

        if thumbnail:
            # 尝试返回缩略图
            thumb_filename = f"thumb_{filename}"
            thumb_filepath = os.path.join(history_root, task_id, thumb_filename)

            # 如果缩略图存在，返回缩略图
            if os.path.exists(thumb_filepath):
                return send_file(thumb_filepath, mimetype='image/png')

        # 返回原图
        filepath = os.path.join(history_root, task_id, filename)

        if not os.path.exists(filepath):
            return jsonify({
                "success": False,
                "error": f"图片不存在：{task_id}/{filename}"
            }), 404

        return send_file(filepath, mimetype='image/png')

    except Exception as e:
        _log_error('/images', e)
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"获取图片失败: {error_msg}"
        }), 500


@api_bp.route('/retry', methods=['POST'])
def retry_single_image():
    """重试生成单张图片"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        page = data.get('page')
        use_reference = data.get('use_reference', True)

        _log_request('/retry', {'task_id': task_id, 'page_index': page.get('index') if page else None})

        if not task_id or not page:
            logger.warning("重试请求缺少必要参数")
            return jsonify({
                "success": False,
                "error": "参数错误：task_id 和 page 不能为空。\n请提供任务ID和页面信息。"
            }), 400

        logger.info(f"🔄 重试生成图片: task={task_id}, page={page.get('index')}")
        image_service = get_image_service()
        result = image_service.retry_single_image(task_id, page, use_reference)

        if result["success"]:
            logger.info(f"✅ 图片重试成功: {result.get('image_url')}")
        else:
            logger.error(f"❌ 图片重试失败: {result.get('error')}")

        return jsonify(result), 200 if result["success"] else 500

    except Exception as e:
        _log_error('/retry', e)
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"重试图片生成失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/retry-failed', methods=['POST'])
def retry_failed_images():
    """批量重试失败的图片（SSE 流式返回）"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        pages = data.get('pages')

        _log_request('/retry-failed', {'task_id': task_id, 'pages_count': len(pages) if pages else 0})

        if not task_id or not pages:
            logger.warning("批量重试请求缺少必要参数")
            return jsonify({
                "success": False,
                "error": "参数错误：task_id 和 pages 不能为空。\n请提供任务ID和要重试的页面列表。"
            }), 400

        logger.info(f"🔄 批量重试失败图片: task={task_id}, 共 {len(pages)} 页")
        image_service = get_image_service()

        def generate():
            """SSE 生成器"""
            for event in image_service.retry_failed_images(task_id, pages):
                event_type = event["event"]
                event_data = event["data"]

                yield f"event: {event_type}\n"
                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )

    except Exception as e:
        _log_error('/retry-failed', e)
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"批量重试失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/regenerate', methods=['POST'])
def regenerate_image():
    """重新生成图片（即使成功的也可以重新生成）"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        page = data.get('page')
        use_reference = data.get('use_reference', True)
        full_outline = data.get('full_outline', '')
        user_topic = data.get('user_topic', '')

        _log_request('/regenerate', {'task_id': task_id, 'page_index': page.get('index') if page else None})

        if not task_id or not page:
            logger.warning("重新生成请求缺少必要参数")
            return jsonify({
                "success": False,
                "error": "参数错误：task_id 和 page 不能为空。\n请提供任务ID和页面信息。"
            }), 400

        logger.info(f"🔄 重新生成图片: task={task_id}, page={page.get('index')}")
        image_service = get_image_service()
        result = image_service.regenerate_image(
            task_id, page, use_reference,
            full_outline=full_outline,
            user_topic=user_topic
        )

        if result["success"]:
            logger.info(f"✅ 图片重新生成成功: {result.get('image_url')}")
        else:
            logger.error(f"❌ 图片重新生成失败: {result.get('error')}")

        return jsonify(result), 200 if result["success"] else 500

    except Exception as e:
        _log_error('/regenerate', e)
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"重新生成图片失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/task/<task_id>', methods=['GET'])
def get_task_state(task_id):
    """获取任务状态"""
    try:
        image_service = get_image_service()
        state = image_service.get_task_state(task_id)

        if state is None:
            return jsonify({
                "success": False,
                "error": f"任务不存在：{task_id}\n可能原因：\n1. 任务ID错误\n2. 任务已过期或被清理\n3. 服务重启导致状态丢失"
            }), 404

        # 不返回封面图片数据（太大）
        safe_state = {
            "generated": state.get("generated", {}),
            "failed": state.get("failed", {}),
            "has_cover": state.get("cover_image") is not None
        }

        return jsonify({
            "success": True,
            "state": safe_state
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"获取任务状态失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "success": True,
        "message": "服务正常运行"
    }), 200


# ==================== 历史记录相关 API ====================

@api_bp.route('/history', methods=['POST'])
def create_history():
    """创建历史记录"""
    try:
        data = request.get_json()
        topic = data.get('topic')
        outline = data.get('outline')
        task_id = data.get('task_id')

        if not topic or not outline:
            return jsonify({
                "success": False,
                "error": "参数错误：topic 和 outline 不能为空。\n请提供主题和大纲内容。"
            }), 400

        history_service = get_history_service()
        record_id = history_service.create_record(topic, outline, task_id)

        return jsonify({
            "success": True,
            "record_id": record_id
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"创建历史记录失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history', methods=['GET'])
def list_history():
    """获取历史记录列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status')

        history_service = get_history_service()
        result = history_service.list_records(page, page_size, status)

        return jsonify({
            "success": True,
            **result
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"获取历史记录列表失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/<record_id>', methods=['GET'])
def get_history(record_id):
    """获取历史记录详情"""
    try:
        history_service = get_history_service()
        record = history_service.get_record(record_id)

        if not record:
            return jsonify({
                "success": False,
                "error": f"历史记录不存在：{record_id}\n可能原因：记录已被删除或ID错误"
            }), 404

        return jsonify({
            "success": True,
            "record": record
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"获取历史记录详情失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/<record_id>', methods=['PUT'])
def update_history(record_id):
    """更新历史记录"""
    try:
        data = request.get_json()
        outline = data.get('outline')
        images = data.get('images')
        status = data.get('status')
        thumbnail = data.get('thumbnail')

        logger.info(f"📝 收到历史记录更新请求: record_id={record_id}, status={status}")
        if images:
            logger.info(f"   图片信息: task_id={images.get('task_id')}, generated_count={len(images.get('generated', []))}")

        history_service = get_history_service()
        success = history_service.update_record(
            record_id,
            outline=outline,
            images=images,
            status=status,
            thumbnail=thumbnail
        )

        if not success:
            logger.error(f"❌ 更新历史记录失败: {record_id}")
            return jsonify({
                "success": False,
                "error": f"更新历史记录失败：{record_id}\n可能原因：记录不存在或数据格式错误"
            }), 404

        logger.info(f"✅ 历史记录更新成功: {record_id}")

        # 如果状态为 completed，自动触发同步到 Notion
        if status == 'completed':
            logger.info(f"📋 检测到历史记录状态更新为 completed: {record_id}")
            try:
                sync_service = get_sync_service()
                logger.debug(f"同步服务状态: enabled={sync_service.enabled if sync_service else None}, service={sync_service is not None}")
                
                if sync_service and sync_service.enabled:
                    # 异步触发同步（不阻塞响应）
                    import threading
                    def sync_async():
                        try:
                            logger.info(f"🔄 开始同步记录到 Notion: {record_id}")
                            result = sync_service.sync_record_to_notion(record_id)
                            if result.get("success"):
                                logger.info(f"✅ 记录 {record_id} 自动同步成功")
                                logger.info(f"   - COS URLs: {len(result.get('cos_urls', []))} 张图片")
                                logger.info(f"   - Notion 页面: {result.get('notion_page_url', 'N/A')}")
                            else:
                                logger.warning(f"⚠️  记录 {record_id} 自动同步失败: {result.get('error')}")
                        except Exception as e:
                            logger.error(f"❌ 记录 {record_id} 自动同步异常: {e}", exc_info=True)
                    
                    thread = threading.Thread(target=sync_async, daemon=True)
                    thread.start()
                    logger.info(f"🔄 已触发记录 {record_id} 的自动同步（后台异步执行）")
                else:
                    if not sync_service:
                        logger.warning(f"⚠️  同步服务未初始化，跳过同步: {record_id}")
                    elif not sync_service.enabled:
                        logger.warning(f"⚠️  同步服务已禁用，跳过同步: {record_id}")
            except Exception as e:
                logger.error(f"❌ 触发自动同步失败: {e}", exc_info=True)

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"更新历史记录失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/<record_id>', methods=['DELETE'])
def delete_history(record_id):
    """删除历史记录"""
    try:
        history_service = get_history_service()
        success = history_service.delete_record(record_id)

        if not success:
            return jsonify({
                "success": False,
                "error": f"删除历史记录失败：{record_id}\n可能原因：记录不存在或ID错误"
            }), 404

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"删除历史记录失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/search', methods=['GET'])
def search_history():
    """搜索历史记录"""
    try:
        keyword = request.args.get('keyword', '')

        if not keyword:
            return jsonify({
                "success": False,
                "error": "参数错误：keyword 不能为空。\n请提供搜索关键词。"
            }), 400

        history_service = get_history_service()
        results = history_service.search_records(keyword)

        return jsonify({
            "success": True,
            "records": results
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"搜索历史记录失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/stats', methods=['GET'])
def get_history_stats():
    """获取历史记录统计"""
    try:
        history_service = get_history_service()
        stats = history_service.get_statistics()

        return jsonify({
            "success": True,
            **stats
        }), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"获取历史记录统计失败。\n错误详情: {error_msg}"
        }), 500


# ==================== 同步相关 API ====================

@api_bp.route('/sync/<record_id>', methods=['POST'])
def sync_to_notion(record_id):
    """手动同步历史记录到 Notion"""
    try:
        _log_request('/sync', {'record_id': record_id})

        sync_service = get_sync_service()
        if not sync_service or not sync_service.enabled:
            return jsonify({
                "success": False,
                "error": "同步服务未启用或未配置"
            }), 400

        logger.info(f"🔄 开始同步记录到 Notion: {record_id}")
        result = sync_service.sync_record_to_notion(record_id)

        if result.get("success"):
            logger.info(f"✅ 同步成功: {record_id}")
            return jsonify({
                "success": True,
                "cos_urls": result.get("cos_urls", []),
                "notion_page_id": result.get("notion_page_id"),
                "notion_page_url": result.get("notion_page_url")
            }), 200
        else:
            logger.error(f"❌ 同步失败: {result.get('error')}")
            return jsonify({
                "success": False,
                "error": result.get("error", "同步失败")
            }), 500

    except Exception as e:
        _log_error('/sync', e)
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"同步失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/scan/<task_id>', methods=['GET'])
def scan_task(task_id):
    """扫描单个任务并同步图片列表"""
    try:
        history_service = get_history_service()
        result = history_service.scan_and_sync_task_images(task_id)

        if not result.get("success"):
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"扫描任务失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/scan-all', methods=['POST'])
def scan_all_tasks():
    """扫描所有任务并同步图片列表"""
    try:
        history_service = get_history_service()
        result = history_service.scan_all_tasks()

        if not result.get("success"):
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"扫描所有任务失败。\n错误详情: {error_msg}"
        }), 500


@api_bp.route('/history/<record_id>/download', methods=['GET'])
def download_history_zip(record_id):
    """下载历史记录的所有图片为 ZIP 文件"""
    try:
        history_service = get_history_service()
        record = history_service.get_record(record_id)

        if not record:
            return jsonify({
                "success": False,
                "error": f"历史记录不存在：{record_id}"
            }), 404

        task_id = record.get('images', {}).get('task_id')
        if not task_id:
            return jsonify({
                "success": False,
                "error": "该记录没有关联的任务图片"
            }), 404

        # 获取任务目录
        task_dir = os.path.join(history_service.history_dir, task_id)
        if not os.path.exists(task_dir):
            return jsonify({
                "success": False,
                "error": f"任务目录不存在：{task_id}"
            }), 404

        # 创建内存中的 ZIP 文件
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 遍历任务目录中的所有图片（排除缩略图）
            for filename in os.listdir(task_dir):
                # 跳过缩略图文件
                if filename.startswith('thumb_'):
                    continue
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(task_dir, filename)
                    # 添加文件到 ZIP，使用 page_N.png 命名
                    try:
                        index = int(filename.split('.')[0])
                        archive_name = f"page_{index + 1}.png"
                    except:
                        archive_name = filename

                    zf.write(file_path, archive_name)

        # 将指针移到开始位置
        memory_file.seek(0)

        # 生成下载文件名（使用记录标题）
        title = record.get('title', 'images')
        # 清理文件名中的非法字符
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_title:
            safe_title = 'images'

        filename = f"{safe_title}.zip"

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False,
            "error": f"下载失败。\n错误详情: {error_msg}"
        }), 500


# ==================== 配置管理 API ====================

def _mask_api_key(key: str) -> str:
    """遮盖 API Key，只显示前4位和后4位"""
    if not key:
        return ''
    if len(key) <= 8:
        return '*' * len(key)
    return key[:4] + '*' * (len(key) - 8) + key[-4:]


def _prepare_providers_for_response(providers: dict) -> dict:
    """准备返回给前端的 providers，返回脱敏的 api_key"""
    result = {}
    for name, config in providers.items():
        provider_copy = config.copy()
        # 返回脱敏的 api_key
        if 'api_key' in provider_copy and provider_copy['api_key']:
            provider_copy['api_key_masked'] = _mask_api_key(provider_copy['api_key'])
            provider_copy['api_key'] = ''  # 不返回实际值，前端用空字符串表示"不修改"
        else:
            provider_copy['api_key_masked'] = ''
            provider_copy['api_key'] = ''
        result[name] = provider_copy
    return result


@api_bp.route('/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        from pathlib import Path
        import yaml

        # 读取图片生成配置
        image_config_path = Path(__file__).parent.parent.parent / 'image_providers.yaml'
        if image_config_path.exists():
            with open(image_config_path, 'r', encoding='utf-8') as f:
                image_config = yaml.safe_load(f) or {}
        else:
            image_config = {
                'active_provider': 'google_genai',
                'providers': {}
            }

        # 读取文本生成配置
        text_config_path = Path(__file__).parent.parent.parent / 'text_providers.yaml'
        if text_config_path.exists():
            with open(text_config_path, 'r', encoding='utf-8') as f:
                text_config = yaml.safe_load(f) or {}
        else:
            text_config = {
                'active_provider': 'google_gemini',
                'providers': {}
            }

        return jsonify({
            "success": True,
            "config": {
                "text_generation": {
                    "active_provider": text_config.get('active_provider', ''),
                    "providers": _prepare_providers_for_response(text_config.get('providers', {}))
                },
                "image_generation": {
                    "active_provider": image_config.get('active_provider', ''),
                    "providers": _prepare_providers_for_response(image_config.get('providers', {}))
                }
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取配置失败: {str(e)}"
        }), 500


@api_bp.route('/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        from pathlib import Path
        import yaml

        data = request.get_json()

        # 更新图片生成配置
        if 'image_generation' in data:
            image_config_path = Path(__file__).parent.parent.parent / 'image_providers.yaml'

            # 读取现有配置
            if image_config_path.exists():
                with open(image_config_path, 'r', encoding='utf-8') as f:
                    image_config = yaml.safe_load(f) or {}
            else:
                image_config = {'providers': {}}

            image_gen_data = data['image_generation']
            if 'active_provider' in image_gen_data:
                image_config['active_provider'] = image_gen_data['active_provider']

            if 'providers' in image_gen_data:
                # 合并 providers，保留未更新的 api_key
                existing_providers = image_config.get('providers', {})
                new_providers = image_gen_data['providers']

                for name, new_config in new_providers.items():
                    # 如果新配置的 api_key 是 True 或空，保留原有的
                    if new_config.get('api_key') in [True, False, '', None]:
                        if name in existing_providers and existing_providers[name].get('api_key'):
                            new_config['api_key'] = existing_providers[name]['api_key']
                        else:
                            new_config.pop('api_key', None)
                    # 移除不需要保存的字段
                    new_config.pop('api_key_env', None)
                    new_config.pop('api_key_masked', None)

                image_config['providers'] = new_providers

            # 保存配置
            with open(image_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(image_config, f, allow_unicode=True, default_flow_style=False)

        # 更新文本生成配置
        if 'text_generation' in data:
            text_gen_data = data['text_generation']
            text_config_path = Path(__file__).parent.parent.parent / 'text_providers.yaml'

            # 读取现有配置
            if text_config_path.exists():
                with open(text_config_path, 'r', encoding='utf-8') as f:
                    text_config = yaml.safe_load(f) or {}
            else:
                text_config = {'providers': {}}

            if 'active_provider' in text_gen_data:
                text_config['active_provider'] = text_gen_data['active_provider']

            if 'providers' in text_gen_data:
                # 合并 providers，保留未更新的 api_key
                existing_providers = text_config.get('providers', {})
                new_providers = text_gen_data['providers']

                for name, new_config in new_providers.items():
                    # 如果新配置的 api_key 是 True 或空，保留原有的
                    if new_config.get('api_key') in [True, False, '', None]:
                        if name in existing_providers and existing_providers[name].get('api_key'):
                            new_config['api_key'] = existing_providers[name]['api_key']
                        else:
                            new_config.pop('api_key', None)
                    # 移除不需要保存的字段
                    new_config.pop('api_key_env', None)
                    new_config.pop('api_key_masked', None)

                text_config['providers'] = new_providers

            # 保存配置
            with open(text_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(text_config, f, allow_unicode=True, default_flow_style=False)

        # 清除配置缓存，确保下次使用时读取新配置
        from backend.config import Config
        Config._image_providers_config = None

        # 清除 ImageService 缓存，确保使用新配置
        from backend.services.image import reset_image_service
        reset_image_service()

        return jsonify({
            "success": True,
            "message": "配置已保存"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"更新配置失败: {str(e)}"
        }), 500


@api_bp.route('/config/test', methods=['POST'])
def test_connection():
    """测试服务商连接"""
    try:
        from pathlib import Path
        import yaml

        data = request.get_json()
        provider_type = data.get('type')
        provider_name = data.get('provider_name')  # 服务商名称（用于从配置文件读取 API Key）
        config = {
            'api_key': data.get('api_key'),
            'base_url': data.get('base_url'),
            'model': data.get('model')
        }

        # 如果没有提供 api_key 或 api_key 为空，从配置文件读取
        if not config['api_key'] and provider_name:
            # 根据类型读取对应的配置文件
            if provider_type in ['google_genai', 'google_gemini']:
                config_path = Path(__file__).parent.parent.parent / 'image_providers.yaml'
                if provider_type in ['google_gemini', 'openai_compatible']:
                    config_path = Path(__file__).parent.parent.parent / 'text_providers.yaml'

                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f) or {}
                        providers = yaml_config.get('providers', {})
                        if provider_name in providers:
                            config['api_key'] = providers[provider_name].get('api_key')
                            # 如果配置文件中有其他参数，也读取
                            if not config['base_url']:
                                config['base_url'] = providers[provider_name].get('base_url')
                            if not config['model']:
                                config['model'] = providers[provider_name].get('model')
            else:
                # openai_compatible 和 image_api 类型
                if provider_type in ['openai_compatible']:
                    config_path = Path(__file__).parent.parent.parent / 'text_providers.yaml'
                else:
                    config_path = Path(__file__).parent.parent.parent / 'image_providers.yaml'

                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f) or {}
                        providers = yaml_config.get('providers', {})
                        if provider_name in providers:
                            config['api_key'] = providers[provider_name].get('api_key')
                            if not config['base_url']:
                                config['base_url'] = providers[provider_name].get('base_url')
                            if not config['model']:
                                config['model'] = providers[provider_name].get('model')

        if not config['api_key']:
            return jsonify({"success": False, "error": "API Key 未配置"}), 400

        # 统一的测试提示词（仅用于文本生成服务商）
        test_prompt = "请回复'你好，红墨'"

        if provider_type == 'google_genai':
            from google import genai
            from google.genai import types
            # 图片生成服务商：仅测试连接，不实际生成
            if config.get('base_url'):
                # 有自定义 base_url，可以测试连接
                client = genai.Client(
                    api_key=config['api_key'],
                    http_options={
                        'base_url': config['base_url'],
                        'api_version': 'v1beta'
                    },
                    vertexai=False
                )
                # 简单测试：列出可用模型
                try:
                    models = list(client.models.list())
                    return jsonify({
                        "success": True,
                        "message": "连接成功！仅代表连接稳定，不确定是否可以稳定支持图片生成"
                    })
                except Exception as e:
                    raise Exception(f"连接测试失败: {str(e)}")
            else:
                # 使用标准 Vertex AI，无法用 API Key 测试
                # 直接返回提示，说明需要在实际使用时验证
                return jsonify({
                    "success": True,
                    "message": "Vertex AI 无法通过 API Key 测试连接（需要 OAuth2 认证）。请在实际生成图片时验证配置是否正确。"
                })

        elif provider_type in ['openai_compatible', 'image_api']:
            import requests
            base_url = config['base_url'].rstrip('/').rstrip('/v1') if config.get('base_url') else 'https://api.openai.com'

            # 对于 image_api 类型，只测试连接不实际生成
            if provider_type == 'image_api':
                url = f"{base_url}/v1/models"
                response = requests.get(
                    url,
                    headers={'Authorization': f"Bearer {config['api_key']}"},
                    timeout=30
                )

                if response.status_code == 200:
                    return jsonify({
                        "success": True,
                        "message": "连接成功！仅代表连接稳定，不确定是否可以稳定支持图片生成"
                    })
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

            # openai_compatible 类型：实际调用文本生成测试
            url = f"{base_url}/v1/chat/completions"

            payload = {
                "model": config.get('model') or 'gpt-3.5-turbo',
                "messages": [{"role": "user", "content": test_prompt}],
                "max_tokens": 50
            }

            response = requests.post(
                url,
                headers={'Authorization': f"Bearer {config['api_key']}", 'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

            result = response.json()
            result_text = result['choices'][0]['message']['content']

            # 检查响应是否包含关键词
            if "你好" in result_text and "红墨" in result_text:
                return jsonify({
                    "success": True,
                    "message": f"连接成功！响应: {result_text[:100]}"
                })
            else:
                return jsonify({
                    "success": True,
                    "message": f"连接成功，但响应内容不符合预期: {result_text[:100]}"
                })

        elif provider_type == 'google_gemini':
            from google import genai
            from google.genai import types
            # 文本生成服务商：实际测试生成
            if config.get('base_url'):
                client = genai.Client(
                    api_key=config['api_key'],
                    http_options={
                        'base_url': config['base_url'],
                        'api_version': 'v1beta'
                    },
                    vertexai=False
                )
            else:
                # 使用标准 Vertex AI 模式
                client = genai.Client(
                    api_key=config['api_key'],
                    vertexai=True
                )

            # 测试生成内容
            model = config.get('model') or 'gemini-2.0-flash-exp'
            response = client.models.generate_content(
                model=model,
                contents=test_prompt
            )
            result_text = response.text if hasattr(response, 'text') else str(response)

            # 检查响应是否包含关键词
            if "你好" in result_text and "红墨" in result_text:
                return jsonify({
                    "success": True,
                    "message": f"连接成功！响应: {result_text[:100]}"
                })
            else:
                return jsonify({
                    "success": True,
                    "message": f"连接成功，但响应内容不符合预期: {result_text[:100]}"
                })

        else:
            raise ValueError(f"不支持的类型: {provider_type}")

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
