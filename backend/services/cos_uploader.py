"""COS 图片上传服务"""
import logging
import base64
import requests
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class COSUploader:
    """COS 图片上传服务类（调用现有 COS 服务）"""

    def __init__(self, service_url: str = "http://212.64.57.87:10009/upload-to-cos"):
        """
        初始化 COS 上传服务

        Args:
            service_url: COS 服务地址
        """
        self.service_url = service_url
        logger.info(f"COS 上传服务初始化: {service_url}")

    def upload_from_base64(
        self,
        image_base64: str,
        filename: str,
        max_retries: int = 3,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        从 Base64 上传图片到 COS（带重试机制）

        Args:
            image_base64: Base64 编码的图片（可以带或不带 data URL 前缀）
            filename: 文件名（不含扩展名，服务端会自动添加）
            max_retries: 最大重试次数（默认 3 次）
            timeout: 超时时间（秒，默认 120 秒）

        Returns:
            {
                "success": True/False,
                "url": "COS URL" (成功时),
                "error": "错误信息" (失败时)
            }
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                # 确保 base64 字符串有 data URL 前缀
                if not image_base64.startswith("data:image/"):
                    # 如果没有前缀，添加默认的 JPEG 前缀
                    image_base64 = f"data:image/jpeg;base64,{image_base64}"

                payload = {
                    "imageBase64": image_base64,
                    "filename": filename
                }

                if attempt > 1:
                    logger.info(f"🔄 重试上传图片到 COS (第 {attempt}/{max_retries} 次): filename={filename}")
                else:
                    logger.debug(f"上传图片到 COS: filename={filename}")
                
                response = requests.post(
                    self.service_url,
                    json=payload,
                    timeout=timeout
                )

                if response.status_code != 200:
                    error_msg = f"COS 服务返回错误: {response.status_code} - {response.text}"
                    logger.warning(f"⚠️  {error_msg} (尝试 {attempt}/{max_retries})")
                    last_error = error_msg
                    if attempt < max_retries:
                        continue  # 重试
                    else:
                        logger.error(error_msg)
                        return {
                            "success": False,
                            "error": error_msg
                        }

                result = response.json()
                if "url" in result:
                    if attempt > 1:
                        logger.info(f"✅ 图片上传成功（重试 {attempt} 次后）: {result['url']}")
                    else:
                        logger.info(f"✅ 图片上传成功: {result['url']}")
                    return {
                        "success": True,
                        "url": result["url"]
                    }
                else:
                    error_msg = f"COS 服务返回格式错误: {result}"
                    logger.warning(f"⚠️  {error_msg} (尝试 {attempt}/{max_retries})")
                    last_error = error_msg
                    if attempt < max_retries:
                        continue  # 重试
                    else:
                        logger.error(error_msg)
                        return {
                            "success": False,
                            "error": error_msg
                        }

            except requests.exceptions.Timeout:
                error_msg = f"COS 上传超时（{timeout}秒）"
                logger.warning(f"⚠️  {error_msg} (尝试 {attempt}/{max_retries})")
                last_error = error_msg
                if attempt < max_retries:
                    import time
                    wait_time = attempt * 2  # 递增等待时间：2秒、4秒、6秒
                    logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue  # 重试
                else:
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
            except requests.exceptions.RequestException as e:
                error_msg = f"COS 上传请求失败: {str(e)}"
                logger.warning(f"⚠️  {error_msg} (尝试 {attempt}/{max_retries})")
                last_error = error_msg
                if attempt < max_retries:
                    import time
                    wait_time = attempt * 2
                    logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue  # 重试
                else:
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg
                    }
            except Exception as e:
                error_msg = f"COS 上传异常: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {
                    "success": False,
                    "error": error_msg
                }
        
        # 所有重试都失败
        logger.error(f"❌ 图片上传失败（已重试 {max_retries} 次）: {last_error}")
        return {
            "success": False,
            "error": f"上传失败（已重试 {max_retries} 次）: {last_error}"
        }

    def upload_from_file(
        self,
        file_path: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        从文件路径上传图片到 COS

        Args:
            file_path: 本地文件路径
            filename: 文件名（不含扩展名）

        Returns:
            上传结果字典
        """
        try:
            # 读取文件并转换为 base64
            with open(file_path, "rb") as f:
                image_data = f.read()

            # 转换为 base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            # 根据文件扩展名确定 MIME 类型
            ext = Path(file_path).suffix.lower()
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }
            mime_type = mime_types.get(ext, "image/jpeg")

            # 添加 data URL 前缀
            image_base64 = f"data:{mime_type};base64,{image_base64}"

            return self.upload_from_base64(image_base64, filename)

        except FileNotFoundError:
            error_msg = f"文件不存在: {file_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"读取文件失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }

    def upload_from_bytes(
        self,
        image_data: bytes,
        filename: str,
        mime_type: str = "image/png"
    ) -> Dict[str, Any]:
        """
        从字节数据上传图片到 COS

        Args:
            image_data: 图片二进制数据
            filename: 文件名（不含扩展名）
            mime_type: MIME 类型（默认 image/png）

        Returns:
            上传结果字典
        """
        try:
            # 转换为 base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            image_base64 = f"data:{mime_type};base64,{image_base64}"

            return self.upload_from_base64(image_base64, filename)

        except Exception as e:
            error_msg = f"转换图片数据失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg
            }

    def upload_batch(
        self,
        images: list,
        base_filename: str
    ) -> Dict[str, Any]:
        """
        批量上传图片到 COS

        Args:
            images: 图片列表，每个元素可以是：
                - 文件路径 (str)
                - 字节数据 (bytes)
                - Base64 字符串 (str)
            base_filename: 基础文件名（会自动添加序号）

        Returns:
            {
                "success": True/False,
                "results": [
                    {"index": 0, "success": True, "url": "...", "error": None},
                    ...
                ],
                "total": 总数,
                "success_count": 成功数,
                "failed_count": 失败数
            }
        """
        results = []
        success_count = 0
        failed_count = 0

        for index, image in enumerate(images):
            # 生成文件名
            filename = f"{base_filename}-{index + 1}"

            # 根据类型调用不同的上传方法
            if isinstance(image, str):
                # 文件路径
                if Path(image).exists():
                    result = self.upload_from_file(image, filename)
                else:
                    # Base64 字符串
                    result = self.upload_from_base64(image, filename)
            elif isinstance(image, bytes):
                result = self.upload_from_bytes(image, filename)
            else:
                result = {
                    "success": False,
                    "error": f"不支持的图片类型: {type(image)}"
                }

            results.append({
                "index": index,
                "success": result.get("success", False),
                "url": result.get("url"),
                "error": result.get("error")
            })

            if result.get("success"):
                success_count += 1
            else:
                failed_count += 1

        return {
            "success": failed_count == 0,
            "results": results,
            "total": len(images),
            "success_count": success_count,
            "failed_count": failed_count
        }


# 全局服务实例
_service_instance = None


def get_cos_uploader(service_url: str = None) -> COSUploader:
    """获取全局 COS 上传服务实例"""
    global _service_instance
    if _service_instance is None:
        if service_url is None:
            # 从环境变量或配置读取
            import os
            service_url = os.getenv("COS_SERVICE_URL", "http://212.64.57.87:10009/upload-to-cos")
        _service_instance = COSUploader(service_url)
    return _service_instance

