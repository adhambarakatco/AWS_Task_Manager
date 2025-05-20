"use client"
import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { format } from "date-fns"
import { CalendarIcon, FileUp } from "lucide-react"
import { cn } from "@/lib/utils"
import { useToast } from "@/hooks/use-toast"
import axios from "axios"
import { todo } from "node:test"




 export async function uploadFile (file:any,task_id:string){
  try{
    const token = localStorage.getItem("id_token")
    const res = await axios.post(
      "/api/uploadFile",
      {
          file_name:file.name,
          task_id:task_id
      },
      {
        headers: {
          Authorization: token,
        },
      }
    )

    console.log(res.data)

    const upload = await axios.put(res.data, file, {
      headers: {
        "Content-Type": file.type, // Make sure this matches the file
      },
    });
    
    
  
  
  }

    
    catch (err: any) {
      console.log(err)
    }

  





}

export default function NewTaskPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [date, setDate] = useState<Date | undefined>(undefined)
  const [attachments, setAttachments] = useState<File[]>([])
  const [priority, setPriority] = useState("medium");
  const [error, setError] = useState<string | null>(null)
  const [response,setResponse] =useState<any>(null)
  let task_id=""

 

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsSubmitting(true)
    const title = (document.getElementById("title") as HTMLInputElement).value;
    const description = (document.getElementById("description") as HTMLTextAreaElement).value;



    try {
      const token = localStorage.getItem("id_token")
      const res = await axios.post("/api/createTask",
  {
    "title": title,
    "description": description,
    "dueDate":date,
    "priority":priority
  },
  {
    headers: {
      Authorization: token,
    },
  }
);

  task_id=res.data
    } catch (err: any) {
      setError(err.message || "Error Creating Task")
    }


    

  if (attachments) {
    try{
      attachments.forEach(async (a)=> await uploadFile(a,task_id))
  
    }
    catch(err: any) {
        setError(err.message || "Error Uploading Attachment")
      }
      

  }
  

  router.push('/dashboard/tasks')






  }




  

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setAttachments((prev) => [...prev, ...newFiles])
    }
  }

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <h1 className="text-3xl font-bold">Create New Task</h1>

        <Card>
          <form onSubmit={handleSubmit}>
            <CardHeader>
              <CardTitle>Task Details</CardTitle>
              <CardDescription>Fill in the details for your new task</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="title">Task Title</Label>
                <Input id="title" placeholder="Enter task title" required disabled={isSubmitting} />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Enter task description"
                  className="min-h-[120px]"
                  disabled={isSubmitting}
                />
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {/* <div className="grid gap-2">
                  <Label htmlFor="status">Status</Label>
                  <Select disabled={isSubmitting} defaultValue="todo" onValueChange={setStatus}>
                    <SelectTrigger id="status">
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="todo">To Do</SelectItem>
                      <SelectItem value="in-progress">In Progress</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                </div> */}

                <div className="grid gap-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select disabled={isSubmitting} defaultValue="medium" onValueChange={setPriority}>
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

            


              

              <div className="grid gap-2">
                <Label>Attachments</Label>
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="dropzone-file"
                    className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-muted/50 hover:bg-muted"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <FileUp className="w-8 h-8 mb-3 text-muted-foreground" />
                      <p className="mb-2 text-sm text-muted-foreground">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-muted-foreground">PDF, PNG, JPG, GIF up to 10MB</p>
                    </div>
                    <input
                      id="dropzone-file"
                      type="file"
                      className="hidden"
                      disabled={isSubmitting}
                      multiple
                      onChange={handleFileChange}
                    />
                  </label>
                </div>

                {attachments.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <Label>Uploaded Files</Label>
                    <div className="rounded-md border">
                      {attachments.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border-b last:border-b-0">
                          <div className="flex items-center gap-2">
                            <FileUp className="h-4 w-4 text-muted-foreground" />
                            <div>
                              <p className="text-sm font-medium">{file.name}</p>
                              <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeAttachment(index)}
                            disabled={isSubmitting}
                          >
                            Remove
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline" type="button" onClick={() => router.back()} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Task"}
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </DashboardLayout>
  )
}
