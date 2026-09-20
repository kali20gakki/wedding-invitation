/**
 * 用 Chrome DevTools Protocol 做多分辨率全页截图，供视觉自查。
 * 用法: node tools/shoot.mjs [端口]
 * 依赖: 已安装 Chrome，且本地静态服务在 127.0.0.1:<端口> 运行
 */
import { spawn } from 'node:child_process'
import { mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

const PORT = Number(process.argv[2] || 8099)
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
const USER_DIR = join(tmpdir(), `shoot-${Date.now()}`)
const OUT = 'generated-raw/shots'
const DEBUG_PORT = 9333

const VIEWPORTS = [
  { name: 'home-375', width: 375, height: 812 },
  { name: 'home-390', width: 390, height: 844 },
  { name: 'home-430', width: 430, height: 932 },
  { name: 'home-desktop', width: 1280, height: 900 }
]

// 交互态截图：点击指定元素后再截图（用于检查抽卡层等交互结果）
const STATES = [
  { name: 'draw-open', width: 390, height: 844, click: '#draw-open', then: '#draw-back', scrollAfter: '.draw-card', full: false },
  { name: 'draw-revealed', width: 390, height: 844, click: '#draw-open', then: '#draw-back', after: '.draw-card', scrollAfter: '.draw-card', full: false },
  { name: 'rsvp-view', width: 390, height: 962, scrollTo: '#rsvp', full: false },
  { name: 'map-view', width: 390, height: 962, scrollTo: '#arrival', full: false },
  { name: 'crew-view', width: 390, height: 962, scrollTo: '#crew', full: false },
  { name: 'chime-section', width: 390, height: 962, scrollTo: '#chime', full: false },
  { name: 'hero-view', width: 390, height: 844, full: false },
  { name: 'hero-view-430', width: 430, height: 932, full: false },
  // 风铃：点一下，三句祝福正在逐条浮现时截图（点完再滚到风铃框，保证它在画面里）
  { name: 'chime-view', width: 390, height: 760, click: '#sonar-button', settle: 900, scrollAfter: '.exploration-frame', full: false },
  // 纸鹤：接住一只，看祝福纸条展开的样子
  { name: 'crane-view', width: 390, height: 760, then: '.pixel-fish', settle: 900, scrollAfter: '#fish-field', full: false }
]

mkdirSync(OUT, { recursive: true })
rmSync(USER_DIR, { recursive: true, force: true })

const chrome = spawn(CHROME, [
  '--headless=new',
  '--disable-gpu',
  '--hide-scrollbars',
  `--remote-debugging-port=${DEBUG_PORT}`,
  `--user-data-dir=${USER_DIR}`,
  '--no-first-run',
  '--no-default-browser-check',
  'about:blank'
], { stdio: 'ignore' })

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

async function getTarget() {
  for (let i = 0; i < 60; i += 1) {
    try {
      const res = await fetch(`http://127.0.0.1:${DEBUG_PORT}/json/version`)
      const info = await res.json()
      if (info.webSocketDebuggerUrl) return info.webSocketDebuggerUrl
    } catch { /* 还没起来 */ }
    await sleep(400)
  }
  throw new Error('Chrome 调试端口未就绪')
}

class CDP {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); this.events = new Map() }
  static async connect(url) {
    const ws = new WebSocket(url)
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject })
    const cdp = new CDP(ws)
    ws.onmessage = (msg) => {
      const data = JSON.parse(msg.data)
      if (data.id && cdp.pending.has(data.id)) {
        const { resolve, reject } = cdp.pending.get(data.id)
        cdp.pending.delete(data.id)
        data.error ? reject(new Error(JSON.stringify(data.error))) : resolve(data.result)
      } else if (data.method && cdp.events.has(data.method)) {
        cdp.events.get(data.method).forEach((fn) => fn(data.params))
        cdp.events.delete(data.method)
      }
    }
    return cdp
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject })
      this.ws.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }))
    })
  }
  once(method) {
    return new Promise((resolve) => {
      if (!this.events.has(method)) this.events.set(method, [])
      this.events.get(method).push(resolve)
    })
  }
}

