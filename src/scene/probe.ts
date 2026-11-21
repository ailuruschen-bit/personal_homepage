/**
 * Switches for finding which part of the scene a Chrome rendering fault comes
 * from: ?no=story,gone,panels leaves those parts out. Diagnostic only; see
 * docs/09.
 *
 *   story   the document does not become scrollable when seated
 *   gone    no patches of the room without the carried objects
 *   panels  no chapter panels and no carried-object element
 */
const off = new Set((new URLSearchParams(location.search).get('no') ?? '').split(','));
export const without = (part: 'story' | 'gone' | 'panels') => off.has(part);
