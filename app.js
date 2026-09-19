/* ============================================================================
   风之旅 · 吉卜力画风婚礼邀请函
   ----------------------------------------------------------------------------
   命名映射（历史遗留名 → 当前场景语义）
     .pixel-fish    → 纸鹤      #fish-field → 纸鹤场      #fish-count → 纸鹤计数
     .fish-blessing → 祝福纸条  .sonar-button → 风铃按钮   .sonar-field → 风铃波纹场
     #depth-value   → 风的刻度  #oxygen-fill → 云的高度
   ============================================================================ */

const weddingDate = new Date('2026-10-02T11:30:00+08:00')
// 真实宾客登记：飞书问卷公开填写链接。留空则退回本地演示模式（仅存本机、不上传）。
const RSVP_FORM_URL = 'https://my.feishu.cn/share/base/form/shrcnFtcbV94GWMm1y3Zh7da99b'
document.querySelector('#days-count').textContent = String(Math.max(0, Math.ceil((weddingDate.getTime() - Date.now()) / 86400000)))

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const revealElements = document.querySelectorAll('.reveal')
if ('IntersectionObserver' in window && !reducedMotion) {
  const revealObserver = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (!entry.isIntersecting) return
    entry.target.classList.add('is-visible')
    revealObserver.unobserve(entry.target)
  }), { threshold: 0.12, rootMargin: '0px 0px -4% 0px' })
  revealElements.forEach((element) => revealObserver.observe(element))
} else revealElements.forEach((element) => element.classList.add('is-visible'))

// 风与叶屑
const bubbleField = document.querySelector('.bubble-field')
for (let index = 0; index < 28; index += 1) {
  const bubble = document.createElement('i')
  bubble.style.left = `${(index * 37 + 9) % 97}%`
  bubble.style.setProperty('--duration', `${9 + (index % 6) * 1.6}s`)
  bubble.style.setProperty('--delay', `${-(index % 9) * 1.5}s`)
  bubbleField.append(bubble)
}

const hud = document.querySelector('.game-hud')
const depthValue = document.querySelector('#depth-value')
const oxygenFill = document.querySelector('#oxygen-fill')
const musicHint = document.querySelector('#music-hint')
let ticking = false
function updateHud() {
  const progress = Math.min(1, window.scrollY / Math.max(1, document.documentElement.scrollHeight - window.innerHeight))
  hud.classList.toggle('is-visible', window.scrollY > window.innerHeight * 0.55)
  depthValue.textContent = String(Math.round(progress * 420))
  oxygenFill.style.transform = `scaleX(${1 - progress * 0.22})`
  if (window.scrollY > 20) musicHint.classList.add('is-hidden')
  ticking = false
}
window.addEventListener('scroll', () => { if (!ticking) requestAnimationFrame(updateHud); ticking = true }, { passive: true })

const missionCard = document.querySelector('.mission-card')
const acceptButton = document.querySelector('#accept-quest')
const questStatus = document.querySelector('#quest-status')
const missionComplete = document.querySelector('#mission-complete')
let holdTimer
function startHold() {
  if (missionCard.classList.contains('is-accepted') || missionCard.classList.contains('is-holding')) return
  missionCard.classList.add('is-holding')
  holdTimer = window.setTimeout(() => {
    missionCard.classList.remove('is-holding')
    missionCard.classList.add('is-accepted')
    questStatus.textContent = 'OPENED'
    acceptButton.textContent = '信已收下 ✓'
    missionComplete.classList.remove('show')
    requestAnimationFrame(() => missionComplete.classList.add('show'))
    navigator.vibrate?.([45, 30, 80])
  }, 1200)
}
function cancelHold() { window.clearTimeout(holdTimer); missionCard.classList.remove('is-holding') }
acceptButton.addEventListener('pointerdown', startHold)
acceptButton.addEventListener('pointerup', cancelHold)
acceptButton.addEventListener('pointerleave', cancelHold)
acceptButton.addEventListener('pointercancel', cancelHold)
acceptButton.addEventListener('keydown', (event) => {
  if (event.key !== 'Enter' && event.key !== ' ') return
  event.preventDefault()
  startHold()
})
acceptButton.addEventListener('keyup', cancelHold)

