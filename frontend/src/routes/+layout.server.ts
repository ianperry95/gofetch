import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch }) => {
	try {
		const [feedsRes, categoriesRes, collectionsRes, tagsRes] = await Promise.all([
			fetch('/api/feed/feeds'),
			fetch('/api/feed/categories'),
			fetch('/api/collections'),
			fetch('/api/tags')
		]);

		const feeds = feedsRes.ok ? await feedsRes.json() : [];
		const categories = categoriesRes.ok ? await categoriesRes.json() : [];
		const collections = collectionsRes.ok ? await collectionsRes.json() : [];
		const tags = tagsRes.ok ? await tagsRes.json() : [];

		return { feeds, categories, collections, tags };
	} catch {
		return { feeds: [], categories: [], collections: [], tags: [] };
	}
};
