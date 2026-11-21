import './styles/base.css';
import { mountScene } from './scene';
import { sectionById } from './content/sections';
import { parse } from './router';

/**
 * One page: the carriage, and the chapters on its scroll (docs/10). A #/id link
 * lands with that chapter open; the scene keeps the hash in step with the
 * chapter being read, by replaceState, so following it later lands there too.
 */
const app = document.querySelector<HTMLElement>('#app')!;
const route = parse();
mountScene(app, {
  startAt: route.name === 'section' && sectionById(route.id) ? route.id : undefined,
});

// A link to another chapter while the page is open: land there the same way
window.addEventListener('hashchange', () => location.reload());
