<script lang="ts">
	import { preferences } from '$lib/stores/preferences.svelte';
	import type { Layout, SortMode } from '$lib/api/types';
	import { onMount } from 'svelte';

	let importStatus = $state<{ type: 'success' | 'error'; message: string } | null>(null);
	let importing = $state(false);

	// Server config state
	let configValues = $state<Record<string, string>>({});
	let configDefs = $state<Record<string, { label: string; type: string; group: string; description: string; options?: string[] }>>({});
	let configLoaded = $state(false);
	let configSaving = $state(false);
	let configStatus = $state<{ type: 'success' | 'error'; message: string } | null>(null);

	onMount(async () => {
		try {
			const res = await fetch('/api/settings/config');
			if (res.ok) {
				const data = await res.json();
				const values: Record<string, string> = {};
				const defs: typeof configDefs = {};
				for (const [key, meta] of Object.entries(data)) {
					const m = meta as any;
					values[key] = m.value || '';
					defs[key] = { label: m.label, type: m.type, group: m.group, description: m.description, options: m.options };
				}
				configValues = values;
				configDefs = defs;
				configLoaded = true;
			}
		} catch {
			// Config endpoint not available, that's fine
		}
	});

	async function saveConfig() {
		configSaving = true;
		configStatus = null;
		try {
			const res = await fetch('/api/settings/config', {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ values: configValues })
			});
			if (res.ok) {
				const data = await res.json();
				configStatus = { type: 'success', message: `Updated ${data.updated?.length || 0} settings.` };
				// Refresh to get masked values
				const refresh = await fetch('/api/settings/config');
				if (refresh.ok) {
					const rdata = await refresh.json();
					for (const [key, meta] of Object.entries(rdata)) {
						configValues[key] = (meta as any).value || '';
					}
				}
			} else {
				configStatus = { type: 'error', message: 'Failed to save settings.' };
			}
		} catch {
			configStatus = { type: 'error', message: 'Failed to save settings. Check your connection.' };
		} finally {
			configSaving = false;
		}
	}

	async function exportOpml() {
		const res = await fetch('/api/settings/opml/export');
		if (!res.ok) return;
		const blob = await res.blob();
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'gofetch-feeds.opml';
		a.click();
		URL.revokeObjectURL(url);
	}

	async function importOpml(e: Event) {
		const input = e.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		importing = true;
		importStatus = null;

		const formData = new FormData();
		formData.append('file', file);

		try {
			const res = await fetch('/api/settings/opml/import', {
				method: 'POST',
				body: formData
			});
			if (res.ok) {
				const data = await res.json();
				importStatus = { type: 'success', message: data.message || 'Import complete. New feeds will appear shortly.' };
			} else {
				importStatus = { type: 'error', message: `Import failed: ${res.statusText}` };
			}
		} catch {
			importStatus = { type: 'error', message: 'Import failed. Check your connection.' };
		} finally {
			importing = false;
			input.value = '';
		}
	}

	const layouts: { value: Layout; label: string; desc: string }[] = [
		{ value: 'cards', label: 'Cards', desc: 'Grid of article cards' },
		{ value: 'list', label: 'List', desc: 'Dense single-column list' },
		{ value: 'magazine', label: 'Magazine', desc: 'Featured article + grid' }
	];

	const sorts: { value: SortMode; label: string; desc: string }[] = [
		{ value: 'ranked', label: 'AI Ranked', desc: 'Sorted by relevance to your interests' },
		{ value: 'newest', label: 'Newest', desc: 'Most recent first' },
		{ value: 'oldest', label: 'Oldest', desc: 'Oldest first' }
	];

	const fonts = [
		{ value: 'system', label: 'System', desc: 'Default system font' },
		{ value: 'serif', label: 'Serif', desc: 'Georgia / Times' },
		{ value: 'mono', label: 'Mono', desc: 'Monospace / code font' }
	];

	// Group config keys by group
	let configGroups = $derived(() => {
		if (!configLoaded) return {};
		const groups: Record<string, string[]> = {};
		for (const key of Object.keys(configDefs)) {
			const group = configDefs[key].group;
			if (!groups[group]) groups[group] = [];
			groups[group].push(key);
		}
		return groups;
	});
</script>

