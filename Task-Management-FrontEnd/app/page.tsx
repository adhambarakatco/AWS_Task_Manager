"use client"

import { Button } from "@/components/ui/button"
import Link from "next/link"
import { motion } from "framer-motion"

const cognito_url:any = process.env.NEXT_PUBLIC_COGNITO_URL

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-background via-muted/50 to-background">
      <header className="border-b bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
          <h1 className="text-xl font-bold tracking-tight">Task Master</h1>
          <Button asChild variant="default">
            <Link href={cognito_url} >
              Access Dashboard
            </Link>
          </Button>
        </div>
      </header>

      <main className="flex-1">
        <section className="relative py-28 md:py-40 text-center">
          <div className="container mx-auto px-4 md:px-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="max-w-3xl mx-auto space-y-6"
            >
              <h2 className="text-5xl md:text-6xl font-extrabold tracking-tight leading-tight">
              Designed for flow. Built with care.
              </h2>
              <p className="text-muted-foreground text-lg md:text-xl">
                Task Master keeps you organized, productive, and stress-free. Securely manage your tasks with AWS integration — wherever you are.
              </p>
              <div className="flex justify-center pt-4">
                <Button asChild size="lg">
                  <Link href={cognito_url}>
                    Get Started
                  </Link>
                </Button>
              </div>
            </motion.div>

            {/* Optional visual placeholder */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6, duration: 0.7 }}
              className="mt-16"
            >
              <div className="mx-auto w-full max-w-4xl rounded-xl border shadow-sm bg-background p-6 text-left">
                <p className="text-muted-foreground">
                  📝 Imagine your task dashboard here: priorities, statuses, deadlines. <br />
                  Beautifully organized. Totally in control.
                </p>
              </div>
            </motion.div>
          </div>
        </section>

        {/* <section className="w-full bg-muted py-16 md:py-24">
          <div className="container mx-auto px-4 md:px-6 text-center space-y-4">
            <h3 className="text-2xl font-semibold tracking-tight">
              Designed for flow. Built with care.
            </h3>
          </div>
        </section> */}
      </main>

      <footer className="border-t py-6 bg-background">
        <div className="container mx-auto flex flex-col items-center justify-center text-sm text-muted-foreground">
          © 2025 Task Master. All rights reserved.
        </div>
      </footer>
    </div>
  )
}
