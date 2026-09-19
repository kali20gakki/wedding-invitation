# 风之旅 · 吉卜力画风婚礼邀请函｜完整实施方案

> 本文是**给后续执行者（人或 AI Agent）用的落地说明书**。读完本文即可独立完成改造，**不需要再做任何设计决策**。凡涉及取舍的地方，本文都给出了确定的默认值与降级路径。
>
> - 项目：`wedding-invitation`（原「BLUE HOLE WEDDING / 潜水员戴夫主题婚礼请柬 Demo」）
> - 目标形态：**吉卜力画风 + 风之旅叙事 + 互动玩法 + 抽卡留念 + GitHub Pages 部署 + 飞书问卷收数据**
> - 技术栈：**零构建纯静态**（HTML + CSS + 原生 JS），无框架、无打包、无依赖
> - 文件命名建议：`PLAN-GHIBLI-WEDDING.zh-CN.md`（与仓库既有 `GUIDE.zh-CN.md`、`SHARE.zh-CN.md` 风格一致）

---

## 0. 执行摘要（先读这一节）

| 项目 | 内容 |
| --- | --- |
| **最终产物** | 一个可在 GitHub Pages 上访问的手机端互动婚礼邀请函：宾客收到链接 → 沉浸式开场 → 接受委托 → 摇风铃、接纸鹤 → 读四位镇民的来信 → 看当日行程 → 手绘地图导航 → 通过飞书问卷登记 → 抽一张邀请函卡片保存留念 |
| **代码改动量** | `style.css`（大）、`index.html`（中）、`app.js`（中）、`admin/*`（路径修复）、8 份文档（轻改/新增） |
| **需要人工产出的素材** | 婚纱照原片 8~12 张（本人拍摄）+ 婚礼文字信息 + 飞书问卷链接 + 背景音乐（可选） |
| **需要 AI 生成的素材** | 约 **18 张**必需图 + 2 张可选装饰图（清单见 §5） |
| **最大风险** | ① 多张 AI 出图风格不统一；② 生成人物脸不像本人；③ 卡面中文字生成错误 |
| **风险对策** | 风格母本图 + 每张都传参考图（§7.2）；`input_fidelity: high` + 显式锁五官提示词（§7.2）；卡面文字改为后期叠加（§8.1） |
| **验收方式** | 功能回归清单（§11.2）+ 三档手机宽度实测（§11.3）+ 多模态看图检查（§9） |
| **明确不做的事** | 不改类名/ID、不做构建流程、不引入前端框架、不引入 Google Fonts CDN、不用任何吉卜力原声或官方美术素材 |

---

## 1. 已锁定的决策（不可自行更改）

这些是与项目所有者确认过的决定。执行时**不要重新讨论**，直接照做。

| # | 决策 | 说明 |
| --- | --- | --- |
| 1 | **不保留海/水下元素** | 整站母题换成"风之旅"：风铃 + 纸鹤 + 旅人手账 + 邮局信箱。声呐、鱼、潜水仪表全部替换 |
| 2 | **角色位 = 1 + 3** | `#crew` 的 4 个位置：1 张新人双人立绘 + 3 张原创小镇角色 |
| 3 | **全部保留互动玩法** | 长按接受委托 / 风铃三响 / 接满 5 只纸鹤，全部保留，只换皮。游戏感也必须统一成吉卜力手绘风 |
| 4 | **生成提示词保留风格指向词** | 提示词中明确使用 `Studio Ghibli style, Hayao Miyazaki style`，不做规避改写。仅限 `PROMPTS.md` 与生成提示词，不写进网页可见文本 |
| 5 | **新增抽卡环节** | 登记后抽一张预生成的邀请函卡片，可保存/分享留念 |
| 6 | **部署到 GitHub Pages，登记走飞书问卷** | 不使用 Cloudflare 后端收集数据 |
| 7 | **引入模型多模态检查** | 素材与页面在入库前必须经过读图检查并回写结论 |

### 1.1 执行者需要自行拍板的两个默认值

若项目所有者未另行指定，**采用以下默认值**（这是推荐值，不要卡住等确认）：

| 待定项 | 默认执行 | 备选方案 |
| --- | --- | --- |
| **Cloudflare 相关路径**（`functions/`、`migrations/`、`admin/`、`wrangler.jsonc`、`_routes.json`） | **一并删除**。理由是 GitHub Pages 不执行 `functions/`，而它会被当静态文件公开源代码，且走飞书收数据后自建后台无用途 | 若所有者要求保留模板能力：**保留目录**，但必须在 `README.md` 与 `后台部署说明.md` 顶部注明"仅 `wrangler pages dev` 或 Cloudflare Pages 可用；GitHub Pages 下不生效" |
| **抽卡个性化姓名** | **先只做预生成卡面**（卡上无宾客姓名）。个性化姓名作为**第二阶段可选增强**，且必须通过 §8.4 的能力探测；探测不通过就静默退回通用文案，不得报错 | 若所有者在实机测试后明确要求：按 §8.4 完整实现 |

---

## 2. 目标与成功标准

### 2.1 目标

把现有"深海潜水任务"主题的互动婚礼请柬，完整改造为**吉卜力画风的"风之旅"主题**，保留全部交互骨架与移动端体验，替换全部文案、视觉、素材与叙事，新增登记后抽卡留念环节，并交付一个可直接部署到 GitHub Pages 的静态站点。

### 2.2 成功标准（全部可客观验证）

1. 手机端（375 / 390 / 430 px）打开页面无横向滚动、无文字溢出、无按钮遮挡
2. 页面可见文本中不再出现 `dave / DAVE / 蓝洞 / BLUE HOLE / 潜水 / 声呐 / 鱼 / 寿司 / 2030 / 示例市` 等旧主题词
3. 全部视觉元素（背景、图标、动画、字体、阴影）统一为手绘水彩质感，**不残留任何像素/霓虹/扫描线风格**
4. 现有 8 项交互行为零回归（清单见 §11.2）
5. 新抽卡环节在 iOS Safari、安卓 Chrome、桌面 Chrome/Edge 上均可完成"抽取 → 保存/分享"
6. 飞书问卷链接可从页面正常打开，`RSVP_FORM_URL` 外链模式生效
7. GitHub Pages 子路径部署（`用户名.github.io/仓库名/`）下无 404
8. `assets/` 目录总量 ≤ 2.5 MB，首页首屏主视觉 ≤ 350 KB
9. 仓库内无 API Key、无原始婚纱照、无 AI 生成中间产物
10. `MATERIALS.md` 与 `PROMPTS.md` 两份台账完整，每张图都有来源与检查结论

---

## 3. 现有项目事实基线（执行前必读）

这一节是执行者做改动时的**事实依据**，不要凭猜测改动。

### 3.1 文件结构

```text
wedding-invitation/
├── index.html                  # 单页请柬（128 行）
├── style.css                   # 全部样式（约 25 KB，压缩成 12 行的超长行）
├── app.js                      # 全部交互（205 行）
├── assets/                     # 图片素材（现有约 4.8 MB）
├── admin/                      # 主办人后台（index.html / admin.css / admin.js）
├── functions/                  # Cloudflare Pages 接口（api/rsvp.js、api/admin/*、_lib/*）
├── migrations/                 # D1 建表脚本 0001_create_rsvps.sql
├── wrangler.jsonc              # Cloudflare 配置
├── _routes.json                # Cloudflare 路由配置
├── README.md
├── GUIDE.zh-CN.md              # 零基础定制教程
├── RSVP_BACKEND.zh-CN.md       # 第三方表单接入教程
├── SHARE.zh-CN.md              # 分享给亲友教程
├── AI_PUBLISH_GUIDE.zh-CN.md   # AI 发布教程
├── COPYRIGHT_NOTICE.md         # 版权风险说明
├── THIRD_PARTY_ASSETS.md       # 第三方素材清单
├── 后台部署说明.md              # Cloudflare 后台部署
├── LICENSE                     # MIT（仅覆盖原创代码）
└── .gitignore                  # .wrangler/ .dev.vars .env node_modules/
```

### 3.2 页面板块与交互骨架（改造时必须保留的行为）

| 板块 | id / class | 现有行为 | 改造后是否改逻辑 |
| --- | --- | --- | --- |
| 首页 | `.hero` `#top` | 整屏背景 + `#start-mission` 按钮：播放音乐并平滑滚动到 `#briefing` | 否 |
| HUD | `.game-hud` | 滚动到 55% 屏高后出现；`#depth-value` = `progress*420`；`#oxygen-fill` = `scaleX(1 - progress*0.22)` | 否 |
| 委托 | `#briefing` `.underwater` | 28 个气泡由 JS 生成；`#sonar-button` 点击生成波纹并高亮场内元素；`app.js` 生成 9 个 `.pixel-fish`，点击捕获，上限 5，随机弹出祝福；集齐弹文案 | 否 |
| 委托卡 | `.mission-card` `#accept-quest` | 长按 1 秒 → `.is-accepted`、`#quest-status` 变 `ACCEPTED`、`#mission-complete` 浮层、`navigator.vibrate` | 仅时长可选调 1.2s |
| 角色 | `#crew` `.crew-slide` × 4 | `[data-crew="prev"/"next"]` 循环切换，计数 `#crew-name` 显示 `NAME · n/4` | 否 |
| 日程 | `#schedule` | 静态 `.menu-board` 列表 + `#days-count` 倒计时（`app.js` 第 1 行 `weddingDate`） | 否 |
| 地图 | `#arrival` | 静态卡片 + 外部地图链接 | 否 |
| 登记 | `#rsvp` | `RSVP_FORM_URL` 非空 → 隐藏本地表单、显示 `#rsvp-external`、状态改 `ONLINE`；为空 → 本地 demo 模式写 `localStorage`，含必填校验、住宿联动、200 字计数、可回填修改 | **本次强制走外链模式** |
| 结尾 | `.ending` | 静态背景图 + 文案 | 否 |
| 底部导航 | `.quick-nav` | 4 个锚点链接 | 否 |
| 音乐坞 | `.music-dock` | `#music-toggle` 播放/暂停；`#music-hint` 滚动 20px 后隐藏 | 否 |

### 3.3 `app.js` 关键行号（改动参考）

