<script lang="ts">
	import type { Feed, Category } from '$lib/api/types';
	import type { CollectionData, TagData } from '$lib/api/client';
	import { preferences } from '$lib/stores/preferences.svelte';

	interface Props {
		feeds: Feed[];
		categories: Category[];
		collections: CollectionData[];
		tags: TagData[];
		currentFeedId?: number;
	}

	let { feeds, categories, collections, tags, currentFeedId }: Props = $props();

	let feedsByCategory = $derived(
		categories.map((cat) => ({
			...cat,
			feeds: feeds.filter((f) => f.category.id === cat.id)
		}))
	);
</script>

<aside
	class="flex h-full w-64 shrink-0 flex-col border-r border-neutral-200 bg-white transition-all dark:border-neutral-800 dark:bg-neutral-950"
	class:hidden={!preferences.sidebarOpen}
>
	<div class="flex items-center gap-2 border-b border-neutral-200 px-4 py-3 dark:border-neutral-800">
		<h1 class="text-lg font-bold tracking-tight">GoFetch</h1>
	</div>

	<nav class="flex-1 overflow-y-auto px-2 py-2">
		<!-- Main views -->
		<a
			href="/feed"
			class="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
			class:bg-neutral-100={!currentFeedId}
			class:dark:bg-neutral-900={!currentFeedId}
		>
			<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
			</svg>
			All Articles
		</a>

		<a
			href="/topics"
			class="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
		>
			<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
			</svg>
			Topics
		</a>

		<!-- Collections -->
		{#if collections.length > 0}
			<div class="my-3 border-t border-neutral-200 dark:border-neutral-800"></div>
			<h3 class="px-3 py-1 text-xs font-semibold tracking-wider text-neutral-500 uppercase">
				Collections
			</h3>
			{#each collections as collection (collection.id)}
				<a
					href="/collections/{collection.id}"
					class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
				>
					<span class="text-sm">{collection.icon || '📁'}</span>
					<span class="truncate">{collection.name}</span>
					<span class="ml-auto text-xs text-neutral-400">{collection.article_count ?? 0}</span>
				</a>
			{/each}
			<a
				href="/collections"
				class="flex items-center gap-2 rounded-md px-3 py-1.5 text-xs text-neutral-400 transition-colors hover:text-neutral-600 dark:hover:text-neutral-300"
			>
				Manage collections
			</a>
		{/if}

		<!-- Tags -->
		{#if tags.length > 0}
			<div class="my-3 border-t border-neutral-200 dark:border-neutral-800"></div>
			<h3 class="px-3 py-1 text-xs font-semibold tracking-wider text-neutral-500 uppercase">
				Tags
			</h3>
			{#each tags as tag (tag.id)}
				<a
					href="/tags/{encodeURIComponent(tag.name)}"
					class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
				>
					{#if tag.color}
						<span class="h-2.5 w-2.5 shrink-0 rounded-full" style="background-color: {tag.color}"></span>
					{/if}
					<span class="truncate">{tag.name}</span>
					<span class="ml-auto text-xs text-neutral-400">{tag.article_count ?? 0}</span>
				</a>
			{/each}
			<a
				href="/tags"
				class="flex items-center gap-2 rounded-md px-3 py-1.5 text-xs text-neutral-400 transition-colors hover:text-neutral-600 dark:hover:text-neutral-300"
			>
				Manage tags
			</a>
		{/if}

		<!-- Feeds by category -->
		<div class="my-3 border-t border-neutral-200 dark:border-neutral-800"></div>
		{#each feedsByCategory as category}
			<div class="mb-2">
				<h3 class="px-3 py-1 text-xs font-semibold tracking-wider text-neutral-500 uppercase">
					{category.title}
				</h3>
				{#each category.feeds as feed}
					<a
						href="/feed?feed_id={feed.id}"
						class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
						class:bg-neutral-100={currentFeedId === feed.id}
						class:dark:bg-neutral-900={currentFeedId === feed.id}
					>
						<span class="truncate">{feed.title}</span>
					</a>
				{/each}
			</div>
		{/each}
	</nav>

	<div class="border-t border-neutral-200 px-2 py-2 dark:border-neutral-800">
		<a
			href="/settings"
			class="flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
		>
			<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
			</svg>
			Settings
		</a>
	</div>
</aside>
