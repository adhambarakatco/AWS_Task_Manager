"use client"
import React, { useEffect, useState } from "react"
import { usePathname, useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { LogOut, CheckSquare, User } from "lucide-react"
import { cn } from "@/lib/utils"
import {jwtDecode} from "jwt-decode"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const router = useRouter()
  const [username, setUsername] = useState<string>("User")

  useEffect(() => {
    const token = localStorage.getItem("id_token")
    if (token) {
      try {
        const decoded: any = jwtDecode(token)
        if (decoded) {
          setUsername(decoded.given_name)
        }
      } catch (error) {
        console.error("Failed to decode JWT", error)
      }
    }
  }, [])

  const signOut = () => {
    localStorage.removeItem("id_token")
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
  
    // // Redirect to Cognito Hosted UI logout endpoint
    // const domain = "https://task-master-app-dev.auth.eu-central-1.amazoncognito.com"
    // const clientId = "2cpvfe8dsbqjekbn3ij7bp22p7"
    // const redirectUri = encodeURIComponent("http://localhost:3000/")
  
    window.location.href = `http://localhost:3000/`
  }
  

  const navigation = [
    { name: "Tasks", href: "/dashboard/tasks", icon: CheckSquare },
  ]

  return (
    <div className="flex min-h-screen"> {/* Changed to flex for horizontal layout */}
      {/* Sidebar */}
      <aside className="w-64 border-r bg-background md:block flex-shrink-0"> {/* Made it visible and fixed width */}
        <div className="flex h-full flex-col gap-2 p-4">
          <div className="flex items-center gap-2 pb-4">
            <User className="h-8 w-8 text-primary" />
            <span className="font-bold text-lg">Welcome {username}</span>
          </div>
          <nav className="flex flex-col gap-1 py-2">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium",
                  pathname === item.href
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>
          <Button onClick={signOut} className="mt-auto">
            <LogOut className="mr-2 h-4 w-4" />
            Log out
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="sticky top-0 z-40 border-b bg-background">
          <div className="max-w-[1280px] mx-auto flex h-16 items-center px-6"> {/* Adjusted padding */}
            <h1 className="font-semibold text-xl">{pathname.split('/').pop() === 'tasks' ? 'Tasks' : 'Dashboard'}</h1> {/* Simple dynamic title */}
            {/* You can add more header content here if needed */}
          </div>
        </header>
        <main className="flex-1 p-4 md:p-6">{children}</main>
      </div>
    </div>
  )
}