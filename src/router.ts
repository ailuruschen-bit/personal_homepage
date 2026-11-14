/**
 * 极简 hash 路由。
 *
 *   #/            车厢（开幕 → 待机 → 主菜单）
 *   #/about 等    板块页，和 content/sections.ts 的 id 对应
 *
 * 用 hash 而不是 history API，是为了能直接作为静态文件部署，
 * 不需要服务端把所有路径都指向 index.html。
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
