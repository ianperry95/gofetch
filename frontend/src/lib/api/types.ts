export interface Entry {
	id: number;
	feed_id: number;
	title: string;
	url: string;
	author: string;
	content: string;
	status: 'unread' | 'read' | 'removed';
	starred: boolean;
	published_at: string;
	created_at: string;
	reading_time: number;
	feed: Feed;
	_score?: number;
	_is_duplicate?: boolean;
	_cluster_id?: number | null;
}

export interface Feed {
	id: number;
	title: string;
	site_url: string;
	feed_url: string;
	category: Category;
	icon?: FeedIcon;
	checked_at: string;
}

export interface FeedIcon {
	feed_id: number;
	icon_id: number;
	data: string;
	mime_type: string;
}

export interface Category {
	id: number;
	title: string;
}

export interface FeedResponse {
	entries: Entry[];
	total: number;
}

export type SortMode = 'ranked' | 'newest' | 'oldest';
export type Layout = 'cards' | 'list' | 'magazine';
