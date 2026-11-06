"""支持的平台及其官方入口。"""

from __future__ import annotations

PLATFORMS: dict[str, dict[str, str]] = {
    "douyin": {
        "name": "抖音创作者中心",
        "short_name": "抖音",
        "url": "https://creator.douyin.com/",
        "color": "#fe2c55",
        "initial": "抖",
    },
    "channels": {
        "name": "微信视频号助手",
        "short_name": "视频号",
        "url": "https://channels.weixin.qq.com/login.html",
        "color": "#07c160",
        "initial": "视",
    },
    "xingtu": {
        "name": "巨量星图",
        "short_name": "星图",
        "url": "https://www.xingtu.cn/",
        "color": "#7c6cf2",
        "initial": "星",
    },
}


def platform_info(platform: str) -> dict[str, str]:
    """Return platform metadata or raise a clear validation error."""
    try:
        return PLATFORMS[platform]
    except KeyError as exc:
        raise ValueError("不支持的平台") from exc
