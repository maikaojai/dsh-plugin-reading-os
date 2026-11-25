import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { join } from 'node:path'
import { existsSync, readFileSync } from 'node:fs'
import { homedir } from 'node:os'

const SCRIPT = join(fileURLToPath(new URL('..', import.meta.url)), 'scripts', 'mcp_server.py')
const CONFIG_PATH = join(homedir(), '.dsh', 'reading-os.config.json')

function loadUserPathEnv() {
  try {
    if (!existsSync(CONFIG_PATH)) return {}
    const cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'))
    const extra = {}
    if (cfg.booksDir && existsSync(cfg.booksDir)) extra.READING_OS_BOOKS_DIR = cfg.booksDir
    if (cfg.customDb && existsSync(cfg.customDb)) extra.READING_OS_APPLE_BOOKS_DIR = cfg.customDb
    return extra
  } catch {
    return {}
  }
}

// 自动探测 macOS / Linux 环境下可靠的 python3 解释器 (避免 GUI 启动缺失 Homebrew PATH)
function resolvePythonPath() {
  const candidates = [
    '/opt/homebrew/bin/python3',
    '/usr/local/bin/python3',
    '/usr/bin/python3',
    'python3'
  ]
  for (const p of candidates) {
    if (p.startsWith('/') && existsSync(p)) {
      return p
    }
  }
  return 'python3'
}

const PYTHON = resolvePythonPath()

// 补齐系统 PATH，确保在 GUI 启动的 DSH 中能够无阻调用 Python 模块
const enrichedPath = [
  '/opt/homebrew/bin',
  '/opt/homebrew/sbin',
  '/usr/local/bin',
  '/usr/bin',
  '/bin',
  '/usr/sbin',
  '/sbin',
  process.env.PATH || ''
].filter(Boolean).join(':')

const str = (description, extra = {}) => ({ type: 'string', description, ...extra })
const text = (value) => [{ type: 'text', text: value }]

function callMcp(name, args = {}) {
  try {
    const req = JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/call',
      params: { name, arguments: args }
    }) + '\n'
    const out = execFileSync(PYTHON, [SCRIPT], {
      input: req,
      encoding: 'utf-8',
      timeout: 15000,
      env: {
        ...process.env,
        ...loadUserPathEnv(),
        PATH: enrichedPath,
        PYTHONIOENCODING: 'utf-8'
      }
    })
    const res = JSON.parse(out)
    return res.result?.content?.[0]?.text || '无返回内容'
  } catch (err) {
    return `执行出错: ${err.message}`
  }
}

export const searchHighlightsTool = {
  name: 'reading_search_highlights',
  description: '在用户的 Apple Books 与本地电子书库的真实划线中检索关键词或概念碰撞（如搜“放下”、“周期”、“本质”、“不确定性”等）。',
  parameters: {
    type: 'object',
    required: ['keyword'],
    properties: {
      keyword: str('检索关键词')
    }
  },
  output: {
    schema: { type: 'object', properties: { text: { type: 'string' } } },
    render: (_args, v) => text(v.text),
  },
  async execute(args) {
    const res = callMcp('search_highlights', { keyword: args.keyword })
    return { text: res }
  }
}

export const getOverviewTool = {
  name: 'reading_get_overview',
  description: '获取用户的整体阅读操作系统大盘数据（藏书量、已读精读数、近30天下载、四大维度权重分布等）。',
  parameters: {
    type: 'object',
    properties: {}
  },
  output: {
    schema: { type: 'object', properties: { text: { type: 'string' } } },
    render: (_args, v) => text(v.text),
  },
  async execute() {
    const res = callMcp('get_reading_overview', {})
    return { text: res }
  }
}

export const getConceptNetworkTool = {
  name: 'reading_get_concept_network',
  description: '获取跨书核心主题网络（如“放下与破执”、“本质与底层”、“风险与期权”、“规律与辩证”、“知行与实践”、“自由与觉察”），返回多书并列观点对比。',
  parameters: {
    type: 'object',
    properties: {
      concept_id: str('概念ID：detachment, essence, uncertainty, law_dialectic, action_practice, freedom。留空则返回所有概念。')
    }
  },
  output: {
    schema: { type: 'object', properties: { text: { type: 'string' } } },
    render: (_args, v) => text(v.text),
  },
  async execute(args) {
    const res = callMcp('get_concept_network', { concept_id: args.concept_id || '' })
    return { text: res }
  }
}

export const getBookHighlightsTool = {
  name: 'reading_get_book_highlights',
  description: '获取指定书籍在 Apple Books 中的所有划线高亮与阅读进度。',
  parameters: {
    type: 'object',
    required: ['book_title'],
    properties: {
      book_title: str('要查询的书名关键词')
    }
  },
  output: {
    schema: { type: 'object', properties: { text: { type: 'string' } } },
    render: (_args, v) => text(v.text),
  },
  async execute(args) {
    const res = callMcp('get_book_highlights', { book_title: args.book_title })
    return { text: res }
  }
}

export const TOOLS = [
  searchHighlightsTool,
  getOverviewTool,
  getConceptNetworkTool,
  getBookHighlightsTool
]