// 风铃三响：三圈波纹 + 一组祝福。风铃每被摇响一次，就换一组，四组十二句。
const sonarField = document.querySelector('.sonar-field')
const chimeBlessingSets = [
  ['一声，愿一路顺风', '二声，愿平安无忧', '三声，愿相爱到老'],
  ['一声，愿归途总有人等', '二声，愿灶上永远有热汤', '三声，愿窗前的灯常亮'],
  ['一声，愿春来有信', '二声，愿夏夜有风', '三声，愿岁岁有今日'],
  ['一声，愿你们永远有话可说', '二声，愿争吵后仍愿并肩', '三声，愿白发时还牵着手']
]
let chimeTimers = []
let chimeRound = 0
document.querySelector('#sonar-button').addEventListener('click', () => {
  chimeTimers.forEach((timer) => window.clearTimeout(timer))
  chimeTimers = []
  sonarField.querySelectorAll('i, .chime-note').forEach((node) => node.remove())

  const blessings = chimeBlessingSets[chimeRound % chimeBlessingSets.length]
  chimeRound += 1

  blessings.forEach((text, index) => {
    chimeTimers.push(window.setTimeout(() => {
      const ring = document.createElement('i')
      sonarField.append(ring)
      window.setTimeout(() => ring.remove(), 1600)

      const note = document.createElement('span')
      note.className = 'chime-note'
      note.textContent = text
      note.style.bottom = `${76 + index * 34}px`
      sonarField.append(note)
      window.setTimeout(() => note.remove(), 2600)
    }, index * 180))
  })

  // 摇响风铃会惊起纸鹤：整场轻微一亮
  document.querySelectorAll('.pixel-fish:not(.caught)').forEach((crane) => crane.animate(
    [{ filter: 'saturate(1) brightness(1)' }, { filter: 'saturate(1.4) brightness(1.15)' }, { filter: 'saturate(1) brightness(1)' }],
    { duration: 900, easing: 'ease-in-out' }
  ))
  navigator.vibrate?.(35)
})

// 纸鹤：接住即展开成一句祝福
const fishField = document.querySelector('#fish-field')
const fishCount = document.querySelector('#fish-count')
// 与 assets/crane-*.svg 同名，CSS 里按 data-tone 取对应的图案
// 只放对比度够的色：天蓝/米白在浅色天空底上几乎看不见，故不采用
const craneTones = ['sunset', 'brick', 'grass', 'road', 'ink']
const craneBlessings = [
  '愿你们的旅途风调雨顺',
  '愿有一盏灯永远为你们亮着',
  '愿每一次出发都能回家',
  '愿岁月温柔，草木长青',
  '愿你们在同一片天空下老去',
  '愿平淡日子里的面包和牛奶都香甜'
]
let caught = 0
function showCraneBlessing(crane) {
  // 原来这里有一句 `if (Math.random() > 0.72) return`：
  // 想着偶尔不出纸条更自然，实际效果是 "点了好几次都没有祝福" —— 交互反馈不能有随机缺失，已删除。
  const blessing = document.createElement('p')
  const craneRect = crane.getBoundingClientRect()
  const fieldRect = fishField.getBoundingClientRect()
  blessing.className = 'fish-blessing'
  blessing.textContent = craneBlessings[Math.floor(Math.random() * craneBlessings.length)]
  // 纸条按 180px 估算排在纸鹤左侧；贴到左边缘时改排右侧，折角也跟着换边
  const craneLeft = craneRect.left - fieldRect.left
  const craneTop = craneRect.top - fieldRect.top
  const side = craneLeft < 196 ? 'right' : 'left'
  blessing.dataset.side = side
  blessing.style.left = `${side === 'right'
    ? Math.min(fieldRect.width - 184, craneLeft + craneRect.width * 0.5)
    : Math.max(6, craneLeft - 148)}px`
  // 连着接住好几只时纸条会叠在一起，按当前存活数量往下错开；最多错两级，免得跑出纸鹤场
  const alive = fishField.querySelectorAll('.fish-blessing').length
  blessing.style.top = `${Math.max(4, craneTop - 46 + Math.min(2, alive) * 52)}px`
  fishField.appendChild(blessing)
  window.setTimeout(() => blessing.remove(), 2600)
}
for (let index = 0; index < 9; index += 1) {
  const crane = document.createElement('button')
  crane.type = 'button'; crane.className = 'pixel-fish'; crane.setAttribute('aria-label', `接住第 ${index + 1} 只纸鹤`)
  crane.dataset.tone = craneTones[index % craneTones.length]
  crane.style.top = `${8 + (index * 53) % 170}px`
  crane.style.setProperty('--swim', `${13 + (index % 4) * 2}s`)
  crane.style.setProperty('--delay', `${-(index * 2.6)}s`)
  // 尺寸仍用内联样式：纸鹤按只大小不一，看起来才像被风吹散的一群
  crane.style.width = `${30 + (index % 3) * 7}px`
  crane.style.height = crane.style.width
  crane.style.padding = '0'
  crane.addEventListener('click', () => {
    if (crane.classList.contains('caught')) return
    crane.classList.add('caught')
    // 接住时朝左上飞走，与纸鹤本身的朝向一致
    crane.style.transformOrigin = '50% 50%'
    caught = Math.min(5, caught + 1); fishCount.textContent = String(caught); navigator.vibrate?.(25); showCraneBlessing(crane)
    if (caught === 5) {
      // 收齐的那一刻只留一句话：先把零散纸条收掉，免得叠在一起看不清
      fishField.querySelectorAll('.fish-blessing').forEach((node) => node.remove())
      const message = document.createElement('p')
      message.className = 'fish-unlock'
      message.textContent = '纸鹤收齐了：愿风替我们把这些祝福捎给你'
      fishField.append(message)
      window.setTimeout(() => message.remove(), 3600)
    }
  })
  fishField.append(crane)
}

