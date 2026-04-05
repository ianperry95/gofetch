<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import ArticleRow from '$lib/components/feed/ArticleRow.svelte';
	import ActionBar from '$lib/components/curation/ActionBar.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import { preferences } from '$lib/stores/preferences.svelte';
	import { keyboard } from '$lib/stores/keyboard.svelte';
	import { api } from '$lib/api/client';
	import { liveUpdates } from '$lib/stores/liveUpdates.svelte';
	import { invalidateAll } from '$app/navigation';

	let { data } = $props();

	let selectedIds: number[] = $state([]);
	let selectable = $derived(selectedIds.length > 0);
	let focusedIndex = $state(0);
	let loadingMore = $state(false);
	let allLoaded = $state(data.entries.length >= data.total);
	let scrollContainer: HTMLDivElement;

	function toggleSelect(id: number) {
		if (selectedIds.includes(id)) {
			selectedIds = selectedIds.filter((i) => i !== id);
		} else {
			selectedIds = [...selectedIds, id];
		}
	}

	async function toggleStar(id: number) {
		const entry = data.entries.find((e: { id: number }) => e.id === id);
		if (entry) {
			entry.starred = !entry.starred;
			try {
				await api.feed.toggleBookmark(id);
			} catch {
				entry.starred = !entry.starred;
			}
		}
	}

	// Scroll focused item into view
	$effect(() => {
		if (data.entries.length > 0) {
			const el = document.querySelector(`[data-entry-index="${focusedIndex}"]`);
			el?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
		}
	});

	onMount(() => {
		keyboard.feedNav = {
			entries: data.entries,
			focusedIndex,
			setFocusedIndex: (i: number) => { focusedIndex = i; },
			toggleStar
		};
	});

	// Keep keyboard nav in sync with reactive state
	$effect(() => {
		if (keyboard.feedNav) {
			keyboard.feedNav = {
				entries: data.entries,
				focusedIndex,
				setFocusedIndex: (i: number) => { focusedIndex = i; },
				toggleStar
			};
		}
	});

	onDestroy(() => {
		keyboard.feedNav = null;
	});

	async function loadMore() {
		if (loadingMore || allLoaded) return;
		loadingMore = true;
		try {
			const result = await api.feed.get({
				sort: preferences.sort,
				limit: 50,
				offset: data.entries.length,
				status: 'unread',
				hide_duplicates: preferences.hideDuplicates
			});
			if (result.entries.length === 0) {
				allLoaded = true;
			} else {
				data.entries = [...data.entries, ...result.entries];
				allLoaded = data.entries.length >= result.total;
			}
		} finally {
			loadingMore = false;
		}
	}

	function onScroll() {
		if (!scrollContainer) return;
		const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
		// Prefetch when within 300px of bottom
		if (scrollHeight - scrollTop - clientHeight < 300) {
			loadMore();
		}
	}
</script>

<Topbar onRefresh={() => { liveUpdates.dismissNewArticles(); invalidateAll(); }} />

{#if liveUpdates.newArticleCount > 0}
	<button
		onclick={() => { liveUpdates.dismissNewArticles(); invalidateAll(); }}
		class="flex w-full items-center justify-center gap-2 bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
	>
		<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
		</svg>
		{liveUpdates.newArticleCount} new {liveUpdates.newArticleCount === 1 ? 'article' : 'articles'} available
	</button>
{/if}

<div class="flex-1 overflow-y-auto" bind:this={scrollContainer} onscroll={onScroll}>
	{#if data.entries.length === 0}
		<div class="flex flex-col items-center justify-center py-24 text-center">
			<svg class="mb-4 h-16 w-16 text-neutral-300 dark:text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
			</svg>
			<h2 class="mb-1 text-lg font-medium text-neutral-900 dark:text-neutral-100">No articles yet</h2>
			<p class="text-sm text-neutral-500">
				Add some feeds in your Miniflux instance to get started.
			</p>
		</div>
	{:else if preferences.layout === 'cards'}
		<div class="grid grid-cols-1 gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each data.entries as entry, i (entry.id)}
				<ArticleCard
					{entry}
					index={i}
					focused={focusedIndex === i}
					selectable={true}
					selected={selectedIds.includes(entry.id)}
					onSelect={toggleSelect}
				/>
			{/each}
		</div>
	{:else if preferences.layout === 'list'}
		<div class="divide-y divide-neutral-100 dark:divide-neutral-900">
			{#each data.entries as entry, i (entry.id)}
				<ArticleRow
					{entry}
					index={i}
					focused={focusedIndex === i}
					selectable={true}
					selected={selectedIds.includes(entry.id)}
					onSelect={toggleSelect}
				/>
			{/each}
		</div>
	{:else}
		{#if data.entries.length > 0}
			<div class="p-4">
				<div class="mb-4">
					<ArticleCard
						entry={data.entries[0]}
						index={0}
						focused={focusedIndex === 0}
						selectable={true}
						selected={selectedIds.includes(data.entries[0].id)}
						onSelect={toggleSelect}
					/>
				</div>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each data.entries.slice(1) as entry, i (entry.id)}
						<ArticleCard
							{entry}
							index={i + 1}
							focused={focusedIndex === i + 1}
							selectable={true}
							selected={selectedIds.includes(entry.id)}
							onSelect={toggleSelect}
						/>
					{/each}
				</div>
			</div>
		{/if}
	{/if}

	{#if loadingMore}
		<div class="flex items-center justify-center py-6">
			<div class="h-5 w-5 animate-spin rounded-full border-2 border-neutral-300 border-t-blue-600"></div>
			<span class="ml-2 text-sm text-neutral-500">Loading more...</span>
		</div>
	{:else if allLoaded && data.entries.length > 0}
		<div class="py-6 text-center text-sm text-neutral-400">
			All caught up
		</div>
	{/if}
</div>

<ActionBar
	{selectedIds}
	onClear={() => (selectedIds = [])}
	onDone={() => { selectedIds = []; invalidateAll(); }}
/>
