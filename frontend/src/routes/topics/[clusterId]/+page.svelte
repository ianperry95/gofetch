<script lang="ts">
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import { invalidateAll } from '$app/navigation';

	let { data } = $props();
	let cluster = $derived(data.cluster);
</script>

<Topbar onRefresh={() => invalidateAll()} />

<div class="flex-1 overflow-y-auto">
	{#if !cluster}
		<div class="flex flex-1 items-center justify-center py-24">
			<p class="text-neutral-500">Topic not found.</p>
		</div>
	{:else}
		<div class="p-4">
			<div class="mb-6">
				<h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
					{cluster.label}
				</h1>
				{#if cluster.summary}
					<p class="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
						{cluster.summary}
					</p>
				{/if}
				<p class="mt-2 text-xs text-neutral-500">
					{cluster.article_count} articles in this topic
				</p>
			</div>

			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each cluster.entries as entry (entry.id)}
					<ArticleCard {entry} />
				{/each}
			</div>
		</div>
	{/if}
</div>
