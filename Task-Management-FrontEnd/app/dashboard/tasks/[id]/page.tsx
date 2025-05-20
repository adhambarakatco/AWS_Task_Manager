"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import axios from "axios"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { uploadFile } from "../new/page"
import { Loader2 } from "lucide-react"
import { motion } from "framer-motion"

import { Badge } from "@/components/ui/badge"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { useToast } from "@/hooks/use-toast"
import { ArrowLeft, Calendar, CheckCircle2, Clock, Download, FileUp, Trash2,Edit } from "lucide-react"



const handleViewObject = async (objectKey:any) => {
  try {
    const res = await axios.get("/api/getFile", {
      params: {
        object_Key: objectKey
      }
    });
    const url = res.data.url
    window.open(url, "_blank"); // Opens in a new tab
  } catch (error) {
    console.error("Error generating S3 URL:", error);
    alert("Failed to open the file.");
  }
};



export default function TaskDetailPage({ params }: { params: any }) {
  const router = useRouter()
  const { toast } = useToast()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [task, setTask] = useState<any>({})
  const [attachments, setAttachments] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const resolvedParams: any = React.use(params) // unwrap promise
  const id = resolvedParams.id

  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const token = localStorage.getItem("id_token")
  //       const res = await axios.get(`${base_api}/${id}`, {
  //         headers: { Authorization: `Bearer ${token}` },
  //       })
  //       console.log(res.data)
  //       setTask(res.data.task)
  //       setAttachments(res.data.attachments)
  //     } catch (err: any) {
  //       setError(err.message || "Error fetching data")
  //     } finally {
  //       setLoading(false)
  //     }
  //   }
  //   fetchData()
  // }, [id])



  useEffect(() => {
    if (!id) return; // skip fetching if id is undefined/null

    const fetchData = async () => {
      try {
        const token = localStorage.getItem("id_token");
        const res = await axios.get("/api/getTask", {
          params: { task_id: id },
          headers: { Authorization: token },
        });
        console.log(res.data);
        setTask(res.data.task);
        setAttachments(res.data.attachments);
      } catch (err:any) {
        setError(err.message || "Error fetching data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);





  if (loading) return  (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background text-primary">
      <motion.div
        className="flex items-center gap-3"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <span className="text-2xl font-semibold">Preparing your workspace</span>
      </motion.div>
    </div>
  )
  if (error) return <p>Error: {error}</p>

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { year: "numeric", month: "short", day: "numeric" }
    return new Date(dateString).toLocaleDateString(undefined, options)
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-500 text-white"
      case "medium":
        return "bg-yellow-500 text-white"
      case "low":
        return "bg-green-500 text-white"
      default:
        return "bg-secondary text-secondary-foreground"
    }
  }

  // const handleDeleteTask = async () => {
  //   try {
  //     setIsSubmitting(true)
  //     const token = localStorage.getItem("id_token")
  //     await axios.delete(`${base_api}/${id}`, {
  //       headers: { Authorization: `Bearer ${token}` },
  //     })
  //     toast({ title: "Task deleted", description: "The task has been deleted successfully" })
  //     router.push("/dashboard/tasks")
  //   } catch {
  //     toast({ title: "Error deleting task", description: "Please try again later", variant: "destructive" })
  //   } finally {
  //     setIsSubmitting(false)
  //   }
  // }


  const handleDeleteTask = async () => {
    try {
      setIsSubmitting(true);
      const token = localStorage.getItem("id_token");
  
      await axios.delete(`/api/deleteTask`, {
        params: { task_id: id },
        headers: { Authorization: token }, 
      });
  
      toast({
        title: "Task deleted",
        description: "The task has been deleted successfully",
      });
  
      router.push("/dashboard/tasks");
    } catch (err) {
      toast({
        title: "Error deleting task",
        description: "Please try again later",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // const handleToggleComplete = async () => {
  //   try {
  //     setIsSubmitting(true)
      
  //     const token = localStorage.getItem("id_token")
  //     if (!token) throw new Error("No token found")

  //     await axios.put(
  //       `${base_api}/${id}`,
  //       {
  //         title: task?.title || "",         
  //         description: task?.description || "",
  //         dueDate: task?.dueDate || "",
  //         priority: task?.priority || "low",
  //         completed: !task?.completed
  //       },
  //       {
  //         headers: { Authorization: `Bearer ${token}` },
  //       }
  //     )
  //     toast({
  //       title: `Task ${!task?.completed ? "completed" : "reopened"}`,
  //       description: `The task has been ${!task?.completed ? "marked as completed" : "reopened"}.`,
  //     })
  //   } catch {
  //     toast({ title: "Error updating task", description: "Please try again later", variant: "destructive" })
  //   } finally {
  //     setIsSubmitting(false)
  //   }
  // }



  const handleToggleComplete = async () => {
    try {
      setIsSubmitting(true);
  
      const token = localStorage.getItem("id_token");
      if (!token) throw new Error("No token found");
      await axios.put(
        `/api/updateTask`,
        {
          title: task?.title || "",
          description: task?.description || "",
          dueDate: task?.dueDate || "",
          priority: task?.priority || "low",
          completed: !task?.completed,
        },
        {
          params: { task_id: id },
          headers: {
            Authorization: token,
          },
        }
      );
  
      toast({
        title: `Task ${!task?.completed ? "completed" : "reopened"}`,
        description: `The task has been ${!task?.completed ? "marked as completed" : "reopened"}.`,
      });
    } catch {
      toast({
        title: "Error updating task",
        description: "Please try again later",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-2xl font-bold">{task?.title || "No title"}</h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Task Details</CardTitle>
            <div className="mt-2">
              <Badge variant="outline" className={task?.priority ? getPriorityColor(task.priority) : "bg-secondary text-secondary-foreground"}>
                {task?.priority ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) + " Priority" : "No Priority"}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium">Description</h3>
                <p className="mt-1 text-muted-foreground">{task?.description || "No description"}</p>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Due: {task?.dueDate ? formatDate(task.dueDate) : "N/A"}</span>
                </div>
                <div className="flex items-center gap-2">
          <CheckCircle2 className={`h-4 w-4 ${task?.completed ? "text-green-600" : "text-muted-foreground"}`} />
          <span className="text-sm">
            {task?.completed ? "Completed" : "Not Completed"}
          </span>
        </div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={() => router.push(`/dashboard/tasks/edit/${id || ""}`)}>
              Edit Task
            </Button>
            <div className="flex gap-2">
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" disabled={isSubmitting}>
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                    <AlertDialogDescription>This action cannot be undone. This will permanently delete the task and all associated data.</AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleDeleteTask} className="bg-destructive text-destructive-foreground">
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              <Button onClick={handleToggleComplete} disabled={isSubmitting}>
          <CheckCircle2 className="mr-2 h-4 w-4" />
          {task?.completed ? "Mark Incomplete" : "Mark Complete"}
        </Button>
            </div>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Attachments</CardTitle>
          </CardHeader>
          <CardContent>
          {attachments?.length > 0 ? (
  <div className="space-y-2">
    {attachments.map((fileName:any) => (
      <div key={fileName} className="flex items-center justify-between p-3 border rounded-md">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-md bg-muted">
            <FileUp className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-medium">{fileName.split('/').pop()}</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => handleViewObject(fileName)}
        >
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      </div>
    ))}
  </div>
) : (
  <div className="flex h-[100px] items-center justify-center rounded-lg border border-dashed">
    <div className="flex flex-col items-center gap-1 text-center">
      <div className="text-sm font-medium">No attachments</div>
      <div className="text-xs text-muted-foreground">This task has no attached files</div>
    </div>
  </div>
)}
          </CardContent>
          <CardFooter>
  <div className="w-full">
    <label
      htmlFor="add-attachment"
      className="flex items-center justify-center w-full p-2 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 hover:bg-muted"
    >
      <div className="flex items-center gap-2">
        <FileUp className="h-4 w-4" />
        <span className="text-sm">Add Attachment</span>
      </div>
      <input
        id="add-attachment"
        type="file"
        className="hidden"
        multiple
        // onChange={(e) => {
        //   const files = e.target.files
        //   if (!files) return
        //   Array.from(files).forEach(file => {
        //     uploadFile(file,id)
        //   })
        //   e.target.value = ""
        // }}
        onChange={async (e) => {
          const files = e.target.files
          if (!files) return
        
          for (const file of Array.from(files)) {
            try {
              await uploadFile(file, id)
              toast({
                title: "File uploaded",
                description: `${file.name} uploaded successfully.`,
              })
            } catch (err) {
              toast({
                title: "Upload failed",
                description: `${file.name} failed to upload.`,
                variant: "destructive",
              })
            }
          }
        
          e.target.value = ""
        }}
        
      />
    </label>
  </div>
</CardFooter>
        </Card>
      </div>
    </DashboardLayout>
  )
}
