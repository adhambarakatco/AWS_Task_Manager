import Link from "next/link"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Clock, FileText, CheckCircle2 } from "lucide-react" // Added CheckCircle2 icon

export function TaskCard({ task }: any) {
  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A"
    const options: Intl.DateTimeFormatOptions = { year: "numeric", month: "short", day: "numeric" }
    return new Date(dateString).toLocaleDateString(undefined, options)
  }

  const getPriorityColor = (priority?: string) => {
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

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-medium">{task?.title || "Untitled Task"}</CardTitle>
          <Badge className={getPriorityColor(task?.priority)}>
            {task?.priority
              ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) + " Priority"
              : "No Priority"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-2">{task?.description || "No description available."}</p>

        <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>Due: {formatDate(task?.dueDate)}</span>
          </div>
          {task?.completed ? (
            <Badge variant="outline" className="flex items-center gap-1 bg-green-100 text-green-800">
              <CheckCircle2 className="h-4 w-4" />
              Completed
            </Badge>
          ) : (
            <Badge variant="outline" className="flex items-center gap-1 bg-gray-200 text-gray-700">
              Incomplete
            </Badge>
          )}
        </div>
      </CardContent>
      <CardFooter>
        <Button asChild variant="outline" className="w-full">
          <Link href={`/dashboard/tasks/${task?.task_id || ""}`}>
            <FileText className="mr-2 h-4 w-4" />
            View Details
          </Link>
        </Button>
      </CardFooter>
    </Card>
  )
}
