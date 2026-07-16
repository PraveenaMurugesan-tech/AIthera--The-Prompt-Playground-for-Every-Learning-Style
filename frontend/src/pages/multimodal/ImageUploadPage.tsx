import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '../../components/common/Card'
import { Button } from '../../components/common/Button'
import { ImageUpload, type UploadedFile } from '../../components/multimodal/ImageUpload'

export const ImageUploadPage = () => {
  const navigate = useNavigate()
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleFilesChange = (filesList: UploadedFile[]) => {
    setUploadedFiles(filesList)
    // Clear previous analysis if files are cleared or changed
    if (filesList.length === 0) {
      setAnalysisResult(null)
    }
  }

  const handleAnalyze = () => {
    if (uploadedFiles.length === 0) return

    setIsAnalyzing(true)
    setAnalysisResult(null)

    // Simulate Vision / OCR analysis processing
    setTimeout(() => {
      const fileNames = uploadedFiles.map(f => f.name).join(', ')
      
      // Construct a dynamic premium simulated prompt extracted from image context
      let extractedTopic = 'Algorithms & Data Structures'
      if (fileNames.toLowerCase().includes('react') || fileNames.toLowerCase().includes('js') || fileNames.toLowerCase().includes('html')) {
        extractedTopic = 'Frontend Web Architecture'
      } else if (fileNames.toLowerCase().includes('python') || fileNames.toLowerCase().includes('django') || fileNames.toLowerCase().includes('flask')) {
        extractedTopic = 'Backend Python Rest API'
      } else if (fileNames.toLowerCase().includes('sql') || fileNames.toLowerCase().includes('database') || fileNames.toLowerCase().includes('schema')) {
        extractedTopic = 'Database Relational Schema Design'
      }

      const generatedAnalysis = `### 👁️ AI Vision Analysis Report

**Analyzed Attachments:** ${fileNames}
**Extracted Concept Focus:** \`${extractedTopic}\`

---

#### 📝 Extracted Learning Challenge Prompt:
> "Please start a comprehensive learning session focused on **${extractedTopic}**. Provide a structural overview explaining the core architectural boundaries, list 3 common pitfalls experienced by intermediate developers, and write a boilerplate code sample demonstrating a production-grade implementation."

*Vision OCR Confidence: 96.8% (Mock Vision Processor)*`
      
      setAnalysisResult(generatedAnalysis)
      setIsAnalyzing(false)
    }, 1800)
  }

  const handleSendToChat = () => {
    if (!analysisResult) return
    
    // Extract topic name for the chat title
    const topicMatch = analysisResult.match(/Focus:\*\* `([^`]+)`/)
    const topic = topicMatch ? topicMatch[1] : 'Image Upload Session'

    navigate('/chat', {
      state: {
        initialPrompt: analysisResult,
        topic: topic,
        learningStyle: 'visual',
        difficulty: 'intermediate'
      }
    })
  }

  const handleSendToWorkspace = () => {
    if (!analysisResult) return

    // Extract focus topic
    const topicMatch = analysisResult.match(/Focus:\*\* `([^`]+)`/)
    const topic = topicMatch ? topicMatch[1] : 'Image Analysis Topic'

    navigate('/workspace', {
      state: {
        prefilledTopic: topic,
        prefilledStyle: 'visual'
      }
    })
  }

  const handleCopyText = async () => {
    if (!analysisResult) return
    try {
      await navigator.clipboard.writeText(analysisResult)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  // Count active uploaded files that are ready for analysis
  const readyFiles = uploadedFiles.filter(f => f.status === 'success')

  return (
    <div className="multimodal-page-container">
      <div className="multimodal-page-header">
        <h1>🖼️ Multimodal Image Playground</h1>
        <p className="muted">
          Enable camera or drag layouts/diagrams here to extract structured prompt templates.
        </p>
      </div>

      <div className="multimodal-page-grid">
        <div className="upload-section-col">
          <Card>
            <ImageUpload onChange={handleFilesChange} />
            
            <div className="analyze-actions-row" style={{ marginTop: '1.25rem' }}>
              <Button
                onClick={handleAnalyze}
                disabled={readyFiles.length === 0 || isAnalyzing}
                style={{ width: '100%', justifyContent: 'center' }}
              >
                {isAnalyzing ? '👁️ Analyzing Image Context...' : '✨ Analyze & Extract Prompt'}
              </Button>
            </div>
          </Card>
        </div>

        <div className="analysis-section-col">
          <Card title="Vision Output" subtitle="Extracted OCR prompt templates will show up here.">
            {isAnalyzing ? (
              <div className="workspace-loading" style={{ minHeight: '12rem', justifyContent: 'center', alignItems: 'center' }}>
                <div className="loading-orb">
                  <div className="loading-orb-core" />
                </div>
                <h4 style={{ marginTop: '1rem' }}>Extracting text schemas...</h4>
                <p className="muted text-xs">Simulating OCR structure mapping...</p>
              </div>
            ) : analysisResult ? (
              <div className="vision-result-layout animate-fade-in">
                <div className="extracted-text-area">
                  {/* Clean preview box */}
                  <div className="vision-markdown-rendered">
                    <pre className="vision-raw-text">
                      <code>{analysisResult}</code>
                    </pre>
                  </div>
                </div>

                <div className="vision-dispatch-actions">
                  <Button onClick={handleSendToChat} variant="primary">
                    💬 Send to Chat
                  </Button>
                  <Button onClick={handleSendToWorkspace} variant="secondary">
                    ✨ Send to Workspace
                  </Button>
                  <Button onClick={handleCopyText} variant="secondary">
                    {copied ? '✅ Copied!' : '📋 Copy Text'}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="workspace-empty-state" style={{ minHeight: '12rem', justifyContent: 'center', alignItems: 'center' }}>
                <div className="empty-state-icon">🖼️</div>
                <h4>No analysis generated yet</h4>
                <p className="muted text-xs">Upload an image or take a photo, then click Analyze.</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
export default ImageUploadPage
