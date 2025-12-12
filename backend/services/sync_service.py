"""同步服务（整合 COS 和 Notion）"""
import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from backend.services.cos_uploader import get_cos_uploader
from backend.services.notion_sync import get_notion_sync
from backend.services.history import get_history_service

logger = logging.getLogger(__name__)


class SyncService:
    """同步服务类（整合 COS 上传和 Notion 同步）"""

    def __init__(
        self,
        cos_service_url: str = None,
        notion_token: str = None,
        notion_database_id: str = None,
        enabled: bool = True
    ):
        """
        初始化同步服务

        Args:
            cos_service_url: COS 服务地址
            notion_token: Notion Integration Token
            notion_database_id: Notion Database ID
            enabled: 是否启用同步
        """
        self.enabled = enabled
        
        if not enabled:
            logger.info("同步服务已禁用")
            return

        # 初始化 COS 上传服务
        self.cos_uploader = get_cos_uploader(cos_service_url)
        
        # 初始化 Notion 同步服务
        self.notion_sync = get_notion_sync(notion_token, notion_database_id)
        
        if self.notion_sync is None:
            logger.warning("Notion 同步服务未初始化，将跳过 Notion 同步")
        
        logger.info("同步服务初始化完成")

    def sync_record_to_notion(
        self,
        record_id: str
    ) -> Dict[str, Any]:
        """
        同步历史记录到 Notion（包括上传图片到 COS）

        Args:
            record_id: 历史记录 ID

        Returns:
            {
                "success": True/False,
                "cos_urls": ["url1", "url2", ...] (成功时),
                "notion_page_id": "页面ID" (成功时),
                "notion_page_url": "页面URL" (成功时),
                "error": "错误信息" (失败时)
            }
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "同步服务已禁用"
            }

        try:
            # 获取历史记录
            history_service = get_history_service()
            record = history_service.get_record(record_id)
            
            if not record:
                return {
                    "success": False,
                    "error": f"历史记录不存在: {record_id}"
                }

            # 获取任务 ID 和图片列表
            task_id = record.get("images", {}).get("task_id")
            image_files = record.get("images", {}).get("generated", [])
            
            if not task_id or not image_files:
                logger.warning(f"记录 {record_id} 没有图片，跳过 COS 上传")
                cos_urls = []
            else:
                # 上传图片到 COS
                cos_result = self._upload_images_to_cos(task_id, image_files, record.get("title", "未命名"))
                
                if not cos_result.get("success"):
                    return {
                        "success": False,
                        "error": f"COS 上传失败: {cos_result.get('error')}"
                    }
                
                cos_urls = cos_result.get("urls", [])

            # 同步到 Notion
            if self.notion_sync is None:
                return {
                    "success": False,
                    "error": "Notion 同步服务未配置"
                }

            notion_result = self.notion_sync.sync_record(record, cos_urls)
            
            if not notion_result.get("success"):
                return {
                    "success": False,
                    "error": f"Notion 同步失败: {notion_result.get('error')}",
                    "cos_urls": cos_urls  # 即使 Notion 失败，也返回 COS URLs
                }

            logger.info(f"✅ 记录 {record_id} 同步成功")
            return {
                "success": True,
                "cos_urls": cos_urls,
                "notion_page_id": notion_result.get("page_id"),
                "notion_page_url": notion_result.get("page_url")
            }

        except Exception as e:
            error_msg = f"同步记录异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }

    def _upload_images_to_cos(
        self,
        task_id: str,
        image_files: List[str],
        base_filename: str = "redink"
    ) -> Dict[str, Any]:
        """
        上传图片到 COS

        Args:
            task_id: 任务 ID
            image_files: 图片文件名列表
            base_filename: 基础文件名

        Returns:
            {
                "success": True/False,
                "urls": ["url1", "url2", ...] (成功时),
                "error": "错误信息" (失败时)
            }
        """
        try:
            # 获取任务目录
            history_service = get_history_service()
            task_dir = os.path.join(history_service.history_dir, task_id)
            
            if not os.path.exists(task_dir):
                return {
                    "success": False,
                    "error": f"任务目录不存在: {task_id}"
                }

            # 清理文件名，用于 COS 文件名
            safe_filename = "".join(c for c in base_filename if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_filename:
                safe_filename = "redink"

            # 批量上传图片
            upload_results = []
            for index, filename in enumerate(image_files):
                file_path = os.path.join(task_dir, filename)
                
                if not os.path.exists(file_path):
                    logger.warning(f"图片文件不存在: {file_path}")
                    continue

                # 生成 COS 文件名（使用任务ID和索引）
                cos_filename = f"{safe_filename}-{task_id[:8]}-{index + 1}"
                
                # 上传到 COS
                result = self.cos_uploader.upload_from_file(file_path, cos_filename)
                
                if result.get("success"):
                    upload_results.append(result.get("url"))
                    logger.info(f"✅ 图片 {filename} 上传成功")
                else:
                    logger.error(f"❌ 图片 {filename} 上传失败: {result.get('error')}")

            if not upload_results:
                return {
                    "success": False,
                    "error": "所有图片上传失败"
                }

            return {
                "success": True,
                "urls": upload_results,
                "total": len(image_files),
                "success_count": len(upload_results),
                "failed_count": len(image_files) - len(upload_results)
            }

        except Exception as e:
            error_msg = f"上传图片到 COS 异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }


# 全局服务实例
_service_instance = None


def get_sync_service() -> Optional[SyncService]:
    """获取全局同步服务实例"""
    global _service_instance
    
    if _service_instance is None:
        # 从配置类读取配置
        from backend.config import Config
        
        cos_service_url = Config.COS_SERVICE_URL
        notion_token = Config.NOTION_INTEGRATION_TOKEN
        notion_database_id = Config.NOTION_DATABASE_ID
        enabled = Config.SYNC_ENABLED
        
        # 如果未配置 Notion，禁用同步
        if not notion_token or not notion_database_id:
            logger.warning("Notion 配置未设置，同步服务将被禁用")
            enabled = False
        
        _service_instance = SyncService(
            cos_service_url=cos_service_url,
            notion_token=notion_token,
            notion_database_id=notion_database_id,
            enabled=enabled
        )
    
    return _service_instance

