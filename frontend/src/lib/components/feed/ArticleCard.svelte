<script lang="ts">
	import type { Entry } from '$lib/api/types';
	import TimeAgo from '$lib/components/shared/TimeAgo.svelte';
	import StarButton from '$lib/components/curation/StarButton.svelte';

	interface Props {
		entry: Entry;
		selectable?: boolean;
		selected?: boolean;
		focused?: boolean;
		index?: number;
		onSelect?: (id: number) => void;
	}

	let { entry, selectable = false, selected = false, focused = false, index, onSelect }: Props = $props();

	let excerpt = $derived(() => {
		if (!entry.content) return '';
		const div = typeof document !== 'undefined' ? document.createElement('div') : null;
		if (!div) return '';
		div.innerHTML = entry.content;
		return div.textContent?.slice(0, 200) || '';
	});
</script>

<article
	data-entry-index={index}
	class="group rounded-xl border bg-white p-4 transition-all hover:shadow-md dark:bg-neutral-950"
	class:border-blue-500={selected}
	class:border-neutral-200={!selected && !focused}
	class:dark:border-blue-500={selected}
	class:dark:border-neutral-800={!selected && !focused}
	class:hover:border-neutral-300={!selected}
	class:dark:hover:border-neutral-700={!selected}
	class:ring-2={focused && !selected}
	class:ring-blue-400={focused && !selected}
	class:dark:ring-blue-600={focused && !selected}
>
	<div class="mb-2 flex items-center gap-2 text-xs text-neutral-500">
		{#if selectable}
			<input
				type="checkbox"
				checked={selected}
				onchange={() => onSelect?.(entry.id)}
				class="h-3.5 w-3.5 rounded border-neutral-300"
			/>
		{/if}
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

	<a href="/article/{entry.id}" class="block">
		<h2 class="mb-1.5 text-base font-semibold leading-snug text-neutral-900 group-hover:text-blue-600 dark:text-neutral-100 dark:group-hover:text-blue-400">
			{entry.title}
		</h2>
		<p class="line-clamp-3 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
			{excerpt()}
		</p>
	</a>

	<div class="mt-3 flex items-center justify-between">
		<div class="flex items-center gap-2">
			<StarButton entryId={entry.id} starred={entry.starred} />
		</div>
		<a
			href={entry.url}
			target="_blank"
			rel="noopener noreferrer"
			class="text-xs text-neutral-400 transition-colors hover:text-neutral-600 dark:hover:text-neutral-300"
		>
			Visit source &rarr;
		</a>
	</div>
</article>
