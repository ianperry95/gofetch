<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import KeyboardHelp from '$lib/components/shared/KeyboardHelp.svelte';
	import { preferences } from '$lib/stores/preferences.svelte';
	import { keyboard } from '$lib/stores/keyboard.svelte';
	import { liveUpdates } from '$lib/stores/liveUpdates.svelte';
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/state';

	onMount(() => liveUpdates.connect());
	onDestroy(() => liveUpdates.disconnect());

	let { data, children } = $props();

	let currentFeedId = $derived.by(() => {
		const param = page.url?.searchParams.get('feed_id');
		return param ? parseInt(param) : undefined;
	});
</script>

<svelte:window onkeydown={(e) => keyboard.handleGlobal(e)} />

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>GoFetch</title>
</svelte:head>

<div class="flex h-screen overflow-hidden text-neutral-900 dark:text-neutral-100" class:dark={preferences.darkMode}>
	<Sidebar
		feeds={data.feeds}
		categories={data.categories}
		collections={data.collections}
		tags={data.tags}
		currentFeedId={currentFeedId}
	/>
	<main class="flex flex-1 flex-col overflow-hidden bg-neutral-50 dark:bg-neutral-950">
		{@render children()}
	</main>
	<KeyboardHelp />
</div>