| 行号 | 内容 | 本次处理 |
| --- | --- | --- |
| 1 | `const weddingDate = new Date('2030-10-01T11:58:00+08:00')` | 换成真实婚礼时间 |
| 3 | `const RSVP_FORM_URL = ''` | 填入飞书问卷链接 |
| 4 | 倒计时写入 `#days-count` | 不改 |
| 6 | `reducedMotion` 判断 | 保留，新动画全部尊重它 |
| 17–24 | 气泡生成循环（28 个） | 保留数量，改 CSS 呈现 |
| 26–39 | `updateHud()` | 保留公式，只改文案与颜色 |
| 41–69 | 长按逻辑 | 保留，时长可调 |
| 71–78 | 声呐点击 | **扩展为风铃三响** |
| 80–112 | 纸鹤/鱼生成与捕获 | 保留逻辑，改图标与数据 |
| 82 | `fishColors` | 换成吉卜力色卡 |
| 83 | `fishBlessings` | 换成 6 条温柔祝福 |
| 114–123 | 角色轮播 | 保留，改 `data-name` 与图片 |
| 125–145 | 音乐控制 | 保留，换音频源与提示文案 |
| 147–205 | 登记表单 | **外链模式分支保留即可，本地 demo 分支保留不删** |
| 169 | `storageKey = 'dave-wedding-demo-rsvp'` | 改为 `journey-wedding-demo-rsvp` |

### 3.4 已确认的现存问题（必须修掉）

| 问题 | 位置 | 后果 | 处理 |
| --- | --- | --- | --- |
| **绝对路径引资源** | `admin/index.html` 第 9、19、39、54 行：`/assets/...`；第 10 行 `/admin/admin.css`；第 82 行 `/admin/admin.js` | 部署到 GitHub Pages 子路径下**全部 404** | 改为 `../assets/...`、`./admin.css`、`./admin.js` |
| **扩展名与真实格式不符** | `assets/bancho.webp` 实测是 **JPEG 1017×572**（同规格的 `bacon.webp`、`cobra.webp`、`dave-character.webp` 均为约 170KB 同批文件） | 浏览器嗅探或压缩流水线可能踩坑 | 旧素材将整体删除；**新素材入库必须用读图工具核对真实格式与尺寸** |
| **登记文案与现实不符** | `index.html` 第 104 行：「DEMO MODE · 登记内容只保存在当前浏览器，不会上传到服务器」 | 接入飞书后这句话是**错误信息**，构成误导 | 改为明确的数据流向披露（见 §10.3） |
| **`og:image` 用绝对域名** | `index.html` 第 12、17 行指向原作者仓库的 GitHub Pages 地址 | 分享卡片显示别人的图 | 换成新部署地址的完整 HTTPS 地址 |
| **无引用的冗余素材** | `dave-key-art.webp`、`dave-logo.webp`、`phone-ui.webp` 在代码中查无引用 | 白占体积 | 随旧素材一并删除 |

### 3.5 部署环境约束

| 约束 | 说明 |
| --- | --- |
| GitHub Pages 是**纯静态** | 不执行任何服务端代码，`functions/` 下的 `.js` 只会被当静态文件公开 |
| 子路径部署 | 仓库名非 `用户名.github.io` 时，站点根路径是 `/仓库名/`，所有绝对路径都会失效 |
| 区分大小写 | 文件名大小写必须与引用完全一致（`GUIDE.zh-CN.md` 第十四节已警示） |
| 无服务端 | 飞书问卷是唯一的数据收集途径，页面无法感知提交结果 |

---

## 4. 叙事框架与元素替换总表

### 4.1 故事闭环

> **信从风车邮局寄出 → 你收信、接受委托 → 循着风铃与纸鹤找到这座小镇 → 读四封镇民的来信 → 看当日的行程 → 沿手绘地图到场 → 在旅人名册上落款 → 抽一张卡片带走。**

寄出 → 收到 → 认路 → 到场 → 落款 → 留念。**每个交互都对应剧情的一个动作**，这是"换皮不突兀"的判据：任何替换后无法解释"宾客为什么要点它"的元素，都算失败。

### 4.2 板块标题与设定

| 板块 | 现标题 | 新标题 | 新设定 |
| --- | --- | --- | --- |
| `.hero` | 蓝洞海面 | **启程** ·「风起时，请来赴约」 | 山丘小镇俯瞰：老式蒸汽火车沿山崖驶过、风车缓缓转动、大朵积云、远处海面 |
| `#briefing` | 蓝洞特别委托 | **一封信** ·「致我们最好的朋友」 | 书桌上的羊皮纸请柬被风吹到窗边，长按拆封 |
| `#crew` | 蓝洞小队来电 | **风车邮局来信** ·「四封信」 | 四位镇民的来信，一封一封摊开 |
| `#schedule` | 婚礼当日菜单 | **旅人手账** ·「当日的行程」 | 手绘路线图 + 亚麻布上的手写便当日程 + 花环倒计时 |
| `#arrival` | 返回海面集合 | **手绘地图** ·「往那盏灯的路」 | 水彩地图、纸纹、咖啡渍，小红旗标出会馆 |
| `#rsvp` | 登记潜水小队 | **旅人名册** ·「在旅人手账上落款」 | 牛皮纸手账本，外链飞书问卷 |
| `#draw`（新增） | — | **带走一张** ·「抽一张属于你的邀请函」 | 卡背扇形展开，翻牌揭晓 |
| `.ending` | 在深蓝里相遇 | **「风会记得我们的名字」** | 夕阳山坡上的两个剪影 |

### 4.3 逐元素替换表

| 现元素（代码钩子） | 现语义 | 新语义 | 具体做法 | 逻辑改动 |
| --- | --- | --- | --- | --- |
| `.hero-art` → `assets/dave-key-art-clean.png` | 蓝洞海面 | 山丘小镇 + 蒸汽火车 + 风车 | 换成 `hero-journey.webp`（竖）/`hero-journey-wide.webp`（横），用 `<picture>` 分档 | 无 |
| `.hero-hud` | `BLUE HOLE` / `2030.10.01` / `MISSION 01` | `A JOURNEY OF WIND` / 日期 / `LETTER 01` | 纯文案 | 无 |
| `.mission-code` | `SPECIAL WEDDING MISSION` | `A LETTER CARRIED BY THE WIND` | 纯文案 | 无 |
| `#start-mission` | 接受委托，开始下潜 | 收下这封信，出发 | 纯文案 | 无 |
| `.game-hud` 三项 | `DEPTH 深度` / `O₂ 氧气` / `🐟 0/5` | `WIND 风的刻度` / `HEIGHT 云的高度` / `🕊 纸鹤 0/5` | 改标签文案；填充色由青色改云白 | **无**（`progress*420` 与 `scaleX` 公式原样保留） |
| `.underwater` | 深蓝水下渐变 | 天空→草原渐变 | `linear-gradient(#A8CFE0 0, #DCEAF0 32%, #8FAE6B 68%, #F7F0E1)` | 无 |
| `.water-rays` + `@keyframes rays` | 水下丁达尔光 | 云隙光 / 风带 | 重写为 `@keyframes drift`：云影横向缓移 12s 循环 | 无 |
| `.bubble-field i` | 上浮气泡 | 风和叶屑 | `@keyframes rise` → `@keyframes float`：小圆点缓旋转上浮，暖白色；JS 数量 28 不变 | 无 |
| `.sonar-button` / `.sonar-field` / `@keyframes sonar` | 声呐探测 | **风铃** | 见 §4.4 | 无（在原监听器内扩展） |
| `.fish-caption` / `.fish-arrow` | 点击海里的鱼试试看 | 风把纸鹤吹来了，点一点看看 | 纯文案 | 无 |
| `.pixel-fish` × 9 | 像素鱼 | **风里的纸鹤** | `clip-path` 改折纸鹤形态；`@keyframes swim` → `glide`（横移 + 正弦上下浮动） | 无 |
| `.pixel-fish.caught` | 被捕获 | 纸鹤展开成祝福笺 | 保留 `caught` 动画，形状改成摊开的纸条 | 无 |
| `.fish-blessing` | 卡通气泡 | 手写纸条 | 纸纹底、微旋转（-2deg）、虚线边、柔和阴影 | 无 |
| 集齐 5 条文案 | 祝福图鉴已完成：幸福值 +1000 | 纸鹤收齐了：愿风替我们把这些祝福捎给你 | 纯文案 | 无 |
| `.crew-phone` + `.phone-top` | `iDIVER` / `INCOMING CALL` | 风车邮局信箱 `WINDMILL POST` / `4 LETTERS` | 改文案；卡片改摊开的信纸质感 | 无 |
| `.restaurant-screen` + `.restaurant-status` | 班乔寿司店动画 | 老街的木窗 + 面包篮与陶杯；状态 `OPEN FOR GUESTS` | 换图 `scene-window.webp` + 文案 | 无 |
| `.menu-board` | 卤素寿司菜单 | 亚麻布上的手写便当单 | 改色与质感；`★` → `❀`；`<time>` 结构不变 | 无 |
| `.countdown-card` | `NEXT DIVE IN` | `距启程还有` | 纯文案 | 无 |
| `.arrival` / `.map-console` | 海面集合导航 | 手绘水彩地图 | 换图 `scene-map.webp`；`.map-pulse` 的 `♥` 保留为小红旗 | 无 |
| `.rsvp-phone` + `.app-bar` | `IDIVER APP` | 旅人手账 `TRAVELER'S NOTEBOOK` | 改文案；牛皮纸 + 横线纸质感 | 无 |
| 登记区提示 | 登记内容只保存在当前浏览器 | 数据流向披露（见 §10.3） | **必改**（现文案错误） | 无 |
| 「发送给新人的声呐留言」 | 声呐留言 | 写在纸背上的话 | 纯文案 | 无 |
| `.success-radar` | 成功雷达 | 圆形木刻印章（朱红 `#B6463C`） | 改 CSS 造型 | 无 |
| `.ending` | `MISSION DESTINATION` | `THE WIND REMEMBERS` | 换图 `scene-ending.webp` + 文案 | 无 |
| `.quick-nav` 4 项 | 任务/日程/地图/登记 | `委托 / 风铃 / 日程 / 登记` | 纯文案；保持 4 项，`grid-template-columns` 不改 | 无 |
| `.surface-glitter` | 海面波光 | 草叶露水 / 飞鸟群 | 同名类只改 `background-image` 与 `animation` | 无 |
| `.camera-corners` | 潜水取景框 | 手绘拐角"翻到这一页" | 保留结构，改颜色为半透明墨色 | 无 |
| `#music-hint` | 点击播放/关闭官方音乐 | 点击播放：风与钢琴 | 纯文案 | 无 |
| `<audio id="official-bgm" src="itunes...">` | 外部试听链接 | 本地 `./assets/wedding-bgm.mp3` | 换源；文件不存在则保留静音，不得引用未授权音乐 | 无 |
| `admin/*` 整体 | 蓝洞任务终端 | 旅人名册（主办人） | 改文案 + 色值 + **修绝对路径** | 接口/表结构不变 |

