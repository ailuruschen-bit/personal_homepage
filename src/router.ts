/**
 * Minimal hash router.
 *
 *   #/              the carriage (opening -> idle -> hub)
 *   #/about, ...    a section page, keyed by the ids in content/sections.ts
 *
 * Hash rather than the history API so the site can be deployed as plain static
 * files: no server rewrite pointing every path at index.html.
 */
export type Route = { name: 'scene' } | { name: 'section'; id: string };

export function parse(hash = location.hash): Route {
  const id = hash.replace(/^#\/?/, '').trim();
  return id ? { name: 'section', id } : { name: 'scene' };
}

export function go(route: Route) {
  const next = route.name === 'scene' ? '#/' : `#/${route.id}`;
  if (location.hash === next) window.dispatchEvent(new HashChangeEvent('hashchange'));
  else location.hash = next;
}

export function onChange(fn: (r: Route) => void) {
  window.addEventListener('hashchange', () => fn(parse()));
}
