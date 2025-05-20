"use client"

import React, { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { format } from "date-fns"
import axios from "axios"
import { useToast } from "@/hooks/use-toast"

export default function UpdateTaskPage({ params }: { params: any }) {
  const router = useRouter()
  const { toast } = useToast()

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [title, setTitle] = useState("")
  const [completed, setcompleted] = useState(Boolean)
  const [description, setDescription] = useState("")
  const [date, setDate] = useState<Date | undefined>(undefined)
  const [priority, setPriority] = useState("medium")
  const [error, setError] = useState<string | null>(null)

  const resolvedParams: any = React.use(params) // unwrap promise
    const id = resolvedParams.id

  // useEffect(() => {
  //   async function fetchTask() {
  //     try {
  //       const token = localStorage.getItem("id_token")
  //       if (!token) throw new Error("No token found")

  //       const res = await axios.get(`${base_api}/${id}`, {
  //         headers: { Authorization: `Bearer ${token}` },
  //       })
  //       const task = res.data.task
  //       setTitle(task.title || "")
  //       setDescription(task.description || "")
  //       setPriority(task.priority || "medium")
  //       setDate(task.dueDate ? new Date(task.dueDate) : undefined)
  //     } catch (err: any) {
  //       setError(err.message || "Failed to fetch task")
  //     }
  //   }
  //   if (id) fetchTask()
  // }, [id])




  useEffect(() => {
    if (!id) return; // Skip if no task ID
  
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("id_token");
        if (!token) throw new Error("No token found");
  
        const res = await axios.get("/api/getTask", {
          params: { task_id: id },
          headers: { Authorization: token },
        });
  
        const task = res.data.task;
        setTitle(task.title || "");
        setDescription(task.description || "");
        setPriority(task.priority || "medium");
        setDate(task.dueDate ? new Date(task.dueDate) : undefined);
        setcompleted(task.completed || true)
      } catch (err: any) {
        setError(err.message || "Error fetching task data");
      }
    };
  
    fetchData();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      const token = localStorage.getItem("id_token")
      if (!token) throw new Error("No token found")

      await axios.put(
        `/api/updateTask`,
        {
          title,
          description,
          dueDate: date,
          priority,
          completed
        },
        {params: { task_id: id },
        headers: { Authorization: token},
        }
      )

      toast({
        title: "Task updated",
        description: "Your task has been updated successfully.",
      })

      router.push("/dashboard/tasks")
    } catch (err: any) {
      setError(err.message || "Failed to update task")
      setIsSubmitting(false)
    }
  }




  // try {
  //   setIsSubmitting(true);

  //   const token = localStorage.getItem("id_token");
  //   if (!token) throw new Error("No token found");
  //   await axios.put(
  //     `/api/updateTask`,
  //     {
  //   title,
  //   description,
  //   dueDate: date,
  //   priority,
  //   completed:true
  // },
  //     {
  //       params: { task_id: id },
  //       headers: {
  //         Authorization: token,
  //       },
  //     }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <h1 className="text-3xl font-bold">Update Task</h1>

        <Card>
          <form onSubmit={handleSubmit}>
            <CardHeader>
              <CardTitle>Task Details</CardTitle>
              <CardDescription>Edit the details of your task</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && <p className="text-red-600">{error}</p>}

              <div className="grid gap-2">
                <Label htmlFor="title">Task Title</Label>
                <Input
                  id="title"
                  placeholder="Enter task title"
                  required
                  disabled={isSubmitting}
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Enter task description"
                  className="min-h-[120px]"
                  disabled={isSubmitting}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="grid gap-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select disabled={isSubmitting} value={priority} onValueChange={setPriority}>
                    <SelectTrigger id="priority">
                      <SelectValue placeholder="Select priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="dueDate">Due Date</Label>
                  <Input
                    type="date"
                    id="dueDate"
                    value={date ? format(date, "yyyy-MM-dd") : ""}
                    onChange={(e) => setDate(e.target.value ? new Date(e.target.value) : undefined)}
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            </CardContent>

            <CardFooter className="flex justify-between">
              <Button variant="outline" type="button" onClick={() => router.back()} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Updating..." : "Update Task"}
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </DashboardLayout>
  )
}