### 4.4 声呐 → 风铃"三响"机制

原声呐是"一次点击 → 波纹扩散 → 场内元素高亮"。新版本赋予它与婚礼强相关的设定：

- 点击风铃 → **依次荡开三圈**波纹（`@keyframes chime-1 / chime-2 / chime-3`，各延迟 180ms 触发）
- 三响对应三句祝福，在按钮下方以纸条形式依次出现：
  - 一声响：「愿一路顺风」
  - 二声响：「愿平安无忧」
  - 三声响：「愿相爱到老」
- 第三响落下时，场内全部纸鹤同步高亮一次：`filter: saturate(1.4) brightness(1.15)`（**不要用原来的白光闪烁** `brightness(2.4)`，那是像素风）
- 无障碍：`aria-label` 由「释放声呐」改为「摇响风铃」
- 实现：在 `app.js` 第 72–78 行的现有点击处理器内部扩展，**不新增监听器**

### 4.5 捕鱼 → 收集纸鹤规格

- 场上 9 个 `.paper-crane`（沿用 `.pixel-fish` 类名，见 §6.1）：从左右两侧穿插飘过，`@keyframes glide` = 横向位移 + 上下正弦浮动，周期 6.5~10s
- 点击 → 展开成祝福笺（`.caught`），计数 `0/5`
- 祝福语池（`app.js` 第 83 行 `fishBlessings`），建议 6 条：
  1. 愿你们的旅途风调雨顺
  2. 愿有一盏灯永远为你们亮着
  3. 愿每一次出发都能回家
  4. 愿岁月温柔，草木长青
  5. 愿你们在同一片天空下老去
  6. 愿平淡日子里的面包和牛奶都香甜
- 颜色池（第 82 行 `fishColors`）：`#E8A657`、`#B6463C`、`#8FAE6B`、`#A8CFE0`、`#F2E3C9`
- 保留机制：`Math.random() > 0.72` 才弹祝福、上限 5、`navigator.vibrate` 保留
- 集齐文案：`纸鹤收齐了：愿风替我们把这些祝福捎给你`

---

## 5. 素材清单

### 5.1 A 类：需要人工提供的素材

| # | 素材 | 规格要求 | 用途 | 阻塞性 |
| --- | --- | --- | --- | --- |
| A1 | 婚纱照原片 **8~12 张**候选 | 原图、长边 ≥ 2000px、sRGB、**禁止微信压缩图、禁止美颜滤镜** | 交给图片 API 做风格转换 | 阻塞 §7 全部 |
| A2 | ≥ 2 张**竖版全身/半身合影** | 3:4 或 2:3 竖构图 | 首页主视觉、结尾页、角色位 1 | 阻塞 B1/B9/B10 |
| A3 | 2 张**单人正面半身照**（各一张） | 五官完整清晰、光线均匀 | 双人立绘的人脸一致性参考 | 阻塞 B10 |
| A4 | 2 张**户外/庭院/海边穿搭照** | 横版 16:9，人物占比不要太小 | 场景级画面 | 不阻塞 |
| A5 | 婚礼文字信息（见下表） | 文字 | 替换 `index.html` 演示文字 | 阻塞文案改造 |
| A6 | **飞书问卷公开填写链接** | URL | 填入 `app.js` 第 3 行 | 阻塞登记区 |
| A7 | 背景音乐（可选） | MP3、≤ 2 MB、可循环 | `./assets/wedding-bgm.mp3` | 不阻塞 |
| A8 | 抽卡卡面祝福语 6 条（可选，执行者可先起草） | 文字 | `#draw` 卡面 | 不阻塞 |

**A5 需要收集的具体字段**：

| 字段 | 示例 | 用在哪 |
| --- | --- | --- |
| 新人中文姓名 | 张三 & 李四 | `.hero-names`、`.ending-copy b`、`#crew` 角色 1 |
| 新人英文名 | ZHANG SAN & LI SI | `.hero-en-name`、logo |
| 婚礼日期与星期 | 2030年10月1日 · 星期二 | `.hero-hud`、`.mission-ticket`、`.mission-card dl` |
| 短日期 | 2030.10.01 | `.hero-hud`、结尾 |
| 仪式时间 | 11:58 | `app.js` 第 1 行、日程第一条 |
| 场地全称 | 示例市蓝湾婚礼中心·深海厅 → 你的场地 | `.mission-ticket`、`.mission-card dl`、`.map-console h3` |
| 地图分享链接 | 高德/百度地图链接 | `.map-console a` href |
| 当天流程 | 10:30 迎宾 / 11:58 仪式 / 12:30 午宴 | `.menu-board article` 的 `<time>` 与说明 |
| 想对宾客说的话 | 一段 50~150 字 | `.mission-card > p` |
| 住宿默认入/退房时间 | 2030-09-30T14:00 / 2030-10-01T12:00 | `app.js` `updateAccommodation()` 与 `fillRsvp()` 中的默认值 |
| 部署域名 | `https://用户名.github.io/仓库名/` | `og:image`、`canonical` |

> **A7 版权要求**：**禁止**使用久石让、任何吉卜力作品原声、或流媒体试听链接。可用可商用授权的钢琴 / 手风琴 / 风琴纯音乐。不提供则保留静音，不要保留现有的 iTunes 试听链接。

### 5.2 B 类：需要 AI 生成的素材

**18 张必需 + 2 张可选。全部使用 §7 的工作流生成。**

| # | 文件名 | API 尺寸 | 用途位置 | 画面内容 | 阻塞 |
| --- | --- | --- | --- | --- | --- |
| B1 | `hero-journey` | 1024×1536 竖 | `.hero-art`（默认档） | 山丘小镇全景，老式蒸汽火车沿山崖驶过，风车转动，远处海面与大朵积云 | 是（同时是风格母本） |
| B2 | `hero-journey-wide` | 1536×1024 横 | `.hero-art` 桌面档 | 同 B1 的横构图 | 否 |
| B3 | `og-share` | 1536×1024 | `og:image` / `twitter:image` | 同场景裁成适合社交卡片的构图 | 否 |
| B4 | `wedding-logo` | 1024×1024 **transparent** | `.hero-brand` + `footer`（2 处） | 手绘水彩字 logo「我们的婚礼 / OUR WEDDING」+ 藤蔓与风纹 | 否 |
| B5 | `wedding-names` | 1024×1024 transparent | `.hero-names` | 新人中英文姓名手写体 + 藤蔓花环 | 否 |
| B6 | `scene-chime` | 1536×1024 | `.exploration-frame` | 老屋檐下的风铃与木长椅，纸笺在风中飘 | 否 |
| B7 | `scene-window` | 1536×1024 | `.restaurant-screen` | 老街木窗，窗台摆当日菜单、面包篮与陶杯 | 否 |
| B8 | `scene-map` | 1536×1024 | `.map-console` 底图 | 手绘水彩地图：山丘、溪流、小径、风车、小红旗 | 否 |
| B9 | `scene-ending` | 1024×1536 | `.ending > img` | 夕阳下起伏草坡与云海，两个人物剪影 | 否 |
| B10 | `couple` | 1024×1536 | `#crew` 角色位 1 | **由 A2/A3 原片风格转换**，保留本人五官与姿态 | 是 |
| B11a | `crew-postman` | 1024×1536 | `#crew` 位 2 | 骑单车送信的邮差少年（原创） | 否 |
| B11b | `crew-baker` | 1024×1536 | `#crew` 位 3 | 面包铺 / 果酱铺主人（原创） | 否 |
| B11c | `crew-tinker` | 1024×1536 | `#crew` 位 4 | 修钟表与风车的老匠人（原创） | 否 |
| B12a–d | `couple-styled-1..4` | 各 1536×1024 | 婚纱照风格转换成品 | 4 张正片，见 §7.4 | 是 |
| B13a–f | `invite-card-1..6` | 各 1536×1024 | `#draw` 卡面 | 6 款成品卡：羊皮纸框 + 藤蔓 + 编号 + 日期 + 卡名 + 一句祝福 | 是 |
| C1（可选） | `ornament-leaves` | 1024×1024 transparent | 板块间装饰分隔 | 压花叶片与风纹 | 否 |
| C2（可选） | `ornament-windmill` | 1024×1024 transparent | 图标 | 手绘小风车 | 否 |

> **未使用的旧素材**：`dave-key-art.webp`、`dave-logo.webp`、`phone-ui.webp` 现仓库中**已无任何代码引用**，可直接随旧素材一并删除。

### 5.3 卡池设计（B13，抽卡环节核心）

| 卡号 | 卡面取图 | 稀有度 | 卡名（手写体） | 说明 |
| --- | --- | --- | --- | --- |
| 01 | B1 `hero-journey` 裁切 | 普通 | 风起时 | 最易抽到 |
| 02 | B6 `scene-chime` 裁切 | 普通 | 风铃三响 | |
| 03 | B7 `scene-window` 裁切 | 普通 | 老街的窗 | |
| 04 | B8 `scene-map` 裁切 | 稀有 | 往那盏灯的路 | |
| 05 | B9 `scene-ending` 裁切 | 稀有 | 风会记得我们的名字 | |
| 06 | B10 `couple` 裁切 | **限定** | 同一页旅程 | 概率最低 |

- 卡面结构：羊皮纸外框 → 场景图 → 卡名手写体 → 一行祝福语 → 右下角编号与婚礼日期
- **决策 5 的关键点**：卡池复用已生成的场景图，**只额外生成 6 张卡面成品**，不新增美术工作量
- 扩展卡池：每加一款 = 多 1 张预生成卡面图 + 在卡池数据数组里加 1 条

---

## 6. 工程约束与命名规范

### 6.1 强制约束：不做类名 / ID 重命名

`#fish-field`、`#fish-count`、`.pixel-fish`、`.fish-blessing`、`.fish-caption`、`.fish-arrow`、`.sonar-button`、`.sonar-field`、`.game-hud`、`.underwater`、`.water-rays`、`.bubble-field` 等**保持原类名与原 ID 不变**。

