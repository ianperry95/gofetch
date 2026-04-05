<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import StarButton from '$lib/components/curation/StarButton.svelte';
	import TimeAgo from '$lib/components/shared/TimeAgo.svelte';
	import TypographyControls from '$lib/components/shared/TypographyControls.svelte';
	import { preferences } from '$lib/stores/preferences.svelte';
	import { api } from '$lib/api/client';

	let { data } = $props();
	let entry = $derived(data.entry);

	const fontFamilies: Record<string, string> = {
		system: 'var(--font-sans)',
		serif: 'Georgia, "Times New Roman", serif',
		mono: '"JetBrains Mono", "Fira Code", "Consolas", monospace'
	};

	let startTime: number;

	onMount(() => {
		if (entry) {
			startTime = Date.now();
			api.interactions.record(entry.id, 'click');
			api.feed.updateStatus([entry.id], 'read');
		}
	});

	onDestroy(() => {
		if (entry && startTime) {
			const seconds = Math.round((Date.now() - startTime) / 1000);
			api.interactions.record(entry.id, 'read', seconds);
		}
	});
</script>

{#if entry}
	<div class="flex-1 overflow-y-auto">
		<div class="sticky top-0 z-10 flex items-center justify-between border-b border-neutral-200 bg-white/80 px-4 py-2 backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/80">
			<a
				href="/feed"
				class="flex items-center gap-1 rounded-md px-2 py-1 text-sm text-neutral-600 transition-colors hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
			>
				<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
				Back
			</a>
			<TypographyControls />
		</div>

		<article
			class="prose prose-neutral mx-auto px-6 py-8 dark:prose-invert"
			style="max-width: {preferences.articleMaxWidth}px; font-size: {preferences.articleFontSize}px; font-family: {fontFamilies[preferences.articleFont] || fontFamilies.system};"
		>
			<header class="not-prose mb-8">
				<div class="mb-3 flex items-center gap-2 text-sm text-neutral-500">
					<span class="font-medium text-neutral-700 dark:text-neutral-300">
						{entry.feed?.title ?? 'Unknown feed'}
					</span>
					<span>&middot;</span>
					<TimeAgo date={entry.published_at} />
					{#if entry.reading_time}
						<span>&middot;</span>
						<span>{entry.reading_time} min read</span>
					{/if}
				</div>

				<h1 class="text-3xl font-bold leading-tight text-neutral-900 dark:text-neutral-100">
					{entry.title}
				</h1>

				{#if entry.author}
					<p class="mt-2 text-sm text-neutral-500">by {entry.author}</p>
				{/if}

				<div class="mt-4 flex items-center gap-3">
					<StarButton entryId={entry.id} starred={entry.starred} />
					<a
						href={entry.url}
						target="_blank"
						rel="noopener noreferrer"
						class="text-sm text-blue-600 hover:underline dark:text-blue-400"
					>
						Read original &rarr;
					</a>
				</div>
			</header>

			{@html entry.content}
		</article>
	</div>
{:else}
	<div class="flex flex-1 items-center justify-center">
		<p class="text-neutral-500">Article not found.</p>
	</div>
{/if}
