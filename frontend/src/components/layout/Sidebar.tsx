// frontend/src/components/Layout/Sidebar.tsx
'use client'
import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { X } from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: '📊' },
  { name: 'Brands', href: '/brands', icon: '🏢' },
  { name: 'Mentions', href: '/mentions', icon: '💬' },
  { name: 'Analytics', href: '/analytics', icon: '📈' },
  { name: 'Crisis Center', href: '/crisis', icon: '🚨' },
]

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

export function Sidebar({ isOpen = false, onClose }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      {/* Mobile sidebar overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-gray-900/80" onClick={onClose} />
          <div className="fixed inset-y-0 left-0 z-50 w-72 bg-white">
            <div className="flex h-16 shrink-0 items-center justify-between px-6">
              <h1 className="text-xl font-bold text-gray-900">Brand Intelligence</h1>
              <button
                type="button"
                className="-m-2.5 p-2.5 text-gray-700"
                onClick={onClose}
              >
                <span className="sr-only">Close sidebar</span>
                <X className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>
            <nav className="flex flex-1 flex-col px-6 pb-4">
              <ul role="list" className="flex flex-1 flex-col gap-y-7">
                <li>
                  <ul role="list" className="-mx-2 space-y-1">
                    {navigation.map((item) => (
                      <li key={item.name}>
                        <Link
                          href={item.href}
                          onClick={onClose}
                          className={`${
                            pathname === item.href
                              ? 'bg-gray-50 text-indigo-600'
                              : 'text-gray-700 hover:text-indigo-600 hover:bg-gray-50'
                          } group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold`}
                        >
                          <span className="text-xl">{item.icon}</span>
                          {item.name}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-lg">
          <div className="flex h-16 shrink-0 items-center">
            <h1 className="text-xl font-bold text-gray-900">Brand Intelligence</h1>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={`${
                          pathname === item.href
                            ? 'bg-gray-50 text-indigo-600'
                            : 'text-gray-700 hover:text-indigo-600 hover:bg-gray-50'
                        } group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold`}
                      >
                        <span className="text-xl">{item.icon}</span>
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </>
  )
}