**理由**：这些名字只出现在 `style.css` 的选择器与 `app.js` 的 `querySelector` 中，重命名会造成大面积漏改并直接白屏。换皮只改视觉与文案，不改标识符。

**替代做法**：在 `style.css` 与 `app.js` 两个文件的**最顶部**各加一段注释映射表：

```js
/* ============================================================
   命名映射（历史遗留名 → 当前场景语义）
   本文件为"风之旅"吉卜力主题，下列标识符沿用旧名以免漏改：
     .pixel-fish      → 纸鹤（天空飘过的折纸鹤）
     #fish-field      → 纸鹤场（天空区域容器）
     #fish-count      → 纸鹤计数 0/5
     .fish-blessing   → 祝福纸条
     .fish-caption    → "风把纸鹤吹来了" 提示
     .sonar-button    → 风铃按钮
     .sonar-field     → 风铃波纹场
     .game-hud        → 风的刻度 / 云的高度 / 纸鹤计数 HUD
     .underwater      → 天空与草原区
     .water-rays      → 云隙光 / 风带
     .bubble-field    → 风和叶屑
   ============================================================ */
```

### 6.2 文件命名规范

- 素材文件名**全部小写 + 连字符**：`scene-chime.webp`、`crew-postman.webp`
- 禁止空格、中文、大写字母（GitHub Pages 区分大小写，大小写不一致会 404）
- 网页引用一律带 `./` 前缀（`index.html` 现有做法正确，新素材必须沿用）
- 每张图同时产出 `.png` 源与 `.webp` 网页版；**`.png` 源不进仓库**

### 6.3 `.gitignore` 补充

在现有 `.gitignore` 末尾追加，防止误提交原始素材与中间产物：

```gitignore
# 原始婚纱照与 AI 生成中间产物（不得入库）
raw-photos/
generated-raw/
*.psd
*.tif
```

---

## 7. 生成工作流与风格锁定

### 7.1 API 参数

| 参数 | 取值 | 说明 |
| --- | --- | --- |
| 端点（风格转换） | `POST /v1/images/edits` | 传原片做风格转换 |
| 端点（全新场景） | `POST /v1/images/generations` | 纯文本生成 |
| `model` | `gpt-image-1`（或 `gpt-image-1.5`） | 用账号已有权限的版本 |
| `image[]` | 第 1 张 = 婚纱照原片；第 2 张 = 已确认的**风格母本图** | 全新场景图可只传母本或不传 |
| `input_fidelity` | **`high`** | 保持人物脸部与构图的关键参数 |
| `size` | `1536x1024` / `1024x1536` / `1024x1024` | API 仅支持这三种非方形尺寸 |
| `quality` | 试稿 `medium` → 定稿 `high` | 控制成本与迭代速度 |
| `background` | `transparent` | 仅 B4 / B5 / C1 / C2 使用 |
| `output_format` | `png`（留无损源） | 网页版再转 WebP |
| 限制 | 输入图片单张 < 50 MB | |

> 官方参数速查：<https://github.com/openai/skills/blob/main/skills/.system/imagegen/references/image-api.md>
> 首次调用前，用最小请求验证账号可用的模型名与支持的参数，**不要照抄本文档的参数名而不验证**。

### 7.2 "保证是吉卜力风格"的三重锁定机制

风格一致性**不能靠单次提示词赌运气**，必须靠机制：

**第一重：主锚稿先行**

先**只生成 B1 `hero-journey`**，用统一主模板反复出到满意。这一张定为**全站风格母本**。在写出满意的 B1 之前，不要生成其他任何图。

> ✅ **母本已定稿**：`generated-raw/hero-journey-v5.png`（1024×1536）。
> 配套产出：`generated-raw/hero-journey-wide-v1.png`（1536×1024，桌面档）、
> `generated-raw/og-share-v1.png`（1200×630，由横版裁切，未过 API）。
> **后续所有图一律以 v5 作为参考图走 `edits` 端点生成。**

**⚠️ 已实测踩过的坑：这条弯路务必不要再走**

风格不可能靠纯文字提示词描述出来。实测了 5 版才定稿，教训如下：

| 版本 | 做法 | 结果 |
| --- | --- | --- |
| v1 | 只有风格词 + 统一风格段落 | 高细节、强体积感的当代动画背景，**不像吉卜力** |
| v2a / v2b | 改成"平涂水粉、低饱和、低对比" | 方向反了：**发灰发闷**，失去参考图的高饱和与明快 |
| v3 | **改用参考图 + `edits` 端点** | ✅ 风格对上了（高饱和宝蓝天空、明亮草地、成团云） |
| v4 | 在 v3 上减细节：大色块草地、去野花、简化树丛 | ✅ 更柔和，但前景笔触仍偏碎、房屋细节偏多 |
| **v5** | 三项微调：**前景笔触完全融掉 + 房屋大幅简化 + 加哑光颗粒** | ✅ **定稿** |

**结论：风格传递必须靠参考图，不能靠文字。** 用户提供的风格参考图（本项目为《起风了》剧照 `起风了.jpg`）就是唯一可靠的风格锚。

**✅ 定稿用的艺术指导段落（后续所有图都必须带上）**

```text
Match the reference image art style very closely: soft classic 2D hand-painted animation background.
1) Foreground: paint as one broad smooth blended gradient with completely soft edges.
   No visible brush strokes, no streaks, no grass texture.
2) Buildings: greatly simplify. Each house reduced to a simple cream block with a simple roof shape
   and one or two plain windows. No shutters, railings, chimneys, stone texture or small details.
   Keep only the windmill and a small church tower as landmarks.
3) Add a soft matte finish with a fine even paper grain and subtle matte dust layer over the whole image:
   matte, slightly grainy, gently faded like old hand-painted animation cels on textured paper.
   Slightly reduced contrast, soft hazy light, no glossy or digital clean smoothness.
Clouds: very simple with soft blurred edges. Sky: gentle gradient of vivid cerulean blue.
No photorealistic detail, no crisp sharp edges, no visible brush strokes in the foreground,
no high-frequency texture, no architectural detail. No watermark, no signature, no text.
```

**✅ 定稿母本色卡（其他图对齐用）**

| 元素 | 颜色 |
| --- | --- |
| 天空 | 高饱和宝蓝，柔和上下渐变 |
| 草地 | 明亮春绿，大色块柔和推移 |
| 云 | 浅灰白，边缘干净但柔 |
| 建筑 | 米白墙 + 红陶瓦顶 |
| 光线 | 暖调，对比适中，哑光颗粒 |

**关键判据**：细节越少越像吉卜力。**草地不能有笔触、建筑不能有门窗细节、云不能有体积渲染**。

**⚠️ 上传参考图时不要传原剧照，传母本**

用户给的参考图是宫崎骏电影剧照，属受版权保护的作品。**该图仅用于本地理解风格与首次探测，不要上传到第三方 API。** 定稿后，风格锚全部改用自己生成、无版权争议的母本 `hero-journey-v5.png`。

**其他已实测结论（本项目专用）**

| 项目 | 结论 |
| --- | --- |
| 实际可用端点 | `https://code28.ccwu.cc/v1/images/generations`（纯文本）与 `https://code28.ccwu.cc/v1/images/edits`（传参考图） |
| 实际可用模型 | `gpt-image-2`、`gpt-image-2.5-flare`、`gpt-image-2.5-sunburst` |
| 支持参数 | `model`、`prompt`、`size`、`quality`、`style`、`n`、`response_format` |
| `1024x1536` 竖版 | ✅ 实测可用 |
| `1536x1024` 横版 | ✅ 实测可用 |
| `quality` | 用 `high`（该接口 `standard` 为默认值，与本方案原假设的 `medium/high` 不同） |
| 返回结构 | `response_format` 默认 `url`，返回**临时 URL**，需立即下载（不要依赖 URL 长期有效） |
| ✅ `edits` 端点 | **实测支持传参考图**，`usage.input_tokens_details.image_tokens` 有值即为图已被接收。B10/B12 的婚纱照风格转换可直接走这个端点 |
| 传图方式 | `curl -F 'image=@文件路径'`，multipart 表单 |
| 参考图尺寸 | 参考图不必与输出同比例。用竖版母本可生成横版输出（v5 竖版 → 横版实测成功） |

**第二重：以图锁风格**

其余每一张图都把**母本作为第 2 张输入图**传入，并在提示词中明确要求：

```text
match the reference image's art style, brushwork, palette and lighting exactly
```

这比纯文本描述稳定得多，是解决"多张图风格不统一"最有效的手段。

**第三重：风格段落唯一**

所有提示词共用**同一段风格句**，只有场景与人物描述变化。禁止逐张改写形容词。

**统一风格段落（所有提示词都必须包含）**：

> ⚠️ **这段原始风格段落已被实测淘汰**（它会导致"高细节、不像吉卜力"，见 §7.2 的踩坑记录）。**实际使用 §7.2 的"定稿艺术指导段落"**。以下保留仅为记录 v1 阶段的错误做法。

```text
Studio Ghibli style, Hayao Miyazaki style hand-painted 2D animation background,
soft watercolor and gouache texture, gentle pastel palette
(cream #F7F0E1, sky #A8CFE0, grass #8FAE6B, sunset #E8A657, ink #3A3B33),
warm golden late-afternoon light, expansive sky with large cumulus clouds,
visible paper grain, nostalgic and peaceful mood,
no watermark, no signature
```

> **决策 4 说明**：提示词中保留 `Studio Ghibli style, Hayao Miyazaki style` 是项目所有者的明确要求。这些词只出现在 `PROMPTS.md` 与生成提示词里，**不得写进网页可见文本、`README.md` 宣传语或交付话术**。

### 7.3 人脸保持的提示词写法（风格转换必带）

```text
Based on this real wedding photo, convert it into the reference image's soft hand-painted
animation style described above.
Strictly preserve the two people's facial features, face shape, hairstyle, pose and relative position;
keep the original composition and aspect ratio.
Change only the art style, background and lighting.
Do not change the number or identity of people.
No watermark, no signature, no text.
```

**迭代节奏**：先用 `quality=high` 出 1 张试稿 → 确认脸像本人 → 再批量出 → 每张出 2~3 个候选挑 1 张。
（该代理的 `quality` 只有 `standard` / `high` 等预设，**用 `high`**。）

### 7.4 婚纱照风格转换（B12）执行细则

