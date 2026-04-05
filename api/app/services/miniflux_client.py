from typing import Any

import httpx

from app.config import settings


class MinifluxClient:
    def __init__(self) -> None:
        self._base_url = settings.miniflux_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=f"{self._base_url}/v1",
            headers={"X-Auth-Token": settings.miniflux_api_key},
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        resp = await self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_entries(
        self,
        *,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        order: str = "published_at",
        direction: str = "desc",
        after_entry_id: int | None = None,
        category_id: int | None = None,
        feed_id: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "order": order,
            "direction": direction,
        }
        if status:
            params["status"] = status
        if after_entry_id:
            params["after_entry_id"] = after_entry_id
        if category_id:
            params["category_id"] = category_id
        if feed_id:
            params["feed_id"] = feed_id
        return await self._get("/entries", params=params)

    async def get_entry(self, entry_id: int) -> dict[str, Any]:
        return await self._get(f"/entries/{entry_id}")

    async def get_feeds(self) -> list[dict[str, Any]]:
        return await self._get("/feeds")

    async def get_feed(self, feed_id: int) -> dict[str, Any]:
        return await self._get(f"/feeds/{feed_id}")

    async def get_categories(self) -> list[dict[str, Any]]:
        return await self._get("/categories")

    async def update_entries(self, entry_ids: list[int], status: str) -> None:
        resp = await self._client.put("/entries", json={"entry_ids": entry_ids, "status": status})
        resp.raise_for_status()

    async def toggle_bookmark(self, entry_id: int) -> None:
        resp = await self._client.put(f"/entries/{entry_id}/bookmark")
        resp.raise_for_status()

    async def search_entries(self, query: str, limit: int = 50) -> dict[str, Any]:
        return await self._get("/entries", params={"search": query, "limit": limit})

    async def get_feed_icon(self, feed_id: int) -> dict[str, Any]:
        return await self._get(f"/feeds/{feed_id}/icon")

    async def export_opml(self) -> str:
        """Export feeds as OPML XML."""
        resp = await self._client.get("/export")
        resp.raise_for_status()
        return resp.text

    async def import_opml(self, opml_content: str) -> dict[str, Any]:
        """Import feeds from OPML XML."""
        resp = await self._client.post(
            "/import",
            content=opml_content.encode(),
            headers={"Content-Type": "application/xml"},
        )
        resp.raise_for_status()
        return resp.json()


miniflux = MinifluxClient()
