"use client"

import { useState,useEffect } from "react"
import { useRouter } from "next/navigation"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Plus, Search } from "lucide-react"
import { TaskCard } from "@/components/task-card"
import { Loader2 } from "lucide-react"
import { motion } from "framer-motion"
import {jwtDecode} from "jwt-decode"
import axios from "axios"

const base_api="https://c8r35uina5.execute-api.eu-central-1.amazonaws.com/prod/tasks"

const base_apigw=process.env.NEXT_PUBLIC_API_BASE_URL || ""

export default function TasksPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const token =localStorage.getItem('id_token')
  //       const res = await axios.get(base_api,
  //         {
  //           headers: {
  //             Authorization: `Bearer ${token}`,
  //           },
  //         })
  //       console.log('API response data:', res.data)
  //       setTasks(res.data.tasks || [])
  //     } catch (err: any) {
  //       setError(err.message || "Error fetching data")
  //     } finally {
  //       setLoading(false)
  //     }
  //   }

  //   fetchData()
  // }, [])





  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('id_token');
        if (!token) {
          setError('No token found');
          setLoading(false);
          return;
        }
  
        const res = await axios.get('/api/getTasks', {
          headers: {
            Authorization: token,
          },
        });
  
        if(res.data.count==0){
          setTasks([]);

        }
        else{
          setTasks(res.data.tasks || []);
        }
       
      } catch (err: any) {
        setError(err.message || 'Error fetching data');
      } finally {
        setLoading(false);
      }
    };
  
    fetchData();
  }, []);

  if (loading) return (
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


  

  const filteredTasks = tasks.filter((task) => {
    if (activeTab === "completed" && !task.completed) {
      return false
    }

    if (
      searchQuery &&
      !task.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !task.description.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false
    }

    return true
  })

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h1 className="text-3xl font-bold">Tasks</h1>
          <Button onClick={() => router.push("/dashboard/tasks/new")}>
            <Plus className="mr-2 h-4 w-4" />
            New Task
          </Button>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search tasks..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <Tabs defaultValue="all" onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Tasks</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
          </TabsList>
          <div className="mt-6">
            {filteredTasks.length > 0 ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {filteredTasks.map((task) => (
                  <TaskCard key={task.task_id} task={task} />
                ))}
              </div>
            ) : (
              <div className="flex h-[300px] items-center justify-center rounded-lg border border-dashed">
                <div className="flex flex-col items-center gap-1 text-center">
                  <div className="text-sm font-medium">No tasks found</div>
                  <div className="text-sm text-muted-foreground">
                    {searchQuery ? "Try adjusting your search" : "Create a new task to get started"}
                  </div>
                  {!searchQuery && (
                    <Button
                      className="mt-4"
                      variant="outline"
                      onClick={() => router.push("/dashboard/tasks/new")}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      New Task
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
