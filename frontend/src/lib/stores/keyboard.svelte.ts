import { goto } from '$app/navigation';

export interface FeedNavigation {
	entries: { id: number }[];
	focusedIndex: number;
	setFocusedIndex: (i: number) => void;
	toggleStar?: (id: number) => void;
}

let _feedNav: FeedNavigation | null = $state(null);
let _showHelp = $state(false);

export const keyboard = {
	get feedNav() { return _feedNav; },
	set feedNav(v: FeedNavigation | null) { _feedNav = v; },

	get showHelp() { return _showHelp; },
	set showHelp(v: boolean) { _showHelp = v; },

	handleGlobal(e: KeyboardEvent) {
		// Ignore when typing in inputs
		const tag = (e.target as HTMLElement)?.tagName;
		if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

		switch (e.key) {
			case '?':
				e.preventDefault();
				_showHelp = !_showHelp;
				break;
			case 'Escape':
				if (_showHelp) {
					_showHelp = false;
					e.preventDefault();
				}
				break;
		}

		if (!_feedNav) return;

		const { entries, focusedIndex, setFocusedIndex, toggleStar } = _feedNav;

		switch (e.key) {
			case 'j':
				e.preventDefault();
				if (focusedIndex < entries.length - 1) {
					setFocusedIndex(focusedIndex + 1);
				}
				break;
			case 'k':
				e.preventDefault();
				if (focusedIndex > 0) {
					setFocusedIndex(focusedIndex - 1);
				}
				break;
			case 'o':
			case 'Enter':
				e.preventDefault();
				if (entries[focusedIndex]) {
					goto(`/article/${entries[focusedIndex].id}`);
				}
				break;
			case 's':
				e.preventDefault();
				if (entries[focusedIndex] && toggleStar) {
					toggleStar(entries[focusedIndex].id);
				}
				break;
		}
	}
};