<div class="flex-1 overflow-y-auto">
	<div class="mx-auto max-w-2xl px-6 py-8">
		<h1 class="mb-8 text-2xl font-bold text-neutral-900 dark:text-neutral-100">Settings</h1>

		<!-- Appearance -->
		<section class="mb-8">
			<h2 class="mb-4 text-lg font-semibold text-neutral-900 dark:text-neutral-100">Appearance</h2>

			<div class="space-y-4">
				<!-- Dark mode -->
				<div class="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<div>
						<p class="font-medium text-neutral-900 dark:text-neutral-100">Dark mode</p>
						<p class="text-sm text-neutral-500">Use dark color scheme</p>
					</div>
					<button
						onclick={() => preferences.toggleDarkMode()}
						class="relative h-6 w-11 rounded-full transition-colors"
						class:bg-blue-600={preferences.darkMode}
						class:bg-neutral-300={!preferences.darkMode}
						role="switch"
						aria-checked={preferences.darkMode}
					>
						<span
							class="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform"
							style="left: {preferences.darkMode ? 'calc(100% - 1.375rem)' : '0.125rem'}"
						></span>
					</button>
				</div>

				<!-- Default layout -->
				<div class="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<p class="mb-2 font-medium text-neutral-900 dark:text-neutral-100">Default layout</p>
					<div class="flex gap-2">
						{#each layouts as l}
							<button
								onclick={() => preferences.setLayout(l.value)}
								class="flex-1 rounded-lg border p-3 text-left transition-colors"
								class:border-blue-500={preferences.layout === l.value}
								class:bg-blue-50={preferences.layout === l.value}
								class:dark:bg-blue-950={preferences.layout === l.value}
								class:border-neutral-200={preferences.layout !== l.value}
								class:dark:border-neutral-700={preferences.layout !== l.value}
								class:hover:border-neutral-300={preferences.layout !== l.value}
							>
								<p class="text-sm font-medium text-neutral-900 dark:text-neutral-100">{l.label}</p>
								<p class="text-xs text-neutral-500">{l.desc}</p>
							</button>
						{/each}
					</div>
				</div>

				<!-- Default sort -->
				<div class="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<p class="mb-2 font-medium text-neutral-900 dark:text-neutral-100">Default sort</p>
					<div class="flex gap-2">
						{#each sorts as s}
							<button
								onclick={() => preferences.setSort(s.value)}
								class="flex-1 rounded-lg border p-3 text-left transition-colors"
								class:border-blue-500={preferences.sort === s.value}
								class:bg-blue-50={preferences.sort === s.value}
								class:dark:bg-blue-950={preferences.sort === s.value}
								class:border-neutral-200={preferences.sort !== s.value}
								class:dark:border-neutral-700={preferences.sort !== s.value}
								class:hover:border-neutral-300={preferences.sort !== s.value}
							>
								<p class="text-sm font-medium text-neutral-900 dark:text-neutral-100">{s.label}</p>
								<p class="text-xs text-neutral-500">{s.desc}</p>
							</button>
						{/each}
					</div>
				</div>
			</div>
		</section>

		<!-- Reading -->
		<section class="mb-8">
			<h2 class="mb-4 text-lg font-semibold text-neutral-900 dark:text-neutral-100">Reading</h2>

			<div class="space-y-4">
				<!-- Font family -->
				<div class="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<p class="mb-2 font-medium text-neutral-900 dark:text-neutral-100">Article font</p>
					<div class="flex gap-2">
						{#each fonts as f}
							<button
								onclick={() => { preferences.articleFont = f.value; preferences.save(); }}
								class="flex-1 rounded-lg border p-3 text-left transition-colors"
								class:border-blue-500={preferences.articleFont === f.value}
								class:bg-blue-50={preferences.articleFont === f.value}
								class:dark:bg-blue-950={preferences.articleFont === f.value}
								class:border-neutral-200={preferences.articleFont !== f.value}
								class:dark:border-neutral-700={preferences.articleFont !== f.value}
								class:hover:border-neutral-300={preferences.articleFont !== f.value}
							>
								<p class="text-sm font-medium text-neutral-900 dark:text-neutral-100">{f.label}</p>
								<p class="text-xs text-neutral-500">{f.desc}</p>
							</button>
						{/each}
					</div>
				</div>

				<!-- Font size -->
				<div class="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<div class="flex items-center justify-between">
						<p class="font-medium text-neutral-900 dark:text-neutral-100">Font size</p>
						<span class="text-sm text-neutral-500">{preferences.articleFontSize}px</span>
					</div>
					<input
						type="range"
						min="14"
						max="28"
						step="1"
						value={preferences.articleFontSize}
						oninput={(e) => { preferences.articleFontSize = parseInt((e.target as HTMLInputElement).value); preferences.save(); }}
						class="mt-2 w-full"
					/>
				</div>

				<!-- Max width -->
				<div class="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<div class="flex items-center justify-between">
						<p class="font-medium text-neutral-900 dark:text-neutral-100">Article width</p>
						<span class="text-sm text-neutral-500">{preferences.articleMaxWidth}px</span>
					</div>
					<input
						type="range"
						min="480"
						max="1080"
						step="40"
						value={preferences.articleMaxWidth}
						oninput={(e) => { preferences.articleMaxWidth = parseInt((e.target as HTMLInputElement).value); preferences.save(); }}
						class="mt-2 w-full"
					/>
				</div>
			</div>
		</section>

		<!-- Server Configuration -->
		{#if configLoaded}
			<section class="mb-8">
				<h2 class="mb-4 text-lg font-semibold text-neutral-900 dark:text-neutral-100">Server Configuration</h2>

				<div class="space-y-4">
					{#each Object.entries(configGroups()) as [group, keys]}
						{#each keys as key, i}
							{@const def = configDefs[key]}
							<div class="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
								<label class="mb-1 block">
									<p class="font-medium text-neutral-900 dark:text-neutral-100">{def.label}</p>
									<p class="text-sm text-neutral-500">{def.description}</p>
								</label>
								{#if def.type === 'select' && def.options}
									<select
										bind:value={configValues[key]}
										class="mt-2 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100"
									>
										{#each def.options as opt}
											<option value={opt}>{opt}</option>
										{/each}
									</select>
								{:else}
									<input
										type={def.type === 'password' ? 'password' : 'text'}
										bind:value={configValues[key]}
										placeholder={def.type === 'password' ? 'Enter new value or leave unchanged' : ''}
										class="mt-2 w-full rounded-lg border border-neutral-200 px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100"
									/>
								{/if}
							</div>
						{/each}
					{/each}

					<!-- Save button -->
					<div class="flex items-center justify-between">
						<button
							onclick={saveConfig}
							disabled={configSaving}
							class="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-neutral-800 disabled:opacity-50 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-200"
						>
							{configSaving ? 'Saving...' : 'Save Configuration'}
						</button>
						<p class="text-xs text-neutral-500">Changes may require a restart to take effect.</p>
					</div>

					{#if configStatus}
						<div
							class="rounded-md px-3 py-2 text-sm"
							class:bg-green-50={configStatus.type === 'success'}
							class:text-green-800={configStatus.type === 'success'}
							class:dark:bg-green-900={configStatus.type === 'success'}
							class:dark:text-green-200={configStatus.type === 'success'}
							class:bg-red-50={configStatus.type === 'error'}
							class:text-red-800={configStatus.type === 'error'}
							class:dark:bg-red-900={configStatus.type === 'error'}
							class:dark:text-red-200={configStatus.type === 'error'}
						>
							{configStatus.message}
						</div>
					{/if}
				</div>
			</section>
		{/if}

		<!-- Feed Management -->
		<section class="mb-8">
			<h2 class="mb-4 text-lg font-semibold text-neutral-900 dark:text-neutral-100">Feed Management</h2>

			<div class="space-y-4">
				<!-- OPML Export -->
				<div class="flex items-center justify-between rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<div>
						<p class="font-medium text-neutral-900 dark:text-neutral-100">Export feeds</p>
						<p class="text-sm text-neutral-500">Download all your feed subscriptions as OPML</p>
					</div>
					<button
						onclick={exportOpml}
						class="rounded-lg bg-neutral-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-neutral-800 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-200"
					>
						Export OPML
					</button>
				</div>

				<!-- OPML Import -->
				<div class="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
					<div class="flex items-center justify-between">
						<div>
							<p class="font-medium text-neutral-900 dark:text-neutral-100">Import feeds</p>
							<p class="text-sm text-neutral-500">Import feed subscriptions from an OPML file</p>
						</div>
						<label
							class="cursor-pointer rounded-lg border border-neutral-300 px-4 py-2 text-sm font-medium transition-colors hover:bg-neutral-50 dark:border-neutral-600 dark:hover:bg-neutral-800"
							class:opacity-50={importing}
						>
							{importing ? 'Importing...' : 'Choose file'}
							<input
								type="file"
								accept=".opml,.xml"
								onchange={importOpml}
								disabled={importing}
								class="hidden"
							/>
						</label>
					</div>

					{#if importStatus}
						<div
							class="mt-3 rounded-md px-3 py-2 text-sm"
							class:bg-green-50={importStatus.type === 'success'}
							class:text-green-800={importStatus.type === 'success'}
							class:dark:bg-green-900={importStatus.type === 'success'}
							class:dark:text-green-200={importStatus.type === 'success'}
							class:bg-red-50={importStatus.type === 'error'}
							class:text-red-800={importStatus.type === 'error'}
							class:dark:bg-red-900={importStatus.type === 'error'}
							class:dark:text-red-200={importStatus.type === 'error'}
						>
							{importStatus.message}
						</div>
					{/if}
				</div>
			</div>
		</section>

		<!-- Keyboard shortcuts -->
		<section class="mb-8">
			<h2 class="mb-4 text-lg font-semibold text-neutral-900 dark:text-neutral-100">Keyboard Shortcuts</h2>
			<div class="rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-950">
				{#each [
					{ key: 'j / k', desc: 'Navigate between articles' },
					{ key: 'o / Enter', desc: 'Open selected article' },
					{ key: 's', desc: 'Toggle star on selected article' },
					{ key: '?', desc: 'Show keyboard shortcuts overlay' },
					{ key: 'Esc', desc: 'Close dialogs' }
				] as shortcut, i}
					<div
						class="flex items-center justify-between px-4 py-3"
						class:border-t={i > 0}
						class:border-neutral-200={i > 0}
						class:dark:border-neutral-800={i > 0}
					>
						<span class="text-sm text-neutral-600 dark:text-neutral-400">{shortcut.desc}</span>
						<kbd class="rounded bg-neutral-100 px-2 py-0.5 text-xs font-mono font-medium text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
							{shortcut.key}
						</kbd>
					</div>
				{/each}
			</div>
		</section>
	</div>
</div>
