import axios from 'axios';

const api_url=process.env.API_BASE_URL!

export async function DELETE(req: Request) {
    const token = req.headers.get('authorization');
    const url = new URL(req.url);
    const task_id = url.searchParams.get('task_id');
    console.log(task_id)
  
    if (!token) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
    }
  
    if (!task_id) {
      return new Response(JSON.stringify({ error: 'Missing task_id' }), { status: 400 });
    }
  
    console.log("DELETE START");
  
    try {
      const response = await axios.delete(`${api_url}/${task_id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      console.log("DELETE WORKS");
  
      // Return success response properly
      return new Response(JSON.stringify({ success: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    } catch (error: any) {
      return new Response(JSON.stringify({ error: error.message }), { status: 500 });
    }
  }


