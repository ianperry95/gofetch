<script lang="ts">
	import ArticleCard from '$lib/components/feed/ArticleCard.svelte';
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import { invalidateAll } from '$app/navigation';

	let { data } = $props();
</script>

<Topbar onRefresh={() => invalidateAll()} />

<div class="flex-1 overflow-y-auto">
	{#if !data.collection}
		<div class="flex flex-1 items-center justify-center py-24">
			<p class="text-neutral-500">Collection not found.</p>
		</div>
	{:else}
		<div class="p-4">
			<div class="mb-6">
				<h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
					{data.collection.icon || '📁'} {data.collection.name}
				</h1>
				{#if data.collection.description}
					<p class="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
						{data.collection.description}
					</p>
				{/if}
			</div>

			{#if data.entries.length === 0}
				<p class="text-sm text-neutral-500">No articles in this collection yet.</p>
			{:else}
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each data.entries as entry (entry.id)}
						<ArticleCard {entry} />
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
