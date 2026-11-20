// ReadingOS · DeepSeek Harness 插件：客户端侧栏与主面板
window.__ModuleLoader__.load({
  id: 'dsh-plugin-reading-os',
  factory: (require) => {
    var module = { exports: {} }
    var exports = module.exports
    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' })

    const React = require('react')
    const h = React.createElement
    const PANEL = 'reading-os'
    const SRC = '/reading-os/'

    // 侧栏图标：一本翻开的书
    function ReadingIcon(props) {
      const s = (props && props.size) || 18
      return h('svg', {
        width: s,
        height: s,
        viewBox: '0 0 24 24',
        fill: 'none',
        stroke: 'currentColor',
        strokeWidth: 1.6,
        strokeLinecap: 'round',
        strokeLinejoin: 'round'
      },
        h('path', { d: 'M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z' }),
        h('path', { d: 'M6 6h10' }),
        h('path', { d: 'M6 10h10' }),
        h('path', { d: 'M6 14h6' })
      )
    }

    function apply(ctx) {
      const LABEL = { zh: 'ReadingOS 读书', en: 'ReadingOS' }

      function ReadingPanel() {
        const ref = React.useRef(null)
        React.useEffect(() => {
          function onMessage(e) {
            const frame = ref.current
            if (!frame || e.source !== frame.contentWindow) return
            const m = e.data
            if (!m || m.type !== 'reading-os:start' || typeof m.prompt !== 'string') return
            try {
              if (ctx.uiWorkspace && ctx.uiWorkspace.startSession) {
                ctx.uiWorkspace.startSession(undefined, { prompt: m.prompt, whenDraftExists: 'replace' })
              }
            } catch (err) {
              console.error('[reading-os] 开启深度研读对话失败:', err)
            }
          }
          addEventListener('message', onMessage)
          return () => removeEventListener('message', onMessage)
        }, [])

        return h('iframe', {
          ref,
          src: SRC,
          title: LABEL.zh,
          allow: 'clipboard-write; clipboard-read',
          style: { width: '100%', height: '100%', border: 0, display: 'block', backgroundColor: 'transparent' }
        })
      }

      ctx.slots.inject('sidebar.panellist', () =>
        ctx.slots.register({ name: 'sidebar.panellist', id: PANEL, order: 8, label: () => LABEL.zh }, ReadingIcon))
      ctx.slots.inject('main', () => ctx.slots.register({ name: 'main', key: PANEL }, ReadingPanel))
    }

    exports.isPlugin = true
    exports.inject = ['slots', 'uiWorkspace']
    exports.apply = apply
    return module.exports
  },
})
