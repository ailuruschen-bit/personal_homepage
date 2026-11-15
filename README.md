# 个人主页

像素风个人站。开幕是一段夜车车窗的动画，车厢本身就是主菜单：
视线聚焦到哪个物件，就进入哪个板块。

当前版本只有**结构和交互**，所有文字都是占位，搜 `TODO` 可以找到要填的地方。

技术栈：Vite + TypeScript，无运行时依赖。

## 开发

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # 类型检查 + 打包到 dist/
npm run preview  # 预览打包结果
npm run format   # Prettier 格式化
```

纯静态站点，`dist/` 可直接部署到任何静态托管。
路由用 hash（`#/about`），所以不需要服务端改写规则。

## 目录

```
public/assets/        场景素材（WebP，由脚本生成，勿手工改）
tools/art/            生成上述素材的脚本（Python）
src/
  main.ts             入口：按路由渲染场景或板块页
  router.ts           hash 路由
  content/
    site.ts           站点级文案（封面标题、外链）  ← 填这里
    sections.ts       板块注册表：id / 名称 / 占位内容  ← 填这里
  scene/
    units.ts          480×480 场景坐标系与屏幕坐标换算
    hotspots.ts       可聚焦物件：目标板块、磁吸范围、光池、抬起轮廓
    dom.ts            生成车厢 DOM
    focus.ts          磁吸聚焦 + 聚光 + 相机（每帧 rAF）
    opening.ts        阶段机 intro/idle/back/hub/peek
    scene.css         场景样式与所有动画时长
  sections/
    layout.ts         板块页外壳（目前所有板块共用）
    sections.css
  styles/
    tokens.css        颜色、字体、动效变量  ← 换色改这里
    base.css
```

## 素材

`public/assets/` 里的场景图（天空、三层城市、车厢）都由 `tools/art/` 的脚本生成，
不是手工导出的。改画面就改脚本，然后重新生成：

```bash
pip install pillow numpy scipy
python3 tools/art/build.py
```

- `street.py` / `city.py` 中景：霓虹街区 + 一段破败街区（`c2.webp`，长图循环）
- `far.py` 远景天际线 `c1.webp`、轨旁设施 `c3.webp`、天空 `sky.webp`
- `room.py` 车厢 `room.webp` 及左右延伸段 `room-l.webp` / `room-r.webp`
- `px.py` / `parts.py` 画布、打光与各种零件

素材按 1 倍的像素坐标来画，输出时放大到 2 倍：固有色用 EPX 算法削掉斜线上的阶梯，
光照和辉光直接在 2 倍分辨率上计算。倍率在 `build.py` 的 `px.SCALE`。

车厢里可聚焦物件的位置要和 `src/scene/hotspots.ts` 对得上；城市素材的尺寸变了，
要同步改 `scene.css` 里 `.ly` 的高度和各层的 `--tile`。

## 几个关键设计

**场景坐标系。** 车厢是一张 480×480 的画。物件位置、磁吸范围、光池都用这套
坐标描述，与屏幕尺寸无关；`units.ts` 负责换算。改物件位置只改 `hotspots.ts`。

**聚焦逻辑。** 镜头保持一个固定的宽构图，不随指针推拉。吸附的是光和物件：
指针靠近物件时被牵引，进入范围瞬间吸附，离开立刻脱离。参考 iPadOS 的指针磁吸
与 tvOS 的焦点（抬起 + 打亮，而不是把其它地方压黑）。

**阶段机。** `.stage` 上的 class 决定阶段，动画时长全部写在 `scene.css` 里，
TS 只切 class。想调开幕节奏，改 CSS 里 `.intro .xxx` 那几行的 duration/delay。

## 待办

- [ ] 填入正式文案：`content/site.ts`、`content/sections.ts`
- [ ] notes / hobby / chat 三个板块还没有对应物件，需要画素材并在 `hotspots.ts` 注册
- [ ] 板块进入转场（目前是淡入，目标是「物件被拿起」式的转场）
- [ ] 笔记系统：Markdown 内容源、分类、搜索
- [ ] 对话板块与机器可读入口
- [ ] 回访者跳过开幕（目前只在单次访问内记住）
- [ ] 移动端真机验证：触摸是「点一下聚焦、再点进入」
- [ ] 多语言
