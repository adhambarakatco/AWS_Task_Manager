'use client'
import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function callback() {
  const router = useRouter()

  useEffect(() => {
    if (typeof window !== "undefined") {
      const hash = window.location.hash.substring(1)
      const params = new URLSearchParams(hash)

      const idToken = params.get("id_token")
      const accessToken = params.get("access_token")
      const expiresIn = params.get("expires_in")

      if (idToken) {
        localStorage.setItem("id_token", idToken)
        if (accessToken) {
          localStorage.setItem("access_token", accessToken)
        }
        if (expiresIn) {
          localStorage.setItem("expires_in", expiresIn)
        }

        router.replace("/dashboard/tasks")
      } else {
        router.replace("/login")
      }
    }
  }, [router])

  return <p>Loading...</p>
}
