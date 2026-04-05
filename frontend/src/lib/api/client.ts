import type { Entry, Feed, FeedResponse, Category } from './types';

const API_BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(`${API_BASE}${path}`, {
		headers: { 'Content-Type': 'application/json', ...init?.headers },
		...init
	});
	if (!res.ok) {
		throw new Error(`API error: ${res.status} ${res.statusText}`);
	}
	return res.json();
}

export interface TagData {
	id: number;
	name: string;
	color: string | null;
	article_count?: number;
}

export interface CollectionData {
	id: number;
	name: string;
	description: string | null;
	icon: string | null;
	is_smart: boolean;
	filter_json: Record<string, unknown> | null;
	sort_order?: number;
	article_count?: number;
	entry_ids?: number[];
}

export interface SavedViewData {
	id: number;
	name: string;
	filter_json: Record<string, unknown>;
	sort_by: string;
	layout: string;
	pinned: boolean;
}

export interface TopicCluster {
	id: number;
	label: string;
	summary: string | null;
	article_count: number;
	created_at: string;
	entry_ids: number[];
}

export interface TopicClusterDetail extends TopicCluster {
	entries: Entry[];
}

export const api = {
	feed: {
		get(params: {
			sort?: string;
			limit?: number;
			offset?: number;
			feed_id?: number;
			status?: string;
			hide_duplicates?: boolean;
		} = {}): Promise<FeedResponse> {
			const search = new URLSearchParams();
			for (const [k, v] of Object.entries(params)) {
				if (v !== undefined) search.set(k, String(v));
			}
			const qs = search.toString();
			return request(`/feed${qs ? `?${qs}` : ''}`);
		},

		getEntry(id: number): Promise<Entry> {
			return request(`/feed/entry/${id}`);
		},

		getFeeds(): Promise<Feed[]> {
			return request('/feed/feeds');
		},

		getCategories(): Promise<Category[]> {
			return request('/feed/categories');
		},

		updateStatus(entryIds: number[], status: string): Promise<void> {
			return request('/feed/entries/status', {
				method: 'PUT',
				body: JSON.stringify({ entry_ids: entryIds, status })
			});
		},

		toggleBookmark(entryId: number): Promise<void> {
			return request(`/feed/entry/${entryId}/bookmark`, { method: 'PUT' });
		},

		search(query: string, limit = 50): Promise<FeedResponse> {
			return request(`/feed/search?q=${encodeURIComponent(query)}&limit=${limit}`);
		}
	},

	topics: {
		list(limit = 20): Promise<TopicCluster[]> {
			return request(`/topics?limit=${limit}`);
		},

		get(id: number): Promise<TopicClusterDetail> {
			return request(`/topics/${id}`);
		}
	},

	tags: {
		list(): Promise<TagData[]> {
			return request('/tags');
		},

		create(name: string, color?: string): Promise<TagData> {
			return request('/tags', {
				method: 'POST',
				body: JSON.stringify({ name, color })
			});
		},

		update(id: number, data: { name?: string; color?: string }): Promise<TagData> {
			return request(`/tags/${id}`, {
				method: 'PATCH',
				body: JSON.stringify(data)
			});
		},

		delete(id: number): Promise<void> {
			return request(`/tags/${id}`, { method: 'DELETE' });
		},

		tagArticles(tagId: number, entryIds: number[]): Promise<void> {
			return request(`/tags/${tagId}/articles`, {
				method: 'POST',
				body: JSON.stringify({ miniflux_entry_ids: entryIds })
			});
		},

		untagArticles(tagId: number, entryIds: number[]): Promise<void> {
			return request(`/tags/${tagId}/articles`, {
				method: 'DELETE',
				body: JSON.stringify({ miniflux_entry_ids: entryIds })
			});
		},

		getEntryTags(entryId: number): Promise<TagData[]> {
			return request(`/tags/entry/${entryId}`);
		}
	},

	collections: {
		list(): Promise<CollectionData[]> {
			return request('/collections');
		},

		create(data: {
			name: string;
			description?: string;
			icon?: string;
			is_smart?: boolean;
			filter_json?: Record<string, unknown>;
		}): Promise<CollectionData> {
			return request('/collections', {
				method: 'POST',
				body: JSON.stringify(data)
			});
		},

		get(id: number): Promise<CollectionData> {
			return request(`/collections/${id}`);
		},

		update(id: number, data: Record<string, unknown>): Promise<CollectionData> {
			return request(`/collections/${id}`, {
				method: 'PATCH',
				body: JSON.stringify(data)
			});
		},

		delete(id: number): Promise<void> {
			return request(`/collections/${id}`, { method: 'DELETE' });
		},

		addArticles(collectionId: number, entryIds: number[]): Promise<void> {
			return request(`/collections/${collectionId}/articles`, {
				method: 'POST',
				body: JSON.stringify({ miniflux_entry_ids: entryIds })
			});
		},

		removeArticles(collectionId: number, entryIds: number[]): Promise<void> {
			return request(`/collections/${collectionId}/articles`, {
				method: 'DELETE',
				body: JSON.stringify({ miniflux_entry_ids: entryIds })
			});
		}
	},

	savedViews: {
		list(): Promise<SavedViewData[]> {
			return request('/saved-views');
		},

		create(data: {
			name: string;
			filter_json: Record<string, unknown>;
			sort_by?: string;
			layout?: string;
			pinned?: boolean;
		}): Promise<SavedViewData> {
			return request('/saved-views', {
				method: 'POST',
				body: JSON.stringify(data)
			});
		},

		get(id: number): Promise<SavedViewData> {
			return request(`/saved-views/${id}`);
		},

		update(id: number, data: Record<string, unknown>): Promise<SavedViewData> {
			return request(`/saved-views/${id}`, {
				method: 'PATCH',
				body: JSON.stringify(data)
			});
		},

		delete(id: number): Promise<void> {
			return request(`/saved-views/${id}`, { method: 'DELETE' });
		}
	},

	settings: {
		exportOpml(): Promise<Blob> {
			return fetch('/api/settings/opml/export').then((r) => r.blob());
		},

		async importOpml(file: File): Promise<{ status: string; message: string }> {
			const formData = new FormData();
			formData.append('file', file);
			const res = await fetch('/api/settings/opml/import', {
				method: 'POST',
				body: formData
			});
			if (!res.ok) throw new Error(`Import failed: ${res.statusText}`);
			return res.json();
		}
	},

	interactions: {
		record(entryId: number, type: string, durationSeconds?: number): Promise<void> {
			return request('/interactions', {
				method: 'POST',
				body: JSON.stringify({
					miniflux_entry_id: entryId,
					interaction_type: type,
					duration_seconds: durationSeconds
				})
			});
		}
	}
};
