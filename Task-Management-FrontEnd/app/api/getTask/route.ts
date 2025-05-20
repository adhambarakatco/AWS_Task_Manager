import axios from 'axios';

const api_url=process.env.API_BASE_URL!


export async function GET(req:any) {
  const token = req.headers.get('authorization');
  const url = new URL(req.url);
  const task_id = url.searchParams.get('task_id');
  if (!token) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
  }

  if (!task_id) {
    return new Response(JSON.stringify({ error: 'Missing task_id' }), { status: 400 });
  }

  try {
    console.log("START")
    const response = await axios.get(`${api_url}/${task_id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    console.log("GET TASK WORKING")

    return Response.json({task:response.data.task,attachments:response.data.attachments}
    );
  } catch (error:any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
}