1. 从 A1 的 8~12 张候选里选出最终 4 张（覆盖：1 张竖版合影 → 首页/结尾；1 张特写 → 角色位 1；2 张场景照 → 卡片与装饰）
2. **走 `edits` 端点**（实测支持传参考图），把婚纱照与母本 `hero-journey-v5.png` 一起传入
3. 每张先出 2~3 个候选，交给项目所有者选
4. 用选中的那张作为**组内色彩参考**，保证 4 张色调一致
5. **构图保障**：首页是整屏背景，必须先定 `object-position` 焦点再出竖版图。母本 v5 已定稿，实测建议起点为 **`object-position: center 62%`**（母本下半部是柔和绿坡，把小镇、风车、火车提到画面中上部，下半部留给 logo / 姓名 / 日期 / 按钮叠字）；接页面时在 375/390/430 三档实测微调，目标是不让叠字压在房屋与风车细节上
6. ⚠️ 婚纱照是个人隐私素材，属第三方 API 上传，**提前告知项目所有者数据流向**；不上传含长辈/儿童的片子

### 7.5 输出整理与入库纪律

- `assets/` 现状约 4.8 MB，**目标 ≤ 2.5 MB**
- 体积上限：首页主视觉 ≤ 350 KB；场景图 ≤ 250 KB；立绘与卡片 ≤ 180 KB
- **PNG 源文件绝不进仓库**：生成后统一转 WebP（用 `quality` 75~85）
- 中间产物（原片副本、未选中候选、含 EXIF 原图）**全部留在仓库外**（放 `generated-raw/`，已在 §6.3 加入 `.gitignore`）
- 每张图入库前必须通过 §9 的多模态检查

---

## 8. 抽卡环节实现规格（决策 5）

### 8.1 默认方案：预生成卡面（**先做这个**）

- 生成 6 张带框带字的成品卡（B13a–f，1536×1024），前端不做任何图片合成
- 优点：零 iOS 兼容风险、零字体问题、零跨域问题
- 卡面文字**优先在生成阶段留白、后期用 SVG/HTML 叠加**。理由：AI 生成中文是高错字率环节，成品卡上的错字不可接受

### 8.2 交互流程

```
#rsvp 登记区 →「完成登记，去抽一张」按钮
  → 全屏抽卡层（role="dialog" aria-modal="true"）
  → 卡背扇形展开 + 呼吸光晕 + 提示"点一下，看看风给你带了什么"
  → 点击抽取 → 翻牌动画（transform: rotateY）→ 卡面揭晓 + 纸屑/纸鹤飘落
  → 按钮组：保存图片 / 分享给新人 / 再抽一次（提示"每人一次哦"）/ 关闭
```

**位置**：新增 `#draw` 板块，排在 `#rsvp` 之后、`.ending` 之前；同时作为 `#rsvp` 成功态的下一步入口。

**闭环设计要点**：飞书表单提交后**无法回传结果给静态页**，页面不知道"宾客填完了"。**抽卡按钮就是那个返回钩子**——文案写成"填完问卷回到这一页抽卡"，把外部表单的断点补成完整闭环。同时提供「我已提交，去抽卡」按钮，让直接打开页面的宾客也能进入。

### 8.3 保存与分享（按能力探测顺序降级）

| 顺序 | 方案 | 条件 |
| --- | --- | --- |
| 1 | `navigator.share({ files: [new File([blob], 'card.png', {type:'image/png'})] })` | 支持 Web Share Level 2（iOS/安卓可分享到微信） |
| 2 | `<a download="invitation-card.png">` | 桌面浏览器 |
| 3 | iOS Safari 无 `download` 属性时，弹出浮层提示"长按图片可保存到相册" | iOS 兜底 |

### 8.4 可选增强：Canvas 叠加宾客姓名（**第二阶段，需通过探测**）

仅在项目所有者明确要求时实现。**必须通过以下三项探测**，任一不通过则静默退回 §8.1 的通用文案，**不得报错、不得白屏**：

| 探测项 | 判据 |
| --- | --- |
| 同源导出 | 图片来自 `assets/` 同源，`img.crossOrigin = 'anonymous'` 下 `canvas.toBlob()` 不抛 `SecurityError` |
| iOS 兼容 | iOS Safari 上 `img.decode()` + `toBlob()` 正常返回 |
| 中文字体 | 实测手机上 Canvas 绘制中文不缺字、不落回方框 |

- 姓名来源优先级：URL 参数 `?to=姓名`（飞书问卷提交后跳转携带）→ `localStorage` → 无则用通用文案「致我最珍贵的朋友」
- 实现位置：`app.js` 新增抽卡模块内的独立函数，与 §8.1 的预生成卡面互不干扰

### 8.5 无障碍与状态管理（必做）

- 抽卡层：`role="dialog"` + `aria-modal="true"` + 标题用 `aria-labelledby`
- 打开时**锁定 body 滚动**，关闭时恢复
- 遮罩点击关闭、`Esc` 关闭
- 关闭后**焦点回到触发按钮**
- `prefers-reduced-motion` 下跳过翻牌动画，直接显示卡面
- 抽卡次数：`localStorage` 键 `journey-wedding-draw` 记录已抽卡号与次数；再次抽卡给**温和提示**而非硬拦截
- 卡面图片**懒加载**：点击抽卡时才请求卡面资源

---

## 9. 多模态检查规程（决策 7）

每一张素材与每一个页面状态，在入库前都必须**用读图工具真正看一眼**，产出结论并回写台账。**不得只凭文字描述判断通过。**

> 环境说明：执行者可用的读图能力是 harness 的 `read_image` 工具（返回真实格式、尺寸并可看图）。若执行 agent 无读图能力，则**必须把该项标记为"未检查"并如实报告**，不得假装通过。

### 9.1 素材检查（逐张）

| 检查项 | 判据 | 不通过怎么办 |
| --- | --- | --- |
| **风格一致性** | 与母本对比：笔触、色相、光线方向、饱和度是否同族；有无像素块、霓虹色、截图痕迹 | 换提示词重出，或把该图作为参考图重跑 |
| **残留元素** | 是否还有水下/海面镜头、发光 HUD、像素方块、现代 logo、水印、签名 | 重出；带水印的直接废弃 |
| **人脸与人物数量** | 人物数量正确、五官未被重绘、脸型与本人相符、手指与肢体无畸变 | `input_fidelity: high` 重出；仍不行退回"仅转换照片风格"的保守提示词 |
| **卡面文字正确性** | 中英文有无错字、乱码、多字漏字 | **优先改为生成时留白、后期叠加文字**；或重出到正确 |
| **可用性** | 人物是否在安全区内、脸部是否会被 `object-position` 裁掉、主体是否被卡框压住 | 重出或调整裁切 |
| **透明通道** | B4/B5/C1/C2 边缘是否干净，有无白边/灰边/黑底，半透明处是否有脏边 | 生成时用纯色底再抠，或改为实底卡片 |
| **文件体检** | 真实格式与扩展名一致、尺寸为 API 允许值、体积达标 | 重命名 / 重编码 / 转 WebP |

**产出物**：每个候选图一段评分（风格一致性 / 身份还原 / 可用性，各 1~5 分）+ 一句话可执行优化建议，回写 `PROMPTS.md` 对应条目。**不通过的图不得进入 `assets/`。**

### 9.2 页面检查（截图后看图）

| 检查项 | 判据 |
| --- | --- |
| 375 / 390 / 430 px 三档 | 无横向滚动、无文字溢出、按钮不被 `.music-dock`（`bottom: max(56px, …)`）或 `.quick-nav` 遮挡 |
| 视觉和谐 | 纸纹、圆角、阴影、图标风格是否统一；有无蓝黑残留、硬边像素阴影 |
| 语义残留 | 页面可见文本中旧主题词全部 0 命中（词表见 §11.4） |
| 抽卡层 | 窄屏卡片不被压扁、保存/分享按钮可点、关闭后页面状态正常 |
| 对比度 | 暖色纸面上的文字对比度是否足够（浅底浅字是高发可读性问题） |

**特别注意**：`read_image` 会把透明 PNG 压平显示，**无法凭它判断透明通道是否真的透明**。透明素材必须另做像素级验证（在 `danger-full-access` 或 `workspace-write` 下用图像库检查 alpha 通道），否则如实标注"透明通道未验证"。

---

## 10. 代码改动清单（按文件）

### 10.1 `style.css`（改动最大，约 264 条规则需过一遍）

1. `:root` **保留旧变量名只换色值**（避免大面积漏改），并新增吉卜力 token：

```css
:root{
  /* 沿用旧变量名，只换色值 */
  --deep:#F7F0E1; --navy:#A8CFE0; --sea:#8FAE6B;
  --cyan:#DCEAF0; --yellow:#E8A657; --paper:#FFFBF2;
  --pixel-shadow:none;
  /* 新增 */
  --ink:#3A3B33; --ink-soft:#6B6A5E; --accent-brick:#B6463C;
  --cloud:#FFFDF6; --sky:#A8CFE0; --grass:#8FAE6B; --sunset:#E8A657;
  --shadow:0 6px 18px rgba(58,59,51,.18);
  --stroke:2px solid rgba(58,59,51,.35);
}
```

2. **全量替换**：`box-shadow: Npx Npx 0 <色>` 硬边阴影 → `var(--shadow)`；`Impact / Arial Black / monospace` 字体栈 → 见 §10.1 第 4 条
3. **字体栈**（不引 Google Fonts CDN）：
   - 标题：`"Songti SC","Noto Serif SC","Source Han Serif SC",serif`
   - 正文：`"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif`
   - 标签：大写拉丁 + `letter-spacing: .12em`
4. **按 §4.3 表格重做背景与质感**：`.hero`、`.underwater`、`.crew-section`、`.schedule-section`、`.arrival`、`.rsvp-section`、`.ending`
5. **重写 CSS 图形与动画**：
   - `.pixel-fish` 的 `clip-path`（鱼 → 纸鹤）
   - `@keyframes swim` → `glide`（含正弦浮动）
   - `@keyframes rays` → `drift`（云影横移）
   - `@keyframes sonar` → `chime-1 / chime-2 / chime-3`
   - `@keyframes rise` → `float`
   - `@keyframes glitter` → 露水 / 飞鸟（保留同名 keyframes 或改引用）
   - 全部动画 `animation-timing-function: ease-in-out`，周期 6~14s，删除所有 `steps()`
