'use client'

import { useState } from 'react'
import { Project } from '@/lib/types'
import { createShareLink, getShareUrl, ShareLink } from '@/lib/services/share-service'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Copy, Link, Check, Loader2 } from 'lucide-react'

interface ShareDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  project: Project | null
}

export function ShareDialog({ open, onOpenChange, project }: ShareDialogProps) {
  const [expiresInDays, setExpiresInDays] = useState(7)
  const [shareLink, setShareLink] = useState<ShareLink | null>(null)
  const [shareUrl, setShareUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerateLink = async () => {
    if (!project) return

    setIsLoading(true)
    setError(null)
    try {
      const response = await createShareLink(project.id, { expiresInDays })
      if (response.success && response.data) {
        setShareLink(response.data)
        setShareUrl(getShareUrl(response.data.token))
      } else {
        setError(response.message || 'Erro ao gerar link')
      }
    } catch {
      setError('Não foi possível gerar o link')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopyLink = async () => {
    await navigator.clipboard.writeText(shareUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleClose = (open: boolean) => {
    if (!open) {
      setShareLink(null)
      setShareUrl('')
      setError(null)
      setCopied(false)
    }
    onOpenChange(open)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>Compartilhar Projeto</DialogTitle>
          <DialogDescription>
            Gere um link temporário para compartilhar o planejamento do projeto.
            Qualquer pessoa com o link poderá visualizar o Gantt.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded">
              {error}
            </div>
          )}

          {!shareLink ? (
            <>
              <div className="space-y-2">
                <Label htmlFor="expires">Validade do link (dias)</Label>
                <Input
                  id="expires"
                  type="number"
                  min={1}
                  max={30}
                  value={expiresInDays}
                  onChange={(e) => setExpiresInDays(Number(e.target.value))}
                />
                <p className="text-xs text-muted-foreground">
                  O link expirará automaticamente após {expiresInDays} dia{expiresInDays > 1 ? 's' : ''}.
                </p>
              </div>
              <Button onClick={handleGenerateLink} disabled={isLoading} className="w-full">
                {isLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Link className="h-4 w-4 mr-2" />
                )}
                {isLoading ? 'Gerando...' : 'Gerar Link'}
              </Button>
            </>
          ) : (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Link de compartilhamento</Label>
                <div className="flex gap-2">
                  <Input value={shareUrl} readOnly className="flex-1 text-sm" />
                  <Button onClick={handleCopyLink} variant="outline" size="icon">
                    {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                Expira em: {new Date(shareLink.expiresAt).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
              <Button
                variant="outline"
                onClick={() => setShareLink(null)}
                className="w-full"
              >
                Gerar Novo Link
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
