import { execFileSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { join } from 'node:path'

const PYTHON = 'python3'
const SCRIPT = join(fileURLToPath(new URL('..', import.meta.url)), 'scripts', 'mcp_server.py')

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
    const out = execFileSync(PYTHON, [SCRIPT], { input: req, encoding: 'utf-8', timeout: 15000 })
    const res = JSON.parse(out)
    return res.result?.content?.[0]?.text || '无返回内容'
  } catch (err) {
    return `执行出错: ${err.message}`
  }
}

export const searchHighlightsTool = {
  name: 'reading_search_highlights',
  description: '在用户的 Apple Books 与本地电子书库的 4,400+ 条真实划线中检索关键词或概念碰撞（如搜“放下”、“周期”、“估值”、“本质”、“不确定性”等）。',
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
      book_title: str('书名关键词，如“金刚经白话”、“估值原理”、“最初和最终的自由”')
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
