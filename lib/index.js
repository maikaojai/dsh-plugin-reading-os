import { createReadStream, existsSync, statSync } from 'node:fs'
import { extname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFileSync } from 'node:child_process'
import { TOOLS } from './tools.js'

const ROOT = fileURLToPath(new URL('..', import.meta.url))
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

function getFreshData() {
  try {
    const stdout = execFileSync('python3', [DATA_FETCHER], { encoding: 'utf-8', timeout: 15000 })
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
          const url = new URL(req.url || '/', 'http://x')
          let rest = decodeURIComponent(url.pathname.slice(BASE.length)) || '/'
          
          // API: 动态拉取与刷新数据
          if (rest === '/api/sync' || rest === '/api/data') {
            const data = getFreshData()
            res.writeHead(200, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' })
            return res.end(JSON.stringify(data))
          }

          if (rest === '' || rest === '/') rest = '/index.html'
          const filePath = join(ROOT, 'dashboard', rest.startsWith('/') ? rest.slice(1) : rest)
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