// 风车邮局来信：照片轮播
const crewSlides = [...document.querySelectorAll('.crew-slide')]
const crewName = document.querySelector('#crew-name')
let crewIndex = 0
function showCrew(nextIndex) {
  crewIndex = (nextIndex + crewSlides.length) % crewSlides.length
  crewSlides.forEach((slide, index) => slide.classList.toggle('is-active', index === crewIndex))
  crewName.textContent = `${crewIndex + 1} / ${crewSlides.length}`
}
document.querySelector('[data-crew="prev"]').addEventListener('click', () => showCrew(crewIndex - 1))
document.querySelector('[data-crew="next"]').addEventListener('click', () => showCrew(crewIndex + 1))

// 背景音乐
const musicToggle = document.querySelector('#music-toggle')
const officialBgm = document.querySelector('#official-bgm')
let musicPlaying = false
function setMusicState(playing) {
  musicPlaying = playing; musicToggle.classList.toggle('playing', playing); musicToggle.setAttribute('aria-pressed', String(playing)); musicToggle.setAttribute('aria-label', playing ? '暂停背景音乐' : '播放背景音乐')
}
async function playMusic() {
  musicHint.classList.add('is-hidden')
  try {
    officialBgm.volume = 0.58
    await officialBgm.play()
    setMusicState(true)
  } catch {
    setMusicState(false)
    musicHint.textContent = '音乐暂未就位，稍后再试'
    musicHint.classList.remove('is-hidden')
  }
}
function pauseMusic() { officialBgm.pause(); setMusicState(false) }
musicToggle.addEventListener('click', () => musicPlaying ? pauseMusic() : playMusic())
officialBgm.addEventListener('error', () => {
  if (musicPlaying) return
  musicHint.textContent = '音乐暂未就位，稍后再试'
  musicHint.classList.remove('is-hidden')
})
document.querySelector('#start-mission').addEventListener('click', () => { playMusic(); document.querySelector('#briefing').scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth' }) })

// 登记：外链模式（飞书问卷）优先，未配置时保留本地演示模式
const rsvpForm = document.querySelector('#rsvp-form')
const rsvpSuccess = document.querySelector('#rsvp-success')
const rsvpExternal = document.querySelector('#rsvp-external')
const rsvpExternalLink = document.querySelector('#rsvp-external-link')
const rsvpStatus = document.querySelector('.rsvp-phone .app-bar small')
const publicRsvpUrl = RSVP_FORM_URL.trim()

if (publicRsvpUrl) {
  rsvpForm.hidden = true
  rsvpSuccess.hidden = true
  rsvpExternal.hidden = false
  rsvpExternalLink.href = publicRsvpUrl
  rsvpStatus.textContent = 'ONLINE'
} else if (rsvpForm) {
  const accommodationDates = document.querySelector('#accommodation-dates')
  const accommodationField = document.querySelector('#accommodation-field')
  const messageField = rsvpForm.elements.message
  const messageCount = document.querySelector('#message-count')
  const rsvpError = document.querySelector('#rsvp-error')
  const rsvpSuccessTitle = document.querySelector('#rsvp-success-title')
  const rsvpSuccessSummary = document.querySelector('#rsvp-success-summary')
  const rsvpSubmit = rsvpForm.querySelector('[type="submit"]')
  const storageKey = 'journey-wedding-demo-rsvp'
  let savedRsvp
  try { savedRsvp = JSON.parse(localStorage.getItem(storageKey)) } catch { savedRsvp = undefined }
  function updateAccommodation() {
    const needed = rsvpForm.elements.needsAccommodation.value === 'yes'
    accommodationDates.hidden = !needed; rsvpForm.elements.checkInAt.required = needed; rsvpForm.elements.checkOutAt.required = needed
    if (needed) { rsvpForm.elements.checkInAt.value ||= '2026-10-01T14:00'; rsvpForm.elements.checkOutAt.value ||= '2026-10-03T12:00' }
  }
  function fillRsvp(data) {
    if (!data) return
    rsvpForm.elements.guestName.value = data.guestName || ''; rsvpForm.elements.partySize.value = String(data.partySize || 1); rsvpForm.elements.phone.value = data.phone || ''; rsvpForm.elements.message.value = data.message || ''
    const choice = rsvpForm.querySelector(`[name="needsAccommodation"][value="${data.needsAccommodation ? 'yes' : 'no'}"]`); if (choice) choice.checked = true
    rsvpForm.elements.checkInAt.value = data.checkInAt || '2026-10-01T14:00'; rsvpForm.elements.checkOutAt.value = data.checkOutAt || '2026-10-03T12:00'; messageCount.value = String(rsvpForm.elements.message.value.length); updateAccommodation()
  }
  function showRsvpError(message) { rsvpError.textContent = message; rsvpError.hidden = false }
  function collectRsvp() {
    const formData = new FormData(rsvpForm); const guestName = String(formData.get('guestName') || '').trim(); const needsAccommodation = formData.get('needsAccommodation') === 'yes'; const checkInAt = String(formData.get('checkInAt') || ''); const checkOutAt = String(formData.get('checkOutAt') || '')
    if (!guestName) throw new Error('请填写宾客姓名。'); if (needsAccommodation && (!checkInAt || !checkOutAt)) throw new Error('请填写完整的住宿时间。'); if (needsAccommodation && checkOutAt <= checkInAt) throw new Error('退房时间必须晚于入住时间。')
    return { id: savedRsvp?.id, editToken: savedRsvp?.editToken, guestName, partySize: Number(formData.get('partySize')), needsAccommodation, checkInAt: needsAccommodation ? checkInAt : null, checkOutAt: needsAccommodation ? checkOutAt : null, phone: String(formData.get('phone') || '').trim(), message: String(formData.get('message') || '').trim() }
  }
  rsvpForm.addEventListener('change', (event) => { if (event.target.name === 'needsAccommodation') { accommodationField.removeAttribute('aria-invalid'); updateAccommodation() } })
  messageField.addEventListener('input', () => { messageCount.value = String(messageField.value.length) })
  rsvpForm.addEventListener('submit', async (event) => {
    event.preventDefault(); rsvpError.hidden = true
    let submission
    try { submission = collectRsvp() } catch (error) { showRsvpError(error.message); return }
    rsvpSubmit.disabled = true; rsvpSubmit.querySelector('span').textContent = '正在保存演示登记……'
    try {
      savedRsvp = { ...submission, id: 'demo-local-only', editToken: undefined }
      localStorage.setItem(storageKey, JSON.stringify(savedRsvp))
      rsvpForm.hidden = true; rsvpSuccess.hidden = false; rsvpSuccessTitle.textContent = `${submission.guestName}，演示登记成功`; rsvpSuccessSummary.textContent = `已在本机保存 ${submission.partySize} 人的演示记录${submission.needsAccommodation ? ' · 已登记住宿需求' : ' · 无需住宿'}；这些内容不会上传。`; rsvpSuccess.focus({ preventScroll: true })
    } catch (error) { showRsvpError(error.message || '保存失败，请检查浏览器设置后重试。') }
    finally { rsvpSubmit.disabled = false; rsvpSubmit.querySelector('span').textContent = '保存赴约信息' }
  })
  document.querySelector('#rsvp-edit').addEventListener('click', () => { fillRsvp(savedRsvp); rsvpForm.hidden = false; rsvpSuccess.hidden = true })
  fillRsvp(savedRsvp)
}

/* ============================================================== 抽卡留念 */
// 卡池：新人做好的 8 张成品邀请卡（原图在 抽卡图片/，转码脚本 tools/build-cards.py）。
// 卡面本身已印好姓名、婚期、地点、日程，所以页面上整张显示，不再叠加卡名/稀有度文字；
// 每张只是照片不同，`name` 仅用于「上次你抽到的是…」这类文案。
const DRAW_CARDS = [
  { id: '01', name: '晨光之约', card: './assets/cards/card-01.webp' },
  { id: '02', name: '门前的花', card: './assets/cards/card-02.webp' },
  { id: '03', name: '黑幕之下', card: './assets/cards/card-03.webp' },
  { id: '04', name: '旧窗与烛', card: './assets/cards/card-04.webp' },
  { id: '05', name: '双喜临门', card: './assets/cards/card-05.webp' },
  { id: '06', name: '落满花瓣的裙摆', card: './assets/cards/card-06.webp' },
  { id: '07', name: '林间的伞', card: './assets/cards/card-07.webp' },
  { id: '08', name: '拱门与水晶灯', card: './assets/cards/card-08.webp' }
]
// 卡面下小铭牌上的纸鹤配色，按顺序循环
const CARD_TONES = ['sunset', 'brick', 'grass', 'road', 'ink']
const DRAW_STORAGE_KEY = 'journey-wedding-draw'

const drawLayer = document.querySelector('#draw-layer')
const drawStage = document.querySelector('#draw-stage')
const drawOpen = document.querySelector('#draw-open')
const drawSave = document.querySelector('#draw-save')
const drawAgain = document.querySelector('#draw-again')
const drawClose = document.querySelector('#draw-close')
const drawNote = document.querySelector('#draw-note')
const drawTitle = document.querySelector('#draw-title')
let drawnCard = null
let lastFocus = null

function readDrawState() {
  try { return JSON.parse(localStorage.getItem(DRAW_STORAGE_KEY)) || {} } catch { return {} }
}
function saveDrawState(state) {
  try { localStorage.setItem(DRAW_STORAGE_KEY, JSON.stringify(state)) } catch { /* 隐私模式下忽略 */ }
}
function pickCard() {
  const state = readDrawState()
  const pool = DRAW_CARDS.filter((card) => card.id !== state.lastId)
  const candidates = pool.length ? pool : DRAW_CARDS
  return candidates[Math.floor(Math.random() * candidates.length)]
}

function renderDrawBack() {
  drawStage.innerHTML = ''
  const back = document.createElement('button')
  back.type = 'button'; back.className = 'draw-back'; back.id = 'draw-back'
  back.setAttribute('aria-label', '翻开卡片')
  // 牌背中央是一枚真实折纸鹤图案（样式见 .draw-back span），不再用「鶴」字形
  const mark = document.createElement('span')
  mark.setAttribute('aria-hidden', 'true')
  back.append(mark)
  back.addEventListener('click', revealCard)
  drawStage.append(back)
}

function renderDrawCard(card) {
  drawStage.innerHTML = ''
  const figure = document.createElement('figure')
  figure.className = 'draw-card'
  figure.dataset.cardId = card.id

  const img = document.createElement('img')
  // card 已是成品卡面；兼容万一有旧数据只填了 image 的情况
  img.src = card.card || card.image
  img.alt = `婚礼邀请函卡片：${card.name}`
  figure.append(img)

  // 卡名小铭牌放在成品卡之外，不压在卡面上
  const plate = document.createElement('figcaption')
  plate.className = 'card-plate'
  const emblem = document.createElement('span')
  emblem.setAttribute('aria-hidden', 'true')
  emblem.dataset.tone = CARD_TONES[(Number(card.id) - 1) % CARD_TONES.length]
  plate.append(emblem, document.createTextNode(card.name))
  figure.append(plate)

  drawStage.append(figure)
}

function revealCard() {
  drawnCard = pickCard()
  renderDrawCard(drawnCard)
  // 记下这一张，下次打开还是它；但允许继续抽，方便挑一张最喜欢的
  saveDrawState({ lastId: drawnCard.id, count: 1 })
  drawSave.hidden = false
  drawNote.hidden = false
  drawNote.textContent = '存进相册，或者再抽一张 —— 选一张你最喜欢的。'
  drawTitle.textContent = '风把你的那一张吹来了'
  if (!reducedMotion) navigator.vibrate?.(30)
}

function openDraw() {
  lastFocus = document.activeElement
  const state = readDrawState()
  const seen = state.lastId ? DRAW_CARDS.find((card) => card.id === state.lastId) : null
  if (seen) {
    drawnCard = seen
    renderDrawCard(seen)
    drawSave.hidden = false; drawNote.hidden = false
    drawTitle.textContent = '你的那一张，还留着'
    drawNote.textContent = '想换一张就点「再抽一张」，选一张你最喜欢的。'
  } else {
    drawnCard = null
    renderDrawBack()
    drawSave.hidden = true; drawNote.hidden = true
    drawTitle.textContent = '风把你的那一张吹来了'
  }
  drawLayer.hidden = false
  document.body.style.overflow = 'hidden'
  const focusTarget = seen ? drawClose : drawStage.querySelector('.draw-back')
  focusTarget?.focus({ preventScroll: true })
}

function closeDraw() {
  drawLayer.hidden = true
  document.body.style.overflow = ''
  lastFocus?.focus?.({ preventScroll: true })
}

async function saveDrawnCard() {
  if (!drawnCard) return
  const source = drawnCard.card || drawnCard.image
  drawSave.disabled = true
  drawSave.textContent = '正在准备图片……'
  try {
    const response = await fetch(source, { mode: 'cors' })
    if (!response.ok) throw new Error('fetch failed')
    const blob = await response.blob()
    const file = new File([blob], `invitation-card-${drawnCard.id}.png`, { type: blob.type })
    if (navigator.canShare?.({ files: [file] })) {
      await navigator.share({ files: [file], title: '风之旅 · 我们的婚礼', text: `我的邀请函卡片：${drawnCard.name}` })
      return
    }
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url; link.download = file.name
    document.body.append(link); link.click(); link.remove()
    window.setTimeout(() => URL.revokeObjectURL(url), 4000)
  } catch {
    drawNote.textContent = '图片没法直接保存，长按卡片图片也能存进相册。'
    drawNote.hidden = false
  } finally {
    drawSave.disabled = false
    drawSave.textContent = '保存到相册'
  }
}

drawOpen.addEventListener('click', openDraw)
drawClose.addEventListener('click', closeDraw)
// 「保存到相册」只负责存图；抽到哪一张在揭示时记下，但不限制继续抽
drawSave.addEventListener('click', saveDrawnCard)
drawAgain.addEventListener('click', () => {
  if (!drawnCard) return
  revealCard()
})
drawLayer.addEventListener('click', (event) => { if (event.target === drawLayer) closeDraw() })
document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !drawLayer.hidden) closeDraw() })
