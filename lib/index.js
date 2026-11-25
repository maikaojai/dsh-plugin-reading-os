import { createReadStream, existsSync, statSync } from 'node:fs'
import { extname, isAbsolute, join, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'
import { TOOLS } from './tools.js'

const ROOT = fileURLToPath(new URL('..', import.meta.url))
const DASHBOARD_ROOT = resolve(ROOT, 'dashboard')
const BASE = '/reading-os'
const DATA_FETCHER = join(ROOT, 'scripts', 'data_fetcher.py')

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
}

export const name = 'reading-os'
export const inject = ['webServer', 'tools']

function serveFile(req, res, file) {
  const type = MIME[extname(file).toLowerCase()] || 'application/octet-stream'
  res.writeHead(200, { 'content-type': type, 'content-length': statSync(file).size, 'cache-control': 'no-cache' })
  if (req.method === 'HEAD') return res.end()
  createReadStream(file).pipe(res)
}

const PYTHON_BIN = ['/opt/homebrew/bin/python3', '/usr/local/bin/python3', '/usr/bin/python3'].find(p => existsSync(p)) || 'python3'

// DSH 宿主访问鉴权与防跨站请求检查 (防止外部恶意网页跨站调用本地路由)
function checkDshAccess(ctx, req, res) {
  const connection = typeof ctx.get === 'function' ? ctx.get('connection') : ctx.connection
  const gate = connection?.requestRejection
  if (typeof gate === 'function') {
    let status
    try {
      status = gate.call(connection, req)
    } catch {
      status = 403
    }
    if (status !== undefined) {
      res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
      res.end(JSON.stringify({ error: status === 401 ? 'DSH login required' : 'Untrusted request origin' }))
      return false
    }
  }

  if (req.headers['sec-fetch-site'] === 'cross-site') {
    res.writeHead(403, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
    res.end(JSON.stringify({ error: 'Cross-site request forbidden' }))
    return false
  }

  const origin = req.headers.origin
  const host = req.headers.host
  if (origin !== undefined) {
    if (origin === 'null' || origin === '') {
      res.writeHead(403, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
      res.end(JSON.stringify({ error: 'Untrusted origin' }))
      return false
    }
    try {
      const originUrl = new URL(origin)
      const isDshApp = originUrl.protocol === 'dsh-app:'
      const isSameHost = host && originUrl.host === host
      const isLoopback = ['127.0.0.1', 'localhost', '[::1]'].includes(originUrl.hostname)
      if (!isDshApp && !isSameHost && !isLoopback) {
        res.writeHead(403, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
        res.end(JSON.stringify({ error: 'Cross-origin request forbidden' }))
        return false
      }
    } catch {
      res.writeHead(403, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
      res.end(JSON.stringify({ error: 'Invalid origin' }))
      return false
    }
  }

  return true
}

function getFreshData(customEnv = {}) {
  try {
    const stdout = execFileSync(PYTHON_BIN, [DATA_FETCHER], {
      encoding: 'utf-8',
      timeout: 25000,
      maxBuffer: 50 * 1024 * 1024,
      env: { 
        ...process.env, 
        ...customEnv,
        PATH: '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:' + (process.env.PATH || '') 
      }
    })
    return JSON.parse(stdout)
  } catch (e) {
    console.error('[reading-os] 获取最新阅读数据失败:', e)
    return { error: e.message }
  }
}

export function apply(ctx) {
  // 注册给模型的四个阅读认知工具
  if (ctx.tools && ctx.tools.register) {
    for (const tool of TOOLS) {
      try {
        ctx.tools.register(tool)
      } catch (e) {
        console.error('[reading-os] 注册工具失败:', tool.name, e)
      }
    }
  }

  // 挂载 /reading-os/ 路由，供侧栏点击时的主面板 iframe 访问
  if (ctx.webServer && ctx.webServer.register) {
    ctx.effect(() =>
      ctx.webServer.register({
        kind: 'prefix',
        path: BASE,
        async handler(req, res) {
          if (!checkDshAccess(ctx, req, res)) return
          const url = new URL(req.url || '/', 'http://x')
          let rest = decodeURIComponent(url.pathname.slice(BASE.length)) || '/'
          
          // API: 动态拉取与刷新数据
          if (rest === '/api/sync' || rest === '/api/data') {
            const customEnv = {}
            const booksDir = url.searchParams.get('booksDir')
            const customDb = url.searchParams.get('customDb')
            const isValidLocalPath = (p, expectDir) => {
              if (!p || typeof p !== 'string' || p.includes('\0') || !isAbsolute(p)) return false
              try {
                if (!existsSync(p)) return false
                const st = statSync(p)
                return expectDir ? st.isDirectory() : (st.isDirectory() || st.isFile())
              } catch {
                return false
              }
            }
            if (booksDir && !isValidLocalPath(booksDir, true)) {
              res.writeHead(400, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
              return res.end(JSON.stringify({ error: '无效的电子书目录路径，请检查目录是否存在' }))
            }
            if (customDb && !isValidLocalPath(customDb, false)) {
              res.writeHead(400, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
              return res.end(JSON.stringify({ error: '无效的数据库路径，请检查路径是否存在' }))
            }
            if (booksDir) customEnv.READING_OS_BOOKS_DIR = resolve(booksDir)
            if (customDb) customEnv.READING_OS_APPLE_BOOKS_DIR = resolve(customDb)

            const data = getFreshData(customEnv)
            res.writeHead(200, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
            return res.end(JSON.stringify(data))
          }

          if (rest === '' || rest === '/') rest = '/index.html'
          const relPath = rest.startsWith('/') ? rest.slice(1) : rest
          const filePath = resolve(DASHBOARD_ROOT, relPath)
          if (!filePath.startsWith(DASHBOARD_ROOT + sep)) {
            res.writeHead(403, { 'content-type': 'text/plain; charset=utf-8' })
            return res.end('Forbidden')
          }
          if (existsSync(filePath) && statSync(filePath).isFile()) {
            return serveFile(req, res, filePath)
          }
          res.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' })
          res.end('Not Found: ' + rest)
        }
      })
    )
  }
}
