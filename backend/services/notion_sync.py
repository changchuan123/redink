"""Notion 同步服务"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class NotionSync:
    """Notion 同步服务类"""

    def __init__(
        self,
        integration_token: str,
        database_id: str,
        api_version: str = "2022-06-28"
    ):
        """
        初始化 Notion 同步服务

        Args:
            integration_token: Notion Integration Token
            database_id: Notion Database ID
            api_version: Notion API 版本
        """
        self.integration_token = integration_token
        self.database_id = database_id
        self.api_version = api_version
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {integration_token}",
            "Content-Type": "application/json",
            "Notion-Version": api_version
        }
        logger.info(f"Notion 同步服务初始化: database_id={database_id[:8]}...")

    def create_page(
        self,
        title: str,
        notes: str,
        image_urls: List[str] = None,
        upload_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        在 Notion 数据库中创建新页面

        Args:
            title: 标题
            notes: 笔记内容
            image_urls: 图片 URL 列表
            upload_time: 上传时间（默认当前时间）

        Returns:
            {
                "success": True/False,
                "page_id": "页面ID" (成功时),
                "page_url": "页面URL" (成功时),
                "error": "错误信息" (失败时)
            }
        """
        try:
            if upload_time is None:
                upload_time = datetime.now()

            # 构建 Properties
            properties = {
                "标题": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "笔记": {
                    "rich_text": [
                        {
                            "text": {
                                "content": notes
                            }
                        }
                    ]
                },
                "上传时间": {
                    "date": {
                        "start": upload_time.isoformat()
                    }
                }
            }

            # 添加图片（如果有）
            if image_urls and len(image_urls) > 0:
                files = []
                for index, url in enumerate(image_urls):
                    files.append({
                        "type": "external",
                        "name": f"图片-{index + 1}",
                        "external": {
                            "url": url
                        }
                    })
                properties["图片"] = {
                    "files": files
                }

            # 构建请求体
            payload = {
                "parent": {
                    "database_id": self.database_id
                },
                "properties": properties
            }

            logger.debug(f"创建 Notion 页面: title={title[:50]}...")
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                error_msg = f"Notion API 返回错误: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }

            result = response.json()
            page_id = result.get("id")
            page_url = result.get("url", "")

            logger.info(f"✅ Notion 页面创建成功: {page_id[:8]}...")
            return {
                "success": True,
                "page_id": page_id,
                "page_url": page_url
            }

        except requests.exceptions.Timeout:
            error_msg = "Notion API 请求超时（30秒）"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Notion API 请求失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"创建 Notion 页面异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }

    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        upload_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        更新 Notion 页面

        Args:
            page_id: 页面 ID
            title: 标题（可选）
            notes: 笔记内容（可选）
            image_urls: 图片 URL 列表（可选）
            upload_time: 上传时间（可选）

        Returns:
            更新结果字典
        """
        try:
            properties = {}

            if title is not None:
                properties["标题"] = {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }

            if notes is not None:
                properties["笔记"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": notes
                            }
                        }
                    ]
                }

            if upload_time is not None:
                properties["上传时间"] = {
                    "date": {
                        "start": upload_time.isoformat()
                    }
                }

            if image_urls is not None and len(image_urls) > 0:
                files = []
                for index, url in enumerate(image_urls):
                    files.append({
                        "type": "external",
                        "name": f"图片-{index + 1}",
                        "external": {
                            "url": url
                        }
                    })
                properties["图片"] = {
                    "files": files
                }

            if not properties:
                return {
                    "success": False,
                    "error": "没有需要更新的属性"
                }

            payload = {
                "properties": properties
            }

            logger.debug(f"更新 Notion 页面: page_id={page_id[:8]}...")
            response = requests.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code not in [200, 201]:
                error_msg = f"Notion API 返回错误: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }

            result = response.json()
            page_url = result.get("url", "")

            logger.info(f"✅ Notion 页面更新成功: {page_id[:8]}...")
            return {
                "success": True,
                "page_id": page_id,
                "page_url": page_url
            }

        except Exception as e:
            error_msg = f"更新 Notion 页面异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }

    def sync_record(
        self,
        record_data: Dict[str, Any],
        cos_urls: List[str] = None
    ) -> Dict[str, Any]:
        """
        同步历史记录到 Notion

        Args:
            record_data: 历史记录数据（包含 title, outline 等）
            cos_urls: COS 图片 URL 列表

        Returns:
            同步结果字典
        """
        try:
            title = record_data.get("title", "未命名笔记")
            outline = record_data.get("outline", {})
            
            # 构建笔记内容
            notes_parts = []
            
            # 添加完整大纲文本
            if outline.get("raw"):
                notes_parts.append("## 完整大纲\n\n" + outline.get("raw"))
            
            # 添加分页内容
            pages = outline.get("pages", [])
            if pages:
                notes_parts.append("\n\n## 分页内容\n\n")
                for page in pages:
                    page_type_map = {
                        "cover": "封面",
                        "content": "内容",
                        "summary": "总结"
                    }
                    page_type = page_type_map.get(page.get("type", "content"), "内容")
                    page_index = page.get("index", 0) + 1
                    page_content = page.get("content", "")
                    notes_parts.append(f"### 第 {page_index} 页 - {page_type}\n\n{page_content}\n\n")

            notes = "\n".join(notes_parts)

            # 获取上传时间
            created_at = record_data.get("created_at")
            upload_time = None
            if created_at:
                try:
                    upload_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                except:
                    pass

            # 创建 Notion 页面
            return self.create_page(
                title=title,
                notes=notes,
                image_urls=cos_urls or [],
                upload_time=upload_time
            )

        except Exception as e:
            error_msg = f"同步记录到 Notion 异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }


# 全局服务实例
_service_instance = None


def get_notion_sync(
    integration_token: str = None,
    database_id: str = None
) -> Optional[NotionSync]:
    """获取全局 Notion 同步服务实例"""
    global _service_instance
    
    if integration_token is None or database_id is None:
        # 从环境变量读取
        import os
        integration_token = integration_token or os.getenv("NOTION_INTEGRATION_TOKEN")
        database_id = database_id or os.getenv("NOTION_DATABASE_ID")
    
    if not integration_token or not database_id:
        logger.warning("Notion 配置未设置，跳过 Notion 同步")
        return None
    
    if _service_instance is None:
        _service_instance = NotionSync(integration_token, database_id)
    
    return _service_instance

