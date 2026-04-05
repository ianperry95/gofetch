<script lang="ts">
	import Topbar from '$lib/components/layout/Topbar.svelte';
	import { invalidateAll } from '$app/navigation';

	let { data } = $props();
</script>

<Topbar onRefresh={() => invalidateAll()} />

<div class="flex-1 overflow-y-auto">
	{#if data.clusters.length === 0}
		<div class="flex flex-col items-center justify-center py-24 text-center">
			<svg class="mb-4 h-16 w-16 text-neutral-300 dark:text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
			</svg>
			<h2 class="mb-1 text-lg font-medium text-neutral-900 dark:text-neutral-100">No topics yet</h2>
			<p class="text-sm text-neutral-500">
				Topics are generated automatically when enough articles are available.
			</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each data.clusters as cluster (cluster.id)}
				<a
					href="/topics/{cluster.id}"
					class="group rounded-xl border border-neutral-200 bg-white p-5 transition-all hover:border-neutral-300 hover:shadow-md dark:border-neutral-800 dark:bg-neutral-950 dark:hover:border-neutral-700"
				>
					<h2 class="mb-2 text-base font-semibold text-neutral-900 group-hover:text-blue-600 dark:text-neutral-100 dark:group-hover:text-blue-400">
						{cluster.label}
					</h2>
					{#if cluster.summary}
						<p class="mb-3 line-clamp-2 text-sm text-neutral-600 dark:text-neutral-400">
							{cluster.summary}
						</p>
					{/if}
					<div class="flex items-center gap-2 text-xs text-neutral-500">
						<span>{cluster.article_count} articles</span>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>