6. **新增样式**：风铃按钮造型（圆形铜铃 + 铃舌 + 吊绳）、纸条祝福（`.fish-blessing`）、木刻印章（`.success-radar`）、**抽卡层与翻牌动画**
7. **顶部加命名映射注释块**（内容见 §6.1）
8. 新增抽卡层全部规则，命名如 `.draw-layer`、`.draw-fan`、`.draw-card`、`.draw-actions`

### 10.2 `index.html`

1. `<head>` 全部换新：`title`、`description`、`theme-color`、`og:*`、`twitter:*`、`og:image`（完整 HTTPS）、`canonical`
2. 替换 10 处旧素材引用：`dave-key-art-clean.png`、`dave-character.webp`、`bancho.webp`、`cobra.webp`、`bacon.webp`、`sea-exploration.webp`、`sushi-service.webp`、`dave-dive.webp`、`wedding-invitation-logo.png`（2 处）、`demo-wedding-names.svg`
3. `.hero-art` 改 `<picture>`：

```html
<picture>
  <source media="(min-width:560px)" srcset="./assets/hero-journey-wide.webp" />
  <img class="hero-art" src="./assets/hero-journey.webp" alt="山丘小镇，蒸汽火车沿山崖驶过" />
</picture>
```

4. 按 §4.3 替换全部文案（6 个板块 + `.hero-hud` + `.game-hud` + `.quick-nav` + `#music-hint`）
5. `#crew` 的 4 个 `data-name` 与 alt（见 §10.6）
6. `aria-label`：`释放声呐` → `摇响风铃`；`捕捉第 N 条鱼` → `接住第 N 只纸鹤`
7. **新增 `#draw` 板块**：卡池容器、抽卡层结构、保存/分享/关闭按钮
8. `<audio>` 的 `src` → `./assets/wedding-bgm.mp3`
9. 登记区文案与数据披露（见 §10.3）

### 10.3 登记区改造（决策 6，**含一处必改的错误文案**）

**必改**：`index.html` 第 104 行现在是

> `DEMO MODE · 登记内容只保存在当前浏览器，不会上传到服务器`

接入飞书后**这句话是错误信息**，构成对宾客的误导。必须改为明确的数据流向披露：

> `您的登记信息将通过飞书问卷提交，并保存在新人维护的飞书表格中，仅用于本次婚礼的安排。`

**外链模式**：`app.js` 第 3 行填入飞书链接即可，现有代码已内建该分支：

```js
const RSVP_FORM_URL = 'https://<你的飞书问卷公开链接>'
```

行为：本地表单隐藏 → `#rsvp-external` 显示 → 链接指向飞书 → `.app-bar small` 状态改 `ONLINE`。

**飞书问卷字段建议**（与页面字段一一对应，便于导出对照）：

| 页面字段（`name`） | 飞书问卷控件 | 必填 |
| --- | --- | --- |
| `guestName` | 单行文本「您的姓名」 | 是 |
| `partySize` | 单选「出席人数」1~6 | 是 |
| `needsAccommodation` | 单选「是否需要住宿」不需要 / 需要 | 是 |
| `checkInAt` / `checkOutAt` | 日期时间（选填） | 否 |
| `phone` | 手机号（选填） | 否 |
| `message` | 多行文本「想对新人说的话」，限 200 字 | 否 |

**保留本地 demo 分支**：`app.js` 第 160–204 行的本地模式代码**保留不删**（未来若要换回自建后台仍有价值），外链模式优先。

### 10.4 `app.js`

1. 第 1 行 `weddingDate` → 真实婚礼时间
2. 第 3 行 `RSVP_FORM_URL` → 飞书链接
3. 第 169 行 `storageKey` → `journey-wedding-demo-rsvp`
4. 第 82 行 `fishColors` → §4.5 色卡；第 83 行 `fishBlessings` → §4.5 六条祝福
5. 第 110 行集齐文案、第 39 行 HUD 文案、第 129/139 行音乐文案 → 按 §4.3 替换
6. 第 72–78 行声呐点击 → 扩展为风铃三响（§4.4），**不新增监听器**
7. 第 76 行纸鹤高亮的 `filter`：`brightness(2.4) drop-shadow(...)` → `saturate(1.4) brightness(1.15)`
8. 长按时长 1s → **1.2s**（可选，配合更舒缓的节奏）
9. **新增抽卡模块**：卡池数据、`localStorage` 次数、翻牌、保存/分享降级、遮罩/`Esc`/锁滚动/焦点回归、`prefers-reduced-motion` 分支、（可选）Canvas 叠名与能力探测
10. 顶部加命名映射注释块（§6.1）

### 10.5 `admin/*`（若按 §1.1 默认删除则跳过本节）

1. **修绝对路径**：`/assets/...` → `../assets/...`（第 9、19、39、54 行）；`/admin/admin.css` → `./admin.css`（第 10 行）；`/admin/admin.js` → `./admin.js`（第 82 行）
2. 文案：`蓝洞任务终端` → `旅人名册`、`宾客任务终端` → `旅人名册`、`进入任务终端` → `进入名册`、`MISSION CONTROL / RSVP ARCHIVE` → `JOURNEY ARCHIVE`
3. `admin.css` 换暖色系（该文件不引用任何 `assets/` 图片，只需改色值）
4. **接口与 `migrations/0001_create_rsvps.sql` 表结构零改动**

### 10.6 `#crew` 四个角色位文案（决策 2）

| 位 | `data-name` | 身份 | 台词 |
| --- | --- | --- | --- |
| 1 | `COUPLE` | 新人双人立绘（原片风格转换） | "从今天起，我们把彼此写进了同一页旅程。请一定来，替我们按个手印。" |
| 2 | `POSTMAN` | 骑单车送信的邮差少年 | "风把这封信吹到你手上了，那我这趟就没白跑。" |
| 3 | `BAKER` | 面包铺 / 果酱铺主人 | "重要的日子就得有刚出炉的面包。那天的面包，我给你们留着。" |
| 4 | `TINKER` | 修钟表与风车的老匠人 | "齿轮我调好了，风车会一直转到你们到场那天。" |

结构沿用：`.crew-slide` × 4 + `[data-crew="prev"/"next"]`，`showCrew()` 与 `n/N` 计数器不改。四张立绘必须同色卡、同光向、同笔触（互为参考图）。

### 10.7 文档改动

| 文件 | 改动 |
| --- | --- |
| `MATERIALS.md`（**新增**） | 素材台账：每张图的路径 / 尺寸 / 来源（自拍 or AI）/ 提示词编号 / 是否就位 |
| `PROMPTS.md`（**新增**） | 提示词台账：每张图的完整 prompt、模型、size、quality、`input_fidelity`、生成日期、多模态检查评分与结论 |
| `THIRD_PARTY_ASSETS.md` | 删除《潜水员戴夫》素材清单，改为声明"本站美术素材均为 AI 生成或本人拍摄" |
| `COPYRIGHT_NOTICE.md` | 更新项目性质段落；**保留"声明不能替代授权"的完整风险原则**（该节仍然必要且正确） |
| `README.md` | 更新标题、简介、素材文件名表；新增"AI 生成与风格转换""抽卡环节""飞书问卷接入"三节；若按默认删除 Cloudflare 路径，则删掉后台相关推荐段落与文件结构条目 |
| `GUIDE.zh-CN.md` | 替换素材文件名与尺寸表；第四节文字替换对照表更新；新增"GitHub Pages 子路径检查"一节 |
| `SHARE.zh-CN.md` | 收敛为 GitHub Pages 单一主线；补抽卡分享文案模板 |
| `RSVP_BACKEND.zh-CN.md` | 保留（第三方表单接入教程仍适用）；补一节飞书问卷字段对照 |
| `后台部署说明.md` | 若按默认删除 Cloudflare 路径，则一并删除；若保留，则顶部注明适用环境 |
| `AI_PUBLISH_GUIDE.zh-CN.md` | 按需更新发布方式描述 |

### 10.8 删除清单（**确认新素材已就位后再执行**）

```text
assets/dave-key-art-clean.png
assets/dave-key-art.webp
assets/dave-logo.webp
assets/dave-character.webp
assets/dave-dive.webp
assets/bancho.webp
assets/cobra.webp
assets/bacon.webp
assets/sea-exploration.webp
assets/sushi-service.webp
assets/phone-ui.webp
assets/demo-wedding-names.svg
assets/wedding-invitation-logo.png      # 换成 wedding-logo.png
```

若按 §1.1 默认执行，另加：

```text
admin/               （整目录）
functions/           （整目录）
migrations/          （整目录）
wrangler.jsonc
_routes.json
后台部署说明.md
```

`assets/sponsor-wechat.jpg` / `assets/sponsor-alipay.jpg` 是原作者赞赏码，若不保留赞赏区可一并删除并同步修改 `README.md`。

---

## 10.9 背景音乐选型（BGM）

> **本节优先于 §5.1 的 A7 与 §14.1 假设 1。** 项目所有者已明确：**选曲阶段先不考虑版权**，以"最贴合主题"为唯一标准。落地前是否需要替换见本节最后"发布前的版权回看"。

### 10.9.1 场景与选曲原则

本页面是**单一循环 BGM**（`<audio loop>`，`app.js` 第 133 行 `volume = 0.58`），所以选曲要满足三个条件：

1. **耐听、无强叙事推进**：宾客可能停留 3~10 分钟，曲子不能有明显的"高潮爆发"
2. **无人声或极弱人声**：中文页面上出现日语歌词会分散注意力；纯器乐版最佳
3. **气质与"风之旅"呼应**：温柔、开阔、有"出发"感，钢琴独奏优先于交响

### 10.9.2 曲目短名单（按契合度排序）

| 优先级 | 曲目 | 出自 | 为什么适合本主题 |
| --- | --- | --- | --- |
| **1（首选）** | **海边的街道** | 《魔女宅急便》 | **字面命中主题**：小镇、海、坡道、风。旋律开阔明朗，是整站"启程"气质的最佳注解。用钢琴独奏版最贴 |
| 2 | 启程 | 《魔女宅急便》/《幽灵公主》 | 曲名与叙事骨架"启程→到场"完全同构，闭环感强；钢琴或弦乐版均可 |
| 3 | 晴天的日子 | 《魔女宅急便》 | 明亮而松弛，适合风铃区与"老街的窗"（面包场景），情绪最"生活化" |
| 4 | 那个夏天 | 《千与千寻》 | 怀旧、湿润的夏天气息，适合登记与抽卡层这类"情绪落点" |
| 5 | 人生的旋转木马 | 《哈尔的移动城堡》 | 三拍子圆舞曲，有"庆典"感，适合日程/酒馆场景 |
| 6 | 散步 | 《龙猫》 | 轻快徒步感，适合纸鹤玩法，但童谣气质偏强，建议只在抽卡音效里用 |
| 7 | 风之甬道 | 《龙猫》 | 旋律里真的有"风"，是最直译的"风之旅"配乐，但整体偏静 |
| 8（备选） | 永远同在 / 生命之名 | 《千与千寻》 | 最著名的治愈曲，认知度极高；人声版与纯器乐版都有，选后者 |
| 9（备选） | 乡村路 / 幻化成风 / 飞机云 | 《侧耳倾听》/《猫的报恩》/《起风了》 | 民谣气质，温暖但更"流行"，适合抽卡分享文案的配乐而非整站 BGM |

