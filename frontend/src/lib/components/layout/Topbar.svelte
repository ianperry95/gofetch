<script lang="ts">
	import { preferences } from '$lib/stores/preferences.svelte';
	import type { Layout, SortMode } from '$lib/api/types';

	interface Props {
		onRefresh?: () => void;
	}

	let { onRefresh }: Props = $props();

	const layouts: { value: Layout; label: string; icon: string }[] = [
		{ value: 'cards', label: 'Cards', icon: '▦' },
		{ value: 'list', label: 'List', icon: '☰' },
		{ value: 'magazine', label: 'Magazine', icon: '▣' }
	];

	const sorts: { value: SortMode; label: string }[] = [
		{ value: 'ranked', label: 'AI Ranked' },
		{ value: 'newest', label: 'Newest' },
		{ value: 'oldest', label: 'Oldest' }
	];
</script>

<header class="flex h-14 items-center justify-between border-b border-neutral-200 bg-white px-4 dark:border-neutral-800 dark:bg-neutral-950">
	<div class="flex items-center gap-3">
		<button
			onclick={() => preferences.toggleSidebar()}
			class="rounded-md p-1.5 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
			aria-label="Toggle sidebar"
		>
			<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
			</svg>
		</button>

		<div class="flex items-center gap-1 rounded-lg bg-neutral-100 p-0.5 dark:bg-neutral-900">
			{#each sorts as s}
				<button
					onclick={() => preferences.setSort(s.value)}
					class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors"
					class:bg-white={preferences.sort === s.value}
					class:shadow-sm={preferences.sort === s.value}
					class:dark:bg-neutral-800={preferences.sort === s.value}
					class:text-neutral-500={preferences.sort !== s.value}
				>
					{s.label}
				</button>
			{/each}
		</div>
	</div>

	<div class="flex items-center gap-2">
		<a
			href="/search"
			class="rounded-md p-1.5 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
			aria-label="Search"
		>
			<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
		</a>

		<div class="flex items-center gap-0.5 rounded-lg bg-neutral-100 p-0.5 dark:bg-neutral-900">
			{#each layouts as l}
				<button
					onclick={() => preferences.setLayout(l.value)}
					class="rounded-md px-2 py-1 text-sm transition-colors"
					class:bg-white={preferences.layout === l.value}
					class:shadow-sm={preferences.layout === l.value}
					class:dark:bg-neutral-800={preferences.layout === l.value}
					class:text-neutral-400={preferences.layout !== l.value}
					aria-label={l.label}
				>
					{l.icon}
				</button>
			{/each}
		</div>

		<button
			onclick={() => preferences.toggleDarkMode()}
			class="rounded-md p-1.5 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
			aria-label="Toggle dark mode"
		>
			{#if preferences.darkMode}
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
				</svg>
			{:else}
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
				</svg>
			{/if}
		</button>

		{#if onRefresh}
			<button
				onclick={onRefresh}
				class="rounded-md p-1.5 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900"
				aria-label="Refresh"
			>
				<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
				</svg>
			</button>
		{/if}
	</div>
</header>
