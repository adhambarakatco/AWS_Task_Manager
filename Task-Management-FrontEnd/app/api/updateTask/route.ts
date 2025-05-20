import axios from 'axios';

const api_url=process.env.API_BASE_URL!

export async function PUT(req:any) {
    const token = req.headers.get('authorization');
    const body = await req.json();
    const url = new URL(req.url);
    const task_id = url.searchParams.get('task_id');
    console.log(task_id)
  
    if (!token) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
    }
  
    if (!task_id) {
      return new Response(JSON.stringify({ error: 'Missing task_id' }), { status: 400 });
    }

  try {
    console.log("update Start")
    const response = await axios.put(`${api_url}/${task_id}`,body, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      console.log("update Done")
      return new Response(
        JSON.stringify({
          message: `Task ${task_id} updated successfully.`,
          updatedTask: response.data.tasks, // or `task` if your API returns a single task
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      );
  } catch (error:any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
}
