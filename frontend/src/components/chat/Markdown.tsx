import React, { useState } from 'react'

type MarkdownProps = {
  content: string
}

export const Markdown = ({ content }: MarkdownProps) => {
  if (!content) return null

  // Split content by ``` to isolate code blocks
  const parts = content.split('```')

  return (
    <div className="markdown-body">
      {parts.map((part, index) => {
        const isCodeBlock = index % 2 === 1
        if (isCodeBlock) {
          return <CodeBlock key={index} rawContent={part} />
        } else {
          return <TextBlock key={index} rawContent={part} />
        }
      })}
    </div>
  )
}

// Sub-component for rendering Code Blocks
type CodeBlockProps = {
  rawContent: string
}

const CodeBlock = ({ rawContent }: CodeBlockProps) => {
  const [copied, setCopied] = useState(false)

  // Extract language from first line (e.g. ```typescript\n)
  const firstNewlineIndex = rawContent.indexOf('\n')
  let language = 'code'
  let code = rawContent

  if (firstNewlineIndex !== -1) {
    const possibleLang = rawContent.substring(0, firstNewlineIndex).trim()
    if (possibleLang && possibleLang.length < 15) {
      language = possibleLang
      code = rawContent.substring(firstNewlineIndex + 1)
    }
  }

  // Remove trailing newline if present
  code = code.replace(/\n$/, '')

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy code: ', err)
    }
  }

  // Simple token highlighter for premium visual appearance
  const highlightCode = (txt: string, lang: string) => {
    const lines = txt.split('\n')
    return lines.map((line, lineIdx) => {
      // Basic syntax coloring regexes (extremely lightweight but works well visually)
      if (lang === 'typescript' || lang === 'javascript' || lang === 'js' || lang === 'ts' || lang === 'json') {
        const parts = line.split(/(\/\/.*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`[^`]*`|\b(?:const|let|var|function|return|export|import|from|class|interface|type|extends|if|else|for|while|async|await|true|false|null|undefined|string|number|boolean|void)\b)/)
        return (
          <div key={lineIdx} className="code-line">
            {parts.map((chunk, chunkIdx) => {
              if (chunk.startsWith('//')) {
                return <span key={chunkIdx} className="code-token-comment">{chunk}</span>
              }
              if ((chunk.startsWith('"') && chunk.endsWith('"')) || (chunk.startsWith("'") && chunk.endsWith("'")) || (chunk.startsWith('`') && chunk.endsWith('`'))) {
                return <span key={chunkIdx} className="code-token-string">{chunk}</span>
              }
              if (/^(const|let|var|function|return|export|import|from|class|interface|type|extends|if|else|for|while|async|await|true|false|null|undefined|string|number|boolean|void)$/.test(chunk)) {
                return <span key={chunkIdx} className="code-token-keyword">{chunk}</span>
              }
              return chunk
            })}
          </div>
        )
      }
      if (lang === 'python' || lang === 'py') {
        const parts = line.split(/(#.*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:def|class|return|import|from|as|if|elif|else|for|in|while|try|except|True|False|None|print|self)\b)/)
        return (
          <div key={lineIdx} className="code-line">
            {parts.map((chunk, chunkIdx) => {
              if (chunk.startsWith('#')) {
                return <span key={chunkIdx} className="code-token-comment">{chunk}</span>
              }
              if ((chunk.startsWith('"') && chunk.endsWith('"')) || (chunk.startsWith("'") && chunk.endsWith("'"))) {
                return <span key={chunkIdx} className="code-token-string">{chunk}</span>
              }
              if (/^(def|class|return|import|from|as|if|elif|else|for|in|while|try|except|True|False|None|print|self)$/.test(chunk)) {
                return <span key={chunkIdx} className="code-token-keyword">{chunk}</span>
              }
              return chunk
            })}
          </div>
        )
      }
      return <div key={lineIdx} className="code-line">{line}</div>
    })
  }

  return (
    <div className="code-block-container">
      <div className="code-block-header">
        <span className="code-block-lang">{language.toUpperCase()}</span>
        <button type="button" className="code-block-copy-btn" onClick={handleCopy}>
          {copied ? '✅ Copied!' : '📋 Copy'}
        </button>
      </div>
      <pre className="code-block-body">
        <code>{highlightCode(code, language)}</code>
      </pre>
    </div>
  )
}

// Sub-component for rendering paragraphs, headings, lists, tables, etc.
type TextBlockProps = {
  rawContent: string
}

const TextBlock = ({ rawContent }: TextBlockProps) => {
  // Split on double newlines to find paragraphs
  const paragraphs = rawContent.split(/\n\n+/)

  // Group list items that are consecutive
  const renderedElements: React.ReactNode[] = []

  let listBuffer: { type: 'ul' | 'ol'; items: string[] } | null = null

  const flushList = (keyPrefix: number) => {
    if (listBuffer) {
      const ListTag = listBuffer.type
      renderedElements.push(
        <ListTag key={`list-${keyPrefix}`} className="markdown-list">
          {listBuffer.items.map((item, idx) => (
            <li key={idx}>{renderInline(item)}</li>
          ))}
        </ListTag>
      )
      listBuffer = null
    }
  }

  paragraphs.forEach((p, pIdx) => {
    const trimmed = p.trim()
    if (!trimmed) return

    // If it's a line-by-line block, let's parse individual lines
    const lines = p.split('\n')

    // Determine if this paragraph is a table
    const isTable = lines.length >= 2 && lines.every(l => l.trim().startsWith('|')) && lines[1].includes('-')
    if (isTable) {
      flushList(pIdx)
      renderedElements.push(<TableBlock key={`table-${pIdx}`} lines={lines} />)
      return
    }

    let isListBlock = false
    lines.forEach((line, lIdx) => {
      const lineTrim = line.trim()
      const ulMatch = lineTrim.match(/^[*+-]\s+(.*)/)
      const olMatch = lineTrim.match(/^(\d+)\.\s+(.*)/)

      if (ulMatch) {
        isListBlock = true
        if (!listBuffer || listBuffer.type !== 'ul') {
          flushList(pIdx + lIdx)
          listBuffer = { type: 'ul', items: [] }
        }
        listBuffer.items.push(ulMatch[1])
      } else if (olMatch) {
        isListBlock = true
        if (!listBuffer || listBuffer.type !== 'ol') {
          flushList(pIdx + lIdx)
          listBuffer = { type: 'ol', items: [] }
        }
        listBuffer.items.push(olMatch[2])
      } else {
        // Line is not a list item. Flush any existing list first
        if (listBuffer) {
          flushList(pIdx + lIdx)
        }

        // Process individual headers, blockquotes, or paragraphs
        if (lineTrim.startsWith('# ')) {
          renderedElements.push(<h1 key={`h1-${pIdx}-${lIdx}`}>{renderInline(lineTrim.substring(2))}</h1>)
        } else if (lineTrim.startsWith('## ')) {
          renderedElements.push(<h2 key={`h2-${pIdx}-${lIdx}`}>{renderInline(lineTrim.substring(3))}</h2>)
        } else if (lineTrim.startsWith('### ')) {
          renderedElements.push(<h3 key={`h3-${pIdx}-${lIdx}`}>{renderInline(lineTrim.substring(4))}</h3>)
        } else if (lineTrim.startsWith('#### ')) {
          renderedElements.push(<h4 key={`h4-${pIdx}-${lIdx}`}>{renderInline(lineTrim.substring(5))}</h4>)
        } else if (lineTrim.startsWith('> ')) {
          renderedElements.push(
            <blockquote key={`quote-${pIdx}-${lIdx}`} className="markdown-quote">
              {renderInline(lineTrim.substring(2))}
            </blockquote>
          )
        } else if (lineTrim) {
          renderedElements.push(<p key={`p-${pIdx}-${lIdx}`}>{renderInline(lineTrim)}</p>)
        }
      }
    })

    if (!isListBlock) {
      flushList(pIdx)
    }
  })

  // Final flush of list items
  flushList(paragraphs.length)

  return <>{renderedElements}</>
}

// Table rendering helper
type TableBlockProps = {
  lines: string[]
}

const TableBlock = ({ lines }: TableBlockProps) => {
  // Parse rows
  const parseRow = (line: string) => {
    return line
      .split('|')
      .slice(1, -1) // remove leading and trailing empty items from outer pipes
      .map(cell => cell.trim())
  }

  const headerCells = parseRow(lines[0])
  const bodyRows = lines.slice(2).map(parseRow) // Skip header (index 0) and separator line (index 1)

  return (
    <div className="table-wrapper">
      <table className="markdown-table">
        <thead>
          <tr>
            {headerCells.map((header, idx) => (
              <th key={idx}>{renderInline(header)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bodyRows.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {row.map((cell, cellIdx) => (
                <td key={cellIdx}>{renderInline(cell)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// Regex parser to render inline elements recursively as React Nodes
const renderInline = (text: string): React.ReactNode[] => {
  if (!text) return []

  // Split on inline code blocks `code`
  const codeParts = text.split(/(`[^`]+`)/g)

  return codeParts.map((part, index) => {
    const isInlineCode = part.startsWith('`') && part.endsWith('`')
    if (isInlineCode) {
      const codeVal = part.substring(1, part.length - 1)
      return <code key={index} className="inline-code">{codeVal}</code>
    }

    // Now split on bold elements **bold**
    const boldParts = part.split(/(\*\*[^*]+\*\*)/g)
    return (
      <React.Fragment key={index}>
        {boldParts.map((bPart, bIdx) => {
          const isBold = bPart.startsWith('**') && bPart.endsWith('**')
          if (isBold) {
            const boldVal = bPart.substring(2, bPart.length - 2)
            return <strong key={bIdx}>{boldVal}</strong>
          }

          // Now split on italic elements *italic*
          const italicParts = bPart.split(/(\*[^*]+\*)/g)
          return (
            <React.Fragment key={bIdx}>
              {italicParts.map((iPart, iIdx) => {
                const isItalic = iPart.startsWith('*') && iPart.endsWith('*')
                if (isItalic) {
                  const italicVal = iPart.substring(1, iPart.length - 1)
                  return <em key={iIdx}>{italicVal}</em>
                }
                return iPart
              })}
            </React.Fragment>
          )
        })}
      </React.Fragment>
    )
  })
}
