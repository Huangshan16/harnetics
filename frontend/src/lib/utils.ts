import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function severityKey(value: string | null | undefined) {
  return (value ?? '').trim().toLowerCase()
}

export function severityLabel(value: string | null | undefined) {
  const key = severityKey(value)
  if (!key) return 'Unknown'
  return `${key.slice(0, 1).toUpperCase()}${key.slice(1)}`
}