### 10.9.3 明确不推荐的曲目（选题与场景不匹配）

这些曲子虽同属吉卜力，但**不适合作为本页面 BGM**，执行者不要因为"知名度高"而选：

| 曲目 | 原因 |
| --- | --- |
| 幽灵公主 / 阿席达卡传奇 / 阿席达卡与珊 | 苍凉、有神性压迫感，与婚礼的温柔基调不匹配（该曲在日本多用于仪式感动片段，不是入场/迎宾） |
| 伴随着你 | 宏伟带冒险感，作为"抵达"结尾的音乐不错，但整站循环会偏重 |
| 悬崖上的金鱼公主 | 童趣跳跃，与手绘水彩的沉静质感冲突 |
| 《千与千寻》的 龙之少年 等紧张段落 | 有戏剧推进，循环会显得躁 |

> **参考**：一份面向日本婚礼的吉卜力选曲整理（按影片分组并含婚礼场景建议）见 [RAG Music（吉卜力 × 婚礼选曲）](https://www.ragnet.co.jp/media/ghibli-wedding-songs/4)。本节的"不推荐"判断与该文一致——《幽灵公主》主题曲在婚礼语境下被归为"仪式感动片段"而非迎宾/入场。

### 10.9.4 技术参数与处理要求

| 项目 | 要求 | 原因 |
| --- | --- | --- |
| 时长 | **2–3 分钟**，循环 2~3 遍 | 单截一段旋律太短会听出重复感 |
| 无缝循环 | 开头 6 秒淡入、结尾前 8 秒淡出，再重新进入 | 现有 `loop` 是硬循环，接缝处会"跳"；必须用音频软件做淡入淡出过渡 |
| 格式 / 码率 | MP3，96–128 kbps，单声道或联合立体声 | iOS Safari 对 MP3 兼容性最好；避免 Opus/WebM（iOS 支持不稳） |
| 文件大小 | **≤ 1.5 MB**（`GUIDE.zh-CN.md` 现写 ≤ 2 MB，本方案收紧） | 移动网络下不阻塞首屏 |
| 音量 | 保持 `app.js` 第 133 行的 `0.58`，不要调高 | 页面要能被微信里低音量环境听清但不打扰 |
| 路径 | `./assets/wedding-bgm.mp3` | 与 `index.html` 的 `<audio src>` 对齐，相对路径保证 GitHub Pages 子路径可用 |

### 10.9.5 关于"抽卡音效"与自动播放限制

**抽卡音效：不实现。** 理由：

1. 每次抽卡切音乐需要停 BGM + 播放音效 + 恢复 BGM，打断感强
2. iOS 首次播放必须有用户手势，音效与 BGM 同处 `AudioContext` 会互相干扰
3. 现有交互已有 `navigator.vibrate` 的触觉反馈（`app.js` 第 56、77、106 行），震动足够替代音效

**自动播放限制**：手机浏览器禁止无交互自动播放，所以 BGM 只能由 `#start-mission` 或 `#music-toggle` 触发——这正是现有实现（`app.js` 第 131–145 行）的行为，不要改动。`#music-hint` 文案在 `app.js` 第 139 行失败分支必须保留。

### 10.9.6 发布前的版权回看（落地时必做一次）

选曲阶段按本节"不考虑版权"执行。但**公开发布该网页前**必须回看一次：

- 若决定保留久石让原曲：明确知晓该做法不符合 `COPYRIGHT_NOTICE.md` 的既有原则，需自行承担下架/删链风险；建议**不公开绑定域名、不投放到公开平台**，仅私聊发给亲友
- 若要合规：本节 §10.9.2 的第 1~5 首选曲目均有大量**可商用授权的翻奏/改编版本**（钢琴独奏、弦乐四重奏、音乐盒版本）以及**无版权费的"吉卜力风格"原创曲**（例：Audiostock 上的"吉卜力风格弦乐"类素材），替换时只需换文件、不改任何代码
- **替换成本极低**：因为代码只依赖一个文件路径，换 BGM 不需要动 `index.html` / `app.js` 的任何逻辑

---

## 11. 验收标准

### 11.1 渐进式准入门槛

素材未就位时，页面必须**允许缺图降级**（`<img>` 有 `alt`、CSS 有背景色兜底），使改造可以分两阶段交付：

1. **阶段一**：完成文案 + 配色 + 动效 + 抽卡流程 + 飞书外链，此时素材未到，走缺图降级，可本地预览
2. **阶段二**：素材到一张换一张，**不做批量重命名后再找图**

### 11.2 功能回归清单（全部为现有行为，不得回归）

| # | 检查项 | 期望 |
| --- | --- | --- |
| 1 | 点击 `#start-mission` | 音乐播放 + 平滑滚动到 `#briefing`；被浏览器阻止时有失败提示文案 |
| 2 | 长按 `#accept-quest` 1.2s | `.is-accepted` + `#quest-status` 变 `ACCEPTED` + `#mission-complete` 浮层 + 震动 |
| 3 | 长按中途松开 | `pointerup` / `pointerleave` / `pointercancel` 任一触发则不接受委托 |
| 4 | 键盘 Enter / Space | 同样可触发接受委托 |
| 5 | 滚动 | HUD 在 55% 屏高后出现；刻度与云高随滚动变化 |
| 6 | `prefers-reduced-motion` | 全部动画关闭，`.reveal` 元素直接可见 |
| 7 | 点击风铃 | 三圈波纹依次荡开，纸鹤同步高亮 |
| 8 | 点击纸鹤 | 捕获 + 计数 `0/5` + 随机弹出祝福纸条；重复点击同一只无效 |
| 9 | 接满 5 只 | 出现「纸鹤收齐了」文案 |
| 10 | 角色 prev/next | 循环切换 4 张，`NAME · n/4` 计数正确 |
| 11 | 倒计时 | `#days-count` 显示正确天数 |
| 12 | 登记（外链模式） | 本地表单隐藏、`#rsvp-external` 显示、状态 `ONLINE`、链接可在微信内打开 |
| 13 | 抽卡 | 抽取后卡面正确、`localStorage` 记录生效、「再抽一次」有温和提示 |
| 14 | 抽卡保存/分享 | iOS Safari、安卓 Chrome、桌面 Chrome/Edge 各测一次成功 |
| 15 | 抽卡关闭 | 遮罩点击、`Esc`、关闭按钮均可关闭；关闭后 body 滚动恢复、焦点回到触发按钮 |
| 16 | 后台（仅若保留） | 仅 `wrangler pages dev` 下可登录、筛选、导出 Excel |

### 11.3 手机端验收

在 **375px / 390px / 430px** 三档宽度逐屏检查：首页、请柬卡、风铃区、纸鹤区、手账、地图、登记区、**抽卡层**、底部导航。

判据：无横向滚动、无文字溢出、按钮不被 `.music-dock`（`bottom: max(56px, calc(env(safe-area-inset-bottom) + 52px))`）与 `.quick-nav` 遮挡。

### 11.4 语义残留检查

在 `index.html` 与 `admin/` 中搜索以下词，**必须全部 0 命中**：

```text
dave      DAVE      蓝洞      BLUE HOLE
潜水      声呐      下潜      海底
鱼        寿司      班乔      戴夫
2030      示例市    蓝湾      深海厅
```

（`DEMO` 一词若用于"本地演示模式"仍可保留，但登记区那句错误的数据描述必须消失。）

### 11.5 性能验收

- `assets/` 总量 ≤ 2.5 MB
- 首页首屏主视觉 ≤ 350 KB
- 无外部字体请求
- 无失效外链（`index.html` 中所有 `http` 链接必须可访问或删除）
- 抽卡层图片懒加载

### 11.6 发布验收

- GitHub Pages 子路径（`用户名.github.io/仓库名/`）下 `admin/` 图片与样式不再 404（若保留）
- `og:image` 为**完整 HTTPS 地址**且可公开访问（相对路径在微信分享卡片中无效）
- 首次上线后用 `SHARE.zh-CN.md` 的流程做三档手机实测 + 二维码测试
- `git status` 干净，仅含预期文件；无 API Key、无原始婚纱照、无 AI 中间产物

---

## 12. 风险与降级方案

| 风险 | 影响 | 降级方案 |
| --- | --- | --- |
| **风格不统一**（最可能的失败点） | 整站观感割裂 | 母本图 + 每张都传参考图 + 唯一风格段落；仍不一致则对成图做统一色调曲线处理后再上线 |
| **生成的脸不像本人** | 核心素材不可用 | `input_fidelity: high` + 补正面参考图 + 提示词显式锁五官；再不行退回"只转换照片风格、不做角色再创作"的保守提示词 |
| **生成图被内容策略拦截** | 生成流程中断 | 提示词去掉角色专有名词，只留风格与场景描述；换模型版本重试 |
| **卡面中文字生成错误** | 成品卡有错字，不可接受 | **默认改为生成时留白、后期用 SVG/HTML 叠加文字**；或重出到正确 |
| **Canvas 导出被跨域/字体阻断** | 个性化姓名不可用 | 已设计为预生成卡面为主；个性化仅在 §8.4 探测通过时启用，失败静默退回通用文案 |
| **iOS 无法直接下载** | 宾客保存不了卡片 | 优先 `navigator.share`；否则弹"长按图片可保存"浮层 |
| **图片比例与槽位不符** | 构图被破坏 | API 仅支持三种尺寸：16:9 槽位靠 `object-fit: cover` 吸收；竖版槽位用 `<picture>` + `object-position` 锁焦点 |
| **飞书数据无回传，宾客以为没提交成功** | 宾客困惑 | 页面明确写"提交后请回到本页抽卡"；提供「我已提交，去抽卡」按钮；支持 `?to=姓名` 带回姓名 |
| **婚纱照隐私**（会经第三方 API） | 隐私风险 | 不上传含长辈/儿童的片子；中间产物全部本地留存，不进仓库 |
| **旧类名漏改导致白屏** | 页面不可用 | 明确不做类名/ID 重命名（§6.1），只加注释映射；改完全量跑 §11.2 回归清单 |
| **GitHub Pages 子路径 404** | 后台或素材打不开 | 修 `admin/` 绝对路径（§3.4）；新素材一律 `./` 相对路径 |
| **部署体积上限** | 上传失败或加载慢 | 全量 WebP；仍有上限则降 `quality` 或牺牲首页分辨率保其他页面 |

---

## 13. 执行顺序（建议的分阶段计划）

### 阶段 0：准备与验证（不产出最终素材）

1. 收集 A5 全部婚礼文字信息、A6 飞书问卷链接
2. 从 A1 选出 4 张最终婚纱照
3. **最小请求验证 API**：确认账号可用的模型名与支持的参数，**不要照抄本文档参数名而不验证**
4. 建立 `MATERIALS.md`、`PROMPTS.md` 两份空台账
5. 在 `.gitignore` 追加 §6.3 内容

### 阶段 1：先出风格母本

6. 只生成 B1 `hero-journey`（竖版），反复迭代到满意
7. 用 `read_image` 做多模态检查（§9.1），回写 `PROMPTS.md`
8. **B1 未定稿前，不生成任何其他图**

### 阶段 2：代码改造（素材未到，走缺图降级）

9. `style.css`：`:root` 换色 + 全员替换阴影与字体 + 重做板块背景 + 重写 CSS 图形动画 + 新增风铃/纸条/印章样式 + 顶部注释映射
10. `index.html`：`<head>` 元信息 + 全部文案替换 + `#crew` 4 个 `data-name` + `aria-label` + `<audio>` 换源
11. `app.js`：数据替换 + 风铃三响 + HUD 文案 + `storageKey` + 顶部注释映射
12. 系统没有新素材也能本地打开预览，此时**先跑一遍 §11.2 的 1~11 项回归**

### 阶段 3：抽卡 + 飞书外链

13. 实现 `#draw` 板块结构（`index.html` + `style.css`）
14. 实现抽卡模块（`app.js`）：卡池、翻牌、次数、保存分享降级、无障碍（§8.5）
15. 卡面未生成前，用占位图先跑通流程
16. 填入飞书链接，改 §10.3 的数据披露文案
17. 跑 §11.2 第 12~15 项回归

### 阶段 4：批量生成素材

18. 按 B2 → B13 顺序生成，**每张都带母本作参考图**
19. 每张过 §9.1 多模态检查，评分与结论回写 `PROMPTS.md`
20. 不通过的图不进 `assets/`，记录原因并重出

### 阶段 5：入库与替换

21. 全部转 WebP，按 §7.5 的体积上限压缩
22. 逐张替换 `index.html` 与 `admin/` 中的引用
23. 每替换一张，用 `read_image` 检查一次页面渲染结果

### 阶段 6：收尾与验收

24. 修 `admin/` 绝对路径（若保留）
25. 按 §10.8 删除旧素材与无用文件
26. 更新 §10.7 全部文档
27. 跑完整 §11 验收清单（含 §11.3 三档手机宽度、§11.4 语义残留、§11.6 发布验收）
28. 部署到 GitHub Pages，拿到地址后回填 `og:image` 与 `canonical`，再验证一次分享卡片
29. 按 `SHARE.zh-CN.md` 准备"亲友分享包"：HTTPS 地址 + 两版微信文案 + 二维码

---

## 14. 假设与待确认项

### 14.1 本方案基于的假设

1. 背景音乐由项目所有者提供**可商用授权**文件；不提供则静音，**不沿用现有 iTunes 试听链接**
2. **站内可见文本**只用原创"风之旅"措辞；`Studio Ghibli / Hayao Miyazaki` 等指向词**仅出现在 `PROMPTS.md` 与生成提示词中**
3. 婚礼日期、场地、流程、地图链接由所有者提供；缺失项先用清晰占位，并在完成后**单独列出待补清单**
4. 卡池默认 6 款；每增加一款 = 多 1 张预生成卡面图 + 1 条卡池数据
5. 部署方式为 GitHub Pages，**不使用** Cloudflare Pages 收集宾客数据
6. `assets/` 中原始赞助码（`sponsor-*.jpg`）是否保留由所有者决定，默认视为可删

### 14.2 执行者需自行拍板（已给默认值，见 §1.1）

1. **Cloudflare 相关目录**：默认**一并删除**；若所有者要求保留，则保留目录并在文档注明适用环境
2. **抽卡个性化姓名**：默认**只做预生成卡面**；个性化姓名作为第二阶段可选增强，且必须通过 §8.4 三项探测

### 14.3 建议向所有者确认的开放项（不阻塞开工）

1. **卡池数量**：默认 6 款是否足够（可扩到 8~9 款）
2. **婚纱照拍摄场景**（海边 / 山林 / 城市 / 棚拍）：影响 B6~B9 的场景图选择——例如棚拍为主则需多补户外原野类场景图，以呼应新人的视觉语境
3. **是否保留赞赏区**：决定 `assets/sponsor-*.jpg` 与 `README.md` 对应段落是否删除

---

## 15. 附：可直接复制的生成提示词模板

> 以下模板已包含 §7.2 的统一风格段落。**每张图都要把母本 `generated-raw/hero-journey-v5.png` 作为输入图传入（走 `edits` 端点）。**
>
> ⚠️ **不要沿用 §15.1 的旧模板生成新图**——它是 v1 阶段的产物，已被实测证明会导致"高细节、不像吉卜力"。**B1 已定稿，不需要再生成。**

### 15.1 B1 首页主视觉（母本）— ✅ 已完成，仅供参考，不要再生成

最终定稿命令形态：

```bash
curl -X POST 'https://code28.ccwu.cc/v1/images/edits' \
  -H "Authorization: Bearer $KEY" \
  -F 'model=gpt-image-2' \
  -F 'size=1024x1536' \
  -F 'quality=high' \
  -F 'n=1' \
  -F 'image=@起风了.jpg' \
  -F "prompt=<§7.2 的定稿艺术指导段落 + 画面内容描述>"
```

产出：`generated-raw/hero-journey-v5.png`（竖版母本）、`hero-journey-wide-v1.png`（横版）、`og-share-v1.png`（1200×630）。

> **已废弃的旧模板（v1 阶段，实测不像吉卜力，不要再用）**：

```text
A peaceful hillside town viewed from above, an old steam train winding along a cliffside railway,
a wooden windmill turning slowly on the hill, large cumulus clouds in an expansive sky,
the distant sea visible beyond the hills, one small house with warm lit windows,
vertical composition.
Studio Ghibli style, Hayao Miyazaki style hand-painted 2D animation background,
soft watercolor and gouache texture, gentle pastel palette
(cream #F7F0E1, sky #A8CFE0, grass #8FAE6B, sunset #E8A657, ink #3A3B33),
warm golden late-afternoon light, expansive sky with large cumulus clouds,
visible paper grain, nostalgic and peaceful mood,
no watermark, no signature, no text
```

### 15.2 B6 风铃场景

```text
A wooden wind chime hanging under the eaves of an old house, a worn wooden bench below,
small hand-written paper notes fluttering in the wind, soft afternoon light,
a quiet countryside street, horizontal composition.
[+ 统一风格段落]
match the reference image's art style, brushwork, palette and lighting exactly
```

### 15.3 B10 新人立绘（风格转换，带锁脸指令）

```text
Based on this real wedding photo, convert it into the Ghibli hand-painted animation style described above:
a loving couple standing on a hillside in early summer, wildflowers around them,
warm golden light, expansive sky.
Strictly preserve the two people's facial features, face shape, hairstyle, pose and relative position;
keep the original composition and aspect ratio.
Change only the art style, background and lighting.
Do not change the number or identity of people.
[+ 统一风格段落]
match the reference image's art style, brushwork, palette and lighting exactly
no watermark, no signature, no text
```

### 15.4 B13 邀请函卡片（卡面，**文字留白**）

```text
A delicate invitation card design: aged parchment paper frame with a subtle vine and wind-swirl
ornament border, a hand-painted Ghibli-style scene as the central illustration
(a hillside town with a steam train and windmill), generous empty space at the bottom
for hand-written text to be added later, horizontal card composition,
keep the bottom third completely blank, do not draw any letters, characters or numbers.
[+ 统一风格段落]
match the reference image's art style, brushwork, palette and lighting exactly
no watermark, no signature, no text, no letters, no numbers
```

> **关键**：卡面必须显式要求 `do not draw any letters, characters or numbers` + `blank`，文字一律后期用 SVG/HTML 叠加。这是规避 AI 生成中文错字的标准做法，不要试图让模型直接写出正确的卡片文字。

---

## 16. 附：现有交互代码的保留清单（不要动的部分）

以下代码逻辑**原样保留**，本次改造只换视觉与文案：

| 位置 | 逻辑 |
| --- | --- |
| `app.js` 6–15 | `prefers-reduced-motion` 判断 + `IntersectionObserver` 的 `.reveal` 入场 |
| `app.js` 17–24 | 28 个气泡生成循环（只改 CSS 呈现） |
| `app.js` 30–39 | `updateHud()` 的进度公式与 `requestAnimationFrame` 节流 |
| `app.js` 45–69 | 长按逻辑（含键盘 Enter/Space 分支与四种中断事件） |
| `app.js` 71–78 | 声呐点击的波纹生成与元素高亮骨架（只扩展） |
| `app.js` 97–112 | 9 个场内元素生成、捕获上限、随机祝福、集齐判定 |
| `app.js` 114–123 | 角色轮播的取模循环与计数显示 |
| `app.js` 125–145 | 音乐播放/暂停、静音回退提示、与滚动提示的联动 |
| `app.js` 147–205 | 登记表单：外链/本地双分支、必填校验、住宿联动、200 字计数、回填修改、`localStorage` 读写 |
| `index.html` | 全部 id 与 class 名、板块顺序、`aria-*` 属性结构、`.reveal` 标记 |
| `style.css` | 响应式骨架、`phone-shell` 480px 容器、安全区 `env(safe-area-inset-*)` 用法、`quick-nav` 与 `music-dock` 的定位 |
