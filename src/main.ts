import './styles/base.css';
import { mountScene, type SceneHandle } from './scene';
import { renderSection } from './sections/layout';
import { sectionById } from './content/sections';
import { go, onChange, parse, type Route } from './router';

const app = document.querySelector<HTMLElement>('#app')!;
let scene: SceneHandle | null = null;
/** 本次访问是否已经看过开幕；从板块页返回时不再重播 */
let openingSeen = false;

function render(route: Route) {
  scene?.destroy();
  scene = null;
  app.replaceChildren();

  if (route.name === 'scene') {
    scene = mountScene(app, {
      onEnter: (id) => go({ name: 'section', id }),
      skipOpening: openingSeen,
    });
    openingSeen = true;
    return;
  }

  const section = sectionById(route.id);
  if (!section) {
    // TODO: 404 页面
    go({ name: 'scene' });
    return;
  }
  openingSeen = true;
  app.append(renderSection(section, () => go({ name: 'scene' })));
}

render(parse());
onChange(render);
