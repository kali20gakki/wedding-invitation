/**
 * 单页截图：把任意本地 HTML 按给定视口截成 PNG，供视觉自查。
 * 用法: node tools/shot.mjs <url> <outPath> <width> <height> [--full]
 */
import { spawn } from 'node:child_process'
import { mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { tmpdir } from 'node:os'

const [url, outPath, wArg, hArg] = process.argv.slice(2)
const full = process.argv.includes('--full')
// 额外的页面内动作（按顺序执行），用 --do="<js>" 传入，可重复
const actions = process.argv.filter((a) => a.startsWith('--do=')).map((a) => a.slice(5))
if (!url || !outPath || !wArg || !hArg) {
  console.error('用法: node tools/shot.mjs <url> <outPath> <width> <height> [--full]')
  process.exit(1)
}
const width = Number(wArg)
const height = Number(hArg)
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
const USER_DIR = join(tmpdir(), `shot-${Date.now()}`)
const DEBUG_PORT = 9344

mkdirSync(dirname(outPath), { recursive: true })
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

const main = async () => {
  const browser = await CDP.connect(await getTarget())
  const { targetId } = await browser.send('Target.createTarget', { url: 'about:blank' })
  const { sessionId } = await browser.send('Target.attachToTarget', { targetId, flatten: true })
  const send = (m, p) => browser.send(m, p, sessionId)

  await send('Page.enable')
  await send('Runtime.enable')
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 700 })
  await send('Page.navigate', { url })
  await sleep(2200)

  const outputs = []
  for (const action of actions) {
    const { result: r } = await send('Runtime.evaluate', { expression: action, returnByValue: true, awaitPromise: true })
    outputs.push(r.value)
    await sleep(300)
  }
  if (outputs.length) console.log('--do 结果:', JSON.stringify(outputs))

  const { result } = await send('Runtime.evaluate', {
    expression: 'JSON.stringify({w:document.documentElement.scrollWidth,h:document.documentElement.scrollHeight})',
    returnByValue: true
  })
  const size = JSON.parse(result.value)
  let clipHeight = full ? size.h : Math.min(height, size.h)
  let clipY = 0
  if (full) {
    await send('Runtime.evaluate', { expression: 'window.scrollTo(0,0)' })
    await sleep(120)
  } else {
    const { result: rect } = await send('Runtime.evaluate', {
      expression: 'JSON.stringify({x:window.scrollX,y:window.scrollY})',
      returnByValue: true
    })
    const scroll = JSON.parse(rect.value)
    clipY = scroll.y
    clipHeight = height
  }

  const shot = await send('Page.captureScreenshot', {
    format: 'png',
    captureBeyondViewport: full,
    clip: { x: 0, y: clipY, width, height: clipHeight, scale: 1 }
  })
  writeFileSync(outPath, Buffer.from(shot.data, 'base64'))
  console.log(JSON.stringify({ url, outPath, viewport: `${width}x${height}`, doc: `${size.w}x${size.h}` }))
  chrome.kill()
  process.exit(0)
}

main().catch((err) => { console.error('截图失败:', err.message); chrome.kill(); process.exit(1) })
