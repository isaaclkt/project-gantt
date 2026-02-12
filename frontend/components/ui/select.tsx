'use client'

import * as React from 'react'
import { createPortal } from 'react-dom'
import { CheckIcon, ChevronDownIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SelectContextValue {
  open: boolean
  setOpen: (open: boolean) => void
  value: string
  displayLabel: string
  onValueChange: (value: string, label: string) => void
  triggerRef: React.RefObject<HTMLButtonElement | null>
}

const SelectContext = React.createContext<SelectContextValue | undefined>(undefined)

function useSelectContext() {
  const context = React.useContext(SelectContext)
  if (!context) {
    throw new Error('Select components must be used within a Select')
  }
  return context
}

interface SelectProps {
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  children: React.ReactNode
  disabled?: boolean
}

function Select({ value, defaultValue, onValueChange, children }: SelectProps) {
  const [open, setOpen] = React.useState(false)
  const [internalValue, setInternalValue] = React.useState(defaultValue || '')
  const [displayLabel, setDisplayLabel] = React.useState('')
  const triggerRef = React.useRef<HTMLButtonElement>(null)

  const currentValue = value !== undefined ? value : internalValue

  const handleValueChange = React.useCallback((newValue: string, label: string) => {
    if (value === undefined) {
      setInternalValue(newValue)
    }
    setDisplayLabel(label)
    onValueChange?.(newValue)
    setOpen(false)
  }, [value, onValueChange])

  const contextValue = React.useMemo(() => ({
    open,
    setOpen,
    value: currentValue,
    displayLabel,
    onValueChange: handleValueChange,
    triggerRef,
  }), [open, currentValue, displayLabel, handleValueChange])

  return (
    <SelectContext.Provider value={contextValue}>
      {children}
    </SelectContext.Provider>
  )
}

function SelectGroup({ children }: { children: React.ReactNode }) {
  return <div role="group">{children}</div>
}

interface SelectValueProps {
  placeholder?: string
  children?: React.ReactNode
}

function SelectValue({ placeholder, children }: SelectValueProps) {
  const { value, displayLabel } = useSelectContext()
  // Priority: children > displayLabel (from clicking) > placeholder
  if (children) {
    return <span>{children}</span>
  }
  if (displayLabel) {
    return <span>{displayLabel}</span>
  }
  return <span className="text-muted-foreground">{placeholder}</span>
}

interface SelectTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  size?: 'sm' | 'default'
}

function SelectTrigger({ className, size = 'default', children, ...props }: SelectTriggerProps) {
  const { open, setOpen, triggerRef } = useSelectContext()

  return (
    <button
      ref={triggerRef}
      type="button"
      role="combobox"
      aria-expanded={open}
      data-slot="select-trigger"
      data-size={size}
      className={cn(
        "border-input data-[placeholder]:text-muted-foreground flex w-full items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-2 text-sm whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
        size === 'default' ? 'h-9' : 'h-8',
        className,
      )}
      onClick={() => setOpen(!open)}
      {...props}
    >
      {children}
      <ChevronDownIcon className={cn("size-4 opacity-50 transition-transform", open && "rotate-180")} />
    </button>
  )
}

interface SelectContentProps extends React.HTMLAttributes<HTMLDivElement> {
  position?: 'popper' | 'item-aligned'
}

function SelectContent({ className, children, position = 'popper', ...props }: SelectContentProps) {
  const { open, setOpen, triggerRef } = useSelectContext()
  const [mounted, setMounted] = React.useState(false)
  const [position_, setPosition_] = React.useState({ top: 0, left: 0, width: 0 })
  const contentRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    setMounted(true)
    return () => setMounted(false)
  }, [])

  React.useEffect(() => {
    if (open && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect()
      setPosition_({
        top: rect.bottom + window.scrollY + 4,
        left: rect.left + window.scrollX,
        width: rect.width,
      })
    }
  }, [open, triggerRef])

  React.useEffect(() => {
    if (!open) return

    const handleClickOutside = (e: MouseEvent) => {
      if (
        contentRef.current &&
        !contentRef.current.contains(e.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(e.target as Node)
      ) {
        setOpen(false)
      }
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [open, setOpen, triggerRef])

  if (!mounted || !open) return null

  return createPortal(
    <div
      ref={contentRef}
      data-slot="select-content"
      className={cn(
        'bg-popover text-popover-foreground z-50 min-w-[8rem] overflow-hidden rounded-md border shadow-md',
        className
      )}
      style={{
        position: 'absolute',
        top: position_.top,
        left: position_.left,
        minWidth: position_.width,
      }}
      {...props}
    >
      <div className="p-1 max-h-[300px] overflow-y-auto">
        {children}
      </div>
    </div>,
    document.body
  )
}

function SelectLabel({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="select-label"
      className={cn('text-muted-foreground px-2 py-1.5 text-xs font-semibold', className)}
      {...props}
    />
  )
}

interface SelectItemProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string
  disabled?: boolean
}

function SelectItem({ className, children, value, disabled, ...props }: SelectItemProps) {
  const { value: selectedValue, onValueChange } = useSelectContext()
  const itemRef = React.useRef<HTMLDivElement>(null)
  const isSelected = selectedValue === value

  const handleClick = React.useCallback(() => {
    if (disabled) return
    const label = itemRef.current?.textContent || value
    onValueChange(value, label)
  }, [disabled, value, onValueChange])

  return (
    <div
      ref={itemRef}
      role="option"
      aria-selected={isSelected}
      data-slot="select-item"
      data-disabled={disabled || undefined}
      className={cn(
        'relative flex w-full cursor-pointer items-center rounded-sm py-1.5 pr-8 pl-2 text-sm outline-none select-none hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground',
        disabled && 'pointer-events-none opacity-50',
        isSelected && 'bg-accent',
        className
      )}
      onClick={handleClick}
      {...props}
    >
      <span className="absolute right-2 flex size-3.5 items-center justify-center">
        {isSelected && <CheckIcon className="size-4" />}
      </span>
      {children}
    </div>
  )
}

function SelectSeparator({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="select-separator"
      className={cn('bg-border -mx-1 my-1 h-px', className)}
      {...props}
    />
  )
}

function SelectScrollUpButton() {
  return null
}

function SelectScrollDownButton() {
  return null
}

export {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectScrollDownButton,
  SelectScrollUpButton,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
}
