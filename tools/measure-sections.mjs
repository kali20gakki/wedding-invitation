/**
 * 逐屏量「屏数」：每个 .story-section 滚进视口后再量高度 ÷ 视口高。
 *
 * 为什么必须滚进视口再量：
 *   .story-section 用了 content-visibility:auto，屏幕外的章节不参与布局，
 *   量到的是 contain-intrinsic-size 的占位值，而不是真实高度。
 *   占位值只算内容盒（不含 64/104 的内边距），所以会稳定偏大约 168px —— 
 *   直接用未滚动状态量，会得出「屏数 1.199」这类假数据。
 *
 * 用法: node tools/measure-sections.mjs [端口]
 * 依赖: 已安装 Chrome，且本地静态服务在 127.0.0.1:<端口> 运行
 */
import { spawn } from 'node:child_process'
import { rmSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

const PORT = Number(process.argv[2] || 8123)
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
const USER_DIR = join(tmpdir(), `measure-${Date.now()}`)
const DEBUG_PORT = 9346

const VIEWPORTS = [
  { width: 360, height: 640 },
  { width: 375, height: 667 },
  { width: 390, height: 844 },
  { width: 390, height: 962 },
  { width: 430, height: 932 }
]

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
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map() }
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
}

// 逐屏滚进视口量一次，返回 { id: {ratio, height, label} }
// topGap = section 顶到标题的距离；bottomGap = 末元素到 section 底的距离。
// 两者都远大于上下内边距（64 / 104）就说明这一屏内容偏少、被 justify-content:center
// 从中间撑开了 —— 视觉上就是「上面空一块、下面空一块」。
const MEASURE = `(async()=>{
  const out = {};
  const sections = [...document.querySelectorAll('.story-section')];
  for (const s of sections) {
    const y = s.getBoundingClientRect().top + window.scrollY;
    window.scrollTo({ top: Math.max(0, y), behavior: 'instant' });
    await new Promise(r => setTimeout(r, 260));
    const h = s.getBoundingClientRect().height;
    const vh = window.innerHeight;
    const sr = s.getBoundingClientRect();
    const kids = [...s.children];
    const last = kids[kids.length - 1].getBoundingClientRect();
    const title = s.querySelector('.section-title');
    out[s.id || '(ending)'] = {
      ratio: Math.round(h / vh * 1000) / 1000,
      height: Math.round(h),
      over: Math.round(h - vh),
      topGap: title ? Math.round(title.getBoundingClientRect().top - sr.top) : null,
      bottomGap: Math.round(sr.bottom - last.bottom)
    };
  }
  window.scrollTo({ top: 0, behavior: 'instant' });
  return JSON.stringify({ viewport: window.innerWidth + 'x' + window.innerHeight, sections: out });
})()`

const main = async () => {
  const browser = await CDP.connect(await getTarget())
  const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank' })
  const { sessionId } = await browser.send('Target.attachToTarget', { targetId, flatten: true })
  const send = (m, p) => browser.send(m, p, sessionId)
  await send('Page.enable')
  await send('Runtime.enable')

  let worst = 0
  for (const vp of VIEWPORTS) {
    await send('Emulation.setDeviceMetricsOverride', {
      width: vp.width, height: vp.height, deviceScaleFactor: 1, mobile: true
    })
    const stamp = Date.now()
    await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/index.html?v=${stamp}` })
    await sleep(2000)
    // 先把整页扫一遍，让 content-visibility 记住各屏真实高度、reveal 动画全部触发
    await send('Runtime.evaluate', {
      expression: `(async()=>{const h=document.documentElement.scrollHeight;
        for(let y=0;y<h;y+=window.innerHeight*0.6){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,70));}
        window.scrollTo(0,0);await new Promise(r=>setTimeout(r,400));})()`,
      awaitPromise: true
    })
    await send('Runtime.evaluate', { expression: `document.querySelectorAll('.reveal').forEach(e=>e.classList.add('is-visible'))` })
    await sleep(300)

    const { result } = await send('Runtime.evaluate', { expression: MEASURE, returnByValue: true, awaitPromise: true })
    const data = JSON.parse(result.value)
    console.log(`\n=== ${data.viewport} ===`)
    for (const [id, m] of Object.entries(data.sections)) {
      worst = Math.max(worst, m.ratio)
      const flag = m.ratio > 1.001 ? `  ← 超出 ${m.over}px` : ''
      const gaps = m.topGap === null ? '' : `  上留白 ${m.topGap}  下留白 ${m.bottomGap}`
      console.log(`  ${id.padEnd(10)} ${String(m.ratio).padEnd(6)} ${String(m.height + 'px').padEnd(7)}${gaps}${flag}`)
    }
  }
  console.log(`\n最差屏数: ${worst}${worst > 1.001 ? '  (存在超屏)' : '  (全部 ≤ 1 屏)'}`)
  chrome.kill()
  process.exit(0)
}

main().catch((err) => { console.error('量屏失败:', err.message); chrome.kill(); process.exit(1) })
