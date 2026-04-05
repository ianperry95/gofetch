import type { Layout, SortMode } from '$lib/api/types';

class PreferencesStore {
	layout: Layout = $state('cards');
	sort: SortMode = $state('ranked');
	darkMode: boolean = $state(false);
	sidebarOpen: boolean = $state(true);
	hideDuplicates: boolean = $state(true);
	articleFontSize: number = $state(18);
	articleMaxWidth: number = $state(720);
	articleFont: string = $state('system');

	constructor() {
		if (typeof window !== 'undefined') {
			this.load();
			this.darkMode =
				localStorage.getItem('gofetch-dark-mode') === 'true' ||
				window.matchMedia('(prefers-color-scheme: dark)').matches;
		}
	}

	private load() {
		try {
			const saved = localStorage.getItem('gofetch-preferences');
			if (saved) {
				const data = JSON.parse(saved);
				Object.assign(this, data);
			}
		} catch {
			// ignore
		}
	}

	save() {
		if (typeof window === 'undefined') return;
		localStorage.setItem(
			'gofetch-preferences',
			JSON.stringify({
				layout: this.layout,
				sort: this.sort,
				darkMode: this.darkMode,
				sidebarOpen: this.sidebarOpen,
				hideDuplicates: this.hideDuplicates,
				articleFontSize: this.articleFontSize,
				articleMaxWidth: this.articleMaxWidth,
				articleFont: this.articleFont
			})
		);
	}

	toggleDarkMode() {
		this.darkMode = !this.darkMode;
		this.save();
	}

	toggleSidebar() {
		this.sidebarOpen = !this.sidebarOpen;
		this.save();
	}

	setLayout(layout: Layout) {
		this.layout = layout;
		this.save();
	}

	setSort(sort: SortMode) {
		this.sort = sort;
		this.save();
	}
}

export const preferences = new PreferencesStore();