const main = async () => {
  const browserWs = await getTarget()
  const browser = await CDP.connect(browserWs)
  const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank' })
  const { sessionId } = await browser.send('Target.attachToTarget', { targetId, flatten: true })

  const send = (m, p) => browser.send(m, p, sessionId)
  await send('Page.enable')
  await send('Runtime.enable')

  const results = []
  const jobs = [
    ...VIEWPORTS.map((v) => ({ ...v, full: true })),
    ...STATES
  ]
  for (const vp of jobs) {
    await send('Emulation.setDeviceMetricsOverride', {
      width: vp.width, height: vp.height, deviceScaleFactor: 1, mobile: vp.width < 700
    })
    await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/index.html` })
    const loaded = browser.once('Page.loadEventFired')
    await Promise.race([loaded, sleep(8000)])
    await sleep(1200)

    // 触发 IntersectionObserver 入场动画：先滚到底再回到顶部
    await send('Runtime.evaluate', {
      expression: `(async()=>{const s=window.scrollY;const h=document.documentElement.scrollHeight;
        for(let y=0;y<h;y+=window.innerHeight*0.6){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,90));}
        window.scrollTo(0,0);await new Promise(r=>setTimeout(r,600));})()`,
      awaitPromise: true
    })
    // 兜底：截图前强制所有 reveal 元素可见（避免时序竞争导致空白）
    await send('Runtime.evaluate', {
      expression: `document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-visible'))`
    })
    await sleep(400)

    // 交互态：滚动到指定区块。
    // 用瞬间滚动 + 自己算位置：scrollIntoView 会走 CSS 的平滑滚动，
    // sleep 结束时间可能还没滚到位，截出来是别的一屏（曾经踩过）。
    if (vp.scrollTo) {
      await send('Runtime.evaluate', {
        expression: `(()=>{const el=document.querySelector('${vp.scrollTo}');
          if(!el)return 'missing';const y=el.getBoundingClientRect().top+window.scrollY;
          window.scrollTo({top:Math.max(0,y),behavior:'instant'});return window.scrollY})()`,
        returnByValue: true
      })
      await sleep(400)
    }
    // 交互态：点击指定元素
    if (vp.click) {
      await send('Runtime.evaluate', { expression: `document.querySelector('${vp.click}')?.click()` })
      // settle 用于抓取「动画正播到一半」的画面（风铃祝福纸条只存在 2.6s）
      await sleep(vp.settle !== undefined ? vp.settle : (vp.then ? 900 : 700))
    }
    if (vp.then) {
      await send('Runtime.evaluate', { expression: `document.querySelector('${vp.then}')?.click()` })
      await sleep(vp.settle !== undefined ? vp.settle : (vp.after ? 1100 : 900))
    }
    // 互动之后再对准目标区块，避免点击时的滚动位置不对（同样用瞬间滚动）
    if (vp.scrollAfter) {
      await send('Runtime.evaluate', {
        expression: `(()=>{const el=document.querySelector('${vp.scrollAfter}');
          if(!el)return 'missing';const r=el.getBoundingClientRect();
          const y=r.top+window.scrollY-(window.innerHeight-r.height)/2;
          window.scrollTo({top:Math.max(0,y),behavior:'instant'});return window.scrollY})()`,
        returnByValue: true
      })
      await sleep(250)
    }
    if (vp.after) {
      const ok = await send('Runtime.evaluate', { expression: `!!document.querySelector('${vp.after}')`, returnByValue: true })
      results.push({ name: `${vp.name}-hassel`, exists: ok.result.value })
    }

    // 首屏那一次顺带做关键行为断言
    if (vp.name === 'home-390') {
      const check = await send('Runtime.evaluate', {
        returnByValue: true,
        expression: `JSON.stringify({
          rsvpFormHidden: document.querySelector('#rsvp-form').hidden,
          rsvpExternalShown: !document.querySelector('#rsvp-external').hidden,
          externalHref: document.querySelector('#rsvp-external-link').getAttribute('href'),
          status: document.querySelector('.rsvp-phone .app-bar small').textContent,
          mapHref: document.querySelector('.map-console a').getAttribute('href'),
          heroNameImg: document.querySelector('.hero-names')?.getAttribute('alt') || null,
          heroArt: document.querySelector('.hero-art')?.getAttribute('src'),
          kicker: document.querySelector('.hero-kicker')?.textContent.trim(),
          crewCount: document.querySelectorAll('.crew-slide').length,
          sectionNums: [...document.querySelectorAll('.section-title > span')].map(s=>s.textContent).join(',')
        })`
      })
      results.push({ name: 'assertions', ...JSON.parse(check.result.value) })
    }

    // 取整页尺寸
    const { result } = await send('Runtime.evaluate', {
      expression: 'JSON.stringify({w:document.documentElement.scrollWidth,h:document.documentElement.scrollHeight,vw:window.innerWidth})',
      returnByValue: true
    })
    const size = JSON.parse(result.value)
    // 视口截图时，clip 的 y 需用当前滚动位置；整页截图从 0 开始
    let clipY = 0
    if (!vp.full) {
      const sc = await send('Runtime.evaluate', { expression: 'window.scrollY', returnByValue: true })
      clipY = Math.max(0, Math.min(Number(sc.result.value) || 0, Math.max(0, size.h - vp.height)))
    }
    const height = vp.full ? Math.min(size.h, 14000) : vp.height

    const shot = await send('Page.captureScreenshot', {
      format: 'png',
      captureBeyondViewport: Boolean(vp.full),
      clip: { x: 0, y: clipY, width: vp.width, height, scale: 1 }
    })
    const buf = Buffer.from(shot.data, 'base64')
    writeFileSync(join(OUT, `${vp.name}.png`), buf)
    results.push({ name: vp.name, viewport: `${vp.width}x${vp.height}`, doc: `${size.w}x${size.h}`, overflowX: size.w > vp.width, bytes: buf.length })
  }

  console.log(JSON.stringify(results, null, 2))
  chrome.kill()
  process.exit(0)
}

main().catch((err) => { console.error('截图失败:', err.message); chrome.kill(); process.exit(1) })
