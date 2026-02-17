'use client'

import Link from 'next/link'
import {
  GanttChart, Users, ShieldCheck, Moon, ArrowRight,
  CheckCircle2, BarChart3, Clock, Layers
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const features = [
  {
    icon: GanttChart,
    title: 'Gráfico Gantt Interativo',
    description: 'Visualize cronogramas, dependências e progresso de tarefas em tempo real com visualizações por dia, semana ou mês.',
  },
  {
    icon: Users,
    title: 'Gestão de Equipe',
    description: 'Gerencie membros, departamentos e cargos. Acompanhe quem está ativo, ausente ou disponível.',
  },
  {
    icon: ShieldCheck,
    title: 'Controle de Permissões',
    description: 'Quatro níveis de acesso — Admin, Gerente, Membro e Visualizador — cada um com permissões específicas.',
  },
  {
    icon: Moon,
    title: 'Tema Personalizável',
    description: 'Tema claro, escuro ou automático. Modo compacto e preferências que se aplicam em toda a plataforma.',
  },
]

const stats = [
  { value: 'Gantt', label: 'Visualização interativa' },
  { value: '4', label: 'Níveis de permissão' },
  { value: '100%', label: 'Responsivo' },
  { value: 'PT-BR', label: 'Totalmente em português' },
]

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-primary flex items-center justify-center">
              <GanttChart className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="font-bold text-xl">ProjectFlow</span>
          </Link>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link href="/login">Entrar</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Cadastrar</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 sm:py-32">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
            <Layers className="h-4 w-4" />
            Plataforma de Gestão de Projetos
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight max-w-3xl mx-auto leading-tight">
            Gerencie seus projetos com{' '}
            <span className="text-primary">visão total</span>
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            Cronogramas Gantt interativos, controle de equipe e permissões avançadas.
            Tudo o que você precisa para entregar projetos no prazo.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button size="lg" className="gap-2 text-base px-8" asChild>
              <Link href="/register">
                Começar Grátis
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-base px-8" asChild>
              <Link href="/login">Já tenho conta</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="pb-20">
        <div className="max-w-5xl mx-auto px-6">
          <div className="rounded-xl border border-border bg-card shadow-2xl overflow-hidden">
            {/* Fake browser bar */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-muted/50">
              <div className="flex gap-1.5">
                <div className="h-3 w-3 rounded-full bg-red-400" />
                <div className="h-3 w-3 rounded-full bg-yellow-400" />
                <div className="h-3 w-3 rounded-full bg-green-400" />
              </div>
              <div className="flex-1 flex justify-center">
                <div className="px-4 py-1 rounded-md bg-background text-xs text-muted-foreground border border-border">
                  projectflow.app/dashboard
                </div>
              </div>
            </div>
            {/* Fake dashboard */}
            <div className="flex">
              {/* Sidebar mock */}
              <div className="w-48 border-r border-border bg-muted/30 p-4 hidden sm:block">
                <div className="flex items-center gap-2 mb-6">
                  <div className="h-7 w-7 rounded-md bg-primary flex items-center justify-center">
                    <GanttChart className="h-4 w-4 text-primary-foreground" />
                  </div>
                  <span className="text-sm font-semibold">ProjectFlow</span>
                </div>
                <div className="space-y-1">
                  {['Dashboard', 'Projetos', 'Equipe', 'Configurações'].map((item, i) => (
                    <div
                      key={item}
                      className={`text-xs px-3 py-2 rounded-md ${i === 0 ? 'bg-primary/10 text-primary font-medium' : 'text-muted-foreground'}`}
                    >
                      {item}
                    </div>
                  ))}
                </div>
              </div>
              {/* Main content mock */}
              <div className="flex-1 p-4 sm:p-6 space-y-4">
                {/* Stats row */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { label: 'Tarefas', value: '24', color: 'text-primary' },
                    { label: 'A Fazer', value: '8', color: 'text-status-todo' },
                    { label: 'Em Progresso', value: '10', color: 'text-status-in-progress' },
                    { label: 'Concluídas', value: '6', color: 'text-status-completed' },
                  ].map((s) => (
                    <div key={s.label} className="p-3 rounded-lg border border-border">
                      <p className="text-[10px] text-muted-foreground">{s.label}</p>
                      <p className={`text-lg font-bold ${s.color}`}>{s.value}</p>
                    </div>
                  ))}
                </div>
                {/* Gantt mock */}
                <div className="rounded-lg border border-border p-4 space-y-2">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-xs font-medium">Gráfico Gantt</p>
                    <div className="flex gap-1">
                      {['Dia', 'Semana', 'Mês'].map((v, i) => (
                        <div key={v} className={`text-[10px] px-2 py-0.5 rounded ${i === 0 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>
                          {v}
                        </div>
                      ))}
                    </div>
                  </div>
                  {[
                    { name: 'Design da Interface', w: '60%', ml: '5%', color: 'bg-status-completed' },
                    { name: 'Backend API', w: '45%', ml: '15%', color: 'bg-status-in-progress' },
                    { name: 'Testes', w: '30%', ml: '35%', color: 'bg-status-todo' },
                    { name: 'Deploy', w: '20%', ml: '55%', color: 'bg-status-review' },
                  ].map((bar) => (
                    <div key={bar.name} className="flex items-center gap-3">
                      <span className="text-[10px] text-muted-foreground w-28 truncate shrink-0">{bar.name}</span>
                      <div className="flex-1 h-5 bg-muted/50 rounded relative">
                        <div
                          className={`h-full rounded ${bar.color} opacity-80`}
                          style={{ width: bar.w, marginLeft: bar.ml }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="border-y border-border bg-muted/30">
        <div className="max-w-5xl mx-auto px-6 py-12 grid grid-cols-2 sm:grid-cols-4 gap-8">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-2xl sm:text-3xl font-bold text-primary">{stat.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold">Tudo que você precisa</h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
              Ferramentas completas para planejar, executar e acompanhar seus projetos do início ao fim.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 gap-8">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-xl border border-border bg-card hover:border-primary/30 transition-colors"
              >
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 border-t border-border bg-muted/20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold">Como funciona</h2>
          </div>
          <div className="grid sm:grid-cols-3 gap-8">
            {[
              { step: '1', icon: CheckCircle2, title: 'Crie sua conta', description: 'Cadastro rápido e gratuito. Em segundos você já está dentro.' },
              { step: '2', icon: BarChart3, title: 'Monte seus projetos', description: 'Adicione projetos, tarefas e membros da equipe. Defina prazos e responsáveis.' },
              { step: '3', icon: Clock, title: 'Acompanhe o progresso', description: 'Visualize tudo no Gantt chart. Saiba exatamente o que está no prazo e o que precisa de atenção.' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="h-14 w-14 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <item.icon className="h-7 w-7 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold">Pronto para começar?</h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Crie sua conta gratuitamente e comece a gerenciar seus projetos hoje.
          </p>
          <div className="mt-8">
            <Button size="lg" className="gap-2 text-base px-8" asChild>
              <Link href="/register">
                Criar Conta Grátis
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-muted/30">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-md bg-primary flex items-center justify-center">
              <GanttChart className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-semibold">ProjectFlow</span>
          </div>
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} ProjectFlow. Todos os direitos reservados.
          </p>
        </div>
      </footer>
    </div>
  )
}
